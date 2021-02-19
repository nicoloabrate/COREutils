"""
Author: N. Abrate.

File: Assembly.py

Description: This file contains classes for some typical assembly geometries
in a nuclear fission reactor.
"""
import numpy as np

class AssemblyGeometry:
    """
    Define geometrical quantities for an assembly in the x-y plane.

    Attributes
    ----------
    edge: str
        Assembly edge
    area: float
        Assembly area
    perimeter: float
        Assembly perimeter
    type: str
        Assembly type.
    numedges: int
        Number of edges of the assembly

    Methods
    -------
    compute_volume(self, height):
        Compute volume of the assembly slice.
    """

    def __init__(self, pitch, asstype):
        """
        Define geometrical quantities for an assembly in the x-y plane.

        Parameters
        ----------
        pitch: float
            Assembly pitch inside the core

        Returns
        -------
        ``None``

        """
        if asstype == 'H':
            # by definition of pitch between two hexagonal assemblies
            self.apothema = pitch/2
            self.pitch = pitch
            self.edge = 2*self.apothema/3**0.5
            self.area = 3*(3**0.5)/2*self.edge**2
            self.perimeter = 6*self.edge
            self.type = "H"
            self.numedges = 6

        elif asstype == 'S':
            self.edge = pitch
            self.area = self.edge**2
            self.perimeter = 4*self.edge
            self.type = "S"
            self.numedges = 4

        else:
            raise OSError("Unknown type of assembly radial geometry!")

    def compute_volume(self, height):
        """
        Compute volume of the assembly slice.

        Parameters
        ----------
        height : float
            Axial width considered for the volume.

        Returns
        -------
        volume : float
            Volume of the assembly slice

        """
        self.height = height  # assign height property
        self.volume = self.area*self.height  # compute volume


class AxialConfig:
    """
    Define the axial core configuration at time instant.

    Attributes
    ----------
    cuts : dict
        Dictionary with values ``AxialCuts`` objects assigned to assembly type
    mycuts : list
        List of cuts common to the whole reactor

    Methods
    -------
    ``None``

    """

    def __init__(self, cuts, splitz):
        """
        Define geometrical quantities for a squared assembly

        Parameters
        ----------
        cuts : dict
            Dictionary with axial cuts.

        Returns
        -------
        ``None``

        """
        # homogenisation cuts
        self.mycuts = cuts['mycuts']
        self.splitz = splitz 
        # cuts defining different material regions
        xscuts = cuts['xscuts']
        # initialise dict
        self.cuts = {}
        for asstype, cuts in xscuts.items():
            # unpack lists
            up, lo, r = [], [], []
            uap, lap, rap = up.append, lo.append, r.append
            for r1, u1, l1 in cuts:
                rap(r1), uap(u1), lap(l1)
            self.cuts[asstype] = AxialCuts(up, lo, r)
        self.AxNodes = np.zeros((sum(splitz), ))
        # assign axial nodes coordinates
        idx = 0
        for iz in range(0, len(self.mycuts[1:])):
            dz = (self.mycuts[iz+1]-self.mycuts[iz])/splitz[iz]
            tmp = np.arange(self.mycuts[iz]+dz/2, self.mycuts[iz+1], dz)
            ns = len(tmp)
            self.AxNodes[idx:idx+ns] = tmp
            idx = idx+ns
        

class AxialCuts:
    """
    Define the axial cuts for a certain type of assembly.

    Attributes
    ----------
    upz : float
        Upper z-coordinate
    loz : float
        Lower z-coordinate
    reg : str
        String identifying the region within upz and lowz

    Methods
    -------
    ``None``

    """

    def __init__(self, up, lo, r):
        """
        Define geometrical quantities for a squared assembly

        Parameters
        ----------
        asscuts : dict
            List with regions and axial cuts.

        Returns
        -------
        ``None``

        """
        # -- check axial cuts consistency
        # check dimensions
        nelz = len(up)
        if nelz != len(lo):
            raise OSError('Upper and lower axial coordinates number mismatch!')

        # check order
        for nz in range(0, nelz):
            # swap if lower and upper are not consistent
            if up[nz] < lo[nz]:
                lo[nz], up[nz] = up[nz], lo[nz]

        for i in range(1, nelz-1):
            if lo[i+1] != up[i]:
                raise OSError('Some axial bin is void!')

        # check upz and loz are monotonically increasing/decreasing
        checkupz = (all(up[i] <= up[i+1] for i in range(len(up) - 1)) or
                    all(up[i] >= up[i+1] for i in range(len(up) - 1)))

        checkloz = (all(lo[i] <= lo[i+1] for i in range(len(lo) - 1)) or
                    all(lo[i] >= lo[i+1] for i in range(len(lo) - 1)))

        if checkupz is False or checkloz is False:
            raise OSError('Axial coordinates are not monotonic!' +
                          ' Check cuts or translation dz.')

        self.upz, self.loz, self.reg = up, lo, r
