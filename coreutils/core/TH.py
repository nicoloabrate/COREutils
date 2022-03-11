"""
Author: N. Abrate.

File: core.py

Description: Class to define the thermal-hydraulics configuration of a core.
"""
import os
import re
import sys
import json
# from tkinter import NE
import numpy as np
import coreutils.tools.h5 as myh5
from copy import deepcopy as cp
# from collections import OrderedDict
from pathlib import Path
from coreutils.tools.utils import parse, MyDict
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import *
from coreutils.core.Assembly import AssemblyGeometry, AxialConfig, AxialCuts


class TH:
    """
    Define TH core configurations.

    Attributes
    ----------
    AssemblyGeom : obj
        Object with assembly geometrical features.
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
    perturbBCs :
        Replace assemblies with user-defined new or existing type.

    """
    def __init__(self, THargs=None, CI=None, inpdict=None):

        if inpdict is None:
            self._init(THargs, CI)
        else:
            self.from_dict(inpdict)

    def _init(self, THargs, CI):
        CZassemblynames = THargs['coolingzonenames']
        THdata = THargs['THargs']
        # sort list
        assnum = np.arange(1, len(CZassemblynames)+1)

        CZassemblynames = MyDict(dict(zip(CZassemblynames, assnum)))
        # define dict between strings and ints for assembly type
        self.CZassemblytypes = MyDict(dict(zip(assnum, CZassemblynames)))

        # define TH core with assembly types
        CZcore = UnfoldCore(THargs['coolingzonesfile'], THargs['rotation'], CZassemblynames).coremap

        if THdata is not None:
            THassemblynames = THdata['assemblynames']
            assnum = np.arange(1, len(THassemblynames)+1)
            THassemblynames = MyDict(dict(zip(THassemblynames,
                                                    assnum)))
            # define dict between strings and ints for assembly type
            self.THassemblytypes = MyDict(dict(zip(assnum,
                                                    THassemblynames)))
            THinp = THdata['filename']
            tmp = UnfoldCore(THinp, THargs['rotation'], THassemblynames)
            THcore = tmp.coremap
            THinp = tmp.inp

        if THcore.shape != CZcore.shape:
            raise OSError("CZ and TH core dimensions mismatch!")
        
        if THdata is not None and "replace" in THdata.keys():
            # loop over assembly types
            for k, v in THdata["replace"].items():
                try:
                    THcore = self.replace(THassemblynames[k], v, THargs['fren'],
                                            THcore)
                except KeyError:
                    raise OSError("%s not present in TH assembly types!"
                                    % k)
        # TH configuration
        self.time = [0]
        self.config = {}
        self.config[0] = THcore

        # CZ replace
        if isinstance(THargs['replace'], dict):
            # loop over assembly types
            for k, v in THargs['replace'].items():
                try:
                    CZcore = self.replace(CZassemblynames[k], v, THargs['fren'],
                                            CZcore)
                except KeyError:
                    raise OSError("%s not present in CZ assembly types!"
                                    % k)
        else:
            if THargs['replace'] is not None:
                raise OSError("'replace' in TH must be of type dict!")

        # assign material properties
        cz = CZMaterialData(THargs['massflowrates'], THargs['pressures'], 
                            THargs['temperatures'], self.CZassemblytypes.values())
        self.CZMaterialData = cz

        # keep each core configuration in time
        self.CZconfig = {}
        self.CZconfig[0] = CZcore
        self.CZtime = [0]
        # check if boundary conditions change in time
        THbcs = THargs['boundaryconditions']
        if THbcs is not None:
            for time in THbcs.keys():
                t = float(time)
                # increment time list
                self.CZtime.append(t)
                self.perturbBC(CI, THbcs[time], time, isfren=THargs['fren'])

    def from_dict(self, inpdict):
        mydicts = ["assemblytypes", "assemblylabel"]
        for k, v in inpdict.items():
            if k in mydicts:
                setattr(self, k, MyDict(v))
            else:
                setattr(self, k, v)

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
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        # check input type
        try:
            # check consistency between dz and which
            if len(pertconfig['which']) != len(pertconfig['what']):
                raise OSError('Groups of assemblies and perturbations do' +
                              'not match in TH "boundaryconditions"!')

            if len(pertconfig['with']) != len(pertconfig['what']):
                raise OSError('Each new value in TH "boundaryconditions"' +
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
                        self.CZMaterialData.__dict__[whatpar][newname] = withpar

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
                          ' in "boundaryconditions" in TH!')

    @property
    def nReg(self):
        return len(self.regions.keys())
