import os
import json
import logging
from collections import OrderedDict
from coreutils.tools.utils import uppcasedict, lowcasedict
from coreutils.frenetic.frenetic_namelists import FreneticNamelist

CImandatory = ('Tf_Tc',)
GEmandatory = ('dim', 'shape', 'lattice_pitch') # 'lattice_pitch' only if shape!='1D', 'cuts' only in '1D'
NEmandatory = ('filename', 'assemblynames', 'rotation', 'energygrid', 'cuts')
THmandatory = ('bcfile', 'massflowrate', 'temperature', 'rotation', 'pressure', 'bcnames', 'htdata')
# TODO add check on data types (e.g., rotation and dim must be integers)
# set to value in dict if this key is missing
setToValue = {
                'CI': {
                        'power': 1.,
                        'nSnap': 1,
                        'tEnd': 0.,
                        'coolant': None,
                      },
                'GE': {
                        'rotation': None,
                        'pin': None,
                        'lattice': None,
                        'assembly': None,
                      },
                'NE': {
                        'NEdata': None,
                        'labels': None,
                        'splitz': None,
                        'egridname': None,
                        'xscuts': None,
                        'zcuts': None,
                        'fren': True,
                        'config': None,
                        'replace': None,
                        'replaceSA': None,
                        'assemblylabel': None,
                        'axplot': False,
                        'radplot': False,
                        'worksheet': False,
                      },
                'TH': {
                        'fren': True,
                        'replace': None,
                        'nelems': None,
                        'nelref': None,
                        'zref': None,
                        'zmesh': None,
                        'HTconfig': None,
                        'BCconfig': None,
                        'BClabels': None,
                        'HTlabels' : None,
                        'BCs': None,
                        'axplot': False,
                        'radplot': False,
                        'worksheet': False,
                       },
                "FRENETIC-NML": None
              }

def parse(inp):
    """
    Parse .json input file.

    Parameters
    ----------
    inp : str
        Path for .json file.

    Raises
    ------
    ParserError
        -Input file path is missing!
        -File %s is missing!
        -Something is wrong with the input .json file!

    Returns
    -------
    CIargs : list
        List of CI module arguments.
    NEargs : list
        List of NE module arguments.
    THargs : list
        List of TH module arguments.
    """
    if isinstance(inp, str) is False:
        raise ParserError("Input file path is missing!")

    # parse .json file
    try:
        with open(inp) as f:
            try:
                inp = json.load(f)
            except json.JSONDecodeError as err:
                print(err.args[0])
                logging.critical(err.args[0])
                raise ParserError(f"{err.args[0]} in {inp}")
    except FileNotFoundError:
        raise ParserError(f"File {inp} not found!")

    # assign default args
    NEargs, THargs = None, None
    FRNargs = None

    # parse .json dict
    if isinstance(inp, dict):

        # convert into an upper-case dict
        inp = uppcasedict(inp)
        # check NE, TH and other optional dictionaries
        if 'CI' in inp.keys():
            CIargs = __parseCI(inp['CI'])
        else:
            raise ParserError('CI input part is missing in .json file!')

        if 'GE' in inp.keys():
            GEargs = __parseGE(inp['GE'])
        else:
            raise ParserError('GE input part is missing in .json file!')

        dim = GEargs['dim']

        if 'NE' in inp.keys():
            NEargs = __parseNE(inp['NE'], dim)

        if 'TH' in inp.keys():
            if dim != 3:
                logging.warning(f'cannot write TH input for {dim}-D core')
            THargs = __parseTH(inp['TH'])

        if 'FRENETIC-NML' in inp.keys():
            FRNargs = __parseFRN(inp['FRENETIC-NML'], CIargs, GEargs, NEargs, THargs)

    else:
        raise ParserError(f"Input file {f} was not dumped into a dict by `json.load` method!")

    return CIargs, GEargs, NEargs, THargs, FRNargs


