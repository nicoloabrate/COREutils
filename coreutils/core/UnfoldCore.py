import numpy as np
from copy import deepcopy


class UnfoldCore:
    """
    Set of methods to rotate the input reactor core geometry.

    Attributes
    ----------
    coremap: array[int]
        2D array representing the whole reactor core. The entries represent
        the assembly types
    inp: array[int]
        2D array representing the reactor core sector defined in input.
        The entries represent the assembly types

    """

    def __init__(self, inpge, rotangle, regionsdict):
        """
        Initialise the class.

        Parameters
        ----------
        inpge: str
            Path of the input file containing the geometry arrangement of the
            core
        rotangle: float
            rotation angle over which the arrangement is symmetrically rotated.
            The rotation angle should be passed in degree (only 0,60,45,90,180
            values are allowed). With rotangle=0 no rotation occurs.

        Raises
        ------
        OSError:
            File %s not found
            Negative values are not allowed in input!
            The lattice should be squared! Check input file

        Returns
        -------
        ``None``
        """
        try:
            coremap = np.loadtxt(inpge, unpack=False, dtype=str, comments='%')
        except OSError:
            raise OSError(f"File {inpge} not found")

        coremap0 = deepcopy(coremap)
        # replace regions name with numbers
        for (k, v) in regionsdict.items():
            coremap[coremap == k] = v
            coremap[coremap == str(v)] = v

        # replace '*' with '0' for conversion, if any
        coremap[coremap == '*'] = '0'

        # convert from string ndarray to ndarray of integers
        try:
            coremap = coremap.astype(np.int64)
        except ValueError:
            raise OSError('Check input .txt entries match with assemblynames')
        coremap0 = coremap+0  # input
        # check negative entries
        if np.sum(coremap == -1) > 0:
            raise OSError("Negative values are not allowed in input!")

        # check that hexagonal symmetry holds
        Nx, Ny = np.shape(coremap)
        if Nx != Ny:
            print("%d rows and %d columns!" % (Ny, Nx))
            raise OSError('The lattice should be squared! Check input file')

        # -- compute number of sectors
        try:
            nsect = np.ceil(360/rotangle)
        except ZeroDivisionError:  # no symmetry, so map assumed as complete
            rotangle = 360
            nsect = 1

        nsect = int(nsect)  # convert to integer

        # -- apply rotation, if needed
        if nsect == 1:
            print("No symmetry rotation is considered")

        elif nsect == 2:
            self.coremap = UnfoldCore.rot180(coremap, Nx)

        elif nsect == 4:
            self.coremap = UnfoldCore.rot90(coremap, Nx)

        elif nsect == 6:
            self.coremap = UnfoldCore.rot60(coremap)

        elif nsect == 8:
            self.coremap = UnfoldCore.rot45(coremap, Nx)

        else:  # no rotation available
            print("Rotation of %d degree not available. Change rotation angle!"
                  % rotangle)
            self.coremap = coremap
        # assign also input file for reproducibility
        self.inp = coremap0

    @staticmethod
    def rot45(coremap, N):  # square geometry
        """Perform a counterclockwise 45° rotation.

        Parameters
        ----------
        coremap: np.array[int]
            2D array representing a 45° portion of the reactor core
        N: int
            number of nonzero elements in the file

        Returns
        -------
        coremap: np.array[int]
            2D array representing the whole reactor core
        """
        # use numpy methods to perform rotation and generate 1/4 of the core
        coremap = np.fliplr(coremap)+np.rot90(coremap)
        # divide by 2 overlappings in the diagonal
        for idiag in range(0, N):
            coremap[idiag, idiag] = coremap[idiag, idiag]/2

        # apply 90° rotation
        coremap = UnfoldCore.rot90(coremap, N)

        return coremap

    @staticmethod
    def rot60(coremap):  # hexagonal geometry
        """
        Perform a counterclockwise 60° rotation.

        Parameters
        ----------
        coremap: array[int]
            2D array representing a 60° portion of the reactor core
        N: int
            number of nonzero elements in the file

        Returns
        -------
        coremap: array[int]
            2D array representing the whole reactor core
        """
        # unpack non-zero coordinates of the matrix
        y, x = np.where(coremap != 0)  # rows, columns
        # define core central assembly
        yc, xc = [np.max(y), np.min(x)]
        # compute number of assemblies
        Nx, Ny = [np.max(x)-xc, yc-np.min(y)+1]
        Nxc = sum(coremap[xc, yc+1:] != 0)
        if Nxc < Nx:
            # non-regular hexagon: add dummy elements to have same Nx and Ny
            coremap[xc, Nxc+xc+1:Nx+xc+1] = -1
            # find min non-zero index
            indNZy = np.argwhere(coremap[:, np.max(x)]).min()
            # add elements along y to have Nx=Ny
            coremap[yc-Nx+1:indNZy, np.max(x)] = -1
            # set Ny equal to Nx (by definition)
            Ny = Nx
            # unpack non-zero coordinates of the matrix (they changed)
            y, x = np.where(coremap != 0)  # rows, columns

        # -- loop over rows
        for nb in range(1, Nx):

            xsectI = np.arange(xc+Nx, xc+nb, -1)  # decreasing order indeces
            ysectI = yc-nb  # going up along the matrix means to decrease yc

            # sector II
            coremap[np.min(y)-1:yc-nb, xc+nb] = coremap[ysectI, xsectI]

            # sector III
            coremap[yc-nb, xc-Nx+nb:xc] = coremap[ysectI, xsectI]

            # sector IV
            coremap[yc+nb, xc-Nx:xc-nb] = coremap[ysectI, xsectI]
            # flip since sectors V and VI are in III and IV cartesian quadrants
            xsectI = np.flip(xsectI, -1)

            # sector V
            coremap[yc+1+nb:yc+Ny+1, xc-nb] = coremap[ysectI, xsectI]

            # sector VI
            coremap[yc+nb, xc+1:xc+Nx-nb+1] = coremap[ysectI, xsectI]

        # -- fill "diagonals" (only sectors II and V actually are diagonals)
        corediag = coremap[yc, xc+1:xc+Nx+1]

        # sector II
        # define coordinates of the diagonal on sector II
        dcoord = (np.arange(yc-1, yc-Ny-1, -1), np.arange(xc+1, xc+Nx+1))
        index = np.ravel_multi_index(dcoord, dims=np.shape(coremap), order='F')
        coremap.ravel()[index] = corediag

        # sector III
        coremap[np.arange(yc-1, yc-Ny-1, -1), xc] = corediag

        # sector IV
        coremap[yc, np.arange(xc-1, xc-Nx-1, -1)] = corediag

        # sector V xc-1:-1:xc-Nx
        # define coordinates of the diagonal on sector II
        dcoord = (np.arange(yc+1, yc+Ny+1), np.arange(xc-1, xc-Nx-1, -1))
        index = np.ravel_multi_index(dcoord, dims=np.shape(coremap), order='F')
        coremap.ravel()[index] = corediag

        # sector VI
        coremap[np.arange(yc+1, yc+Ny+1), xc] = corediag

        # replace dummy elements "-1" with 0
        coremap[coremap == -1] = 0

        return coremap

    @staticmethod
    def rot90(coremap, N):  # square geometry
        """
        Perform a counterclockwise 90° rotation.

        Parameters
        ----------
        coremap: array[int]
            2D array representing a 90° portion of the reactor core
        N: int
            number of nonzero elements in the file

        Returns
        -------
        coremap: array[int]
            2D array representing the whole reactor core
        """
        # -- rotate to have 180° symmetry
        coremap = np.fliplr(coremap)+coremap
        # divide by 2 overlappings along rows
        if np.mod(N, 2) != 0:
            for irow in range(0, N):
                icol = (np.rint((N-1)/2)).astype(int)
                coremap[irow, icol] = coremap[irow, icol]/2

        # apply 180° rotation
        coremap = UnfoldCore.rot180(coremap, N)

        return coremap

    @staticmethod
    def rot180(coremap, N):  # square geometry
        """
        Perform a counterclockwise 180° rotation.

        Parameters
        ----------
        coremap: array[int]
            2D array representing a 180° portion of the reactor core
        N: int
            number of nonzero elements in the file

        Returns
        -------
        coremap: array[int]
            2D array representing the whole reactor core
        """
        coremap = np.flipud(coremap)+coremap
        # divide by 2 overlappings along columns
        if np.mod(N, 2) != 0:
            for icol in range(0, N):
                irow = (np.rint((N-1)/2)).astype(int)
                coremap[irow, icol] = coremap[irow, icol]/2

        return coremap
