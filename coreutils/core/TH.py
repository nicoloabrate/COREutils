import os
import re
import sys
import json
import logging
# from tkinter import NE
import numpy as np
import coreutils.tools.h5 as myh5
from copy import deepcopy as cp
# from collections import OrderedDict
from pathlib import Path
from coreutils.tools.utils import MyDict
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import HTHexData
from coreutils.core.Geometry import Geometry, AxialConfig, AxialCuts
from coreutils.input.TH_input import *
class TH:
    """
    Define TH core configurations.

    Attributes
    ----------
    labels : dict
        Dictionary with regions names and strings for plot labelling.
    assemblytypes : dict
        Ordered dictionary with names of assembly NE types.
    AxialConfig : obj
        Axial regions defined for NE purposes.
    data : obj
        NE data (multi-group constants) for each region defined in input.
        Neutronics configurations according to time.
    time : list
        Neutronics time instants when configuration changes.

    Methods
    -------
        from_dict:
        replaceSA: 
            Replace full assemblies.
        perturbBC:
            Spatially perturb cooling zone boundary conditions.

    """
    def __init__(self, THargs=None, CI=None, inpdict=None):

        if inpdict is None:
            self._init(THargs, CI)
        else:
            self.from_dict(inpdict)

    def _init(self, THargs, CI):
        # parse inp args
        dim = CI.dim  # it could be useful in the future for 1D and 2D cases
        BCassemblynames = THargs['bcnames']
        BCconfig = THargs['bcconfig']
        HTconfig = THargs['htconfig']
        HTdata = THargs['htdata']
        # sort list
        assnum = np.arange(1, len(BCassemblynames)+1)

        BCassemblynames = MyDict(dict(zip(BCassemblynames, assnum)))
        # define dict between strings and ints for assembly type
        self.BCassemblytypes = MyDict(dict(zip(assnum, BCassemblynames)))
        if 'bclabels' not in THargs.values():
            self.BClabels = self.BCassemblytypes
        else:
            self.BClabels = MyDict(dict(zip(assnum, THargs['bclabels'])))
        # define TH core with assembly types
        BCcore = UnfoldCore(THargs['bcfile'], THargs['rotation'], BCassemblynames).coremap

        # --- define THcore
        HTassemblynames = THargs['htnames'].keys()
        self.HTtoGE = THargs['htnames']
        assnum = np.arange(1, len(HTassemblynames)+1)
        HTassemblynames = MyDict(dict(zip(HTassemblynames, assnum)))
        # define dict between strings and ints for assembly type
        self.HTassemblytypes = MyDict(dict(zip(assnum, HTassemblynames)))
        if 'assemblylabels' not in HTdata.values():
            self.HTassemblylabels = self.HTassemblytypes
        else:
            self.HTassemblylabels = MyDict(dict(zip(assnum, HTdata['assemblylabels'])))

        HTinp = HTdata['filename']
        tmp = UnfoldCore(HTinp, THargs['rotation'], HTassemblynames)
        HTcore = tmp.coremap
        HTinp = tmp.inp

        if HTcore.shape != BCcore.shape:
            raise OSError("BC and HT core dimensions mismatch!")

        self.BCtime = [0.]
        self.HTtime = [0.]
        self.BCs = {}
        self.BCconfig = {}
        self.HTconfig = {}
        self.BCconfig[0] = BCcore
        self.HTconfig[0] = HTcore
        # --- set initial value of Boundary Conditions
        self.BCs = {
                    "massflowrate": {"time": [0.], "values" : np.zeros((1, CI.nAss))},
                    "temperature": {"time": [0.], "values" : np.zeros((1, CI.nAss))},
                    "pressure": {"time": [0.], "values" : np.zeros((1, CI.nAss))},
                    }
        for n in CI.Map.fren2serp.keys():
            if n > CI.nAss:
                break
            # get data in assembly
            idx = CI.getassemblytype(n, BCcore, isfren=True) - 1
            for field in ["massflowrate", "temperature", "pressure"]:
                self.BCs[field]["values"][0, n-1] = THargs[field][idx]

        # --- build time-dependent TH and BC core configuration
        configurations = {'HTconfig': HTconfig, 'BCconfig': BCconfig}
        for name, config in configurations.items():
            configtype = name.split('config')[0]
            if config is not None:
                for time in config.keys():
                    if time != '0':
                        t = float(time)
                        # increment time list
                        self.__dict__[f"{configtype}time"].append(t)
                    else:
                        # set initial condition
                        t = 0

                    if "perturbBCs" in config[time]:
                        self.perturbBCs(CI, config[time]["perturbBCs"], time=time, isfren=True)

                    if "replace" in config[time]:
                        self.replaceSA(CI, config[time]["replace"], time, configtype=configtype, isfren=True)

        self.HTdata = {}
        for HAtype, data in HTdata['data'].items():
            atype = HTassemblynames[HAtype]
            which = CI.getassemblylist(atype, self.HTconfig[0], match=True, isfren=True)
            self.HTdata[HAtype] = HTHexData(which, data)

        # --- ADD OPTIONAL OUTPUT ARGUMENTS
        self.plot = {}
        self.plot['axplot'] = THargs["axplot"]
        self.plot['radplot'] = THargs["radplot"]
        self.worksheet = THargs["worksheet"]

        if THargs["nelems"] is not None:
            self.nVol = THargs["nelems"]
            self.zmesh = [z/100 for z in THargs["zmesh"]]
            self.zmesh.sort()
            if THargs["nelref"] is not None:
                self.nVolRef = THargs["nelref"]
                self.zref = [z/100 for z in THargs["zref"]]
                self.zref.sort()
            nVolRef = self.nVolRef if hasattr(self, "nVolRef") else None
            zref = self.zref if hasattr(self, "zref") else [0, 0]
            zcoord, axstep = meshTH1d(min(self.zmesh), max(self.zmesh), self.nVol, 
                                        nvolref=nVolRef, zminref=min(zref),
                                        zmaxref=max(zref))
            self.zcoord = zcoord
            self.axstep = axstep

    def from_dict(self, inpdict):
        mydicts = ["assemblytypes", "assemblylabel"]
        for k, v in inpdict.items():
            if k in mydicts:
                setattr(self, k, MyDict(v))
            else:
                setattr(self, k, v)

    def replaceSA(self, core, repl, time, configtype="BC", isfren=False):
        """
        Replace full assemblies.

        Parameters
        ----------
        repl : dict
            Dictionary with SA name as key and list of SAs to be replaced as value
        isfren : bool, optional
            Flag for FRENETIC numeration, by default ``False``.

        Returns
        -------
        ``None``

        """
        if configtype == "BC":
            asstypes = self.BCassemblytypes.reverse()
            config = self.BCconfig
        elif configtype == "HT":
            asstypes = self.HTassemblytypes.reverse()
            config = self.HTconfig
        else:
            raise OSError(f"{configtype} configtype argument unknown!")
        
        if float(time) in config.keys():
            now = float(time)
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]
            time = self.time[nt]
        
        for SAtype in repl.keys():
            if SAtype not in asstypes.keys():
                raise OSError(f"SA {SAtype} not defined in {configtype} config.! Replacement cannot be performed!")
            lst = repl[SAtype]
            if not isinstance(lst, list):
                raise OSError("replaceSA must be a dict with SA name as key and"
                                "a list with assembly numbers (int) to be replaced"
                                "as value!")
            if core.dim == 1:
                newcore = [asstypes[SAtype]]
            else:
                # --- check map convention
                if isfren:
                    # translate FRENETIC numeration to Serpent
                    index = [core.Map.fren2serp[i]-1 for i in lst]  # -1 for index
                else:
                    index = [i-1 for i in lst]  # -1 to match python indexing
                # --- get coordinates associated to these assemblies
                index = (list(set(index)))
                rows, cols = np.unravel_index(index, core.Map.type.shape)
                newcore = config[now]+0
                # --- load new assembly type
                newcore[rows, cols] = asstypes[SAtype]

            config[float(time)] = newcore

    def perturbBCs(self, core, pert, time, isfren=False):
        """
        Spatially perturb cooling zone boundary conditions.

        Parameters
        ----------
        newtype : list
            List of new/existing types of assemblies.
        asslst : list
            List of assemblies to be replaced.
        isfren : bool, optional
            Flag for FRENETIC numeration, by default ``False``.

        Returns
        -------
        ``None``

        """
        try:
            pert =  perturbBCs_obj(**pert)
        except ValidationError as e:
            print("ValidationError. Check the .json input file!")
            raise THError(e.errors())
        # check input type
        i_pert = 0
        for what in pert.model_fields_set:
            p = pert.__dict__[what]
            newcore = None
            # if float(time) in self.BCconfig.keys():
            #     now = float(time)
            # else:
            #     nt = self.BCtime.index(float(time))
            #     now = self.BCtime[nt-1]

            if hasattr(p, "func"):
                # add initial time
                t0 = float(time)
                t = t0
                BC = self.BCs[what]
                BC["time"].append(t)
                n_tstart = BC["time"].index(t0)
                n_t = n_tstart
                n_ass = self.BCs[what]["values"].shape[1]
                for f in p.func:
                    for func in f.keys():
                        dt = f[func].dt
                        var = f[func].variation

                        if func == "step" or func == "linear":
                            if func == "step":
                                if dt == 0 or dt > 1E-3:
                                    dt = 1E-12
                            if n_t == n_tstart:
                                BC["values"] = np.concatenate((BC["values"], 
                                                               BC["values"][n_t - 1, :][np.newaxis, :]), axis=0)
                                n_t += 1
                            else:
                                if dt <= dt_old:
                                    raise THError("dt in perturbBCs should be increasing!")
                            # perturb at time
                            BC["values"] = np.concatenate((BC["values"], BC["values"][n_t - 1, :][np.newaxis, :]), axis=0)
                            BC["time"].append(t0+dt)
                            for w_lst in p.which:
                                for w in w_lst:
                                    BC["values"][n_t, w - 1] = BC["values"][n_tstart, w - 1]*var

                            n_t += 1
                            dt_old = dt

                        else:
                            raise THError(f"{func} type not implemented!")

            i_pert += 1

