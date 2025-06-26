import os
import re
import sys
import json
import logging
import numpy as np
import coreutils.tools.h5 as myh5

from copy import deepcopy as cp
from shutil import which
from pathlib import Path

from coreutils.tools.utils import MyDict, write_log_header, write_coreutils_msg
from coreutils.tools.parser import parse
from coreutils.core.Map import Map
from coreutils.core.NE import NE
from coreutils.core.TH import TH
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import *
from coreutils.core.Geometry import Geometry, AxialConfig, AxialCuts
from coreutils.frenetic.InpGen import inpgen, fillFreneticNamelist

write_log_header()
logging.basicConfig(filename="coreutils.log",
                    filemode='a',
                    format='%(asctime)s :: %(name)s :: %(levelname)-8s ::  %(funcName)s :: %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


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
        if '.h5' in str(inpjson):
            write_coreutils_msg(f"Build core object from an existing .h5 file, {inpjson}")
            self._from_h5(inpjson)
        elif ".json" in str(inpjson):
            write_coreutils_msg(f"Build core object from a .json input file, {inpjson}")
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
                raise OSError('Hexagonal core geometry requires one sextant, so'
                              ' "rotation" must be 60 degree!')

        # --- ASSIGN COMMON INPUT DATA
        write_coreutils_msg(f"Assign general core data")

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
        write_coreutils_msg(f"Build core geometry")
        self.Geometry = Geometry(GEargs=GEargs)
        # backward compatibility
        if dim != 1:
            self.Map = self.Geometry.Map
            self.nAss = self.Geometry.nAss
        else:
            NEcore = [1]
            self.nAss = 1

        # --- NE OBJECT
        write_coreutils_msg(f"Build neutronics object (NE)")
        if isNE:
            # --- assign map
            assemblynames = NEargs['assemblynames']
            nAssTypes = 1 if dim == 1 else len(assemblynames)
            assemblynames = MyDict(dict(zip(assemblynames.keys(), np.arange(1, nAssTypes+1))))
            if dim != 1:
                tmp = UnfoldCore(NEargs['filename'], NEargs['rotation'], assemblynames)
                NEcore = tmp.coremap
            self.NE = NE(NEargs, self)
        else:
            if dim == 1:
                raise OSError('Cannot generate core object without NE namelist!')
            else:
                logger.info('NE input not available, writing TH input only!')

        # --- TH OBJECT
        write_coreutils_msg(f"Build thermal-hydraulics object (TH)")
        if isTH and dim != 1:
            # --- assign TH map
            assemblynames = THargs['htnames']
            nAssTypes = len(assemblynames)
            assemblynames = MyDict(dict(zip(assemblynames, np.arange(1, nAssTypes+1))))
            THcore = UnfoldCore(THargs['htdata']['filename'], THargs['rotation'], assemblynames).coremap
            self.TH = TH(THargs, self)
        else:
            logger.info('TH input not available, writing NE input only!')

        # --- NE and TH CONSISTENCY CHECK
        write_coreutils_msg(f"Perform NE-TH sanity check")
        if isNE and isTH:

            # dimensions consistency check
            BCcore = self.TH.BCconfig[0]
            if BCcore.shape != NEcore.shape:
                msg = (f"NE and TH core dimensions mismatch: {BCcore.shape} vs. {NEcore.shape}")
                logger.critical(msg)
                raise OSError(msg)

            # non-zero elements location consistency check
            tmp1 = cp(BCcore)
            tmp1[tmp1 != 0] = 1

            tmp2 = cp(NEcore)
            tmp2[tmp2 != 0] = 1

            if THargs['htdata'] is not None:
                tmp3 = cp(THcore)
                tmp3[tmp3 != 0] = 1

            if (tmp1 != tmp2).all():
                msg = "Assembly positions in BC and NE mismatch. Check core input file!"
                logger.critical(msg)
                raise OSError(msg)

            if (tmp1 != tmp3).all():
                msg = "Assembly positions in BC and TH mismatch. Check core input file!"
                logger.critical(msg)
                raise OSError(msg)

        # --- complete FRENETIC namelist and make input, if any
        if FRNargs is not None:
            write_coreutils_msg("Parse FRENETIC input settings")
            # update missing args with ones coming from Core object
            updatedFreneticNamelist = fillFreneticNamelist(self)
            self.FreneticNamelist = updatedFreneticNamelist

            if "makeinput" in CIargs.keys():
                if CIargs["makeinput"]:
                    # make FRENETIC input
                    write_coreutils_msg("Prepare FRENETIC input case")
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
