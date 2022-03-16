"""
Author: N. Abrate.

File: utils.py

Description: Set of utilities.
"""
import os
import json
from collections import OrderedDict, UserDict

# TODO use sth like
# to check for mandatory argument and use dict to easily extend
# the number of keys

CImandatory = ('dim', 'shape', 'pitch', 'Tc', 'Tf') # 'pitch' only if shape!='1D', 'cuts' only in '1D'
NEmandatory = ('filename', 'assemblynames', 'rotation',
               'energygrid', 'cuts')
THmandatory = ('coolingzonefile', 'massflowrates', 'temperatures', 'rotation',
               'pressures', 'coolingzonenames')
# set to value in dict if this key is missing
setToValue = {
                'CI': {
                        'power': 1,
                        'nSnap': 1,
                        'tEnd': 0,
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
                      },
                'TH': {
                        'fren': True,
                        'THdata': None, 
                        'replace': None, 
                        'boundaryconditions': None,
                       }
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
    try:
        with open(inp) as f:
            try:
                inp = json.load(f)
            except json.JSONDecodeError as err:
                print(err.args[0])
                raise OSError(err.args[0]+' in %s' % inp)
    except FileNotFoundError:
        raise OSError(f"File {inp} not found!")

    # assign default args
    NEargs, THargs = None, None

    # parse .json dict
    if isinstance(inp, dict):

        # check NE/PH and TH namelists
        if 'CI' in inp.keys():
            CIargs = __parseCI(inp['CI'])
        else:
            raise OSError('CI input part is missing in .json file!')

        dim = CIargs['dim']
        if 'NE' in inp.keys():
            NEargs = __parseNE(inp['NE'], dim)

        if 'TH' in inp.keys():
            if dim != 3:
                print(f'WARNING: cannot write TH input for {dim}-D core')
            THargs = __parseTH(inp['TH'])

    return CIargs, NEargs, THargs


def __parseCI(inp):
    """
    Parse CI input from .json dict.

    Parameters
    ----------
    inp : dict
        json input.

    Raises
    ------
    OSError
        Missing mandatory arguments.

    Returns
    -------
    NEargs : dict
        Dict of arguments.

    """
    # assign keys
    CIargs = {}
    for k in inp.keys():
        CIargs[k] = inp[k]
    # --- parse mandatory keys            
    for k in CImandatory:
        if k in inp.keys():
            pass
        else:
            if k == 'shape' and CIargs['dim'] == 1:
                CIargs[k] = '1D'
            elif k == 'pitch' and CIargs['dim'] == 1:
                CIargs[k] = 1.1547005383792517**0.5
                pass
            elif (k == 'Tf' or k == 'Tc') and CIargs['dim'] != 3:
                CIargs[k] = [300]
            else:
                raise OSError(f'Mandatory {k} key missing in CI input file!')                            

    # check non-mandatory arguments
    if 'tEnd' not in inp.keys():
        print("WARNING: No final simulation time is provided in CI!")

    if 'nSnap' not in inp.keys():
        print("WARNING: No number of time profiles is provided in CI!")

    if 'nSnap' not in inp.keys():
        print("WARNING: No number of time profiles is provided in CI!")

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['CI'].items():
        if k not in CIargs.keys():
            CIargs[k] = v
    
    if 'trans' not in CIargs.keys():
        CIargs['trans'] = True if CIargs['tEnd'] != 0 else False

    return CIargs


def __parseNE(inp, dim):
    """
    Parse NE input from .json dict.

    Parameters
    ----------
    inp : dict
        NE input.

    Raises
    ------
    OSError
        Missing mandatory arguments.

    Returns
    -------
    NEargs : dict
        Dict of arguments.

    """
    # assign keys
    NEargs = {}
    for k in inp.keys():
        if k == 'cuts':
            NEargs['xscuts'] = inp[k]
        else:
            NEargs[k] = inp[k]
    # --- parse mandatory keys
    for k in NEmandatory:
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
                    raise OSError(f'Mandatory {k} key missing in NE input file!')
            elif k == 'cuts':
                if dim != 2:
                    raise OSError(f'Mandatory {k} key missing in NE input file!')
            elif k in ['energygrid', 'egridname']:
                pass
            else:
                raise OSError(f'Mandatory "{k}" key missing in NE input file!')

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['NE'].items():
        if k not in NEargs.keys():
            NEargs[k] = v 

    # sanity check
    if dim != 1:
        if not os.path.isabs(NEargs['filename']):
            raise OSError(f'NE input: filename must be an absolute path to file!')

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
    OSError
        Missing mandatory arguments.

    Returns
    -------
    THargs : dict
        Dict of arguments.

    """
    # assign keys
    THargs = {}
    for k in inp.keys():
        THargs[k] = inp[k]
    # --- parse mandatory keys
    for k in THmandatory:
        if k in inp.keys():
            pass
        else:
            # check mandatory args not needed for 1D case
            if k in ['coolingzonesnames']:
                # in case of misplelling
                if 'coolingzonenames' in inp.keys():
                    THargs[k] = inp['coolingzonenames']
                else:
                    raise OSError(f'Mandatory {k} key missing in CI input file!')
            else:
                raise OSError(f'Mandatory {k} key missing in CI input file!')

    # set missing (not mandatory) keys to default value
    for k, v in setToValue['TH'].items():
        if k not in THargs.keys():
            THargs[k] = v 
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
    
class MyDict(OrderedDict):

    def reverse(self):
        if len(set(self.values())) != len(self.values()):
            raise OSError("Cannot reverse dict, values not unique!")
        return dict(zip(self.values(), self.keys()))
