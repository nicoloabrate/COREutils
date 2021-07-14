"""
Author: N. Abrate.

File: utils.py

Description: Set of utilities.
"""
import json


def parse(inp):
    """
    Parse .json input file.

    Parameters
    ----------
    inp : str
        Path for .json file.

    Raises
    ------
    OSError
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
        raise OSError("Input file path is missing!")

    # parse .json file
    with open(inp) as f:

        try:
            inp = json.load(f)
        except json.JSONDecodeError as err:
            print(err.args[0])
            raise OSError(err.args[0]+' in %s' % inp)
        except FileNotFoundError:
            raise OSError("File %s is missing!" % inp)

    # assign default args
    NEargs, THargs = None, None

    # parse .json dict
    if isinstance(inp, dict):

        # check NE/PH and TH namelists
        if 'CI' in inp.keys():
            CIargs = __parseCI(inp['CI'])
        else:
            raise OSError('CI input part is missing in .json file!')

        if 'NE' in inp.keys():
            NEargs = __parseNE(inp['NE'])

        if 'TH' in inp.keys():
            THargs = __parseTH(inp['TH'])

    return CIargs, NEargs, THargs


def __parseCI(CIinp):
    """
    Parse CI input from .json dict.

    Parameters
    ----------
    CIinp : dict
        CI input.

    Raises
    ------
    OSError
        Missing mandatory arguments.

    Returns
    -------
    NEargs : list
        List of arguments.

    """
    # check mandatory arguments
    if 'tEnd' in CIinp.keys():
        tEnd = CIinp['tEnd']
    else:
        tEnd = 0
        print("WARNING: No final simulation time is provided in CI!")

    if 'nProf' in CIinp.keys():
        nProf = CIinp['nProf']
    else:
        nProf = 1
        print("WARNING: No number of time profiles is provided in CI!")

    if 'shape' in CIinp.keys():
        shape = CIinp['shape']
    else:
        raise OSError("Assembly shape is missing in CI!")

    if 'power' in CIinp.keys():
        power = CIinp['power']
    else:
        power = None

    if shape != '1D':
        if 'pitch' in CIinp.keys():
            pitch = CIinp['pitch']
        else:
            raise OSError("Core pitch is missing in CI!")
    
        if 'trans' in CIinp.keys():
            trans = CIinp['trans']
        else:
            trans = True
    else:
        pitch, trans = 1, False

    CIargs = [tEnd, nProf, pitch, shape, power, trans]

    return CIargs


def __parseNE(NEinp):
    """
    Parse NE input from .json dict.

    Parameters
    ----------
    NEinp : dict
        NE input.

    Raises
    ------
    OSError
        Missing mandatory arguments.

    Returns
    -------
    NEargs : list
        List of arguments.

    """
    # check mandatory arguments
    if 'filename' in NEinp.keys():
        geinp = NEinp['filename']
    else:
        raise OSError("No core geometry input file is provided!")

    if 'assemblynames' in NEinp.keys():
        assemblynames = NEinp['assemblynames']
    else:
        raise OSError("Core assembly names are missing!")

    if 'assemblylabel' in NEinp.keys():
        assemblylabel = NEinp['assemblylabel']
    else:
        assemblylabel = None

    if 'rotation' in NEinp.keys():
        rotation = NEinp['rotation']
    else:
        rotation = 0
        raise OSError('No rotation angle provided!')

    if 'replace' in NEinp.keys():
        replace = NEinp['replace']
    else:
        replace = None

    if 'config' in NEinp.keys():
        config = NEinp['config']
    else:
        config = None

    if 'cuts' in NEinp.keys():
        cuts = {}
        if 'mycuts' in NEinp.keys():
            mycuts = NEinp['mycuts']
        else:
            mycuts = None

        cuts['mycuts'] = mycuts
        cuts['xscuts'] = NEinp['cuts']

    else:
        cuts = None

    if 'splitz' in NEinp.keys():
        splitz = NEinp['splitz']
    else:
        splitz = None

    if 'fren' in NEinp.keys():
        fren = NEinp['fren']
    else:
        fren = False

    if 'regionsplot' in NEinp.keys():
        regionslegendplot = NEinp['regionsplot']
    else:
        regionslegendplot = None

    if 'NEdata' in NEinp.keys():
        NEdata = NEinp['NEdata']
    else:
        NEdata = None

    NEargs = [geinp, rotation, assemblynames, assemblylabel,
              replace, cuts, splitz, config, fren, regionslegendplot, NEdata]

    return NEargs


def __parseTH(THinp):
    """
    Parse TH input from .json dict.

    Parameters
    ----------
    THinp : dict
        TH input.

    Raises
    ------
    OSError
        Missing mandatory arguments.

    Returns
    -------
    THargs : list
        List of arguments.

    """
    # check mandatory arguments
    if 'coolingzonesfile' in THinp.keys():
        geinp = THinp['coolingzonesfile']
    else:
        # check if name is mispelled
        if 'coolingzonefile' in THinp.keys():
            geinp = THinp['coolingzonefile']

        else:
            raise OSError("No core cooling zones input file is provided!")

    if 'rotation' in THinp.keys():
        rotation = THinp['rotation']
    else:
        rotation = 0

    if 'massflowrates' in THinp.keys():
        mflow = THinp['massflowrates']
    else:
        raise OSError('"massflowrates" is missing!')

    if 'temperatures' in THinp.keys():
        temperatures = THinp['temperatures']
    else:
        raise OSError('"temperatures" is missing!')

    if 'pressures' in THinp.keys():
        pressures = THinp['pressures']
    else:
        raise OSError('"pressures" is missing!')

    if 'coolingzonenames' in THinp.keys():
        cznames = THinp['coolingzonenames']
    else:
        # check if name is mispelled
        if 'coolingzonesnames' in THinp.keys():
            cznames = THinp['coolingzonenames']

        else:
            raise OSError("Core cooling zones names are missing!")

    if 'fren' in THinp.keys():
        fren = THinp['fren']
    else:
        fren = False

    if 'THdata' in THinp.keys():
        THdata = THinp['THdata']
    else:
        THdata = None

    if 'replace' in THinp.keys():
        replace = THinp['replace']
    else:
        replace = None

    if 'boundaryconditions' in THinp.keys():
        bcs = THinp['boundaryconditions']
    else:
        bcs = None

    THargs = [geinp, rotation, cznames, replace, fren,
              bcs, mflow, temperatures, pressures, THdata]

    return THargs


def uncformat(data, std, fmtn=".5e", fmts=None):

    if len(data) != len(std):
        raise ValueError("Data and std dimension mismatch!")

    if std is None:
        try:
            # data are ufloat
            inptup = [(d.n, d.s) for d in data]
        except OSError:
            raise TypeError("If std is not provided, data must be ufloat type")
    else:
        inptup = list(zip(data, std))

    percent = False

    if '%' in fmtn:
        fmtn.replace('%', '')

    if fmts is None:
        fmt = "{:%s}%s{:%s}" % (fmtn, u"\u00B1", fmtn)
    else:
        if '%' in fmts:
            percent = True
            fmts = fmts.replace('%', '')
            fmt = "{:%s}%s{:%s}%%" % (fmtn, u"\u00B1", fmts)
        else:
            fmt = "{:%s}%s{:%s}" % (fmtn, u"\u00B1", fmts)

    out = []
    outapp = out.append
    for tup in inptup:
        d, s = tup
        if percent is True:
            s = s*100
        outapp(fmt.format(d, s))

    return out


def fortranformatter(value, type):
    """
    Convert python format to Fortran-wise format.

    Parameters
    ----------
    value : int or float
        Value to be converted.
    type : str
        Value output type.

    Returns
    -------
    str
        Output string.

    """
    if type == 'int':
        return "%d" % int(value)
    elif type == 'float':
        return ("%.10e" % value)
    elif type == 'double':
        return ("%.10e" % value).replace('e', 'd')