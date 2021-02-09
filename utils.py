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
        if 'NE' in inp.keys():
            NEargs = __parseNE(inp['NE'])

        if 'TH' in inp.keys():
            THargs = __parseTH(inp['TH'])

        # input sanity check
        if THargs is not None and NEargs is not None:
            if inp['NE']['pitch'] != inp['TH']['pitch']:
                raise OSError('NE and TH pitch must be equal! Check .json!')

            if inp['NE']['shape'] != inp['TH']['shape']:
                raise OSError('NE and TH shape must be equal! Check .json!')

    return NEargs, THargs


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

    if 'pitch' in NEinp.keys():
        pitch = NEinp['pitch']
    else:
        raise OSError("Core pitch is missing!")

    if 'shape' in NEinp.keys():
        shape = NEinp['shape']
    else:
        raise OSError("Assembly shape is missing!")

    if 'assemblynames' in NEinp.keys():
        assemblynames = NEinp['assemblynames']
    else:
        raise OSError("Core assembly names are missing!")

    if 'rotation' in NEinp.keys():
        rotation = NEinp['rotation']
    else:
        rotation = 0

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

    NEargs = [geinp, rotation, pitch, shape, assemblynames, replace, cuts,
              config, fren, regionslegendplot, NEdata]

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

    if 'pitch' in THinp.keys():
        pitch = THinp['pitch']
    else:
        raise OSError("Core pitch is missing!")

    if 'shape' in THinp.keys():
        shape = THinp['shape']
    else:
        raise OSError("Assembly shape is missing!")

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

    THargs = [geinp, rotation, pitch, shape, cznames, replace, fren,
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
