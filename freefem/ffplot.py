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

from matplotlib.tri import Triangulation as tri
from matplotlib.patches import Polygon
from matplotlib.collections import PolyCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar


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

    def __init__(self, fname, verbosity=False):

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
                if dimension != 2:
                    raise OSError('Only 2D meshes are supported!')

                nv, nt, nbe = tests
                # verteces
                p = np.zeros((3, nv))*np.nan
                idx = 0
                for i in range(1, nv+1):
                    idx = idx + 1
                    p[:, i-1] = [float(j) for j in lines[idx].split(' ')]

                # triangles
                t = np.zeros((4, nt), dtype=np.int64)
                for i in range(1, nt+1):
                    idx = idx + 1
                    t[:, i-1] = [int(j) for j in lines[idx].split(' ')]

                # boundaries
                b = np.zeros((3, nbe), dtype=np.int64)
                for i in range(1, nbe+1):
                    idx = idx + 1
                    b[:, i-1] = [int(j) for j in lines[idx].split(' ')]

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
    """Gather pde data for plotting."""

    def __init__(self, ffnames, vhname):

        if os.path.exists(vhname):
            vh = np.loadtxt(vhname, dtype=np.int64)
        else:
            raise OSError('%s not found!' % vhname)

        datadict = {}
        for f in ffnames:
            if os.path.exists(f):
                try:
                    data = np.loadtxt(f)
                    if len(data.shape) == 1:
                        data = data[:, np.newaxis]
                except ValueError:
                    tmp = {0: lambda s: complex(s.decode().replace('+-', '-'))}
                    data = np.loadtxt(f, dtype=complex,
                                      converters=tmp)
                f = f.split(os.path.sep)[-1].split('.txt')[0]
                datadict[f] = data
            else:
                raise OSError('%s not found!' % f)
        # add dict with names in ffnames!
        self.data = datadict
        self.vh = vh


