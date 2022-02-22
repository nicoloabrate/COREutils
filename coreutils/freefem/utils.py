"""
Author: N. Abrate.

File: FreeFEM++.py

Description: Set of methods related to FreeFEM++ code.

"""

import numpy as np
import pandas as pd


def readfeinput(fname, datamap, NG, matrixfmt=False):
    """
    Read input FreeFEM++ fespace file.

    Parameters
    ----------
    fname : TYPE
        DESCRIPTION.
    datamap : TYPE
        DESCRIPTION.
    NG : TYPE
        DESCRIPTION.
    matrixfmt : TYPE, optional
        DESCRIPTION. The default is False.

    Raises
    ------
    OSError
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # TODO: read list of files and convert in dict their content
    lines = []
    linesapp = lines.append
    with open(fname) as f:
        for i, line in enumerate(f):
            if i == 0:
                n_elem = int(line)
            else:
                linesapp(line.split("\n"))

    data = pd.DataFrame([string[0].split() for string in lines]).to_numpy()
    data = data.reshape((data.size, ), order='C')
    data = data[0:n_elem]
    data = data.astype(np.float)

    idx = 0
    for key in datamap:

        if 'scatt' in key.lower():
            for g in range(0, NG):
                idx = idx+NG
        else:
            idx = idx+NG

    # index sanity check
    nass = int(n_elem/idx)
    if nass != n_elem/idx:
        raise OSError("%s maybe incomplete. No. of assembly and data mismatch"
                      % fname)

    parameters = {}
    skip = 1
    for key in datamap:

        for g in range(0, NG):

            if 'scatt' in key.lower():
                for ge in range(0, NG):
                    dictkey = key+"%d%d" % (g+1, ge+1)
                    tmp = data[0+nass*(skip-1):skip*nass]
                    # reshape to make FF lexicographic order consistent with ours
                    Nx = int(np.sqrt(nass))
                    tmp = tmp.reshape((Nx, Nx), order='F')
                    if matrixfmt is False:
                        tmp = tmp.flatten(order='C')
                    parameters[dictkey] = tmp
                    skip = skip+1

            else:
                dictkey = key+"%d" % (g+1)
                tmp = data[0+nass*(skip-1):skip*nass]
                # reshape to make FF lexicographic order consistent with ours
                Nx = int(np.sqrt(nass))
                tmp = tmp.reshape((Nx, Nx), order='F')
                if matrixfmt is False:
                    tmp = tmp.flatten(order='C')

                parameters[dictkey] = tmp
                skip = skip+1

    return parameters


def readfearray(fname, datamap):
    """
    Read input FreeFEM++ fespace file.

    Parameters
    ----------
    fname : TYPE
        DESCRIPTION.
    datamap : TYPE
        DESCRIPTION.
    NG : TYPE
        DESCRIPTION.
    matrixfmt : TYPE, optional
        DESCRIPTION. The default is False.

    Raises
    ------
    OSError
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # TODO: read list of files and convert in dict their content
    lines = []
    linesapp = lines.append
    with open(fname) as f:
        for i, line in enumerate(f):
            linesapp(line.split("\n"))

    data = pd.DataFrame([string[0].split() for string in lines]).to_numpy()
    data = data.reshape((data.size, ), order='C')
    data = data.astype(np.float)

    return data


def makesnapshot(parameters, which=None, ismat=False):
    """
    Convert parameters dict into numpy array.

    Parameters
    ----------
    parameters : TYPE
        DESCRIPTION.
    which : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    if which is None:
        which = parameters.keys()

    data = []
    datamap = {}
    idx = 0
    for ikey, key in enumerate(which):

        v = parameters[key]
        if v.ndim == 2:
            v = v.flatten(order='C')

        if ikey == 0:
            nel = len(v)

        data = np.concatenate((data, v))
        datamap[key] = [idx, idx+nel]
        idx = idx + nel

    return data, datamap


def rot(v, angle, ismat=True):
    """
    Rotate matrix/array v of "angle"-degree.

    Parameters
    ----------
    v : TYPE
        DESCRIPTION.
    angle : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    for ik, key in enumerate(v.keys()):

        mat = v[key]
        # convert in matrix
        if ismat is False:
            if ik == 0:
                Nx = int(np.sqrt(len(mat)))

            mat = mat.reshape((Nx, Nx))

        nn = int(angle/90)
        mat = np.rot90(mat, k=-nn)
        v[key] = mat

    return v
