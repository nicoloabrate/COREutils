"""
Author: N. Abrate.

File: ffplot.py

Description: Set of methods to plot FreeFEM++ output, based on ffmatlib.

"""
import os
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection

class mesh:
    """
    Read mesh file created with savemesh(Th,"2dmesh.msh").

    Parameters
    ----------
    fname : str
        Path to file containing FF++ mesh.

    Returns
    -------
    None.

    """
    def __init__(self, fname, verbosity):

        lines = []
        linesapp = lines.append
        if os.path.exists(fname):
            # read each line
            with open(fname) as f:
                for i, line in enumerate(f):
                    linesapp(line.split("\n")[0])

            # check format
            meshformat = None
            if 'MeshVersionFormatted' in lines[0]:
                meshformat = 'MEDIT'
            else:
                tests = lines[0].split(' ')
                if len(tests) > 0:
                    tests = [int(i) for i in tests]
                    if len(tests) == 3:
                        meshformat = 'FF++'

            # readmesh
            if meshformat == 'FF++':

                dimension = len(lines[1].split(' '))-1
                if dimension !=2:
                    raise OSError('Only 2D meshes are supported!')

                nv, nt, nbe = tests
                # verteces
                p = np.zeros((3, nv))*np.nan
                idx = 0
                for i in range(1, nv+1):
                    idx = idx + 1
                    p[:, i-1] = [float(j) for j in lines[idx].split(' ')]

                # triangles
                t = np.zeros((4, nt))*np.nan
                for i in range(1, nt+1):
                    idx = idx + 1
                    t[:, i-1] = [float(j) for j in lines[idx].split(' ')]


                # boundaries
                b = np.zeros((3, nbe))*np.nan
                for i in range(1, nbe+1):
                    idx = idx + 1
                    b[:, i-1] = [float(j) for j in lines[idx].split(' ')]

                # look for labels
                labels = np.unique(b[2, :])
                nlabels = len(labels)
                # look for regions
                regions = np.unique(t[3, :])
                nregions = len(regions)

            elif meshformat == 'MEDIT':
                print('Under development!')
            else:
                raise OSError('mesh format unknown!')

        else:
            raise OSError('%s not found!' % fname)

        self.points, self.triangles, self.boundaries = p, t, b
        self.nv, self.nbe, self.nt = nv, nbe, nt
        self.labels, self.regions = labels, regions


class ffdata:
    def __init__(self, ffnames, vhname):

        if os.path.exists(vhname):
            vh = np.loadtxt(vhname)
        else:
            raise OSError('%s not found!' % vhname)

        datadict = {}
        for f in ffnames:
            if os.path.exists(f):
                try:
                    data = np.loadtxt(f)
                except ValueError:
                    data = np.loadtxt(f, dtype=complex,
                                      converters={0: lambda
                                                  s: complex(s.decode().replace('+-', '-'))})
                f = f.split(os.filesep)[-1]
                datadict[f] = data
            else:
                raise OSError('%s not found!' % f)
        # add dict with names in ffnames!
        self.data = datadict
        self.vh = vh

def ffplot(ffdata, mesh, Vh, surf=False, dispmesh=False,
           boundary=True, clevels=10, **kwargs):

    xp, yp, xmsh, ymsh = PrepareMesh(mesh.points, mesh.triangles)
    xyrawdata = rowvec(ffdata)
    elementType, xydata = ConvertPdeData(mesh, Vh, xyrawdata)
    # Based on the Element Space create various Meshes for plotting and interpolation
    xdata, xdataz, ydata, ydataz = PrepareCoordinates(elementType, xmesh,
                                                      ymesh, true)
    # Convert the color data according corresponding to xdata, xdataz and interpolation
    cdata, cdataz, cdatainterpn = PrepareData(elementType, triangles, xydata,
                                              xmesh, ymesh, true)


def PrepareMesh(points, triangles):
    """
    Define mesh parameters for plotting.

    Parameters
    ----------
    points : TYPE
        DESCRIPTION.
    triangles : TYPE
        DESCRIPTION.

    Returns
    -------
    xp : TYPE
        DESCRIPTION.
    yp : TYPE
        DESCRIPTION.
    xmsh : TYPE
        DESCRIPTION.
    ymsh : TYPE
        DESCRIPTION.

    """
    xp, yp = points[0, :], points[1, :]
    xmsh = np.array([xp[triangles[0, :]],
                     xp[triangles[1, :]],
                     xp[triangles[2, :]]])
    ymsh = np.array([yp[triangles[0, :]],
                     yp[triangles[1, :]],
                     yp[triangles[2, :]]])
    return xp, yp, xmsh, ymsh
    return xp, yp, xmsh, ymsh


def rowvec(S):
    """
    Transpose array if needed.

    Parameters
    ----------
    S : TYPE
        DESCRIPTION.

    Returns
    -------
    S : TYPE
        DESCRIPTION.

    """
    s1, s2 = S.shape
    if s1 > s2:
        S = S.T
    return S


def ConvertPdeData(mesh, Vh, xyrawdata):
    """
    Detect FE type and return data in points-triangles format.

    Parameters
    ----------
    mesh : TYPE
        DESCRIPTION.
    Vh : TYPE
        DESCRIPTION.
    xyrawdata : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    nt = mesh.nt
    ndim, ndof = xyrawdata.shape
    nv = mesh.nv
    xydata = []
    xydatapp = xydata.append
    nel = len(Vh)

    if nel == nt:
        eltype = 'P0'
        for i in range(0, ndim):
            cCols = xyrawdata[i, :]
            tmp = cCols[Vh+1]
            tmp = np.array([tmp, tmp, tmp])
            xydatapp([tmp])

    elif nel == 3*nt:
        eltype = 'P1'
        for i in range(0, ndim):
            cCols = xyrawdata[i, :]
            tmp = np.reshape(cCols(Vh+1), (3, nt))
            xydatapp([tmp])

    elif nel == 4*nt:
        eltype = 'P1b'
        for i in range(0, ndim):
            cCols = xyrawdata[i, :]
            tmp = np.reshape(cCols(Vh+1), (4, nt))
            xydatapp([tmp])

    elif nel == 6*nt:
        eltype = 'P2'
        for i in range(0, ndim):
            cCols = xyrawdata[i, :]
            tmp = np.reshape(cCols(Vh+1), (6, nt))
            xydatapp([tmp])
    else:
        raise OSError('Unknown Lagrangian FE: Vh does not match with no. of mesh triangles')