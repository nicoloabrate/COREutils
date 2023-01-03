"""
Author: N. Abrate.

File: core.py

Description: Class to define the neutronic configuration of a core.

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


class NE:
    """
    Define NE core configurations.

    Attributes
    ----------
    AssemblyGeom : obj
        Object with assembly geometrical features.
    labels : dict
        Dictionary with regions names and strings for plot labelling.
    assemblytypes : dict
        Ordered dictionary with names of assembly NE types.
    Map : obj
        Object mapping the core assemblies with the different numerations.
    AxialConfig : obj
        Axial regions defined for NE purposes.
    data : obj
        NE data (multi-group constants) for each region defined in input.
        Neutronics configurations according to time.
    time : list
        Neutronics time instants when configuration changes.

    Methods
    -------
    replace :
        Replace assemblies with user-defined new or existing type.
    perturb :
        Replace assemblies with user-defined new or existing type.
    translate :
        Replace assemblies with user-defined new or existing type.
    """

    def __init__(self, NEargs=None, CI=None, inpdict=None, datacheck=True,
                 P1consistent=False):

        if inpdict is None:
            self._init(NEargs, CI, datacheck=datacheck)
        else:
            self.from_dict(inpdict)

    def _init(self, NEargs, CI, datacheck=True, P1consistent=False):
        # parse inp args
        dim = CI.dim
        assemblynames = tuple(NEargs['assemblynames'])
        cuts = {'xscuts': NEargs['xscuts'],
                'zcuts': NEargs['zcuts']}
        config = NEargs['config']
        NEfren = NEargs['fren']
        NEassemblylabel = NEargs['assemblylabel']
        NEdata = NEargs['NEdata']
        isPH = True if 'PH' in NEargs.keys() else False

        self.time = [0]
        # --- AXIAL GEOMETRY, IF ANY
        if cuts is not None and dim != 2:
            # initial axial configuration
            self.AxialConfig = AxialConfig(cuts, NEargs['splitz'], labels=NEargs['labels'], 
                                            NE_dim=dim, assemblynames=assemblynames)

        # --- PARSE INPUT REGIONS
        if dim == 2:
            # SAs types are the regions
            nReg = len(assemblynames)
            nAssTypes = nReg
            self.regions = MyDict(dict(zip(np.arange(1, nReg+1), assemblynames)))
            self.labels = dict(zip(self.regions.values(), self.regions.values()))
            # define dict mapping strings into ints for assembly type
            self.assemblytypes = MyDict(dict(zip(np.arange(1, nReg+1),
                                                        NEargs['assemblynames'])))
        else:
            self.regions = self.AxialConfig.regions
            self.labels = self.AxialConfig.labels
            self.assemblytypes = MyDict()
            NZ = len(self.AxialConfig.zcuts)-1
            NEtypes = assemblynames
            nAssTypes = len(NEtypes)
            # loop over SAs types (one cycle for 1D)
            for iType, NEty in enumerate(NEtypes):
                self.assemblytypes[iType+1] = NEty

        # --- PARSE ASSEMBLY NAMES AND MAP
        self.config = {}
        assemblynames = MyDict(dict(zip(assemblynames, np.arange(1, nAssTypes+1))))
        # --- define core Map, assembly names and types
        if dim != 1:
            tmp = UnfoldCore(NEargs['filename'], NEargs['rotation'], assemblynames)
            NEcore = tmp.coremap
        else:
            NEcore = [1]
        # --- define core time-dep. configurations
        self.config[0] = NEcore

        # --- define core time-dep. configurations
        # save coordinates for each layer (it can be updated later!)
        if cuts is not None and dim != 2:
            self.zcoord = MyDict()
            zc = self.AxialConfig.zcuts
            for iR, z1z2 in enumerate(zip(zc[:-1], zc[1:])):
                self.zcoord[iR] = z1z2

        if NEassemblylabel is not None:
            self.assemblylabel = MyDict(dict(zip(np.arange(1, nAssTypes+1),
                                                NEassemblylabel)))
        else:
            self.assemblylabel = cp(self.assemblytypes)

        # --- parse names of NE universes (==region mix)
        if dim != 2:
            univ = []  # consider axial regions in "cuts"
            for k in self.AxialConfig.cuts.keys():
                univ.extend(self.AxialConfig.cuts[k].reg)
        else:
            univ = cp(assemblynames)  # regions are assembly names
        # squeeze repetitions
        univ = list(set(univ))

        # ------ NE MATERIAL DATA AND ENERGY GRID
        if NEdata is not None:
            self.get_energy_grid(NEargs)
            self.NEdata = NEdata
            self.get_material_data(univ, CI, datacheck=datacheck, P1consistent=P1consistent)
            # --- check precursors family consistency
            NP = -1
            NPp = -1
            for temp in CI.TfTc:
                for k, mat in self.data[temp].items():
                    if NP == -1:
                        NP = mat.NPF
                    else:
                        if NP != mat.NPF:
                            raise OSError(f'Number of neutron precursor families in {k} '
                                        'not consistent with the other regions!')
                if isPH: # add photon data
                    PHargs = NEargs['PH']
                    self.get_PH_energy_grid(PHargs)
                    #for k, mat in self.PHMaterialData[temp].items():
                    #    if NPp == -1:
                    #        NPp = mat.NPF
                    #    else:
                    #        if NPp != mat.NPF:
                    #            raise OSError(f'Number of photon precursor families in {k} '
                    #                        'not consistent with the other regions!')
        
            self.nPre = NP
            if isPH:
                self.nPrp = 0 # FIXME TODO!
                self.nGrp = len(self.PHenergygrid)-1
                self.nDhp = 1 # FIXME TODO!
                print("WARNING: DHP set to 1!")
            else:
                self.nPrp = 0
                self.nGrp = 0
                self.nDhp = 0
        
        # ------ BUILD NE TIME_DEP. CONFIGURATIONS
        # do replacements if needed at time=0 s
        if NEargs["replaceSA"] is not None:
            self.replaceSA(CI, NEargs["replaceSA"], 0, isfren=NEfren)
        if NEargs["replace"] is not None:
            self.replace(CI, NEargs["replace"], 0, isfren=NEfren, P1consistent=P1consistent)

        # build time-dependent core configuration
        if config is not None:
            for time in config.keys():
                if time != '0':
                    t = float(time)
                    # increment time list
                    self.time.append(t)
                else:
                    # set initial condition
                    t = 0
                # check operation
                if config[time] == {}:  # enforce constant properties
                    nt = self.time.index(float(time))
                    now = self.time[nt-1]
                    self.config[float(time)] = self.config[now]
                if "translate" in config[time]:
                    self.translate(CI, config[time]["translate"],
                                   time, isfren=NEfren)

                if "critical" in config[time]:
                    self.critical(CI, config[time]["critical"], time)

                if "perturb" in config[time]:
                    self.perturb(CI, config[time]["perturb"],
                                   time, isfren=NEfren, P1consistent=P1consistent)

                if "replace" in config[time]:
                    self.replace(CI, config[time]["replace"], 
                                time, isfren=NEfren, P1consistent=P1consistent)

                if "replaceSA" in config[time]:
                    self.replaceSA(CI, config[time]["replaceSA"], 
                                   time, isfren=NEfren)

        # --- CLEAN DATASET 
        # remove unused regions
        if NEdata is not None:
            # remove Material objects if not needed anymore
            for temp in CI.TfTc:
                tmp = self.data[temp]
                universes = list(tmp.keys())
                for u in universes:
                    if u not in self.regions.values():
                        tmp.pop(u)

        # --- ADD OPTIONAL ARGUMENTS
        if "axplot" in NEargs and NEargs["axplot"] is not None:
            if not hasattr(self, "plot"):
                self.plot = {}
            self.plot['axplot'] = NEargs["axplot"]
        if "radplot" in NEargs and NEargs["radplot"] is not None:
            if not hasattr(self, "plot"):
                self.plot = {}
            self.plot['radplot'] = NEargs["radplot"]

    def from_dict(self, inpdict):
        mydicts = ["assemblytypes", "regions", "zcoord", "assemblylabel"]
        for k, v in inpdict.items():
            if k == "AxialConfig":
                setattr(self, k, AxialConfig(inpdict=v))
            else:
                if k in mydicts:
                    setattr(self, k, MyDict(v))
                else:
                    setattr(self, k, v)    

    def replaceSA(self, core, repl, time, isfren=False):
        """
        Replace full assemblies or axial regions.

        Parameters
        ----------
        repl : dict
            Dictionary with SA name as key and list of SAs to be replaced as value
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        if float(time) in self.config.keys():
            now = float(time)
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]
            time = self.time[nt]
        
        asstypes = self.assemblytypes.reverse()
        for NEtype in repl.keys():
            if NEtype not in self.assemblytypes.values():
                raise OSError(f"SA {NEtype} not defined! Replacement cannot be performed!")
            lst = repl[NEtype]
            if not isinstance(lst, list):
                raise OSError("replaceSA must be a dict with SA name as key and"
                                "a list with assembly numbers (int) to be replaced"
                                "as value!")
            if core.dim == 1:
                newcore = [asstypes[NEtype]]
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
                newcore = self.config[now]+0
                # --- load new assembly type
                newcore[rows, cols] = asstypes[NEtype]

            self.config[float(time)] = newcore


    def replace(self, core, rpl, time, isfren=False, action='repl', P1consistent=False):
        """
        Replace full assemblies or axial regions.
        
        This method is useful to replace axial regions in 1D or 3D models. Replacements can
        affect disjoint regions, but each replacement object should involve either the
        region subdivision (self.NE.AxialConfig.zcuts) or the xscuts subdivision (the one in 
        self.NE.AxialConfig.cuts[`AssType`]). If the replacement affect this last axial grid,
        homogenised data are computed from scratch and added to the material regions.
        The methods ``perturb`` and ``translate`` rely on this method to arrange the new
        regions.

        Parameters
        ----------
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        if core.dim == 2:
            return None
        
        if not isinstance(rpl, dict):
            raise OSError("Replacement object must be a dict with"
                          " `which`, `where` and `with` keys!")
        # map region names into region numbers
        regtypes = self.regions.reverse()
        if len(rpl['which']) != len(rpl['where']) or len(rpl['where']) != len(rpl['with']):
            raise OSError('Replacement keys must have the same number of elements '
                          'for which, where and with keys!')

        pconf = zip(rpl['which'], rpl['with'], rpl['where'])

        if float(time) in self.config.keys():
            nt = self.time.index(float(time))
            now = float(time)
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]

        iR = 0  # replacement counter
        for r in list(self.regions.values()):
            if action in r:
                iR += 1

        for which, withreg, where in pconf:
            iR += 1
            # arrange which into list of lists according to SA type
            whichlst = {}
            for w in which:
                itype = core.getassemblytype(w, self.config[now], isfren=isfren)
                if itype not in whichlst.keys():
                    whichlst[itype] = []
                whichlst[itype].append(w)

            for itype, assbly in whichlst.items(): # loop over each assembly
                atype = self.assemblytypes[itype]
                # --- parse replacement axial locations
                axpos = []
                axposapp = axpos.append

                cutaxpos = [] 
                cutaxposapp = cutaxpos.append
                if not isinstance(where, list):
                    where = [where]
                else:
                    if len(where) == 2:
                        if not isinstance(where[0], list):
                            where = [where]
                for rplZ in where:
                    rplZ.sort()
                    notfound = True  # to check consistency of "where" arg
                    incuts = False  # replacement may be in SA cuts
                    for ipos, coord in self.zcoord.items(): # check in zcoords
                        if tuple(rplZ) == coord:
                            notfound = False
                            axposapp(ipos)
                            break
                    if notfound: # check in cuts defining axial regions (e.g., from Serpent)
                        zcuts = zip(self.AxialConfig.cuts[atype].loz, self.AxialConfig.cuts[atype].upz)
                        for ipos, coord in enumerate(zcuts):
                            if tuple(rplZ) == coord:
                                notfound = False
                                incuts = True
                                cutaxposapp(ipos)
                                break
                        if notfound:
                            raise OSError(f"Cannot find axial region in {rplZ} for replacement!")
                # --- avoid replacement in xscuts and zcuts at the same time
                if len(axpos) > 0 and len(cutaxpos) > 0:
                    raise OSError('Cannot replace in xscuts and zcuts at the same time!'
                                  ' Add separate replacements!')

                # --- update object with new SA type
                if action in atype:
                    regex = rf"\-[0-9]{action}" # TODO test with basename like `IF-1-XXX-1repl`
                    basetype = re.split(regex, atype, maxsplit=1)[0]
                    newtype = f"{basetype}-{iR}{action}"
                    oldtype = atype
                else:
                    newtype = f"{atype}-{iR}{action}"
                    oldtype = newtype

                # --- identify new region number (int)
                if isinstance(withreg, list):  # look for region given its location
                    withwhich, z = withreg[0], withreg[1]
                    if not isinstance(z, list):
                        raise OSError("Replacement: with should contain a list with integers"
                                        " and another list with z1 and z2 coordinates!")
                    z.sort()
                    notfound = True  # to check consistency of "withreg" arg
                    for ipos, coord in self.zcoord.items():
                        if tuple(z) == coord:
                            notfound = False
                            break
                    if notfound:
                        for ipos, coord in enumerate(zcuts):
                            if tuple(rplZ) == coord:
                                notfound = False
                                break
                        if notfound:
                            raise OSError(f"Cannot find axial region to be replaced in {z}!")

                    iasstype = core.getassemblytype(withwhich, self.config[now], isfren=isfren)
                    if not incuts:
                        asstype = self.assemblytypes[iasstype]
                        newreg_str = self.AxialConfig.config_str[asstype][ipos]
                        newlab_str = self.labels[newreg_str]
                        newreg_int = self.AxialConfig.config[iasstype][ipos]
                    else:
                        newreg_str = self.AxialConfig.cuts[atype].reg[ipos]
                        newlab_str = self.AxialConfig.cuts[atype].label[ipos]
                        newreg_int = False
                elif isinstance(withreg, str):
                    newreg_str = withreg
                    if not incuts:
                        if withreg not in regtypes.keys():
                            self.regions[self.nReg+1] = withreg
                            self.labels[withreg] = withreg
                            regtypes = self.regions.reverse()
                        newreg_int = regtypes[withreg]
                        newlab_str = self.labels[newreg_str]
                    else:
                        newreg_int = False
                        idx = self.AxialConfig.cuts[atype].reg.index(newreg_str)
                        newlab_str = self.AxialConfig.cuts[atype].labels[idx]
                else:
                    raise OSError("'with' key in replacemente must be list or string!")

                nTypes = len(self.assemblytypes.keys())
                newaxregions = cp(self.AxialConfig.config[itype])
                newaxregions_str = cp(self.AxialConfig.config_str[atype])
                if not incuts:
                    for ax in axpos:
                        newaxregions[ax] = newreg_int
                        newaxregions_str[ax] = newreg_str
                    # add new type in xscuts (mainly for plot)
                    for irplZ, rplZ in enumerate(where):
                        # check new atype exists (if len(where) > 1)
                        if irplZ == 0:
                            cuts = cp(self.AxialConfig.cuts[atype])
                        else:
                            cuts = cp(self.AxialConfig.cuts[newtype])
                        upz, loz, reg, lab = cuts.upz, cuts.loz, cuts.reg, cuts.labels
                        if rplZ[0] not in loz:
                            loz.append(rplZ[0])
                            loz.sort()
                            upz.insert(loz.index(rplZ[0])-1, rplZ[0])
                        if rplZ[1] not in upz:
                            upz.append(rplZ[1])
                            upz.sort()
                            loz.insert(upz.index(rplZ[1])+1, rplZ[1])
                        for iz, zc in enumerate(list(zip(loz, upz))):
                            if tuple(rplZ) == zc:
                                break
                        reg.insert(iz, newreg_str)
                        lab.insert(iz, newlab_str)
                        self.AxialConfig.cuts[newtype] = AxialCuts(upz, loz, reg, lab)
                        # TODO add new data if replaced region is missing
                        # if withreg not in self.data[core.TfTc[0]].keys():
                        #     self.get_material_data([withreg], core, datacheck=datacheck)

                else: 
                    # --- define cutsregions of new SA type
                    cuts = cp(self.AxialConfig.cuts[atype])
                    # replace region in cuts
                    for ax in cutaxpos:
                        cuts.reg[ax] = newreg_str
                        cuts.labels[ax] = newlab_str
                    # --- update cuts object
                    self.AxialConfig.cuts[newtype] = cuts
                    cuts = list(zip(cuts.reg, cuts.labels, cuts.loz, cuts.upz))
                    zr, zl, zw = self.AxialConfig.mapFine2Coarse(cuts, self.AxialConfig.zcuts)
                    # --- update info for homogenisation
                    self.AxialConfig.cutsregions[newtype] = zr
                    self.AxialConfig.cutslabels[newtype] = zl
                    self.AxialConfig.cutsweights[newtype] = zw

                    regs = []
                    lbls = []
                    regsapp = regs.append
                    lblsapp = lbls.append
                    for k, val in zr.items():
                        # loop over each axial region
                        for iz in range(self.AxialConfig.nZ):
                            if k == 'M1':
                                regsapp(val[iz])
                                lblsapp(zl[k][iz])
                            else:
                                mystr = val[iz]
                                mylab = zl[k][iz]
                                if mystr != 0: # mix name
                                    regs[iz] = f'{regs[iz]}+{mystr}'
                                    lbls[iz] = f'{lbls[iz]}+{mylab}'
                    # --- UPDATE REGIONS
                    # make mixture name unique wrt iType and axial coordinates
                    iMix = 1
                    newmix = []  # new mix of different materials
                    newonlymat = []  # material used in mix but not present alone
                    # axial regions are equal except for replacements and new mixes
                    for jReg, r in enumerate(regs): # axial loop
                        if '+' in r:
                            # update counter if mix already exists
                            if r in regs[:jReg]:
                                iMix += 1 
                            # add SAs type
                            newmixname = f'{atype}{iMix}_{r}'
                            if newmixname not in self.regions.values():
                                newmix.append(f'{newtype}{iMix}_{r}')
                                self.regions[self.nReg+1] = f'{newtype}{iMix}_{r}'
                                self.labels[f'{newtype}{iMix}_{r}'] = f'{lbls[jReg]}'
                                newaxregions_str[jReg] = f'{newtype}{iMix}_{r}'
                                newaxregions[jReg] = self.nReg
                        else:
                            if r not in self.regions.values():
                                self.regions[self.nReg+1] = r
                                self.labels[r] = f'{lbls[jReg]}'
                    # --- homogenise
                    if self.AxialConfig.homogenised:
                        for temp in core.TfTc:
                            tmp = self.data[temp]  
                            for u0 in newmix:
                                # identify SA type and subregions
                                strsplt = re.split(r"\d_", u0, maxsplit=1)
                                NEty = strsplt[0]
                                names = re.split(r"\+", strsplt[1])
                                # parse weights
                                w = np.zeros((len(names), ))
                                for iM, mixname in enumerate(names):
                                    idz = newaxregions_str.index(u0)
                                    w[iM] = self.AxialConfig.cutsweights[NEty][f"M{iM+1}"][idz]
                                # perform homogenisation
                                mat4hom = {}
                                for name in names:
                                    mat4hom[name] = self.data[temp][name]
                                weight4hom = dict(zip(names, w))
                                tmp[u0] = Homogenise(mat4hom, weight4hom, u0, P1consistent=P1consistent)

                # --- update info in object
                if newtype not in self.assemblytypes.keys():
                    self.assemblytypes.update({nTypes+1: newtype})
                    self.assemblylabel.update({nTypes+1: newtype})

                    self.AxialConfig.config.update({nTypes+1: newaxregions})
                    self.AxialConfig.config_str.update({newtype: newaxregions_str})        
                    # --- replace assembly
                    if not isinstance(assbly, list):
                        assbly = [assbly]
                    self.replaceSA(core, {newtype: assbly}, time, isfren=isfren)

    def critical(self, core, prt):
        """
        
        Enforce criticality, given the static keff of the system

        Parameters
        ----------
        core : _type_
            _description_
        """
        iP = 0  # perturbation counter
        for p in list(self.regions.values()):
            if action in p:
                iP += 1
        if float(time) in self.config.keys():
            now = float(time)
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]

        # --- dict sanity check
        if 'keff' not in prtdict.keys():
            raise OSError(f'Mandatoy key `keff` missing in ''critical'' card for t={time} s')
        
        keff = keff*self.nGro

        # # --- get all fissile regions at the present config
        # if core.dim == 2: # check all regions
        #     reg2d_now = self.config[now].unique()
        #     fiss_mat = []
        #     for iReg in reg2d_now:
        #         reg_str = self.regions[iReg]
            #     for temp in core.TfTc:
        #             if self.data[temps][reg_str].isfiss:
                #         self.data[temp][prtreg] = cp(self.data[temp][oldreg])
                #         self.data[temp][prtreg].perturb(perturbation, howmuch, depgro, sanitycheck=sanitycheck, P1consistent=P1consistent)

        # else:
            #     # --- perturb data and assign it

        #     # --- add new assemblies
        #     self.regions[self.nReg+1] = prtreg
        #     self.labels[prtreg] = f"{self.labels[oldreg]}-{iP}{action}"
        #     # --- define replacement dict to introduce perturbation
        #     if core.dim == 2:
        #         repl = {atype: assbly}
        #         self.replaceSA(core, repl, time, isfren=isfren)
        #     else:
        #         repl = {"which": [assbly], "with": [prtreg], "where": [zpert]}
        #         self.replace(core, repl, time, isfren=isfren, action=action, P1consistent=P1consistent)


    def perturb(self, core, prt, time=0, sanitycheck=True, isfren=True,
                action='pert', P1consistent=False):
        """

        Perturb material composition.

        Parameters
        ----------
        what : TYPE
            DESCRIPTION.
        howmuch : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if not isinstance(prt, list):
            prt = [prt]

        iP = 0  # perturbation counter
        for p in list(self.regions.values()):
            if action in p:
                iP += 1
        if float(time) in self.config.keys():
            now = float(time)
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]
        
        zcoord = self.zcoord
        # loop over perturbations
        for prtdict in prt:
            # check perturbation
            if not isinstance(prtdict, dict):
                raise OSError("Replacement object must be a dict with"
                              " `which`, `where` and `howmuch` keys!")
            iP += 1
            # --- dict sanity check
            mandatorykeys = ['where', 'howmuch', 'which', 'what']
            for mk in mandatorykeys:
                if mk not in prtdict.keys():
                    if mk == 'which' and core.dim == 1:
                        prtdict['which'] = self.config[now]
                    elif mk == 'where' and core.dim == 2:
                        prtdict['where'] = None
                    else:
                        if mk == 'where' and 'region' in prtdict.keys():
                            prtdict['where'] = None
                            continue
                        else:
                            raise OSError(f'Mandatoy key `{mk}` missing in perturbation for t={time} s')
            if 'depgro' not in prtdict.keys():
                prtdict['depgro'] = None

            # parse all SAs including the "region" if specified by the user
            if prtdict['which'] == 'all':
                # determine integer type of SAs according to "region" and "where" keys
                for iSA, SA_str in enumerate(self.AxialConfig.config_str.keys()):
                    if prtdict['region'] in self.AxialConfig.config_str[SA_str]:
                        atype = iSA+1
                prtdict['which'] = core.getassemblylist(atype, config=self.config[now], isfren=isfren)
            
            # arrange which into list of lists according to SA type
            whichlst = {}
            for w in prtdict['which']:
                itype = core.getassemblytype(w, self.config[now], isfren=isfren)
                if itype not in whichlst.keys():
                    whichlst[itype] = []
                whichlst[itype].append(w)

            z1z2 = prtdict['where']
            howmuch = prtdict['howmuch']
            depgro = prtdict['depgro']
            perturbation = prtdict['what']
            if perturbation != 'density':
                if len(howmuch) != self.nGro:
                    if len(howmuch) == 1:
                        howmuch = howmuch*self.nGro
                    else:
                        raise OSError('The perturbation intensities' 
                                      f' required should be list of 1 or {self.nGro} elements')

            notfound = True  # to check consistency of "where" arg
            for itype, assbly in whichlst.items(): # loop over each assembly
                atype = self.assemblytypes[itype]
                # --- localise region to be perturbed
                if z1z2 is not None:
                    z1z2.sort()
                    incuts = False  # replacement may be in SA cuts
                    for ipos, coord in self.zcoord.items(): # check in zcoords
                        if tuple(z1z2) == coord:
                            notfound = False
                            break
                    if notfound: # check in cuts
                        zcuts = list(zip(self.AxialConfig.cuts[atype].loz, self.AxialConfig.cuts[atype].upz))
                        for ipos, coord in enumerate(zcuts):
                            if tuple(z1z2) == coord:
                                notfound = False
                                incuts = True
                                break
                        if notfound:
                            raise OSError(f"Cannot find axial region in {z1z2} for replacement!")
                    if incuts:
                        oldreg = self.AxialConfig.cuts[atype].reg[ipos]
                        zpert = [list(zcuts[ipos])]
                    else:
                        oldreg = self.AxialConfig.config_str[atype][ipos]
                        zpert = [list(self.zcoord[ipos])]
                else:
                    if core.dim == 2:  # perturb full SA (only in 2D case)
                        oldreg = self.assemblytypes[itype]
                    else:
                        # --- parse all axial regions with oldreg
                        oldreg = prtdict['region']
                        izpos = []
                        for i, r in enumerate(self.AxialConfig.config_str[atype]):
                            if r == oldreg:
                                izpos.append(i)
                        # ensure region is not also in mix
                        for r in self.regions.values():
                            if "+" in r:
                                if oldreg in r:
                                    raise OSError('Cannot perturb region which is both alone and'
                                                  'in mix! Use separate perturbation cards!')                     
                        if izpos == []:  # look in xscuts
                            for i, r in enumerate(self.AxialConfig.cuts[atype].reg):
                                if r == oldreg:
                                    izpos.append(i)
                        # get coordinates
                        zpert = []
                        for i in izpos:
                            zpert.append(list(self.zcoord[i]))
                # define perturbed region name
                prtreg = f"{oldreg}-{iP}{action}"
                # --- perturb data and assign it
                for temp in core.TfTc:
                    self.data[temp][prtreg] = cp(self.data[temp][oldreg])
                    self.data[temp][prtreg].perturb(perturbation, howmuch, depgro, sanitycheck=sanitycheck, P1consistent=P1consistent)
                # --- add new assemblies
                self.regions[self.nReg+1] = prtreg
                self.labels[prtreg] = f"{self.labels[oldreg]}-{iP}{action}"
                # --- define replacement dict to introduce perturbation
                if core.dim == 2:
                    repl = {atype: assbly}
                    self.replaceSA(core, repl, time, isfren=isfren)
                else:
                    repl = {"which": [assbly], "with": [prtreg], "where": [zpert]}
                    self.replace(core, repl, time, isfren=isfren, action=action, P1consistent=P1consistent)

    def translate(self, core, transconfig, time, isfren=False, action='trans'):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        transconfig : dict
            Dictionary with details on translation transformation
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        # check input type
        # check consistency between dz and which
        if len(transconfig['which']) != len(transconfig['dz']):
            raise OSError('Groups of assemblies and number of ' +
                            'translations do not match!')

        if 'dz' not in transconfig.keys():
            raise OSError('dz missing in translate input!')
        if 'which' not in transconfig.keys():
            raise OSError('which missing in translate input!')

        if isinstance(transconfig['which'], str):
            str2int = self.assemblytypes.reverse()
            asstype = str2int[transconfig['which']]
            which = self.getassemblylist(asstype, self.config[now])
            transconfig['which'] = which

        if float(time) in self.config.keys():
            now = float(time)
            time = now
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]
            time = self.time[nt]
        
        iT = 0  # replacement counter
        for v in list(self.regions.values()):
            if action in v:
                iT += 1

        for dz, which in zip(transconfig['dz'], transconfig['which']):
            # repeat configuration if dz = 0
            if dz != 0:
                iT += 1
                # arrange which into list of lists according to SA type
                whichlst = {}
                for w in which:
                    itype = core.getassemblytype(w, self.config[now], isfren=isfren)
                    if itype not in whichlst.keys():
                        whichlst[itype] = []
                    whichlst[itype].append(w)
                for itype, assbly in whichlst.items():
                    atype = self.assemblytypes[itype]
                    nTypes = len(self.assemblytypes.keys())
                    # --- assign new assembly name
                    if action in atype:
                        regex = rf"\-[0-9]{action}" # TODO test with basename like `IF-1-XXX-1trans`
                        basetype = re.split(regex, atype, maxsplit=1)[0]
                        newtype = f"{basetype}-{iT}{action}"
                        oldtype = atype
                    else:
                        newtype = f"{atype}-{iT}{action}"
                        oldtype = newtype

                    # --- define new cuts
                    if newtype not in self.AxialConfig.cuts.keys():
                        # --- operate translation
                        cuts = cp(self.AxialConfig.cuts[atype])
                        cuts.upz[0:-1] = [z+dz for z in cuts.upz[0:-1]]
                        cuts.loz[1:] = [z+dz for z in cuts.loz[1:]]
                        self.AxialConfig.cuts[newtype] = AxialCuts(cuts.upz, cuts.loz, cuts.reg, cuts.labels)
                        cuts = list(zip(cuts.reg, cuts.labels, cuts.loz, cuts.upz))
                        zr, zl, zw = self.AxialConfig.mapFine2Coarse(cuts, self.AxialConfig.zcuts)
                        # --- update info for homogenisation
                        self.AxialConfig.cutsregions[newtype] = zr
                        self.AxialConfig.cutslabels[newtype] = zl
                        self.AxialConfig.cutsweights[newtype] = zw

                        regs = []
                        lbls = []
                        regsapp = regs.append
                        lblsapp = lbls.append
                        for k, val in zr.items():
                            # loop over each axial region
                            for iz in range(self.AxialConfig.nZ):
                                if k == 'M1':
                                    regsapp(val[iz])
                                    lblsapp(zl[k][iz])
                                else:
                                    mystr = val[iz]
                                    mylab = zl[k][iz]
                                    if mystr != 0: # mix name
                                        regs[iz] = f'{regs[iz]}+{mystr}'
                                        lbls[iz] = f'{lbls[iz]}+{mylab}'
                        # --- update region dict
                        newaxregions = [None]*len(regs)
                        newaxregions_str = [None]*len(regs)
                        # make mixture name unique wrt itype and axial coordinates
                        iMix = 1
                        newmix = []  # new mix of different materials
                        newonlymat = []  # material used in mix but not present alone
                        for jReg, r in enumerate(regs): # axial loop
                            # nMIX = self.nReg
                            if '+' in r:
                                # update counter if mix already exists
                                if r in regs[:jReg]:
                                    iMix += 1
                                # add SAs type
                                newmixname = f'{newtype}{iMix}_{r}'
                                if newmixname not in self.regions.values():
                                    newmix.append(f'{newtype}{iMix}_{r}')
                                    self.regions[self.nReg+1] = f'{newtype}{iMix}_{r}'
                                    self.labels[f'{newtype}{iMix}_{r}'] = f'{lbls[jReg]}'
                                    newaxregions_str[jReg] = f'{newtype}{iMix}_{r}'
                                    newaxregions[jReg] = self.nReg
                                else:
                                    str2int = self.regions.reverse()
                                    newaxregions[jReg] = str2int[f'{newtype}_{r}']
                                    newaxregions_str[jReg] = f"{newtype}_{r}"  # or oldtype?
                            else:
                                if r not in self.regions.values():
                                    self.regions[self.nReg+1] = r
                                    self.labels[r] = f'{lbls[jReg]}'
                                    nMIX = self.nReg
                                else:
                                    str2int = self.regions.reverse()
                                    nMIX = str2int[r]
                                newaxregions[jReg] = nMIX
                                newaxregions_str[jReg] = r
                        # --- homogenise
                        for temp in core.TfTc:
                            tmp = self.data[temp]  
                            for u0 in newmix:
                                # identify SA type and subregions
                                strsplt = re.split(r"\d_", u0, maxsplit=1)
                                NEty = strsplt[0]
                                names = re.split(r"\+", strsplt[1])
                                # parse weights
                                w = np.zeros((len(names), ))
                                for iM, mixname in enumerate(names):
                                    idz = newaxregions_str.index(u0)
                                    w[iM] = self.AxialConfig.cutsweights[NEty][f"M{iM+1}"][idz]
                                # perform homogenisation
                                mat4hom = {}
                                for name in names:
                                    mat4hom[name] = self.data[temp][name]
                                weight4hom = dict(zip(names, w))
                                tmp[u0] = Homogenise(mat4hom, weight4hom, u0)

                    # --- update info in object
                    if newtype not in self.assemblytypes.keys():
                        self.assemblytypes.update({nTypes+1: newtype})
                        self.assemblylabel.update({nTypes+1: newtype})
                        self.AxialConfig.config.update({nTypes+1: newaxregions})
                        self.AxialConfig.config_str.update({newtype: newaxregions_str})
                    # --- replace assembly
                    if not isinstance(assbly, list):
                        assbly = [assbly]
                    dim = 3
                    self.replaceSA(core, {newtype: assbly}, time, isfren=isfren)

    def get_material_data(self, univ, core, datacheck=True, P1consistent=False):
        try:
            path = self.NEdata['path']
        except KeyError:
            pwd = Path(__file__).parent.parent.parent
            if 'coreutils' not in str(pwd):
                raise OSError(f'Check coreutils tree for NEdata: {pwd}')

            # look into default NEdata dir
            path = str(pwd.joinpath('NEdata', self.egridname))

        if "checktempdep" not in self.NEdata.keys():
            self.NEdata["checktempdep"] = 0

        try:
            files = self.NEdata['beginwith']
        except KeyError:
            # look for Serpent files in path/serpent
            pwd = Path(__file__).parent.parent.parent
            serpath = str(pwd.joinpath('NEdata', f'{self.egridname}',
                                        'serpent'))
            try:
                files = [f for f in os.listdir(serpath)]
            except FileNotFoundError as err:
                print(str(err))
                files = []

        if not hasattr(self, 'data'):
            self.data = {}
        for temp in core.TfTc:
            if temp not in self.data.keys():
                self.data[temp] = {}
            tmp = self.data[temp]
            # get temperature for OS operation on filenames or do nothing
            T = temp if self.NEdata["checktempdep"] else None
            # look for all data in Serpent format
            serpres = {}
            serpuniv = []
            for f in files:
                sdata = readSerpentRes(path, self.energygrid, T, 
                                        beginswith=f, egridname=self.egridname)
                if sdata is not None:
                    serpres[f] = sdata
                    for univtup in sdata.universes.values():
                        # access to HomogUniv attribute name
                        serpuniv.append(univtup.name)

            for u in univ:
                if u in serpuniv:
                    tmp[u] = NEMaterial(u, self.energygrid, egridname=self.egridname, 
                                        serpres=serpres, temp=T, datacheck=datacheck, P1consistent=P1consistent)
                else: # look for data in json and txt format
                    tmp[u] = NEMaterial(u, self.energygrid, 
                                        egridname=self.egridname,
                                        datapath=path, temp=T, basename=u, datacheck=datacheck, P1consistent=P1consistent)
            # --- HOMOGENISATION (if any)
            if core.dim != 2:
                if self.AxialConfig.homogenised:
                    for u0 in self.regions.values():
                        if "+" in u0: # homogenisation is needed
                            # identify SA type and subregions
                            strsplt = re.split(r"\d_", u0, maxsplit=1)
                            NEty = strsplt[0]
                            names = re.split(r"\+", strsplt[1])
                            # parse weights
                            w = np.zeros((len(names), ))
                            for iM, mixname in enumerate(names):
                                idx = self.AxialConfig.config_str[NEty].index(u0)
                                w[iM] = self.AxialConfig.cutsweights[NEty][f"M{iM+1}"][idx]
                            # perform homogenisation
                            mat4hom = {}
                            for name in names:
                                mat4hom[name] = self.data[temp][name]
                            weight4hom = dict(zip(names, w))
                            tmp[u0] = Homogenise(mat4hom, weight4hom, u0)

    def get_energy_grid(self, NEargs):
        if 'egridname' in NEargs.keys():
            ename = NEargs['egridname']
        else:
            ename = None

        if 'energygrid' in NEargs.keys():
            energygrid = NEargs['energygrid']
        else:
            energygrid = ename

        if isinstance(energygrid, (list, np.ndarray, tuple)):
            self.nGro = len(energygrid)-1
            self.egridname = f'{self.nGro}G' if ename is None else ename
            self.energygrid = energygrid
        elif isinstance(energygrid, (str, float, int)):
            pwd = Path(__file__).parent.parent.parent
            if 'coreutils' not in str(pwd):
                raise OSError(f'Check coreutils tree for NEdata: {pwd}')
            else:
                pwd = pwd.joinpath('NEdata')
                if isinstance(energygrid, str):
                    fgname = f'{energygrid}.txt'
                    self.egridname = str(energygrid)
                else:
                    fgname = f'{energygrid}G.txt'
                    self.egridname = str(energygrid)

                egridpath = pwd.joinpath('group_structures', fgname)
                self.energygrid = np.loadtxt(egridpath)
                self.nGro = len(self.energygrid)-1
        else:
            raise OSError(f'Unknown energygrid \
                            {type(energygrid)}')

        if self.energygrid[0] < self.energygrid[0]:
            self.energygrid[np.argsort(-self.energygrid)]

    def get_PH_energy_grid(self, PHargs):
        #FIXME FIXME FIXME this should be integrated in the foregoing method
        if 'egridname' in PHargs.keys():
            ename = PHargs['egridname']
        else:
            ename = None

        if 'energygrid' in PHargs.keys():
            energygrid = PHargs['energygrid']
        else:
            energygrid = ename

        if isinstance(energygrid, (list, np.ndarray, tuple)):
            self.nGrp = len(energygrid)-1
            self.egridname = f'{self.nGrp}G' if ename is None else ename
            self.PHenergygrid = energygrid
        elif isinstance(energygrid, (str, float, int)):
            pwd = Path(__file__).parent.parent.parent
            if 'coreutils' not in str(pwd):
                raise OSError(f'Check coreutils tree for PHdata: {pwd}')
            else:
                pwd = pwd.joinpath('PHdata')
                if isinstance(energygrid, str):
                    fgname = f'{energygrid}.txt'
                    self.egridname = str(energygrid)
                else:
                    fgname = f'{energygrid}G.txt'
                    self.egridname = str(energygrid)

                egridpath = pwd.joinpath('group_structures', fgname)
                self.PHenergygrid = np.loadtxt(egridpath)
                self.nGrp = len(self.PHenergygrid)-1
        else:
            raise OSError(f'Unknown energygrid \
                            {type(energygrid)}')

        if self.PHenergygrid[0] < self.PHenergygrid[0]:
            self.PHenergygrid[np.argsort(-self.PHenergygrid)]

    @property
    def nReg(self):
        return len(self.regions.keys())
