"""
Author: N. Abrate.

File: utils.py

Description: Set of utilities.
"""
import json
# from coreutils.utils import OSError


def parse(inp):

    if isinstance(inp, str) is False:
        raise OSError("Input file path is missing!")

    # parse .json file
    with open(inp) as f:
        try:
            inp = json.load(f)
        except FileNotFoundError:
            raise OSError("File %s is missing!" % inp)

    if isinstance(inp, dict):

        # check mandatory arguments
        if 'filename' in inp.keys():
            geinp = inp['filename']
        else:
            raise OSError("No core geometry input file is provided!")

        if 'pitch' in inp.keys():
            pitch = inp['pitch']
        else:
            raise OSError("Core pitch is missing!")

        if 'assemblynames' in inp.keys():
            assemblynames = inp['assemblynames']
        else:
            raise OSError("Core assembly names are missing!")

        if 'rotation' in inp.keys():
            rotation = inp['rotation']
        else:
            rotation = 0

        if 'replace' in inp.keys():
            replace = inp['replace']
        else:
            replace = None

        if 'config' in inp.keys():
            config = inp['config']
        else:
            config = None

        if 'cuts' in inp.keys():
            cuts = {}
            if 'mycuts' in inp.keys():
                mycuts = inp['mycuts']
            else:
                mycuts = None

            cuts['mycuts'] = mycuts
            cuts['xscuts'] = inp['cuts']

        else:
            cuts = None

        if 'fren' in inp.keys():
            fren = inp['fren']
        else:
            fren = False

        if 'fill' in inp.keys():
            fill = inp['fill']
        else:
            fill = None

        if 'regionsplot' in inp.keys():
            regionslegendplot = inp['regionsplot']
        else:
            regionslegendplot = None
    else:
        raise OSError("Something is wrong with the input .json file!")

    args = [geinp, rotation, pitch, assemblynames, replace, cuts, config,
            fren, fill, regionslegendplot]

    return args


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
