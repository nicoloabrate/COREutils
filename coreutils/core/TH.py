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
from coreutils.core.MaterialData import THHexData, CZdata
from coreutils.core.Geometry import Geometry, AxialConfig, AxialCuts


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
        CZassemblynames = THargs['cznames']
        CZconfig = THargs['czconfig']
        THconfig = THargs['thconfig']
        THdata = THargs['thdata']
        # sort list
        assnum = np.arange(1, len(CZassemblynames)+1)

        CZassemblynames = MyDict(dict(zip(CZassemblynames, assnum)))
        # define dict between strings and ints for assembly type
        self.CZassemblytypes = MyDict(dict(zip(assnum, CZassemblynames)))
        if 'czlabels' not in THargs.values():
            self.CZlabels = self.CZassemblytypes
        else:
            self.CZlabels = MyDict(dict(zip(assnum, THargs['czlabels'])))
        # define TH core with assembly types
        CZcore = UnfoldCore(THargs['czfile'], THargs['rotation'], CZassemblynames).coremap

        # --- define THcore
        THassemblynames = THargs['thnames'].keys()
        self.THtoGE = THargs['thnames']
        assnum = np.arange(1, len(THassemblynames)+1)
        THassemblynames = MyDict(dict(zip(THassemblynames, assnum)))
        # define dict between strings and ints for assembly type
        self.THassemblytypes = MyDict(dict(zip(assnum, THassemblynames)))
        if 'assemblylabels' not in THdata.values():
            self.THassemblylabels = self.THassemblytypes
        else:
            self.THassemblylabels = MyDict(dict(zip(assnum, THdata['assemblylabels'])))

        THinp = THdata['filename']
        tmp = UnfoldCore(THinp, THargs['rotation'], THassemblynames)
        THcore = tmp.coremap
        THinp = tmp.inp

        if THcore.shape != CZcore.shape:
            raise OSError("CZ and TH core dimensions mismatch!")

        self.CZtime = [0.]
        self.THtime = [0.]
        self.CZconfig = {}
        self.THconfig = {}
        self.CZconfig[0] = CZcore
        self.THconfig[0] = THcore

        # --- build time-dependent TH and CZ core configuration
        configurations = {'THconfig': THconfig, 'CZconfig': CZconfig}
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
                    # check operation
                    if config[time] == {}:  # enforce constant properties
                        nt = self.__dict__[f"{configtype}time"].index(float(time))
                        now = self.__dict__[f"{configtype}time"][nt-1]
                        self.__dict__[name][float(time)] = self.__dict__[name][now]

                    if "perturbBCs" in config[time]:
                        self.perturb(CI, config[time]["perturb"], time, configtype=configtype, isfren=True)

                    if "replace" in config[time]:
                        self.replaceSA(CI, config[time]["replace"], time, configtype=configtype, isfren=True)

        # assign material properties
        cz = CZdata(THargs['massflowrates'], THargs['pressures'], 
                            THargs['temperatures'], self.CZassemblytypes.values())
        self.CZdata = cz

        self.THdata = {}
        for HAtype, data in THdata['data'].items():
            atype = THassemblynames[HAtype]
            which = CI.getassemblylist(atype, self.THconfig[0], match=True, isfren=True)
            self.THdata[HAtype] = THHexData(which, data)

        # --- ADD OPTIONAL ARGUMENTS
        if "axplot" in THargs:
            if not hasattr(self, "thplot"):
                self.THplot = {}
            self.THplot['axplot'] = THargs["axplot"]

        if "radplot" in THargs:
                    if not hasattr(self, "thplot"):
                        self.THplot = {}
                    self.THplot['radplot'] = THargs["radplot"]

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

    def replaceSA(self, core, repl, time, configtype="CZ", isfren=False):
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
        if configtype == "CZ":
            asstypes = self.CZassemblytypes.reverse()
            config = self.CZconfig
        elif configtype == "TH":
            asstypes = self.THassemblytypes.reverse()
            config = self.THconfig
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

    def perturbBC(self, core, pertconfig, time, isfren=False):
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
        print("TODO: this method is an older version, it should be updated!")
        # check input type
        try:
            # check consistency between dz and which
            if len(pertconfig['which']) != len(pertconfig['what']):
                raise OSError('Groups of assemblies and perturbations do' +
                              'not match in TH "BCs"!')

            if len(pertconfig['with']) != len(pertconfig['what']):
                raise OSError('Each new value in TH "BCs"' +
                              ' must come with its identifying parameter!')

            pconf = zip(pertconfig['which'], pertconfig['with'],
                        pertconfig['what'])

            newcore = None
            if float(time) in self.CZconfig.keys():
                now = float(time)
            else:
                nt = self.CZtime.index(float(time))
                now = self.CZtime[nt-1]

            p = 0
            for which, withpar, whatpar in pconf:
                p = p + 1
                for assbly in which:
                    nt = self.CZtime.index(float(time))
                    atype = core.getassemblytype(assbly, self.CZconfig[now], isfren=isfren)
                    what = self.CZassemblytypes[atype]
                    basename = re.split(r"_t\d+.\d+_p\d+", what)[0]
                    newname = "%s_t%s_p%d" % (basename, time, p)

                    # take region name
                    if newname not in self.CZassemblytypes.values():
                        nass = len(self.CZassemblytypes.keys())
                        self.CZassemblytypes[nass + 1] = newname
                        # update values inside parameters
                        self.CZdata.__dict__[whatpar][newname] = withpar

                    # replace assembly
                    if newcore is None:
                        # take previous time-step configuration
                        newcore = self.replace(nass+1, assbly, isfren,
                                               self.CZconfig[now])
                    else:
                        # take "newcore"
                        newcore = self.replace(nass+1, assbly, isfren,
                                               newcore)
            # update cooling zones
            self.CZconfig[float(time)] = newcore

        except KeyError:
            raise OSError('"which" and/or "with" and/or "what" keys missing' +
                          ' in "BCs" in TH!')


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