def __parseCI(inp):
    """
    Parse CI input from .json dict.

    Parameters
    ----------
    inp : dict
        json input.

    Raises
    ------
    ParserError
        Missing mandatory arguments.

    Returns
    -------
    CIargs : dict
        Dict of arguments.

    """
    # assign keys
    CIargs = {}
    # make keys lower case to be case insensitive
    inp = lowcasedict(inp)
    for k in inp.keys():
        CIargs[k] = inp[k]
    # --- parse mandatory keys
    for k in CImandatory:
        k = k.casefold()
        if k in inp.keys():
            pass
        else:
            if (k == 'tf_tc') and CIargs['dim'] != 3:
                CIargs[k.lower()] = [300]
            else:
                raise ParserError(f'Mandatory {k} key missing in CI input file!')                            

    # check non-mandatory arguments
    if 'tEnd'.lower() not in inp.keys():
        logging.info("No final simulation time is provided in CI!")

    if 'nSnap'.lower() not in inp.keys():
        logging.info("No number of time profiles is provided in CI!")

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['CI'].items():
        if k.lower() not in CIargs.keys():
            CIargs[k.lower()] = v
    
    if 'trans' not in CIargs.keys():
        CIargs['trans'] = True if CIargs['tEnd'.lower()] != 0 else False

    return CIargs


def __parseGE(inp):
    """
    Parse GE input from .json dict.

    Parameters
    ----------
    inp : dict
        json input.

    Raises
    ------
    ParserError
        Missing mandatory arguments.

    Returns
    -------
    GEargs : dict
        Dict of arguments.

    """
    # assign keys
    GEargs = {}
    # make keys lower case to be case insensitive
    inp = lowcasedict(inp)
    for k in inp.keys():
        GEargs[k] = inp[k]
    # --- parse mandatory keys
    for k in GEmandatory:
        k = k.casefold()
        if k in inp.keys():
            pass
        else:
            if k == 'shape' and GEargs['dim'] == 1:
                GEargs[k] = '1D'
            elif k == 'lattice_pitch' and GEargs['dim'] == 1:
                GEargs[k] = 1.1547005383792517**0.5
                pass
            else:
                raise ParserError(f'Mandatory {k} key missing in GE input file!')                            

    # check non-mandatory arguments
    if GEargs['dim'] != 1:
        warn_keys = ["pin", "lattice", "assembly"]
        for k in warn_keys:
            if k.lower() not in inp.keys():
                logging.info(f"No {k} info is provided in GE!")

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['GE'].items():
        if k.lower() not in GEargs.keys():
            GEargs[k.lower()] = v

    return GEargs


def __parseNE(inp, dim):
    """
    Parse NE input from .json dict.

    Parameters
    ----------
    inp : dict
        NE input.

    Raises
    ------
    ParserError
        Missing mandatory arguments.

    Returns
    -------
    NEargs : dict
        Dict of arguments.

    """
    # make keys lower case to be case insensitive
    inp = lowcasedict(inp)
    # assign keys
    NEargs = {}
    for k in inp.keys():
        if k == 'cuts':
            NEargs['xscuts'] = inp[k]
        else:
            NEargs[k] = inp[k]
    # --- parse mandatory keys
    for k in NEmandatory:
        k = k.casefold()
        if k in inp.keys():
            pass
        else:
            # check mandatory args not needed for 1D and 2D
            if k in ['filename', 'assemblynames', 'rotation']:
                if dim == 1:
                    NEargs['filename'] = None
                    if 'assemblynames' not in NEargs.keys():
                        NEargs['assemblynames'] = ["slab"]
                    NEargs['rotation'] = None
                else:
                    raise ParserError(f"Mandatory '{k}' key missing in NE input file!")
            elif k == 'cuts':
                if dim != 2:
                    raise ParserError(f"Mandatory '{k}' key missing in NE input file!")
            elif k in ['energygrid', 'egridname']:
                pass
            else:
                raise ParserError(f"Mandatory '{k}' key missing in NE input file!")

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['NE'].items():
        if k.lower() not in NEargs.keys():
            NEargs[k.lower()] = v 

    # sanity check
    if dim != 1:
        if not os.path.isabs(NEargs['filename']):
            raise ParserError(f'NE input: filename must be an absolute path to file!')

    return NEargs


