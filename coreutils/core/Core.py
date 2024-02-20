import os
import re
from shutil import which
import sys
import json
# from tkinter import NE
import numpy as np
import coreutils.tools.h5 as myh5
from copy import deepcopy as cp
# from collections import OrderedDict
from pathlib import Path

from coreutils.tools.utils import MyDict
from coreutils.tools.parser import parse
from coreutils.core.Map import Map
from coreutils.core.NE import NE
from coreutils.core.TH import TH
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import *
from coreutils.core.Geometry import Geometry, AxialConfig, AxialCuts
from coreutils.frenetic.InpGen import inpgen, fillFreneticNamelist


class Core:
    """
    Define NE and TH core configurations.

    Parameters
    ----------
    inpjson: string
        Path to the input file in .json format.

    Attributes
    ----------
    AssemblyGeom : :class:`coreutils.core.Geometry.AssemblyGeometry`
        Object with assembly geometrical features.
    Map: :class:`coreutils.core.Map`
        Object mapping the core assemblies with the different numerations.
    NAss: int
        Number of assemblies.
    NE: :class:`coreutils.core.NE`
        Object for the NEutronic configuration.
    TH: :class:`coreutils.core.TH`
        Object for the Thermo-Hydraulic configuration.
    Tc: np.array
        Array with coolant temperatures for NE data.
    Tf: np.array
        Array with fuel temperatures for NE data.
    TfTc: np.array
        Array with fuel and coolant temperatures for NE data.
    TimeEnd: float
        End simulation time in seconds.
    dim: int
        Number of spatial dimensions.
    power: float
        Total power in Watt.
    trans: bool
        Boolean for transient case.
    FreneticNamelist: dict
        Dictionary containing keywords needed for FRENETIC input.

    Methods
    -------
    getassemblytype :
        Get type of a certain assembly.
    replace :
        Replace assemblies with user-defined new or existing type.
    perturb :
        Replace assemblies with user-defined new or existing type.
    translate :
        Replace assemblies with user-defined new or existing type.
    perturbBC :
        Spatially perturb cooling zone boundary conditions.
    writecentermap :
        Write assembly number and x and y coordinates of centers to text file.
    getassemblylist :
        Return assemblies belonging to a certain type.
    writecorelattice :
        Write core lattice to txt file.
    """

    def __init__(self, inpjson):
        if '.h5' in inpjson:
            self._from_h5(inpjson)
        elif ".json" in inpjson:
            self.from_json(inpjson)
        else:
            raise OSError("Input must .h5 or .json file!")

    def from_json(self, inpjson):
        """Generate object from .json file.

        Parameters
        ----------
        inpjson : string
            Path to .json input file

        Raises
        ------
        OSError
            If input file is not in .json format
        OSError
            If input rotation angle is != 60 for hexagonal
            assemblies
        OSError
            If NE input is not provided
        OSError
            If BC and NE assembly map are not consistent
        OSError
            If BC and TH assembly map are not consistent

        """
        if ".json" not in inpjson:
            raise OSError("Input file must be in .json format!")
        # -- parse input file
        else:

            CIargs, GEargs, NEargs, THargs, FRNargs = parse(inpjson)

            tEnd = CIargs['tend']
            nProf = CIargs['nsnap'] 
            power = CIargs['power'] 
            trans = CIargs['trans']
            pitch = GEargs['lattice_pitch'] 
            shape = GEargs['shape'] 
            dim = GEargs['dim']

            # check if NEargs and THargs are not empty
            isNE = True if NEargs is not None else False
            isTH = True if THargs is not None else False
            if isNE:
                isPH = True if 'PH' in NEargs.keys() else False
            if isPH:
                PHargs = NEargs['PH']

        # --- sanity check
        if dim != 1 and shape == 'H':
            flag = False
            if THargs is not None:
                if 'rotation' in THargs.keys():
                    flag = THargs['rotation'] != 60 and THargs['rotation'] != 0
            if NEargs is not None:
                if 'rotation' in NEargs.keys():
                    if not flag:
                        flag = NEargs['rotation'] != 60 and NEargs['rotation'] != 0
            if not flag and GEargs['rotation'] is not None:
                flag = GEargs['rotation'] != 60 and GEargs['rotation'] != 0

            if flag:
                raise OSError('Hexagonal core geometry requires one sextant, so' +
                              ' "rotation" must be 60 degree!')

        if not isNE:
            if dim == 1:
                raise OSError('Cannot generate core object without NE namelist!')
            else:
                logging.info('NE input not available, writing TH input only!')
        if not isTH and dim != 1:
            logging.info('TH input not available, writing NE input only!')

        # --- ASSIGN COMMON INPUT DATA
        TfTc = []
        CIargs['tf_tc'].sort()
        self.TfTc = [(Ttup[0], Ttup[1]) for Ttup in CIargs['tf_tc']]
        self.Tf = []
        self.Tc = [] 
        for Tf, Tc in self.TfTc:
            if Tf < Tc:
                raise OSError(f"Tf={Tf} < Tc={Tc}! Check input file.")
            else:
                self.Tf.append(Tf)
                self.Tc.append(Tc)
        self.Tf = list(set(self.Tf))
        self.Tc = list(set(self.Tc))
        self.Tf.sort()
        self.Tc.sort()

        self.TimeEnd = tEnd
        self.trans = trans
        self.dim = dim
        self.power = power
        self.coolant = CIargs['coolant']

        if FRNargs is not None:
            self.FreneticNamelist = FRNargs

        # TODO FIXME ensure consistency with NE and TH modules
        # foresee start time for restarted simulations (TimeSnap could be translated in time but only for FRN input)
        if isinstance(nProf, (float, int)):
            dt = tEnd/nProf
            self.TimeSnap = np.arange(0, tEnd+dt, dt) if dt > 0 else [0]
        elif isinstance(nProf, list) and len(nProf) > 1:
            self.TimeSnap = nProf
        else:
            raise OSError('nSnap in .json file must be list with len >1, float or int!')

        # --- GE object
        self.Geometry = Geometry(GEargs=GEargs)

        # --- NE OBJECT
        if isNE:
            # --- assign map
            assemblynames = NEargs['assemblynames']
            nAssTypes = 1 if dim == 1 else len(assemblynames)
            assemblynames = MyDict(dict(zip(assemblynames.keys(), np.arange(1, nAssTypes+1))))
            if dim != 1:
                tmp = UnfoldCore(NEargs['filename'], NEargs['rotation'], assemblynames)
                NEcore = tmp.coremap
                self.Map = Map(NEcore, NEargs['rotation'], self.Geometry.AssemblyGeometry, inp=tmp.inp)
                if not hasattr(self, 'Nass'):
                    self.nAss = len((self.Map.serpcentermap))
            else:
                NEcore = [1]
                self.nAss = 1
            datacheck = 1
            self.NE = NE(NEargs, self, datacheck=datacheck)

        # --- TH OBJECT
        if isTH and dim != 1:
            # --- assign TH map
            assemblynames = THargs['htnames']
            nAssTypes = len(assemblynames)
            assemblynames = MyDict(dict(zip(assemblynames, np.arange(1, nAssTypes+1))))
            THcore = UnfoldCore(THargs['htdata']['filename'], THargs['rotation'], assemblynames).coremap
            if not hasattr(self, 'Map'):
                self.Map = Map(THcore, THargs['rotation'], self.Geometry.AssemblyGeometry, inp=tmp.inp)
            if not hasattr(self, 'Nass'):
                self.nAss = len((self.Map.serpcentermap))

            self.TH = TH(THargs, self)

        # --- NE and TH CONSISTENCY CHECK
        if isNE and isTH:
            # dimensions consistency check
            BCcore = self.TH.BCconfig[0]
            if BCcore.shape != NEcore.shape:
                raise OSError("NE and TH core dimensions mismatch:" +
                              f"{BCcore.shape} vs. {NEcore.shape}")

            # non-zero elements location consistency check
            tmp1 = cp(BCcore)
            tmp1[tmp1 != 0] = 1

            tmp2 = cp(NEcore)
            tmp2[tmp2 != 0] = 1

            if THargs['htdata'] is not None:
                tmp3 = cp(THcore)
                tmp3[tmp3 != 0] = 1

            if (tmp1 != tmp2).all():
                raise OSError("Assembly positions in BC and NE mismatch. " +
                              "Check core input file!")

            if (tmp1 != tmp3).all():
                raise OSError("Assembly positions in BC and TH mismatch. " +
                              "Check core input file!")

        # --- complete FRENETIC namelist and make input, if any
        if FRNargs is not None:
            # update missing args with ones coming from Core object
            updatedFreneticNamelist = fillFreneticNamelist(self)
            self.FreneticNamelist = updatedFreneticNamelist

            if "makeinput" in CIargs.keys():
                if CIargs["makeinput"]:
                    # make FRENETIC input
                    inpgen(self, inpjson)

    def _from_h5(self, h5name):
        """Instantiate object from h5 file.

        Parameters
        ----------
        h5name : str
            Path to h5 file.

        Returns:
            None
        """
        h5f = myh5.read(h5name, metadata=False)
        for k, v in h5f.core.items():
            if k == "NE":
                setattr(self, k, NE(inpdict=v))
            elif k == "TH":
                setattr(self, k, TH(inpdict=v))
            elif k == 'Geometry':
                setattr(self, k, Geometry(inpdict=v))
            elif k == 'Map':
                setattr(self, k, Map(inpdict=v))
            else:
                setattr(self, k, v)

    def getassemblytype(self, assemblynumber, config, isfren=False):
        """
        Get type of a certain assembly.

        Parameters
        ----------
        assemblynumber : int
            Number of the assembly of interest
        config: np.array
            Array defining the assembly arrangement with integers
        isfren : bool, optional
            Flag for FRENETIC numeration, by default ``False``

        Returns
        -------
        which : int
            Type of assembly corresponding to ``assemblynumber``.

        """
        if self.dim == 1:
            return config[0]
        if isfren:
            # translate FRENETIC numeration to Serpent
            index = self.Map.fren2serp[assemblynumber]-1  # -1 for py indexing
        else:
            index = assemblynumber-1  # -1 for py indexing
        # get coordinates associated to these assemblies
        rows, cols = np.unravel_index(index, self.Map.type.shape)
        which = config[rows, cols]
        return which

    def writecentermap(self, numbers=True, fren=True, fname="centermap.txt"):
        """Write assembly number and x and y coordinates of centers to text file.

        Parameters
        ----------
        numbers : bool, optional
            Write assembly numbers in the first columns, by default
            ``True``. If ``False``, the assembly type are written instead.
        fren : bool, optional
            Flag for FRENETIC numeration, by default ``False``
        fname : str, optional
            Centermap file name, by default "centermap.txt".

        Returns
        -------
        ``None``

        """
        # define regions
        typelabel = np.reshape(self.Map.type, (self.Map.Nx*self.Map.Ny, 1))
        regions = []
        for key, coord in (self.Map.serpcentermap).items():
            x, y = coord
            if not numbers:
                key = typelabel[key-1, 0]
            else:
                if fren:
                    key = self.Map.serp2fren[key]

            regions.append((key, x, y))

        # write region to external file
        with open(fname, 'w') as f:  # open new file
            f.write("\n".join("{:03d} {:5f} {:5f}".format(elem[0], elem[1],
                                                          elem[2])
                              for elem in regions))
            f.write("\n")

    def getassemblylist(self, atype, config, match=True, isfren=False):
        """
        Return assemblies belonging to a certain type.

        Parameters
        ----------
        atype : int
            Desired assembly type.
        config: np.array
            Array defining the assembly arrangement with integers
        match : bool, optional
            If ``True``, it takes the assemblies matching with atype. If
            ``False``, it takes all the others, by default ``True``.
        isfren : bool, optional
            Flag for FRENETIC numeration, by default ``False``

        Returns
        -------
        matchedass : list
            List of matching/non-matching assemblies.

        """
        asstypes = config.flatten(order='C')

        if match:
            matchedass = np.where(asstypes == atype)[0]+1  # +1 for py indexing
        else:
            matchedass = np.where(asstypes != atype)[0]+1

        if isfren:
            matchedass = [self.Map.serp2fren[m] for m in matchedass]

        matchedass.sort()

        return matchedass

    def writecorelattice(self, flatten=False, fname="corelattice.txt",
                         serpheader=False, string=True, whichconf="NE",
                         numbers=False, fren=True, time=0):
        """Write core lattice to txt file.

        Parameters
        ----------
        flatten : bool, optional
            Flag to print matrix or flattened array, by default ``False``.
        fname : str, optional
            File name, by default "corelattice.txt".
        serpheader : bool, optional
            Serpent 2 code instructions for core lattice geometry
            header, by default ``False``.
        string: bool
            Format of the file entries, by default ``True``.
        whichconf: string
            Type of configuration, by default ``"NE"``.
        numbers : bool, optional
            Print assembly numbers instead of assembly names in the core 
            lattice.
        fren : bool, optional
            Flag for FRENETIC numeration, by default ``True``
        time: float
            Time instant of the desired configuration, in seconds

        Returns
        -------
        ``None``

        """
        Nx, Ny = self.Map.Nx+0, self.Map.Ny+0
        asstypes = cp(self.__dict__[whichconf].config[time])
        assemblynames = self.__dict__[whichconf].assemblytypes

        if numbers:
            # flatten typelabel matrix
            typemap = np.reshape(asstypes, (Nx*Ny, 1))
            if fren:
                for s, f in self.Map.serp2fren.items():
                    typemap[s-1] = f
            else:
                for s in self.Map.serpcentermap.keys():
                    typemap[s-1] = s
            asstypes = np.reshape(typemap, (Nx, Ny), order='F')

        # define regions
        if flatten is False:
            typelabel = asstypes
        else:
            typelabel = np.reshape(asstypes, (Nx*Ny, 1))

        # determine file format
        if string is False:
            # determine number of digits
            nd = str(len(str(self.Map.type.max())))
            fmt = "%0"+nd+"d"
        else:
            fmt = "%s"
            typelabel = typelabel.astype(str)
            for key, val in assemblynames.items():
                typelabel[typelabel == str(key)] = val

            typelabel[typelabel == '0'] = 'VV'

        # determine header
        if serpheader is False:
            header = ""
            comm = '#'
        else:  # Serpent-2 style header (define core lattice)
            # define assembly type according to Serpent
            if self.Geometry.AssemblyGeometry.type == 'S':
                asstype = '1'  # square
            elif self.Geometry.AssemblyGeometry.type == 'H':
                asstype = '3'  # hexagon
            # define central assembly coordinates
            x0, y0 = self.Map.serpcentermap[self.Map.fren2serp[1]][:]
            x0, y0 = str(x0), str(y0)
            # define number of assemblies along x and y directions
            Nx, Ny = str(Nx), str(Ny)
            # define assembly pitch
            P = str(2*self.Geometry.AssemblyGeometry.apothema)
            header = " ".join(("lat core ", asstype, x0, y0, Nx, Ny, P))
            comm = ''
        # save array to file
        if fname is not None:
            np.savetxt(fname, typelabel, delimiter=" ", fmt=fmt, header=header,
                    comments=comm)
        else:
            return typelabel
