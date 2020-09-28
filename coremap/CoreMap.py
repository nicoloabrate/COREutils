"""
Author: N. Abrate.

File: CoreMap.py

Description: Class to define the nuclear reactor core geometry defined in an
external text file.
"""

import itertools as it
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import coreutils.coremap.AssemblyGeometry as ag
from matplotlib import rc
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
from coreutils.coremap.UnfoldCore import UnfoldCore
from numpy import pi, cos, sin
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection


class CoreMap:
    """
    This class defines the nuclear reactor core geometry defined in an external
    text file.

    Attributes
    ----------
    geinp: str
        <Path/filename> of the input file containing the geometry arrangement
        of the core.
    rotangle: float
        rotation angle over which the arrangement is symmetrically rotated.
        The rotation angle should be passed in degree (only 0,60,45,90,180
        values are allowed).
        With rotangle=0 no rotation occurs.
    P: float
        assembly pitch (distance between centers in two adjacent assemblies)

    Methods
    -------
    coremap: array[int]
        2D array representing the whole reactor core. The entries represent
        the assembly types
    """

    def __init__(self, geinp, rotangle, pitch):

        rotangle = int(rotangle)
        # -- compute assembly geometrical features
        if rotangle == 60:
            assemblygeom = ag.AssemblyHex(pitch)
        else:
            assemblygeom = ag.AssemblySqr(pitch)

        # unfold input geometry over a certain rotation angle
        core = UnfoldCore(geinp, rotangle)
        self.rotation_angle = rotangle
        self.inp = core.inp
        self.type = core.coremap
        self.assembly = assemblygeom  # assign assembly object
        self.Nx, self.Ny = (self.type).shape
        # define assembly map
        serpmap = CoreMap.drawserpmap(self)  # Serpent numeration
        # define assembly centers coordinate
        coord = CoreMap.locatecenter(self)

        if self.assembly.type == "H":
            # define assembly numeration according to FRENETIC
            frenmap = CoreMap.drawfrenmap(self)
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
        # FIXME define also a dict to map the ass numbers of each type!

    def locatecenter(self):

        # define assemblies characteristics
        Nx, Ny = np.shape(self.type)
        L = self.assembly.edge  # assembly edge

        if self.assembly.type == "S":
            # evaluate coordinates points along x- and y- axes
            xspan = (np.arange(-(Nx-1)*L/2, (Nx)*L/2, L))
            yspan = np.flip(np.arange(-(Ny-1)*L/2, (Ny)*L/2, L))

            # replace "numerical zero" with 0
            xspan[abs(xspan) < 1e-10] = 0
            yspan[abs(yspan) < 1e-10] = 0

            # take cartesian product of coordinates set
            coord = tuple(it.product(xspan, yspan))

        elif self.assembly.type == "H":

            # define core geometrical features
            nsect = 6  # only six sextants for 60 degree rotation are allowed
            nass = nsect*(np.count_nonzero(self.inp)-1)+1  # tot ass.bly number
            P = 2*self.assembly.apothema  # assembly pitch [cm]
            theta = pi/3  # hexagon inner angle
            L = self.assembly.edge  # hexagon edge [cm]
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

            coord = list(zip(x, y))

        return coord

    def drawserpmap(self):
        """
        This class defines the assembly centers coordinates and the assembly
        numeration according to Serpent-2 Monte Carlo code convention

        Parameters:
        =========== INPUT

        =========== OUTPUT

        """
        ## FIXME
        # # define assemblies characteristics
        # Nx, Ny = np.shape(self.type)
        # # define assembly numeration (flattening sq. or hex. lattice by rows)
        # assnum = np.arange(1, Nx*Ny+1)
        #
        # if self.assembly.type == "H":
        #
        #     # flatten the matrix by rows
        #     coretype = self.type.flatten('C')
        #     # squeeze out void assembly numbers
        #     assnum[coretype == 0] = 0
        # # select non-zero elements
        # sermap = assnum[assnum != 0]
        # return sermap
        # define assemblies characteristics
        Nx, Ny = np.shape(self.type)
        L = self.assembly.edge  # assembly edge
        # define assembly numeration (same for squared and hex.lattice)
        assnum = np.arange(1, Nx*Ny+1)  # array with assembly numbers
        assnum = assnum.reshape(Nx, Ny)  # reshape as a matrix
        assnum = assnum.flatten('F')  # flattening the matrix by columns

        if self.assembly.type == "H":

            # flatten the matrix by rows
            coretype = self.type.flatten('C')
            # squeeze out void assembly numbers
            assnum[coretype == 0] = 0
        # select non-zero elements
        sermap = assnum[assnum != 0]
        return sermap

    def drawfrenmap(self):
        """
        This class defines the assembly centers coordinates and the assembly
        numeration according to FRENETIC code convention.
        WATCH OUT: this method only applies to the hexagonal core geometry.

        Parameters:
        =========== INPUT

        =========== OUTPUT

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
            inf = float("inf")
            frenmap[xc, Nxc+xc+1:Nx+xc+1] = -inf
            # find min non-zero index
            indNZy = np.argwhere(frenmap[:, np.max(x)]).min()
            # add elements along y to have Nx=Ny
            frenmap[yc-Nx+1:indNZy, np.max(x)] = -inf
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

    def loadassembly(self, newtype, asslst, flagfren=None):
        # check input type
        if type(newtype) is int:
            # convert integer to list
            newtype = list(newtype)
        if type(asslst[0]) is int:
            # convert list to list of lists
            asslst = [asslst]

        for ipos, ilst in enumerate(asslst):  # loop over lists
            # check map convention
            if flagfren is not None:
                # translate FRENETIC numeration to Serpent
                index = [self.fren2serp[l]-1 for l in ilst]  # -1 for py index
            else:
                index = [l-1 for l in ilst]  # -1 to match python indexing
            # get coordinates associated to these assemblies
            index = (list(set(index)))
            rows, cols = np.unravel_index(index, self.type.shape)
            # load new assembly type
            self.type[rows, cols] = newtype[ipos]

    def writecentermap(self, numbers=True, fname="centermap.txt"):
        """ Write centermap to text file """
        # define regions
        typelabel = np.reshape(self.type, (self.Nx*self.Ny, 1))
        regions = []
        for key, coord in (self.serpcentermap).items():
            x, y = coord
            if numbers is False:
                key = typelabel[key-1, 0]
            regions.append((key, x, y))
        # write region to external file
        with open(fname, 'w') as f:  # open new file
            f.write("\n".join("{:03d} {:5f} {:5f}".format(elem[0], elem[1], elem[2])
                              for elem in regions))
            f.write("\n")

    def getassemblylist(self, atype, match=True):
        """
        Return assemblies belonging to a certain type.

        Parameters
        ----------
        atype : TYPE
            DESCRIPTION.
        match : TYPE, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        matchedass : TYPE
            DESCRIPTION.

        """
        asstypes = self.type.flatten(order='F')
        if match is True:
            matchedass = np.where(asstypes == atype)[0]+1
        else:
            matchedass = np.where(asstypes != atype)[0]+1

        return matchedass
    # TODO: add writeregionmap method to plot region id, x and y for each assembly


    def writecoremap(self, flatten=None, fname="coremap.txt", serpheader=False):
        """ Write centermap to text file """
        # define regions
        if flatten is None:
            typelabel = self.type
        else:
            typelabel = np.reshape(self.type, (self.Nx*self.Ny, 1))

        # determine file format
        nd = str(len(str(self.type.max())))  # determine number of digits
        fmt = "%0"+nd+"d"

        # determine header
        if serpheader is False:
            header = ""
            comm = '#'
        else:  # Serpent-2 style header (define core lattice)
            # define assembly type according to Serpent
            if self.assembly.type == 'S':
                asstype = '1'  # square
            elif self.assembly.type == 'H':
                asstype = '3'  # hexagon
            # define central assembly coordinates
            x0, y0 = self.serpcentermap[self.fren2serp[1]]
            x0, y0 = str(x0), str(y0)
            # define number of assemblies along x and y directions
            Nx, Ny = str(self.Nx), str(self.Ny)
            # define assembly pitch
            P = str(2*self.assembly.apothema)
            header = " ".join(("lat core ", asstype, x0, y0, Nx, Ny, P))
            comm = ''
        # save array to file
        np.savetxt(fname, typelabel, delimiter=" ", fmt=fmt, header=header,
                   comments=comm)

    def plot(self, label=False, dictname=None, figname=None, fren=False,
             which=None, what=None, asstype=False, usetex=False, fill=True,
             axes=None, cmap='Spectral_r', thresh=None, cbarLabel=None,
             xlabel=None, ylabel=None, loglog=None, logx=None, logy=None,
             title=None, scale=1, fmt="%.2f", numbers=False, **kwargs):
        """
        Plot the core map.

        Parameters
        ----------
        label : TYPE, optional
            DESCRIPTION. The default is False.
        dictname : TYPE, optional
            DESCRIPTION. The default is None.
        figname : TYPE, optional
            DESCRIPTION. The default is None.
        fren : TYPE, optional
            DESCRIPTION. The default is False.
        which : TYPE, optional
            DESCRIPTION. The default is None.
        what : TYPE, optional
            DESCRIPTION. The default is None.
        usetex : TYPE, optional
            DESCRIPTION. The default is False.
        fill : TYPE, optional
            DESCRIPTION. The default is True.
        axes : TYPE, optional
            DESCRIPTION. The default is None.
        cmap : TYPE, optional
            DESCRIPTION. The default is 'Spectral_r'.
        thresh : TYPE, optional
            DESCRIPTION. The default is None.
        cbarLabel : TYPE, optional
            DESCRIPTION. The default is None.
        xlabel : TYPE, optional
            DESCRIPTION. The default is None.
        ylabel : TYPE, optional
            DESCRIPTION. The default is None.
        loglog : TYPE, optional
            DESCRIPTION. The default is None.
        logx : TYPE, optional
            DESCRIPTION. The default is None.
        logy : TYPE, optional
            DESCRIPTION. The default is None.
        title : TYPE, optional
            DESCRIPTION. The default is None.
        scale : TYPE, optional
            DESCRIPTION. The default is 1.
        fmt : TYPE, optional
            DESCRIPTION. The default is "%.2f".
        **kwargs : TYPE
            DESCRIPTION.

        Raises
        ------
        IndexError
            DESCRIPTION.
        TypeError
            DESCRIPTION.

        Returns
        -------
        None.

        """

        # set default font and TeX interpreter
        rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
        rc('text', usetex=usetex)

        L = self.assembly.edge
        Nass = self.type.size
        # array of assembly type
        typelabel = np.reshape(self.type, (Nass, 1))
        maxtype = int(max(typelabel))
        coretype = range(0, maxtype+1)  # define

        kwargs.setdefault("edgecolor", "k")
        kwargs.setdefault("ec", "k")
        kwargs.setdefault("linewidth", 0.5)
        kwargs.setdefault("lw", 0.5)
        kwargs.setdefault("alpha", 1)
        fontsize = kwargs.get("fontsize", 4)
        # delete size from kwargs to use it in pathces
        if 'fontsize' in kwargs:
            del kwargs['fontsize']

        if what is None:

            physics = False
            # define default colorsets (if not enough, random colours are added)
            if self.assembly.type == "S":
                def_colors = ['deepskyblue', 'white', 'limegreen', 'gold',
                              'lightgray', 'firebrick', 'orange', 'turquoise',
                              'royalblue', 'yellow']
                orientation = np.pi/4
                L = L/2*np.sqrt(2)

            elif self.assembly.type == "H":
                def_colors = ['turquoise', 'firebrick', 'chocolate', 'gold',
                              'lightgray', 'seagreen', 'darkgoldenrod', 'grey',
                              'royalblue', 'yellow', 'forestgreen', 'magenta',
                              'lime']
                orientation = 0

            # check if more colors are needed and append in case
            if len(def_colors) < maxtype+1:
                N = len(def_colors)-(maxtype+1)
                for icol in range(0, N):
                    def_colors.append(np.random.rand(3,))

            # color dict
            asscol = dict(zip(coretype, def_colors))

        else:  # cont. <- if type(fill) is bool


            if self.assembly.type == "S":
                orientation = np.pi/4
                L = L/2*np.sqrt(2)

            elif self.assembly.type == "H":
                orientation = 0

            physics = True
            patches = []
            # values = []
            patchesapp = patches.append
            # valuesapp = values.append
            errbar = False
            # check data type is correct
            if type(what) is dict:
                # check keys
                if 'tallies' in what.keys():
                    tallies = what['tallies']

                if 'errors' in what.keys():
                    errors = what['errors']
                    errbar = True

            elif type(what) is np.ndarray:
                tallies = what
                # check on data shape
                try:
                    # associate tallies to Serpent assemblies numeration
                    Nx, Ny = tallies.shape
                    assnum = np.arange(1, Nx*Ny+1)
                    # flattening sq. or hex. lattice by rows
                    tallies = dict(zip(assnum, tallies.flatten('C')))
                except ValueError:
                    # TODO (possible enhancement: plot ND array slicing)
                    raise IndexError('Only 2D arrays are currently supported!')

            else:
                raise TypeError('Data must be dict or numpy array!')

            # TODO: place these lines somewhere where tallies is array for automatic formatting
            # peak = np.max(np.max(tallies))
            # if abs(peak) > 999:
            #     fmt = ".2e"
            # else:
            #     fmt = ".2f"

        # open figure
        fig = plt.figure()
        ax = fig.add_subplot(111)

        # check which variable
        if which is None:
            which = (self.serpcentermap).keys()

        elif which is not None:
            if fren is True:
                which = [self.fren2serp[k] for k in which]
            # else:
            #     tmp = list((self.serpcentermap).keys())
            #     which = [tmp[k] for k in which]

        for key, coord in (self.serpcentermap).items():
            x, y = coord
            # scale coordinate
            coord = (x*scale, y*scale)
            # check key is in which list
            if key not in which:
                continue

            if physics is False:
                # select color
                col = asscol[typelabel[key-1, 0]]
                # define assembly patch
                asspatch = RegularPolygon(coord, self.assembly.numedges, L*scale,
                                          orientation=orientation, color=col,
                                          fill=fill, **kwargs)
                ax.add_patch(asspatch)

            else:
                # define assembly patch
                asspatch = RegularPolygon(coord, self.assembly.numedges, L*scale,
                                          orientation=orientation, **kwargs)
                patchesapp(asspatch)
                # define value to be plotted
                #if fren is False:  # Serpent numeration
                # FIXME: per ora "valuesapp(tallies[key])" viene messo sotto per evitare che sia tutto disordinato
                #valuesapp(tallies[key])
                #else:  # Frenetic numeration
                   # keyF = self.serp2fren[key]
                   # valuesapp(tallies[keyF])

        # plot physics, if any
        if physics is True:
            # values = np.asarray(values)
            patches = np.asarray(patches, dtype=object)
            if which is None:
                coord = np.array(list(self.serpcentermap.values()))
            else:
                coord, values = [], []
                for k in which:
                    coord.append(self.serpcentermap[k])
                    values.append(tallies[k])

                coord = np.asarray(coord)
                values = np.asarray(values)

            normalizer = normalizerFactory(values, None, False, coord[:, 0]*scale,
                                           coord[:, 1]*scale)
            pc = PatchCollection(patches, cmap=cmap, **kwargs)
            formatPlot(ax, loglog=loglog, logx=logx, logy=logy,
                       xlabel=xlabel or "X [cm]",
                       ylabel=ylabel or "Y [cm]", title=title)
            pc.set_array(values)
            pc.set_norm(normalizer)
            ax.add_collection(pc)
            addColorbar(ax, pc, cbarLabel=cbarLabel)

        # add labels on top of the polygons
        for key, coord in (self.serpcentermap).items():
            # check key is in "which" list
            if key not in which:
                continue

            x, y = coord
            # plot text inside assemblies
            if dictname is None:
                if label is True:  # plot assembly number
                    if physics is False:
                        if fren is True:  # FRENETIC numeration
                            txt = str(self.serp2fren[key])  # translate keys
                        else:
                            txt = str(key)

                    else:
                        # define value to be plotted
                        if numbers is False:
                            if fren is False:  # Serpent numeration
                                txt = fmt % tallies[key]

                            else:  # Frenetic numeration
                                txt = fmt % tallies[key]  # self.serp2fren[key]

                            if errbar is True:
                                txt = "%s \n %.2f%%" % (txt, errors[key]*100)
                        else:
                            if fren is True:  # FRENETIC numeration
                                txt = str(self.serp2fren[key])  # translate keys
                            else:
                                txt = str(key)

                    plt.text(x*scale, y*scale, txt, ha='center',
                             va='center', size=fontsize)

            else:
                if asstype is True:  # plot assembly type
                    txt = dictname[typelabel[key-1, 0]]
                    plt.text(x*scale, y*scale, txt, ha='center', va='center',
                             size=fontsize)

                # FIXME: must be a better way to do this avoiding asstype, maybe.
                # change "dictname" because maybe we want tuples to have overlappings (phytra fig)
                # write other labels
                if asstype is False:
                    for assN, txt in dictname:
                        x, y = self.serpcentermap[self.fren2serp[assN]]
                        plt.text(x*scale, y*scale, txt, ha='center',
                                 va='center', size=fontsize)

        ax.axis('equal')
        if xlabel is None and ylabel is None:
            plt.axis('off')

        # save figure
        if figname is not None:
            fig.savefig(figname, bbox_inches='tight', dpi=250)


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