def __parseTH(inp):
    """
    Parse TH input from .json dict.

    Parameters
    ----------
    inp : dict
        TH input.

    Raises
    ------
    ParserError
        Missing mandatory arguments.

    Returns
    -------
    THargs : dict
        Dict of arguments.

    """
    # make keys lower case to be case insensitive
    inp = lowcasedict(inp)
    # assign keys
    THargs = {}
    for k in inp.keys():
        THargs[k] = inp[k]
    # --- parse mandatory keys
    for k in THmandatory:
        k = k.casefold()
        if k in inp.keys():
            pass
        else:
            # check mandatory args not needed for 1D case
            if k in ['bcnames']:
                # in case of misplelling
                if 'bcnames' in inp.keys():
                    THargs[k.lower()] = inp['bcnames']
                else:
                    raise ParserError(f"Mandatory '{k}' key missing in TH input file!")
            else:
                raise ParserError(f"Mandatory '{k}' key missing in TH input file!")

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['TH'].items():
        if k.lower() not in THargs.keys():
            THargs[k.lower()] = v

    # input sanity check
    if "nelems" in THargs:
        if "zmesh" not in THargs:
            raise ParserError("zmesh args needed for TH mesh!")
        if "nelref" in THargs:
            if "zref" not in THargs:
                raise ParserError("`zref` list with beginning and end of the mesh refinement zone is missing!")

    htdata = THargs["htdata"]
    mandatory_args = ["htc_corr", "frict_corr", "chan_coupling_corr"]

    if htdata is not None:
        if "data" not in htdata.keys():
            raise ParserError("'data' dict missing in HTdata dict in input .json file!")
        else:
            if isinstance(htdata["data"], dict):
                for thtype, v in htdata["data"].items():
                    v = lowcasedict(v)
                    for k in mandatory_args:
                        if k.casefold() not in v.keys():
                            raise ParserError(f"{k} is missing in HTdata['data'] dict in input .json!")
            else:
                raise ParserError("'data' key in HTdata dict in input .json should be associated with a dict!")

    return THargs


def __parseFRN(inp, CIargs, GEargs, NEargs, THargs):
    """
    Parse FRENETIC keywords from .json dict.

    Parameters
    ----------
    inp : dict
        FRENETIC-NML input.
    CIargs : dict
        Common input arguments.
    GEargs : dict
        Geometry input arguments.
    NEargs : dict
        Neutronic input arguments.
    THargs : dict
        Thermal-hydraulic input arguments.

    Raises
    ------
    ParserError
        Missing mandatory arguments.

    Returns
    -------
    FRNargs : dict
        Dict of arguments.

    """
    # make keys lower case to be case insensitive
    inp = lowcasedict(inp)
    # initialise FreneticNamelist
    frenml = FreneticNamelist()
    # assign default values
    FRNargs = FreneticNamelist().DefaultValue

    # --- check existence of mandatory keys or assign derivate values (many of them assigned later)
    NE = False if NEargs is None else True
    TH = False if THargs is None else True
    for inptype, lst in frenml.mandatory.items(): # check each input type
        for k in lst: # check each kw
            # check each argument
            if inptype == "NE":
                if k.lower() not in inp.keys():
                    if k == "SplitZ":
                        if "splitz" in NEargs.keys():
                            pass
                        elif CIargs["dim"] == 2:
                            pass
                        else:
                            raise ParserError(f"'splitz' kw is mandatory for FRENETIC-NML and is missing in .json file!")
                    else:
                        raise ParserError(f"Mandatory '{k}' key missing in FRENETIC-NML dict!")
            elif inptype == "TH":
                if GEargs["dim"] == 3 and TH:
                    if k.lower() not in inp.keys():
                        if k.lower() == "xLengt".lower():
                            if "zmesh" in THargs.keys():
                                pass
                            else:
                                raise ParserError(f"'zmesh' kw is mandatory for FRENETIC-NML but is missing in .json file!")
                        else:
                            raise ParserError(f"Mandatory '{k}' key missing in FRENETIC-NML dict!")
            else:
                raise ParserError(f"Consistency check for {inptype} not implemented!")

    # override default value with keys provided by the user
    lowcaseFRNargs = [s.lower() for s in FRNargs.keys()]
    cassensFRNargs = [s for s in FRNargs.keys()]
    for k, v in inp.items():
        idx = lowcaseFRNargs.index(k.lower())
        FRNargs[cassensFRNargs[idx]] = v 

    return FRNargs


class ParserError(Exception):
    pass