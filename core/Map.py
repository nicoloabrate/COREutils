"""
Author: N. Abrate.

File: Map.py

Description: Class to define the nuclear reactor core geometry defined in an
external text file.
"""
import numpy as np
import itertools as it
from numpy import pi, cos, sin
from coreutils.core.UnfoldCore import UnfoldCore


class Map:
    """
    Build the nuclear reactor core geometry map defined in a file.

    Attributes
    ----------
    inp : ndarray

    type : ndarray

    rotation_angle : int
        Rotation angle employed to unfold the input geometry
    Nx : int
        Number of assemblies along x
    Ny : int
        Number of assemblies along y
    fren2serp : dict
        Dictionary mapping FRENETIC numeration to Serpent 2 one.
    serp2fren : dict
        Dictionary mapping Serpent 2 numeration to FRENETIC one.
    serpcentermap : dict
        Dictionary mapping assembly number to its center coordinates.

    Methods
    -------
    ``None``
    """

    def __init__(self, geinp, rotangle, AssRadGeom, regionsdict=None,
                 inp=None):
        """
        Initialise the object.

        Parameters
        ----------
        geinp: str or ndarray
            If ``str`` <Path/filename> of the input file containing the
            geometry arrangement of the core, if ``ndarray`` the geometry
            arrangement is already defined by the user.
        rotangle: int
            rotation angle over which the arrangement is symmetrically rotated.
            The rotation angle should be passed in degree (only 0,60,45,90,180
            values are allowed).
            With rotangle=0 no rotation occurs.
        AssRadGeom : obj
            Assembly radial geometry object.

        Returns
        -------
        ``None``

        """
        if isinstance(geinp, str):
            rotangle = int(rotangle)
            core = UnfoldCore(geinp, rotangle, regionsdict)
            self.inp = core.inp
            self.type = core.coremap

        else:
            self.inp = inp
            self.type = geinp

        # -- compute assembly geometrical features
        self.rotation_angle = rotangle
        self.Nx, self.Ny = (self.type).shape
        # define assembly map
        serpmap = Map.__drawserpmap(self, AssRadGeom)  # Serpent numeration
        # define assembly centers coordinate
        coord = Map.__findcenters(self, AssRadGeom)

        if AssRadGeom.type == "H":
            # define assembly numeration according to FRENETIC
            frenmap = Map.__drawfrenmap(self)
            # sort FRENETIC map in ascending way
            sortind = np.argsort(frenmap)
            frenmap = frenmap[sortind]
            # sort Serpent map accordingly
            serpmap = serpmap[sortind]
            # FRENETIC to Serpent dict
            self.fren2serp = dict(zip(frenmap, serpmap))
            # Serpent to FRENETIC dict
            self.serp2fren = dict(zip(serpmap, frenmap))

        # Serpent centers map
        self.serpcentermap = dict(zip(serpmap, coord))
        # TODO define also a dict to map the ass numbers of each type!

    def __findcenters(self, AssRadGeom):
        """
        Compute x and y coordinates of the centers of each assembly.

        Returns
        -------
        coord : tuple
            Tuple of x and y coordinates of the centers of each assembly.

        """

        # define assemblies characteristics
        Nx, Ny = np.shape(self.type)
        L = AssRadGeom.edge  # assembly edge

        if AssRadGeom.type == "S":
            # evaluate coordinates points along x- and y- axes
            xspan = (np.arange(-(Nx-1)*L/2, (Nx)*L/2, L))
            yspan = np.flip(np.arange(-(Ny-1)*L/2, (Ny)*L/2, L))

            # replace "numerical zero" with 0
            xspan[abs(xspan) < 1e-10] = 0
            yspan[abs(yspan) < 1e-10] = 0

            # take cartesian product of coordinates set
            coord = tuple(it.product(xspan, yspan))

        elif AssRadGeom.type == "H":

            # define core geometrical features
            nsect = 6  # only six sextants for 60 degree rotation are allowed
            nass = nsect*(np.count_nonzero(self.inp)-1)+1  # tot ass.bly number
            P = 2*AssRadGeom.apothema  # assembly pitch [cm]
            theta = pi/3  # hexagon inner angle
            L = AssRadGeom.edge  # hexagon edge [cm]
            x0 = P  # x-centre coordinate
            y0 = 0  # y-centre coordinate

            # unpack non-zero coordinates of the matrix
            y, x = np.where(self.inp != 0)  # rows, columns
            # define core central assembly
            yc, xc = [np.max(y), np.min(x)]  # central row, central column
            # compute number of assemblies
            Nx, Ny = [np.max(x)-xc, yc-np.min(y)+1]  # tot. columns, tot. rows
            # compute assemblies per row
            FA = [np.count_nonzero(row)
                  for row in self.inp[yc-Ny+1:yc+1, xc+1:]]
            # convert to np array
            FA = np.flip(np.asarray(FA))
            NFA = sum(FA)  # sum number of assemblies per sextant

            # arrays preallocation
            x, y = np.nan*np.empty((nass, )), np.nan*np.empty((nass, ))
            # assign central assembly coordinates
            x[0], y[0] = 0, 0
            count = 1
            # compute (x, y) of assembly centers
            for iSex in range(0, nsect):  # sextant loop
                # compute rotation matrix for each sextant
                rotmat = np.array([[cos(theta*iSex), -sin(theta*iSex)],
                                   [sin(theta*iSex), cos(theta*iSex)]])
                count = NFA*iSex+1  # keep score of number of assemblies done
                for irow in range(0, len(FA)):  # row loop
                    # lists preallocation
                    xc, yc = [], []
                    xcapp, ycapp = xc.append, yc.append
                    # compute centers for each assembly in irow
                    for icol in range(0, FA[irow]):  # column loop
                        xcapp(x0+P*icol+P/2*irow)
                        ycapp(y0+(L*(1+sin(pi/6)))*irow)

                    count = count+FA[irow-1]*(irow > 0)
                    xcyc = np.asarray([xc, yc])
                    FArot = np.dot(rotmat, xcyc)
                    iS, iE = count, count+FA[irow]
                    x[iS:iE, ] = FArot[0, :]
                    y[iS:iE, ] = FArot[1, :]

            coord = tuple(zip(x, y))

        return coord

    def __drawserpmap(self, AssRadGeom):
        """
        Define the core map  according to Serpent 2 code ordering.

        Parameters
        ----------
        ``None``

        Returns
        -------
        serpmap : ndarray
            Array with assembly numbers

        """
        # define assemblies characteristics
        Nx, Ny = np.shape(self.type)
        # define assembly numeration (same for squared and hex.lattice)
        assnum = np.arange(1, Nx*Ny+1)  # array with assembly numbers
        assnum = assnum.reshape(Nx, Ny).T  # reshape as a matrix
        assnum = assnum.flatten('F')  # flattening the matrix by columns

        if AssRadGeom.type == "H":

            # flatten the matrix by rows
            coretype = self.type.flatten('C')
            # squeeze out void assembly numbers
            assnum[coretype == 0] = 0
        # select non-zero elements
        sermap = assnum[assnum != 0]

        return sermap

    def __drawfrenmap(self):
        """
        Define the core map  according to FRENETIC code ordering.

        Parameters
        ----------
        ``None``

        Returns
        -------
        frenmap : ndarray
            Array with assembly numbers

        """
        # check on geometry
        if self.rotation_angle != 60:
            print("FrenMap method works only for hexagonal core geometry!")
            raise OSError("rotation angle != 60 degree")

        nsect = 6  # only six sextants for 60 degree rotation are allowed
        frenmap = self.inp+0  # copy input matrix

        # number of assemblies
        nass = nsect*(np.count_nonzero(frenmap)-1)+1
        # unpack non-zero coordinates of the matrix
        y, x = np.where(frenmap != 0)  # rows, columns
        # define core central assembly
        yc, xc = [np.max(y), np.min(x)]
        # compute number of assemblies
        Nx, Ny = [np.max(x)-xc, yc-np.min(y)+1]
        # frenmap[yc, xc] = 1  # first assembly is the central one
        iS = 1  # the 1st assembly is the central
        for irow in range(0, Ny):
            # take extrema of non-zero arrays
            NZx = np.flatnonzero(frenmap[yc-irow, xc:])
            # compute array length to numerate assemblies
            iE = NZx[-1]-NZx[0]+1  # length of array
            # write assembly numbers
            frenmap[yc-irow, NZx[0]+xc:NZx[-1]+1+xc] = np.arange(iS, iE+iS)
            # keep record of assembly number
            iS = iS+iE

        # unpack non-zero coordinates of the matrix
        y, x = np.where(frenmap != 0)  # rows, columns
        # define core central assembly
        yc, xc = [np.max(y), np.min(x)]
        # compute number of assemblies
        Nx, Ny = [np.max(x)-xc, yc-np.min(y)+1]
        Nxc = sum(frenmap[xc, yc+1:] != 0)
        if Nxc < Nx:
            # non-regular hexagon: add dummy elements to have same Nx and Ny
            frenmap[xc, Nxc+xc+1:Nx+xc+1] = -100000000000
            # find min non-zero index
            indNZy = np.argwhere(frenmap[:, np.max(x)]).min()
            # add elements along y to have Nx=Ny
            frenmap[yc-Nx+1:indNZy, np.max(x)] = -100000000000
            # set Ny equal to Nx (by definition)
            Ny = Nx
            # unpack non-zero coordinates of the matrix (they changed)
            y, x = np.where(frenmap != 0)  # rows, columns

        # -- loop over rows
        for nb in range(1, Nx):

            xsectI = np.arange(xc+Nx, xc+nb, -1)  # decreasing order indeces
            ysectI = yc-nb  # going up along the matrix means to decrease yc
            # select non-zero elements position
            NZx = np.flatnonzero(frenmap[ysectI, xsectI])
            # -- sector II
            # count non-zero element for summation (continue numeration)
            nz = (nass-1)/nsect*(frenmap[ysectI, xsectI] > 0)
            # select rotation coordinates
            dcoord = [np.arange(yc-nb-1, np.min(y)-2, -1),
                      np.arange(xc+1, xc+NZx[-1]+2)]
            # select indeces  matching dcoord
            ind = np.ravel_multi_index(dcoord, dims=np.shape(frenmap),
                                       order='C')
            # write ass numbers
            frenmap.ravel()[ind] = np.flip(frenmap[ysectI, xsectI]+nz)

            # -- sector III
            frenmap[yc-Ny+nb:yc, xc-nb] = frenmap[ysectI, xsectI]+2*nz

            # -- sector IV
            frenmap[yc+nb, xc-Nx:xc-nb] = frenmap[ysectI, xsectI]+3*nz

            # flip since sectors V and VI are in III and IV cartesian quadrants
            xsectI = np.flip(xsectI, -1)

            # -- sector V
            # select rotation coordinates
            dcoord = [np.arange(xc+nb+1, xc+NZx[-1]+2+nb),
                      np.arange(yc-1, np.min(y)-1+(nb-1), -1)]
            # TODO: this is only a temporary patch for ebr-II case
            if dcoord[0].shape != dcoord[1].shape:
                dcoord[0] = np.arange(xc+nb+1,
                                      xc+NZx[-1]+1*(NZx[-1] == 0)+2+nb)
            # select indeces  matching dcoord
            ind = np.ravel_multi_index(dcoord, dims=np.shape(frenmap),
                                       order='C')
            # write ass numbers
            frenmap.ravel()[ind] = frenmap[ysectI, xsectI]+np.flip(4*nz)

            # -- sector VI
            frenmap[yc+1:yc+Ny-nb+1, xc+nb] = frenmap[ysectI,
                                                      xsectI]+np.flip(5*nz)

        # -- fill "diagonals" (only sectors II and V actually are diagonals)
        corediag = frenmap[yc, xc+1:xc+Nx+1]

        # sector II
        # select rotation coordinates
        dcoord = (np.arange(xc+1, xc+Nx+1), np.arange(yc-1, yc-Ny-1, -1))
        # select indeces  matching dcoord
        ind = np.ravel_multi_index(dcoord, dims=np.shape(frenmap), order='F')
        nz = (nass-1)/nsect
        frenmap.ravel()[ind] = corediag+nz

        # sector III
        nz = 2*(nass-1)/nsect
        frenmap[np.arange(yc-1, yc-Ny-1, -1), xc] = corediag+nz

        # sector IV
        nz = 3*(nass-1)/nsect
        frenmap[yc, np.arange(xc-1, xc-Nx-1, -1)] = corediag+nz

        # sector V
        # select rotation coordinates
        dcoord = (np.arange(xc-1, xc-Nx-1, -1), np.arange(yc+1, yc+Ny+1))
        # select indeces  matching dcoord
        ind = np.ravel_multi_index(dcoord, dims=np.shape(frenmap), order='F')
        nz = 4*(nass-1)/nsect
        frenmap.ravel()[ind] = corediag+nz

        # sector VI
        nz = 5*(nass-1)/nsect
        frenmap[np.arange(yc+1, yc+Ny+1), xc] = corediag+nz

        # replace negative dummy elements with 0
        frenmap[frenmap < 0] = 0

        # flatten 2D array along 1 axis
        frenmap = frenmap.flatten('C')
        # squeeze out 0 assemblies
        frenmap = frenmap[frenmap != 0]

        return frenmap