def meshTH1d(zmin, zmax, nvol, nvolref=None, 
             zminref=None, zmaxref=None):
    """provide baricenter of each nodes between zmin and zmax with optional refinement.
       This method is based on the subroutine mesh.f90 of FRENETIC.

    Parameters
    ----------
    zmin : float
        Minimum axial coordinate.
    zmax : float
        Maximum axial coordinate.
    nvol : integer
        Number of axial volumes.
    nvolref : integer, optional
        Number of volumes to be used in the refined region.
    zminref : float
        Minimum axial coordinate in the refined region.
    zmaxref : float
        Maximum axial coordinate in the refined region.

    Returns
    -------
    centers : np.array
        Centers of each axial cell
    
    """
    refinement = True if nvolref is not None else False

    # allocation
    zcoord = np.zeros((nvol,), dtype=float)
    axstep = np.zeros((nvol,), dtype=float)
    zltot = zmax-zmin

    if refinement:
        # variable definition
        nvol1 = nvol-nvolref
        zlref = zmaxref-zminref
        zlout = zltot-zlref
        # build mesh
        axstep[0] = zminref/np.floor(nvol1*(zminref/zlout))
        zcoord[0] = 0.0 + axstep[0]/2.0
        iz = 0
        while zcoord[iz]+axstep[iz]/2.+1E-10 <= zminref:
            z0 = zcoord[iz]
            axstep[iz+1] = zminref/np.floor(nvol1*(zminref/zlout))
            zcoord[iz+1] = z0 + axstep[iz+1]/2.+axstep[iz]/2.
            iz += 1
        while zcoord[iz]+axstep[iz]/2.+1E-10 <= zmaxref:
            z0 = zcoord[iz]
            axstep[iz+1] = zlref/nvolref
            zcoord[iz+1] = z0 + axstep[iz+1]/2.+axstep[iz]/2.
            iz += 1
        while zcoord[iz]+axstep[iz]/2.+1E-10 <= zltot:
            z0 = zcoord[iz]
            axstep[iz+1] = (zltot-zmaxref)/(np.ceil(nvol1*(zltot-zmaxref)/zlout))
            zcoord[iz+1] = z0 + axstep[iz+1]/2.+axstep[iz]/2.
            iz += 1
    else:
        # build mesh
        axstep[:] = zltot/nvol
        zcoord[0] = 0.0 + axstep[0]/2.0
        for iz in range(1, nvol):
            z0 = zcoord[iz-1]
            zcoord[iz] = z0 + axstep[iz]

    return zcoord, axstep

class THError(Exception):
    pass