"""
Author: N. Abrate.

File: core.py

Description: Class to define the nuclear reactor core geometry defined in an
external text file.
"""
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

from coreutils.tools.utils import parse, MyDict
from coreutils.core.Map import Map
from coreutils.core.NE import NE
from coreutils.core.TH import TH
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import *
from coreutils.core.Assembly import AssemblyGeometry, AxialConfig, AxialCuts


class Core:
    """
    Define NE, TH and CZ core configurations.

    Attributes
    ----------
    AssemblyGeom : obj
        Object with assembly geometrical features.
    Map : obj
        Object mapping the core assemblies with the different numerations.
    NE : obj
        Axial regions defined for NE purposes.


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
        if ".json" not in inpjson:
            raise OSError("Input file must be in .json format!")
        # -- parse input file
        else:

            CIargs, NEargs, THargs = parse(inpjson)

            tEnd = CIargs['tEnd']
            nProf = CIargs['nSnap'] 
            pitch = CIargs['pitch'] 
            shape = CIargs['shape'] 
            power = CIargs['power'] 
            trans = CIargs['trans']
            dim = CIargs['dim']

            # check if NEargs and THargs are not empty
            isNE = True if NEargs is not None else False
            isTH = True if THargs is not None else False
            if isNE:
                isPH = True if 'isPH' in NEargs.keys() else False
            if isPH:
                PHargs = NEargs['PH']

        # --- sanity check
        if dim != 1 and shape == 'H':
            flag = False
            if THargs is not None:
                if 'rotation' in THargs.keys():
                    flag = THargs['rotation'] != 60
            if NEargs is not None:
                if 'rotation' in NEargs.keys():
                    if not flag:
                        flag = NEargs['rotation'] != 60
            if flag:
                raise OSError('Hexagonal core geometry requires one sextant, so' +
                            '"rotation" must be 60 degree!')

        if not isNE:
            if dim == 1:
                raise OSError('Cannot generate core object without NE namelist!')
            else:
                print('NE input not available, writing TH input only!')
        if not isTH and dim != 1:
            print('TH input not available, writing NE input only!')

        # --- ASSIGN COMMON INPUT DATA
        TfTc = []
        CIargs['Tf'].sort()
        CIargs['Tc'].sort()
        fuel_temp = CIargs['Tf']
        cool_temp = CIargs['Tc']
        fuel_temp = np.asarray(fuel_temp,dtype=np.double)
        cool_temp = np.asarray(cool_temp,dtype=np.double)
        # ensure ascending order
        for Tf in fuel_temp:
            for Tc in cool_temp:
                if Tf >= Tc:
                    TfTc.append((Tf, Tc))
        self.TfTc = TfTc
        self.Tf = fuel_temp
        self.Tc = cool_temp
        self.TimeEnd = tEnd
        self.trans = trans
        self.dim = dim
        self.power = power

        if isinstance(nProf, (float, int)):
            dt = tEnd/nProf
            self.TimeSnap = np.arange(0, tEnd+dt, dt) if dt > 0 else [0]
        elif isinstance(nProf, list) and len(nProf) > 1:
            self.TimeSnap = nProf
        else:
            raise OSError('nSnap in .json file must be list with len >1, float or int!')

        # --- initialise assembly radial geometry object
        self.AssemblyGeom = AssemblyGeometry(pitch, shape)  # module indep.
        # --- NE OBJECT
        if isNE:
            # --- assign map
            assemblynames = NEargs['assemblynames']
            nAssTypes = 1 if dim == 1 else len(assemblynames)
            assemblynames = MyDict(dict(zip(assemblynames, np.arange(1, nAssTypes+1))))
            if dim != 1:
                tmp = UnfoldCore(NEargs['filename'], NEargs['rotation'], assemblynames)
                NEcore = tmp.coremap
                self.Map = Map(NEcore, NEargs['rotation'], self.AssemblyGeom, inp=tmp.inp)
                if not hasattr(self, 'Nass'):
                    self.NAss = len((self.Map.serpcentermap))
            else:
                NEcore = [1]
                self.NAss = 1
            datacheck = 1
            self.NE = NE(NEargs, self, datacheck=datacheck)

        # --- TH OBJECT
        if isTH and dim != 1:
            # --- assign TH map
            assemblynames = THargs['assemblynames']
            nAssTypes = len(assemblynames)
            assemblynames = MyDict(dict(zip(assemblynames, np.arange(1, nAssTypes+1))))
            THcore = UnfoldCore(THargs['filename'], THargs['rotation'], assemblynames).coremap
            if not hasattr(self, 'Map'):
                self.Map = Map(THcore, THargs['rotation'], self.AssemblyGeom, inp=tmp.inp)
            if not hasattr(self, 'Nass'):
                self.NAss = len((self.Map.serpcentermap))

            self.TH = TH(THargs, self)

        # --- NE and TH CONSISTENCY CHECK
        if isNE and isTH:
            # dimensions consistency check
            CZcore = self.TH.CZconfig[0]
            if CZcore.shape != NEcore.shape:
                raise OSError("NE and TH core dimensions mismatch:" +
                              f"{CZcore.shape} vs. {NEcore.shape}")

            # non-zero elements location consistency check
            tmp1 = cp(CZcore)
            tmp1[tmp1 != 0] = 1

            tmp2 = cp(NEcore)
            tmp2[tmp2 != 0] = 1

            if THargs['THargs'] is not None:
                tmp3 = cp(THcore)
                tmp3[tmp3 != 0] = 1

            if (tmp1 != tmp2).all():
                raise OSError("Assembly positions in CZ and NE mismatch. " +
                              "Check core input file!")

            if (tmp1 != tmp3).all():
                raise OSError("Assembly positions in CZ and TH mismatch. " +
                              "Check core input file!")

    def _from_h5(self, h5name):
        """Instantiate object from h5 file.

        Parameters
        ----------
        h5name : str
            Path to h5 file.
        """
        h5f = myh5.read(h5name, metadata=False)
        for k, v in h5f.core.items():
            if k == "NE":
                setattr(self, k, NE(inpdict=v))
            elif k == "TH":
                setattr(self, k, TH(inpdict=v))
            elif k == 'AssemblyGeom':
                setattr(self, k, AssemblyGeometry(inpdict=v))
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
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is False.

        Returns
        -------
        which : int
            Type of assembly.

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

    def writecentermap(self, numbers=True, fname="centermap.txt"):
        """
        Write centermap to text file.

        Parameters
        ----------
        numbers : bool, optional
            Write assembly numbers in the first columns. The default is
            ``True``. If ``False``, the assembly type are written instead.
        fname : str, optional
            Centermap file name. The default is "centermap.txt".

        Returns
        -------
        ``None``

        """
        # define regions
        typelabel = np.reshape(self.Map.type, (self.Map.Nx*self.Map.Ny, 1))
        regions = []
        for key, coord in (self.Map.serpcentermap).items():
            x, y = coord
            if numbers is False:
                key = typelabel[key-1, 0]
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
        match : bool, optional
            If ``True``, it takes the assemblies matching with atype. If
            ``False``, it takes all the others. The default is ``True``.

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
        """
        Write core lattice to txt file.

        Parameters
        ----------
        flatten : bool, optional
            Flag to print matrix or flattened array. The default is ``False``.
        fname : str, optional
            File name. The default is "corelattice.txt".
        serpheader : bool, optional
            Serpent 2 code instructions for core lattice geometry
            header. The default is ``False``.
        numbers : bool, optional
            Print assembly numbers instead of assembly names in the core 
            lattice.

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
                for s in self.Map.serp2fren.keys():
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
            if self.AssemblyGeom.type == 'S':
                asstype = '1'  # square
            elif self.AssemblyGeom.type == 'H':
                asstype = '3'  # hexagon
            # define central assembly coordinates
            x0, y0 = self.Map.serpcentermap[self.Map.fren2serp[1]][:]
            x0, y0 = str(x0), str(y0)
            # define number of assemblies along x and y directions
            Nx, Ny = str(Nx), str(Ny)
            # define assembly pitch
            P = str(2*self.AssemblyGeom.apothema)
            header = " ".join(("lat core ", asstype, x0, y0, Nx, Ny, P))
            comm = ''
        # save array to file
        if fname is not None:
            np.savetxt(fname, typelabel, delimiter=" ", fmt=fmt, header=header,
                    comments=comm)
        else:
            return typelabel

    def to_h5(self, name):

        LoaderManager.register_class(
            Core,                # MyClass type object this loader handles
            b'Core',             # byte string representing the name of the loader 
            create_group, # the create dataset function defined in first example above
            None,                   # usually None
            CoreContainer,          # the PyContainer to be used to restore content of MyClass
            True,                   # Set to False to force explicit storage of MyClass instances in any case 
            None                    # if set to None loader is enabled unconditionally
            )
        hkl.dump(self, f'{name}.h5', mode='w')