def ffplot(mesh, Vh, ffdata=None, surf=False, showmesh=False,
           showboundary=True, clevels=10, contour=False, interp=True,
           cmap='Spectral_r', levels=25, **kwargs):

    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    xp, yp, xmsh, ymsh = PrepareMesh(mesh.points, mesh.triangles)

    if ffdata is not None:
        xyrawdata = rowvec(ffdata)
        elementType, xydata = ConvertPdeData(mesh, Vh, xyrawdata)
        # # Create meshes for plotting and interpolation according to FEtype
        # xdata, ydata, xdataz, ydataz = PrepareCoordinates(elementType, xmsh,
        #                                                   ymsh)
        # # Convert the color data according to xdata, xdataz and interpolation
        # cdata, cdataz, cdatainterpn = PrepareData(elementType,
        #                                           mesh.triangles,
        #                                           xydata, xmsh, ymsh)

        if contour is False:

            if surf is False:

                if interp is True:

                    if showmesh is False:

                        if elementType in ['P0', 'P1']:

                            triang = tri(mesh.points[0, :], mesh.points[1, :])
                            plt.tricontourf(triang, np.squeeze(ffdata),
                                            cmap=cmap, levels=levels)

                        else:
                            raise OSError('Unknown FE-space order!')

                    else:
                        triang = tri(mesh.points[0, :], mesh.points[1, :])
                        plt.tricontourf(triang, np.squeeze(ffdata),
                                        cmap=cmap, levels=levels)

                else:
                    print('Under develop')

            else:
                print('Under develop')

        else:
            print('Under develop')

    else:
        # plot Vh mesh
        print('Under develop')

    if showboundary is True:
        boundary = rowvec(mesh.boundaries)
        x = np.array([xp[boundary[0, :]-1], xp[boundary[1, :]-1]])
        y = np.array([yp[boundary[0, :]-1], yp[boundary[1, :]-1]])
        plt.plot(x, y, color='k', linewidth=1)
        plt.gca().set_aspect('equal', adjustable='box')
        # matplotlib.lines(xp, yp)


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
    xmsh = np.array([xp[triangles[0, :]-1],
                     xp[triangles[1, :]-1],
                     xp[triangles[2, :]-1]])
    ymsh = np.array([yp[triangles[0, :]-1],
                     yp[triangles[1, :]-1],
                     yp[triangles[2, :]-1]])
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
    try:
        s1, s2 = S.shape
        if s1 > s2:
            S = S.T
    except ValueError:
        S = S
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
    # xydata = []
    # xydatapp = xydata.append
    nel = len(Vh)
    t = mesh.triangles

    if Vh is not None:

        if nel == nt:
            eltype = 'P0'
            for i in range(0, ndim):
                cCols = xyrawdata[i, :]
                tmp = cCols[Vh+1]
                tmp = np.array([tmp, tmp, tmp])
                xydata = tmp

        elif nel == 3*nt:
            eltype = 'P1'
            for i in range(0, ndim):
                cCols = xyrawdata[i, :]
                tmp = np.reshape(cCols[Vh+1], (3, nt))
                xydata = tmp

        elif nel == 4*nt:
            eltype = 'P1b'
            for i in range(0, ndim):
                cCols = xyrawdata[i, :]
                tmp = np.reshape(cCols[Vh+1], (4, nt))
                # xydatapp([tmp])

        elif nel == 6*nt:
            eltype = 'P2'
            for i in range(0, ndim):
                cCols = xyrawdata[i, :]
                tmp = np.array([cCols[t[0, :]],
                                cCols[t[1, :]],
                                cCols[t[2, :]]])
                # xydatapp([tmp])
        else:
            raise OSError('Unknown Lagrangian FE: Vh does not match with no.' +
                          ' of mesh triangles')

    else:

        if ndof == nv:
            eltype = 'P1'
            for i in range(0, ndim):
                cCols = xyrawdata[i, :]
                tmp = np.reshape(cCols(Vh+1), (6, nt))
                # xydatapp([tmp])

        else:
            raise OSError('Unknown FE-space order: No Vh and NDOF != NV')

    return eltype, xydata


def PrepareCoordinates(eltype, xmsh, ymsh, doz=True):

    if eltype in ['P0', 'P1']:

        xdata, ydata = xmsh, ymsh
        xdataz, ydataz = [], []

    elif eltype == 'P1b':

        px4, py4 = np.sum(xmsh, axis=0)/3, np.sum(ymsh, axis=0)/3
        # refine mesh
        xmsh124 = np.array([xmsh[0, :], xmsh[1, :], px4]).T
        ymsh124 = np.array([ymsh[0, :], ymsh[1, :], py4]).T
        xmsh234 = np.array([xmsh[1, :], xmsh[2, :], px4]).T
        ymsh234 = np.array([ymsh[1, :], ymsh[2, :], py4]).T
        xmsh143 = np.array([xmsh[0, :], px4, xmsh[2, :]]).T
        ymsh143 = np.array([ymsh[0, :], py4, ymsh[2, :]]).T
        # assemble the refined mesh
        xdata = np.array([xmsh124, xmsh234, xmsh143])
        ydata = np.array([ymsh124, ymsh234, ymsh143])
        if doz:
            xdataz, ydataz = xmsh, ymsh
        else:
            xdataz, ydataz = [], []

    elif eltype == 'P2':

        print('Under development!')

    else:
        raise OSError('Unknown FE-space order: No Vh and NDOF != NV')

    return xdata, ydata, xdataz, ydataz


def PrepareData(eltype, triangles, xydata, xmsh, ymsh):

    ndim = len(xydata)
    if eltype in ['P0', 'P1']:

        cdata = xydata
        cdataz, cdatainterp = None, None

    elif eltype == 'P1b':

        print('Under development!')

    elif eltype == 'P2':

        print('Under development!')

    else:
        raise OSError('Unknown FE-space order: No Vh and NDOF != NV')

    return cdata, cdataz, cdatainterp
