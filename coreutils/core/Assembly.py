"""
Author: N. Abrate.

File: Assembly.py

Description: This file contains classes for some typical assembly geometries
in a nuclear fission reactor.
"""
import numpy as np
from coreutils.tools.utils import MyDict

class AssemblyGeometry:
    """
    Define an assembly object in the x-y plane.

    Parameters
    ----------
    pitch: float, optional
        Pitch of the assembly, by default ``None``. If ``None``, it 
        assumed that the object is parsed from a dictionary.
    asstype: string, optional
        It can be "H" (hexagonal) or "S" (squared), by default ``None``.
        If ``None``, it assumed that the object is parsed from a dictionary.
    inpdict: dict, optional
        Object stored as a dict, by default ``None``.

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

    def __init__(self, pitch=None, asstype=None, inpdict=None):
        if inpdict is None:
            self._init(pitch, asstype)
        else:
            self._from_dict(inpdict)
    
    def _init(self, pitch, asstype):
        if asstype == 'H' or asstype == '1D':
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
        """Compute volume of the assembly slice.

        Parameters
        ----------
        height: float
            Axial width considered for the volume.

        Returns
        -------
        volume: float
            Volume of the assembly slice
        """
        volume = self.area*height
        return volume

    def _from_dict(self, inpdict):
        """Parse object from dictionary.

        Parameters
        ----------
        inpdict : dict
            Input dictionary containing the class object (maybe read from 
            external file).
        """
        for k, v in inpdict.items():
            if isinstance(v, bytes):
                v = v.decode()
            setattr(self, k, v)


class AxialConfig:
    """
    Define the NE axial core configuration at a certain time instant.

    Parameters
    ----------
    cuts : dict, optional
        Cuts defining different material regions, by default ``None``
    splitz : list, optional
        List with the number of elements per axial region, by default ``None``
    labels : list, optional
        List of region labels, by default ``None``
    NE_dim : int, optional
        Number of spatial dimensions of the model, by default 3
    inpdict : _type_, optional
        Input dictionary with the object (if read outside this class), by default None
    assemblynames : list, optional
        List with names of the various assembly type, by default None


    Attributes
    ----------
    cuts : ordered dict
        Dictionary with values ``AxialCuts`` objects assigned to assembly type
    zcuts : list
        List of cuts common to the whole reactor
    nZ: int
        Number of zcuts.
    cutsregions: ordered dict
        Dict containing the regions composing the various cuts
        of each assembly type. It is useful to identify the 
        regions involved in the the spatial homogenisation.
    cutslabels: ordered dict
        Dict containing the labels of the regions composing the various cuts
        of each assembly type. It is useful to identify the 
        regions involved in the the spatial homogenisation.
    cutsweights: ordered dict
        Dict containing the weight of each regions composing 
        the various cuts of each assembly type. 
        It is useful to identify the percentage of each
        regions involved in the the spatial homogenisation.
    regions: ordered dict
        Dict mapping the number identifying each region (integer) 
        with its name (string)
    labels: ordered dict
        Dict mapping the name of each region with its own label. More
        regions could share the same label.
    config_str: ordered dict
        Dict containing the axial regions (as string)
        inside each assembly type (dict keys).
    config: ordered dict
        Dict containing the number of axial regions
        inside each assembly type (dict keys).
    homogenised: bool
        Flag to indicate if regions are homogenised.
    splitz: np.array
        Number of elements in each axial region. The array has length
        equal to the number of zcuts -1.
    AxNodes: np.array
        Axial coordinates. The array has length
        equal to the sum of all the numbers in 
        splitz.
    dz: np.array
        Height of each axial element. The array has length
        equal to the sum of all the numbers in 
        splitz.

    Methods
    -------
    nReg: returns the number of regions.
    mapFine2Coarse: returns the regions, labels and weights for 
        the axial regions involved in the spatial homogenisation. 

    """

    def __init__(self, cuts=None, splitz=None, labels=None,
                 NE_dim=3, inpdict=None, assemblynames=None):
        if inpdict is None:
            self._init(cuts, splitz, labels=labels, NE_dim=NE_dim,
                       assemblynames=assemblynames)
        else:
            self._from_dict(inpdict)

    def _init(self, cuts, splitz, labels=None, NE_dim=3, assemblynames=None):
        if isinstance(splitz, list):
            splitz = np.asarray(splitz)
        
        # cuts defining different material regions
        xscuts = cuts['xscuts']
        # homogenisation cuts
        if cuts['zcuts'] is None:
            self.zcuts = list(set(up+lo))
        else:
            self.zcuts = cuts['zcuts']
            self.zcuts.sort()

        self.nZ = len(self.zcuts)-1
        if len(splitz) != self.nZ:
            raise OSError(f"Number of splitz ({len(splitz)}) does not match with number of cuts ({self.nZ})!")

        # initialise dict
        attributes = ['regions', 'labels', 'cuts', 'config', 'config_str',
                      'cutsregions', 'cutslabels', 'cutsweights']
        for at in attributes:
            self.__dict__[at] = MyDict()
        if labels is None:
            labels = MyDict()
            for asstype, cuts in xscuts.items():
                for r1, u1, l1 in cuts:
                    labels[r1] = r1

        homog = False
        nReg = 0
        iType = 0
        for asstype in assemblynames:
            iType += 1
            cuts = xscuts[asstype]
            # unpack lists
            up, lo, r, lb = [], [], [], []
            uap, lap, rap, lbp = up.append, lo.append, r.append, lb.append
            for r1, u1, l1 in cuts:
                rap(r1), uap(u1), lap(l1)
                if r1 in labels.keys():
                    lbp(labels[r1])
            # force ascending order to be consistent with FRENETIC
            idx = sorted(range(len(up)), key=lambda k: up[k])
            tmp1, tmp2, tmp3 = lo[:], r[:], lb[:]
            for i in idx:
                lo[i] = tmp1[i]
                r[i] = tmp2[i]
                # FIXME label should be mandatory argument
                lb[i] = tmp3[i]
            lbl = []
            if labels is None:
                labels.update()
            for ir in r:
                if ir in labels.keys():
                    lbl.append(labels[ir])
            self.cuts[asstype] = AxialCuts(up, lo, r, lbl)
            cuts = tuple(zip(r, lbl, lo, up))
            zr, zl, zw = self.mapFine2Coarse(cuts, self.zcuts)
            self.cutsregions[asstype] = zr
            self.cutslabels[asstype] = zl
            self.cutsweights[asstype] = zw
            if not homog:
                # check if homogenisation is needed
                if any(y < 1 for y in zw['M1']):
                    homog = True

            regs = []
            regsapp = regs.append
            lbls = []
            lblsapp = lbls.append

            for k, val in zr.items():
                # loop over each axial region
                for iz in range(self.nZ):
                    if k == 'M1':
                        regsapp(val[iz])
                        lblsapp(labels[val[iz]])
                    else:
                        mystr = val[iz]
                        if mystr != 0: # mix name
                            regs[iz] = f'{regs[iz]}+{mystr}'
                            lbls[iz] = f'{lbls[iz]}+{labels[mystr]}'
            # make mixture name unique wrt iType and axial coordinates
            iMix = 1
            for jReg, r in enumerate(regs): # axial loop
                if '+' in r:
                    # update counter if mix already exists
                    if r in regs[:jReg]:
                        iMix += 1 
                    # add SAs type
                    regs[jReg] = f'{asstype}{iMix}_{r}'
                    l = lbls[jReg]
                    lbls[jReg] = f'{l}'
            # get unique regions without changing list order
            ureg = set()
            ureg_add = ureg.add
            tmp_dict = {}
            for iz in range(self.nZ):
                if not (regs[iz] in ureg or ureg_add(regs[iz])):
                    if regs[iz] not in self.regions.values():
                        self.regions[self.nReg+1] = regs[iz]
                        self.labels[regs[iz]] = lbls[iz]
                        tmp_dict[regs[iz]] = self.nReg
                    else:
                        tmp_dict[regs[iz]] = list(self.regions.values()).index(regs[iz])+1
            # --- assign axial configuration of iType SA 
            self.config_str.update({asstype: regs})
            self.config.update({iType: [tmp_dict[r] for r in regs]})
        # --- assign homog. flag
        self.homogenised = homog
        if splitz is not None:
            self.splitz = splitz
            mesh, centers = AxialCuts.mesh1d(splitz, self.zcuts)
            self.AxNodes = centers
            self.dz = mesh[1:]-mesh[:-1]

    def _from_dict(self, inpdict):
        """Parse object from dictionary.

        Parameters
        ----------
        inpdict : dict
            Input dictionary containing the class object (maybe read from 
            external file).
        """
        mydicts = ['regions', 'labels', 'config', 
                    'config_str', 'cutsregions', 'cutslabels',
                    'cutsweights']
        for k, v in inpdict.items():
            if k in mydicts:
                setattr(self, k, MyDict(v))
            elif k == "cuts":
                self.cuts = {}
                for k2, v2 in v.items():
                    self.cuts[k2] = AxialCuts(inpdict=v2)
            else:
                setattr(self, k, v)

    @property
    def nReg(self):
        """Returns the number of NE axial regions.

        Returns
        -------
        int
            Number of NE regions in the object.
        """
        return len(self.regions)

    @staticmethod
    def mapFine2Coarse(cuts, zcuts):
        """
        Generate dictionaries with region names, labels and weights for homogenisation.

        Parameters
        ----------
        cuts : ordered dict
            Dictionary with values ``AxialCuts`` objects assigned to assembly type
        zcuts : list
            List of cuts common to the whole reactor

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        OSError
            _description_
        """
        NZ = len(zcuts)-1
        cutsregions = {'M1': np.zeros((NZ,), dtype=object)}
        cutslabels = {'M1': np.zeros((NZ,), dtype=object)}
        cutsweights = {'M1': np.zeros((NZ,))}
        for iz in range(NZ): # loop over axial partitions
            lo, up = zcuts[iz], zcuts[iz+1]
            nmix = 1
            for r1, l1, lf, uf in cuts:
                if uf > lo and lf < up:
                    # --> belongs to partition
                    idx = f'M{nmix}'
                    if idx not in cutsregions.keys():
                        cutsregions[idx] = np.zeros((NZ,), dtype=object)
                        cutslabels[idx] = np.zeros((NZ,), dtype=object)
                        cutsweights[idx] = np.zeros((NZ,))

                    cutsregions[idx][iz] = r1
                    cutslabels[idx][iz] = l1
                    dzc = (up-lo)
                    isInCrs = lf >= lo and uf <= up
                    crssCrs = lf < lo or uf > up
                    if isInCrs or crssCrs: # (up-lf) < dzc or (uf-lo) < dzc: #(l1 >= lo and u1 < up) or (l1 > lo and u1 <= up):
                        nmix += 1
                        if isInCrs:
                            dzf = uf-lf
                        else:
                            if uf > up and lf < lo:
                                dzf = dzc # no homogenisation, only this region
                            elif lf < lo:
                                dzf = uf-lo
                            else:
                                dzf = up-lf
                        cutsweights[idx][iz] = dzf/dzc
                    else:
                        cutsweights[idx][iz] = 1

                elif lf >= up:
                    break
        # convert to list to avoid issue with h5 storage
        for k in cutsregions.keys():
            cutsregions[k] = cutsregions[k].tolist()
            cutslabels[k] = cutslabels[k].tolist()
            cutsweights[k] = cutsweights[k].tolist()

        # sanity check on weights
        checkw = np.zeros((NZ, ))
        for m, wm in cutsweights.items():
            checkw += wm
        if np.any(abs(checkw-1) > 1E-5):
            raise OSError("Weights for homogenisation are not"
                            f" normalised in {m}!")
        return cutsregions, cutslabels, cutsweights


class AxialCuts:
    """
    Define the axial cuts for a certain type of assembly.

    Parameters
    ----------
    up: list, optional
        Upper z-coordinate, by default ``None``
    lo: list, optional
        Lower z-coordinate, by default ``None``
    r: list, optional
        String identifying the region within upz and lowz, by default ``None``
    labels: list, optional
        Label for the region within upz and lowz, by default ``None``
    inpdict: dict, optional
        Input dictionary containing the object (if it comes
        from the outside), by default ``None``

    Attributes
    ----------
    upz: list
        Upper z-coordinate
    loz: list
        Lower z-coordinate
    reg: list
        String identifying the region within upz and lowz
    labels: list
        Label for the region within upz and lowz.
    Methods
    -------
    mesh1d: Compute nodes according to FRENETIC mesh1d.f90

    """

    def __init__(self, up=None, lo=None, r=None, labels=None,
                 inpdict=None):
        if inpdict is None:
            self._init(up, lo, r, labels)
        else:
            self._from_dict(inpdict)

    def _init(self, up, lo, r, labels):
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

        if not checkupz or not checkloz:
            raise OSError('Axial coordinates are not monotonic!' +
                          ' Check cuts or translation dz.')

        self.upz = up
        self.loz = lo
        self.reg = r
        self.labels = labels

    def _from_dict(self, inpdict):
        """Parse object from dictionary.

        Parameters
        ----------
        inpdict : dict
            Input dictionary containing the class object (maybe read from 
            external file).
        """
        for k, v in inpdict.items():
            setattr(self, k, v)

    def mesh1d(split, mesh0):
        """Compute nodes according to FRENETIC mesh1d.f90

        Parameters
        ----------
        split : np.array
            Array with axial split.
        mesh0 : list or np.array
            Iterable with axial boundaries.

        Returns
        -------
        mesh : np.array
            Axial mesh
        centers : np.array
            Centers of each axial cell
        
        """
        # --- 
        nelz = split.sum()
        mesh = np.zeros((nelz+1,))
        idz = 0
        for iz in range(len(mesh0)-1):
            dz = (mesh0[iz+1]-mesh0[iz])/split[iz]
            for i in range(split[iz]+1):
                mesh[idz+i] = mesh0[iz]+i*dz
            idz += split[iz]
        centers = (mesh[1:]+mesh[:-1])/2 
        return mesh, centers

