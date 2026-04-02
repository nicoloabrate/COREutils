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
from collections import OrderedDict
from coreutils.tools.utils import MyDict, write_coreutils_msg
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import MGC_reader, NEMaterial, Homogenise
from coreutils.core.Geometry import Geometry, AxialConfig, AxialCuts
from matplotlib import colors

logger = logging.getLogger(__name__)

mycols1 = ["#19647e", "#28afb0", "#ee964b", # generated with Coloor
           "#ba324f", "#1f3e9e", "#efd28d",
           "#ffffff", 
           "#f0c808", "#fff1d0", "#dd1c1a",
           "#003049", "#d62828", "#f77f00", "#fcbf49", "#eae2b7",
           "#6C5548", "#B45A38", "#603827", "#13466E", "#F5A964", 
           "#1980A7", "#491F15", "#006094", "#E8743F", "#2AA3C4", "#1f271b", 
           "#f66024", "#104b6d", "#3bbeaa", "#18441b", "#79ac3d", "#e27db1", "white",   # generated with Colorgorical (http://vrl.cs.brown.edu/color)
           "#e99863", "#5b0891", "#3986da", "#8e80fb", "#e3488e", "#02b72e", 
           "#e26df8", "#52351d", "#852405", "#9ca08c", "#2524f9", "#e194be", "#fa1bfc",
           "#851657"]
xkcd = list(colors.XKCD_COLORS.keys())  
mycols1.extend(xkcd)

reader_ext = {
            "serpent": "_res.m",
            "json": ".json",
            "scone": ".json",
            "txt": ".txt",
            "nemtab": ".XS",
             }

multi_material_readers = ["serpent", "scone"]

n_digits_max = 14

class NE:
    """
    Define NE core configurations.

    Attributes
    ----------
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

    def __init__(self, NEargs=None, CI=None, inpdict=None):

        if inpdict is None:
            self._init(NEargs, CI)
        else:
            self.from_dict(inpdict)

    def _init(self, NEargs, CI):
        # parse inp args
        dim = CI.dim
        self.NEtoGE = NEargs['assemblynames']
        # --- ADD OPTIONAL PLOTTING ARGUMENTS
        self.plot = {}
        self.plot['SAcolors'] = NEargs["sacolors"]
        self.plot['AXcolors'] = NEargs["axcolors"]
        self.plot['axplot'] = NEargs["axplot"]
        self.plot['radplot'] = NEargs["radplot"]

        assemblynames = tuple(NEargs['assemblynames'])

        cuts = {'xscuts': NEargs['xscuts'],
                'zcuts': NEargs['zcuts']}
        config = NEargs['config']
        NEfren = NEargs['fren']
        NEassemblylabel = NEargs['assemblylabel']
        MMGCdata = NEargs['mgcdata']
        self.time = [0.]
        # ------ GEOMETRY ------
        # --- AXIAL GEOMETRY, IF ANY
        if cuts is not None and dim != 2:
            write_coreutils_msg(f"Build core axial geometry for NE object")
            # initial axial configuration
            self.AxialConfig = AxialConfig(cuts, NEargs['splitz'], labels=NEargs['labels'], 
                                           NE_dim=dim, assemblynames=assemblynames, colors=self.plot['AXcolors'])

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
        write_coreutils_msg(f"Build core radial geometry for NE object")
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
            NE_regions = []  # consider axial regions in "cuts"
            for k in self.AxialConfig.cuts.keys():
                NE_regions.extend(self.AxialConfig.cuts[k].reg)
        else:
            NE_regions = cp(assemblynames)  # regions are assembly names
        # squeeze repetitions
        NE_regions = list(set(NE_regions))

        # ------ NE MATERIAL DATA AND ENERGY GRID ------
        if MMGCdata is not None:
            self.MGClibrary = MGClibrary(MMGCdata, NE_regions, CI, self)

        # ------ BUILD NE TIME_DEP. CONFIGURATIONS
        write_coreutils_msg(f"Define NE time-dependent configurations")
        # do replacements if needed at time=0 s
        if NEargs["replacesa"] is not None:
            self.replaceSA(CI, NEargs["replacesa"], 0, isfren=NEfren)
        if NEargs["replace"] is not None:
            self.replace(CI, NEargs["replace"], 0, isfren=NEfren)

        # build time-dependent core configuration
        # TODO specify in docs that perturbation at same t should be in the order
        # consistent with the following one (translate, critical, perturb, replace, replaceSA)
        if config is not None:
            for time in config.keys():
                if "." in time:
                    n_digits = len(time.split(".")[1])
                    if n_digits > n_digits_max:
                        raise NEError(f"Time {time} [s] has > {n_digits_max} digits after the decimal point! ")

                if float(time) != 0:
                    t = float(time)
                    # increment time list
                    self.time.append(t)
                else:
                    # set initial condition
                    t = 0.
                # check operation
                if config[time] == {}:  # enforce constant properties
                    nt = self.time.index(float(time))
                    now = self.time[nt-1]
                    self.config[float(time)] = self.config[now]

                if "translate" in config[time]:
                    self.translate(CI, config[time]["translate"], time,
                                   isfren=NEfren)

                if "replace" in config[time]:
                    self.replace(CI, config[time]["replace"], time,
                                 isfren=NEfren)

                if "replaceSA" in config[time]:
                    self.replaceSA(CI, config[time]["replaceSA"], time,
                                   isfren=NEfren)

                if "critical" in config[time]:
                    self.critical(CI, config[time]["critical"], time)

                if "perturb" in config[time]:
                    self.perturb(CI, config[time]["perturb"], time,
                                 isfren=NEfren)
        # --- CLEAN DATASET 
        # remove unused regions
        if MMGCdata is not None:
            # remove Material objects if not needed anymore
            for iPar in self.MGClibrary.data.keys():
                tmp = self.MGClibrary.data[iPar]
                universes = list(tmp.keys())
                for u in universes:
                    if u not in self.regions.values():
                        tmp.pop(u)

        # ------ PERFORM COLLAPSING, IF ANY
        if MMGCdata is not None:
            if 'collapse' in MMGCdata:
                write_coreutils_msg(f"Carry out multi-group collapsing")
                # check path to data
                if 'path' in MMGCdata['collapse']:
                    collpath = Path(MMGCdata['collapse']['path'])
                else:
                    collpath = None
                    spectrum = None # use default flux in data

                # get few groups and grid name
                if 'energy_grid_name' in MMGCdata['collapse'].keys():
                    ename = MMGCdata['collapse']['energy_grid_name']
                else:
                    ename = None

                if 'energy_grid' in MMGCdata['collapse'].keys():
                    fewgrp = MMGCdata['collapse']['energy_grid']
                else:
                    fewgrp = ename

                if ename is None and fewgrp is None:
                    raise NEError("'collapse' dict needs 'energy_grid' or 'energy_grid_name' keys!")

                if isinstance(fewgrp, (list, np.ndarray, tuple)):
                    n_groups = len(fewgrp)-1
                    energy_grid_name = f'{self.MGClibrary.n_groups}G' if ename is None else ename
                    fewgrp = fewgrp
                elif isinstance(fewgrp, (str, float, int)):
                    pwd = Path(__file__).parent.parent.parent
                    if 'COREutils'.lower() not in str(pwd).lower():
                        raise OSError(f'Check coreutils tree for NEdata: {pwd}')
                    else:
                        pwd = pwd.joinpath('NEdata')
                        if isinstance(fewgrp, str):
                            fgname = f'{fewgrp}.txt'
                            energy_grid_name = str(fewgrp)
                        else:
                            fgname = f'{fewgrp}G.txt'
                            energy_grid_name = str(fewgrp)

                        egridpath = pwd.joinpath('group_structures', fgname)
                        fewgrp = np.loadtxt(egridpath)
                        n_groups = len(fewgrp)-1
                else:
                    raise OSError(f'Unknown fewgrp grid for collapsing {type(fewgrp)}')

                if fewgrp[0] < fewgrp[0]:
                    fewgrp[np.argsort(-fewgrp)]

                # check existence of multiple collapsing spectra
                if 'config' in MMGCdata['collapse'].keys():
                    xs_config = MMGCdata['collapse']['config']
                    # sanity check on xs collapsing times
                    for k in xs_config.keys():
                        if k not in config.keys():
                            raise OSError(f"t={k} [s] for collapsing not included in NE config. times!")
                    # sanity check on config times
                    for k in config.keys():
                        if k not in xs_config.keys():
                            raise OSError(f"t={k} [s] for collapsing not included in collapsing config. times!")
                    # transient = True 
                    nConf = len(xs_config.keys())
                else:
                    if config is None:
                        xs_config = {"0.0": None}
                    else:
                        xs_config = dict(zip(config.keys(), [collpath]*len(config.keys())))
                    # transient = False

                new_config = {}
                data = {}
                labels = {}
                regions = MyDict()
                assemblytypes = MyDict()
                assemblylabel = MyDict()
                if CI.dim != 2:
                    AxialConfig_config = MyDict()
                    AxialConfig_config_str = MyDict() # orderedict
                    AxialConfig_cuts = MyDict()
                    AxialConfig_cutslabels = MyDict()
                    AxialConfig_cutsregions = MyDict()
                    AxialConfig_cutsweights = MyDict()
                    AxialConfig_labels = MyDict()
                    AxialConfig_regions = MyDict()

                nT = 1 # configuration counter
                nReg = 0
                for t in xs_config.keys():
                    conf = xs_config[t]
                    # add new regions
                    tf = float(t)
                    new_config[tf] = self.config[tf]+0
                    # get SAs @ t=tf and corresponding universes
                    sa_types = np.unique(self.config[tf])
                    sa_types = sa_types[sa_types != 0]
                    univ_at_t = []
                    # update SA-related objects
                    for sa in sa_types:
                        sa_name = cp(self.assemblytypes[sa])
                        if CI.dim != 2:
                            univ = self.AxialConfig.config_str[sa_name]
                            univ_str_newT = [f"({u})-T{nT}" for u in univ]
                            sa_name_new = f"({sa_name})-T{nT}"
                            AxialConfig_config_str[sa_name_new] = univ_str_newT
                            n_SA = len(AxialConfig_config_str.keys())
                            # FIXME nR
                            if n_SA == 1:
                                nU = 0
                                nR = len(AxialConfig_config_str[sa_name_new]) # len()  # 1
                            else:
                                nU = AxialConfig_config[n_SA-1][-1]
                                nR = len(AxialConfig_config_str[sa_name_new])
                            AxialConfig_config[n_SA] = [-1]*nR
                            # copy starting objects (only strings change, coordinates are fixed)
                            AxialConfig_cuts[sa_name_new] = cp(self.AxialConfig.cuts[sa_name])
                            AxialConfig_cutsregions[sa_name_new] = cp(self.AxialConfig.cutsregions[sa_name])
                            AxialConfig_cutslabels[sa_name_new] = cp(self.AxialConfig.cutslabels[sa_name])
                            AxialConfig_cutsweights[sa_name_new] = cp(self.AxialConfig.cutsweights[sa_name])
                            # update names of the axial regions (assuming that different spectra are used at different times)
                            for i, name in enumerate(AxialConfig_cuts[sa_name_new].reg):
                                AxialConfig_cuts[sa_name_new].reg[i] = f"({name})-T{nT}"

                            for i, name in enumerate(AxialConfig_cuts[sa_name_new].labels):
                                AxialConfig_cuts[sa_name_new].labels[i] = f"({name})-T{nT}"

                            for M in AxialConfig_cutsregions[sa_name_new].keys():
                                for iCell in range(len(AxialConfig_cutsregions[sa_name_new][M])):
                                    if AxialConfig_cutsregions[sa_name_new][M][iCell] != 0:
                                        AxialConfig_cutsregions[sa_name_new][M][iCell] = f"({AxialConfig_cutsregions[sa_name_new][M][iCell]})-T{nT}"
                                        AxialConfig_cutslabels[sa_name_new][M][iCell] = f"({AxialConfig_cutslabels[sa_name_new][M][iCell]})-T{nT}"

                            for n in range(1, nR+1):
                                if univ_str_newT[n-1] not in regions.values():
                                    nReg += 1
                                    AxialConfig_config[n_SA][n-1] = nReg
                                    # univ_int_newT = np.arange(nU+1, nU+len(univ_str_newT)+1).tolist()
                                    regions[nReg] = univ_str_newT[n-1]
                                    lbl_key = univ_str_newT[n-1].split(f"-T{nT}")[0][1:-1]
                                    labels[univ_str_newT[n-1]] = self.labels[lbl_key]
                                else:
                                    AxialConfig_config[n_SA][n-1] = list(regions.values()).index(univ_str_newT[n-1])+1

                                AxialConfig_regions[n+nU+1] = univ_str_newT[n-1]

                            assemblytypes[n_SA] = sa_name_new
                            which = list(self.assemblytypes.values()).index(sa_name)
                            assemblylabel[n_SA] = self.assemblylabel[which+1]
                            AxialConfig_labels[sa_name_new] = self.AxialConfig.cuts[sa_name].labels
                            univ_at_t.extend(univ)

                            # update config
                            lst = CI.getassemblylist(sa, self.config[tf])
                            lst = [i-1 for i in lst]
                            lst = (list(set(lst)))
                            rows, cols = np.unravel_index(lst, CI.Map.type.shape)
                            new_config[tf][rows, cols] = n_SA
                        else:
                            sa_name_new = f"({sa_name})-T{nT}"
                            nR = len(assemblytypes.keys())
                            regions[nR+1] = sa_name_new
                            assemblytypes[nR+1] = sa_name_new
                            which = list(self.assemblytypes.values()).index(sa_name)
                            assemblylabel[nR+1] = cp(self.assemblylabel[which+1])
                            labels[sa_name_new] = cp(self.labels[sa_name])
                            univ_at_t.append(sa_name)
                            # update config
                            lst = CI.getassemblylist(sa, self.config[tf])
                            lst = [i-1 for i in lst]
                            lst = (list(set(lst)))
                            rows, cols = np.unravel_index(lst, CI.Map.type.shape)
                            new_config[tf][rows, cols] = nR+1

                    for iPar in self.MGClibrary.data.keys():
                        if iPar not in data.keys():
                            data[iPar] = {}
                        for u in self.MGClibrary.data[iPar].keys():
                            if u in univ_at_t:
                                new_u = f"({u})-T{nT}"
                                data[iPar][new_u] = cp(self.MGClibrary.data[iPar][u])

                                if collpath is not None:
                                    # FIXME FIXME
                                    fname = str(collpath.joinpath(conf, f"par{iPar:g}", self.energy_grid_name, f"{u}.txt"))
                                    if not Path(fname).exists():
                                        fname = str(collpath.joinpath(conf, f"par{iPar:g}", self.energy_grid_name, f"{u}.txt"))
                                    spectrum = np.loadtxt(fname)

                                    if spectrum.shape[0] != self.MGClibrary.n_groups:
                                        raise NEError(f"Cannot collapse to {len(fewgrp)} with {spectrum.shape[0]} groups!",
                                                    f"Check {fname} file!")
                                # FIXME
                                self.P1consistent = False
                                # TODO add photon collapsing
                                data[iPar][new_u].collapse(fewgrp, self.MGClibrary.energy_grid, spectrum=spectrum, fixdata=self.MGClibrary.fixdata)

                    nT += 1

                # update energy grid
                self.MGClibrary.fine_energy_grid = self.MGClibrary.energy_grid + 0
                self.MGClibrary._energy_grid = fewgrp
                self.MGClibrary._n_groups = len(fewgrp) - 1
                self.MGClibrary.energy_grid_name = energy_grid_name if energy_grid_name else f'{G}G'
                # update regions
                self.config = new_config
                self.regions = regions
                if CI.dim != 2:
                    self.AxialConfig.config = AxialConfig_config
                    self.AxialConfig.config_str = AxialConfig_config_str
                    self.AxialConfig.cuts = AxialConfig_cuts
                    self.AxialConfig.cutslabels = AxialConfig_cutslabels
                    self.AxialConfig.cutsweights = AxialConfig_cutsweights
                    self.AxialConfig.cutsregions = AxialConfig_cutsregions

                self.assemblytypes = assemblytypes
                self.assemblylabel = assemblylabel
                self.labels = labels
                self.MGClibrary.data = data
                # update attributes in self
                self.n_groups = len(fewgrp)-1
                self.energy_grid = fewgrp
                self.energy_grid_name = energy_grid_name

        if NEargs["regionslabel"] is None:
            if CI.dim != 2:
                self.regionslabel = {}
                for a in self.AxialConfig.cuts.keys():
                    for c in self.AxialConfig.cuts[a].labels:
                        self.regionslabel[c] = c
            else:
                lst = list(self.assemblylabel.keys())
                self.regionslabel = dict(zip(lst, lst))
        else:
            self.regionslabel = NEargs["regionslabel"]

        if CI.dim != 2:
            if self.plot["AXcolors"] is None:
                self.plot["AXcolors"] = {} # dict(zip(self.AxialConfig.regions.values(), mycols1))
                idx_col = 0
                # assign colors to each assembly axial configuration
                for NEty, ty_dict in self.AxialConfig.cutsregions.items():
                    self.AxialConfig.cutscolors[NEty] = {}
                    for n, reg_lst in ty_dict.items():
                        self.AxialConfig.cutscolors[NEty][n] = [0]*len(reg_lst)
                        for i, regcol in enumerate(reg_lst):
                            if regcol != 0:
                                if regcol not in self.plot["AXcolors"].keys():
                                    self.plot["AXcolors"][regcol] = mycols1[idx_col]
                                    idx_col += 1

                                self.AxialConfig.cutscolors[NEty][n][i] = self.plot["AXcolors"][regcol]

        # # FIXME TODO temporary patch
        # for v in self.labels.values():
        #     if v not in NEargs["regionslabel"]:
        #         NEargs["regionslabel"][v] = v

        self.worksheet = NEargs["worksheet"]

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
            Flag for FRENETIC numeration, by default ``False``.

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
                raise OSError(f"SA {NEtype} not defined in NE config! Replacement cannot be performed!")
            lst = repl[NEtype]
            if not isinstance(lst, (list, str)):
                raise OSError("replaceSA must be a dict with SA name as key and"
                                "a list with assembly numbers (int) to be replaced"
                                "as value or the SA name to be replaced!")
            # ensure current config. is taken when multiple replacement occurs at the same time
            if time in self.config.keys():
                current_config = self.config[time]
            else:
                current_config = self.config[now]

            if isinstance(lst, str):
                lst = core.getassemblylist(asstypes[lst], current_config, isfren=isfren)

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
                newcore = current_config+0
                # --- load new assembly type
                newcore[rows, cols] = asstypes[NEtype]

            self.config[float(time)] = newcore

    def replace(self, core, rpl, time, isfren=False, action='repl'):
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
            Flag for FRENETIC numeration, by default ``False``.

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
                            # incuts = True
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
                    if action != "crit":
                        newtype = f"{basetype}-{iR}{action}"
                        oldtype = atype
                    else:
                        if '-crit' not in basetype:
                            newtype = f"{basetype}-{action}"
                            oldtype = atype
                        else:
                            newtype = atype
                            oldtype = atype
                else:
                    if action != "crit":
                        newtype = f"{atype}-{iR}{action}"
                    else:
                        if '-crit' not in atype:
                            newtype = f"{atype}-{action}"
                        else:
                            newtype = atype

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
                        # if action != 'crit':
                        idx = self.AxialConfig.cuts[atype].reg.index(newreg_str)
                        # else:
                        #     non_crit_reg = newreg_str.split('-crit')[0]
                        #     idx = self.AxialConfig.cuts[atype].reg.index(non_crit_reg)
                        newlab_str = self.AxialConfig.cuts[atype].labels[idx]
                else:
                    raise OSError("'with' key in replacemente must be list or string!")

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
                        # add possible new axial planes
                        if rplZ[0] not in loz:
                            loz.append(rplZ[0])
                            loz.sort()
                            upz.insert(loz.index(rplZ[0])-1, rplZ[0])
                            reg.insert(loz.index(rplZ[0]), reg[loz.index(rplZ[0])])
                            lab.insert(loz.index(rplZ[0]), lab[loz.index(rplZ[0])])
                        if rplZ[1] not in upz:
                            upz.append(rplZ[1])
                            upz.sort()
                            loz.insert(upz.index(rplZ[1])+1, rplZ[1])
                            reg.insert(upz.index(rplZ[1]), reg[upz.index(rplZ[1])])
                            lab.insert(upz.index(rplZ[1]), lab[upz.index(rplZ[1])])

                        # select axial bin location
                        for iz, zc in enumerate(list(zip(loz, upz))):
                            if tuple(rplZ) == zc:
                                break

                        if action != 'crit':
                            reg.insert(iz, newreg_str)
                            lab.insert(iz, newlab_str)
                        else: # critical region must replace old region
                            reg[iz] = newreg_str
                            lab[iz] = newlab_str

                        self.AxialConfig.cuts[newtype] = AxialCuts(upz, loz, reg, lab)
                        cuts = list(zip(cuts.reg, cuts.labels, cuts.loz, cuts.upz))
                        zr, zl, zw, zc = self.AxialConfig.mapFine2Coarse(cuts, self.AxialConfig.zcuts, self.plot['AXcolors'])
                        # --- update info for homogenisation
                        self.AxialConfig.cutsregions[newtype] = zr
                        self.AxialConfig.cutslabels[newtype] = zl
                        self.AxialConfig.cutsweights[newtype] = zw
                        self.AxialConfig.cutscolors[newtype] = zc
                        # TODO add new data if replaced region is missing
                        # if withreg not in self.data[core.TfTc[0]].keys():
                        #     self.get_material_data([withreg], core, fixdata=fixdata)

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
                    zr, zl, zw, zc = self.AxialConfig.mapFine2Coarse(cuts, self.AxialConfig.zcuts, self.plot['AXcolors'])
                    # --- update info for homogenisation
                    self.AxialConfig.cutsregions[newtype] = zr
                    self.AxialConfig.cutslabels[newtype] = zl
                    self.AxialConfig.cutsweights[newtype] = zw
                    self.AxialConfig.cutscolors[newtype] = zc

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
                            newmixname = f'{atype}:n.{iMix}: {r}'
                            if newmixname not in self.regions.values():
                                newmix.append(f'{newtype}:n.{iMix}: {r}')
                                self.regions[self.nReg+1] = f'{newtype}:n.{iMix}: {r}'
                                self.labels[f'{newtype}:n.{iMix}: {r}'] = f'{lbls[jReg]}'
                                newaxregions_str[jReg] = f'{newtype}:n.{iMix}: {r}'
                                newaxregions[jReg] = self.nReg
                        else:
                            if r not in self.regions.values():
                                self.regions[self.nReg+1] = r
                                self.labels[r] = f'{lbls[jReg]}'
                    # --- homogenise
                    if self.AxialConfig.homogenised:
                        for temp in core.NE.MGClibrary.values.keys():
                            tmp = self.MGClibrary.data[temp]  
                            for u0 in newmix:
                                # identify SA type and subregions
                                strsplt = re.split(r"\d_", u0, maxsplit=1)
                                NEty = strsplt[0]
                                names = re.split(r"\+", strsplt[1])
                                # identify axial planes
                                idx_coarse = self.AxialConfig.config_str[NEty].index(u0)
                                z_coarse_lo = self.AxialConfig.zcuts[idx_coarse]
                                z_coarse_up = self.AxialConfig.zcuts[idx_coarse + 1]
                                # compute volumes
                                V_heter = np.zeros((len(names), ))
                                V_homog = np.zeros((len(names), ))
                                for iM, mixname in enumerate(names):
                                    # fine region
                                    idx_fine = self.AxialConfig.cuts[NEty].reg.index(mixname)
                                    z_lo = self.AxialConfig.cuts[NEty].loz[idx_fine]
                                    z_up = self.AxialConfig.cuts[NEty].upz[idx_fine]
                                    V_heter[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_lo)
                                    if z_lo >= z_coarse_lo and z_up <= z_coarse_up:
                                        V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_lo)
                                    elif z_lo >= z_coarse_lo and z_up > z_coarse_up:
                                        V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_coarse_up-z_lo)
                                    elif z_lo <= z_coarse_lo and z_up <= z_coarse_up:
                                        V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_coarse_lo)
                                    else:
                                        raise NEError(f"Error in homogenisation!")

                                # perform homogenisation
                                mat4hom = {}
                                for name in names:
                                    mat4hom[name] = self.MGClibrary.data[temp][name]
                                vol4hom = {"homog": dict(zip(names, V_homog)), 
                                        "heter": dict(zip(names, V_heter))}
                                tmp[u0] = Homogenise(mat4hom, vol4hom, u0, self.fixdata, self.energy_grid, add_missing_MGC=self.add_missing_MGC)

                # --- update info in object
                if newtype not in self.assemblytypes.values():
                    nType = len(self.assemblytypes.keys()) + 1
                    self.assemblytypes.update({nType: newtype})
                    self.assemblylabel.update({nType: newtype})
                    self.AxialConfig.config.update({nType: newaxregions})
                else:
                    nType = list(self.assemblytypes.values()).index(newtype) + 1
                    self.AxialConfig.config.update({nType: newaxregions})

                # TEST FIXME TODO temporary patch
                    # self.AxialConfig.config.update({nTypes + 1: newaxregions})
                    # self.AxialConfig.config_str.update({newtype: newaxregions_str})        
                    # # --- replace assembly
                    # if not isinstance(assbly, list):
                    #     assbly = [assbly]
                    # self.replaceSA(core, {newtype: assbly}, time, isfren=isfren)

                # TEST FIXME TODO temporary patch for imposing criticality 
                self.AxialConfig.config_str.update({newtype: newaxregions_str})        
                # --- replace assembly
                if not isinstance(assbly, list):
                    assbly = [assbly]
                self.replaceSA(core, {newtype: assbly}, time, isfren=isfren)



    def critical(self, core, prt, time):
        """
        Enforce criticality, given the static keff of the system

        Parameters
        ----------
        core : _type_
            _description_
        """
        if float(time) in self.config.keys():
            now = float(time)
        else:
            nt = self.time.index(float(time))
            now = self.time[nt-1]
            time = self.time[nt]

        # --- dict sanity check
        if 'keff' not in prt.keys():
            raise NEError(f'Mandatory key `keff` missing in ''critical'' card for t={time} s')
        else:
            keff = prt['keff']

        SA_fiss = self.get_fissile_types(t=now)
        # impose criticality in each FA type
        for SA in SA_fiss:
            if hasattr(self, "AxialConfig"):
                SA_reg = self.AxialConfig.config[SA]
            else: # 2D object
                SA_reg = [SA]

            # TODO FIXME this should be more systematic and robust
            fiss_reg = []
            for ireg in SA_reg:
                reg = self.regions[ireg]
                # check that reg is fissile
                for iPar in self.MGClibrary.parameters.values.keys():
                    perturb_list = []
                    if reg in self.MGClibrary.data[iPar].keys():
                        if self.MGClibrary.data[iPar][reg].isfiss():
                            if reg not in fiss_reg:
                                fiss_reg.append(reg)
                    break # just to perform the check

            perturb_list = []
            lst_app = perturb_list.append
            for reg in fiss_reg:
                lst_app({"region": reg, "howmuch": [1/keff-1],
                        "what": "nu_fiss", "which": "all"})

        self.perturb(core, perturb_list, time=time, action="crit")

    def perturb(self, core, prt, time=0, fixdata=True, isfren=True,
                action='pert'):
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
        
        if core.dim != 2:
            zcoord = self.zcoord
        else:
            zcoord = None
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
                prtdict['which'] = []
                # determine integer type of SAs according to "region" and "where" keys
                if core.dim != 2:
                    for iSA, SA_str in enumerate(self.AxialConfig.config_str.keys()):
                        if prtdict['region'] in self.AxialConfig.config_str[SA_str]:
                            prtdict['which'] += core.getassemblylist(iSA + 1, config=self.config[now], isfren=isfren)
                else:
                    for iSA, SA_str in enumerate(self.assemblytypes.values()):
                        if SA_str == prtdict['region']:
                            prtdict['which'] += core.getassemblylist(iSA + 1, config=self.config[now], isfren=isfren)

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
                if len(howmuch) != self.MGClibrary.n_groups:
                    if len(howmuch) == 1:
                        howmuch = howmuch * self.MGClibrary.n_groups
                    else:
                        raise OSError('The perturbation intensities' 
                                      f' required should be list of 1 or {self.MGClibrary.n_groups} elements')

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
                        # for r in self.regions.values():
                        #     if "+" in r:
                        #         if oldreg in r:
                        #             raise OSError('Cannot perturb region which is both alone and'
                        #                           ' in mix! Use separate perturbation cards!')                     
                        if izpos == []:  # look in xscuts
                            for i, r in enumerate(self.AxialConfig.cuts[atype].reg):
                                if r == oldreg:
                                    izpos.append(i)
                        # get coordinates
                        zpert = []
                        for i in izpos:
                            zpert.append(list(self.zcoord[i]))
                # define perturbed region name
                if action != "crit":
                    prtreg = f"{oldreg}-{iP}{action}"
                else:
                    prtreg = f"{oldreg}-{action}"

                # --- perturb data and assign it
                for iPar in self.MGClibrary.data.keys():
                    self.MGClibrary.data[iPar][prtreg] = cp(self.MGClibrary.data[iPar][oldreg])
                    self.MGClibrary.data[iPar][prtreg].perturb(perturbation, howmuch, depgro, fixdata=fixdata)

                # --- add new assemblies
                if action != "crit":
                    self.regions[self.nReg + 1] = prtreg
                else:
                    if prtreg not in self.regions.values():
                        self.regions[self.nReg + 1] = prtreg

                # --- add new label
                if action != "crit":
                    self.labels[prtreg] = f"{self.labels[oldreg]}-{iP}{action}"
                else:
                    self.labels[prtreg] = f"{self.labels[oldreg]}-{action}"

                # --- define replacement dict to introduce perturbation
                if core.dim == 2:
                    # --- update info in object
                    if prtreg not in self.assemblytypes.keys():
                        nTypes = len(self.assemblytypes.keys())
                        self.assemblytypes.update({nTypes + 1: prtreg})
                        self.assemblylabel.update({nTypes + 1: prtreg})
                    repl = {prtreg: assbly}
                    self.replaceSA(core, repl, time, isfren=isfren)
                else:
                    repl = {"which": [assbly], "with": [prtreg], "where": [zpert]}
                    self.replace(core, repl, time, isfren=isfren, action=action)

    def translate(self, core, transconfig, time, isfren=False, action='trans'):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        transconfig : dict
            Dictionary with details on translation transformation
        isfren : bool, optional
            Flag for FRENETIC numeration, by default ``False``.

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
        
        # account for repetitions for updating replacement counter
        repetitions = []
        for v in list(self.regions.values()):
            if action in v:
                repetitions.append(v.split(action)[0])

        repetitions = list(set(repetitions))
        iT = len(repetitions)

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
                        oldtype = atype

                    # --- define new cuts
                    if newtype not in self.AxialConfig.cuts.keys():
                        # --- operate translation
                        cuts = cp(self.AxialConfig.cuts[atype])
                        cuts.upz[0:-1] = [z+dz for z in cuts.upz[0:-1]]
                        cuts.loz[1:] = [z+dz for z in cuts.loz[1:]]
                        self.AxialConfig.cuts[newtype] = AxialCuts(cuts.upz, cuts.loz, cuts.reg, cuts.labels)
                        cuts = list(zip(cuts.reg, cuts.labels, cuts.loz, cuts.upz))
                        zr, zl, zw, zc = self.AxialConfig.mapFine2Coarse(cuts, self.AxialConfig.zcuts, self.plot['AXcolors'])
                        # --- update info for homogenisation
                        self.AxialConfig.cutsregions[newtype] = zr
                        self.AxialConfig.cutslabels[newtype] = zl
                        self.AxialConfig.cutsweights[newtype] = zw
                        self.AxialConfig.cutscolors[newtype] = zc

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
                                newmixname = f'{newtype}:n.{iMix}: {r}'
                                if newmixname not in self.regions.values():
                                    newmix.append(f'{newtype}:n.{iMix}: {r}')
                                    self.regions[self.nReg+1] = f'{newtype}:n.{iMix}: {r}'
                                    self.labels[f'{newtype}:n.{iMix}: {r}'] = f'{lbls[jReg]}'
                                    newaxregions_str[jReg] = f'{newtype}:n.{iMix}: {r}'
                                    newaxregions[jReg] = self.nReg
                                else:
                                    str2int = self.regions.reverse()
                                    newaxregions[jReg] = str2int[f'{newtype}: {r}']
                                    newaxregions_str[jReg] = f"{newtype}: {r}"  # or oldtype?
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

                        # --- update info in object
                        self.assemblytypes.update({nTypes+1: newtype})
                        self.assemblylabel.update({nTypes+1: newtype})
                        self.AxialConfig.config.update({nTypes+1: newaxregions})
                        self.AxialConfig.config_str.update({newtype: newaxregions_str})

                        # --- homogenise
                        for iPar in self.MGClibrary.data.keys():
                            tmp = self.MGClibrary.data[iPar]  
                            for u0 in newmix:
                                # identify SA type and subregions
                                strsplt = re.split(r"\d: ", u0, maxsplit=1)
                                NEty = strsplt[0].split(":n.")[0]
                                names = re.split(r"\+", strsplt[1])
                                # identify axial planes for homogenisation
                                idx_coarse = self.AxialConfig.config_str[NEty].index(u0)
                                z_coarse_lo = self.AxialConfig.zcuts[idx_coarse]
                                z_coarse_up = self.AxialConfig.zcuts[idx_coarse + 1]
                                # compute volumes
                                V_heter = np.zeros((len(names), ))
                                V_homog = np.zeros((len(names), ))
                                for iM, mixname in enumerate(names):
                                    # fine region
                                    idx_fine = self.AxialConfig.cuts[NEty].reg.index(mixname)
                                    z_lo = self.AxialConfig.cuts[NEty].loz[idx_fine]
                                    z_up = self.AxialConfig.cuts[NEty].upz[idx_fine]
                                    V_heter[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_lo)
                                    if z_lo >= z_coarse_lo and z_up <= z_coarse_up:
                                        V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_lo)
                                    elif z_lo >= z_coarse_lo and z_up > z_coarse_up:
                                        V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_coarse_up-z_lo)
                                    elif z_lo <= z_coarse_lo and z_up <= z_coarse_up:
                                        V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_coarse_lo)
                                    else:
                                        raise NEError(f"Error in homogenisation!")

                                # perform homogenisation
                                mat4hom = {}
                                for name in names:
                                    mat4hom[name] = self.MGClibrary.data[iPar][name]
                                vol4hom = {"homog": dict(zip(names, V_homog)), 
                                        "heter": dict(zip(names, V_heter))}
                                tmp[u0] = Homogenise(mat4hom, vol4hom, u0, self.MGClibrary.fixdata, self.MGClibrary.energy_grid, add_missing_MGC=self.MGClibrary.add_missing_MGC)

                    # # --- update info in object
                    # if newtype not in self.assemblytypes.keys():
                    #     self.assemblytypes.update({nTypes+1: newtype})
                    #     self.assemblylabel.update({nTypes+1: newtype})
                    #     self.AxialConfig.config.update({nTypes+1: newaxregions})
                    #     self.AxialConfig.config_str.update({newtype: newaxregions_str})
                    # --- replace assembly
                    if not isinstance(assbly, list):
                        assbly = [assbly]
                    dim = 3
                    self.replaceSA(core, {newtype: assbly}, time, isfren=isfren)

    def get_fissile_types(self, t=0):
        """Return fissile assembly types.

        Returns
        -------
        fissile_types : list
            Return fissile assembly types.
        """
        fissile_types = []
        param = list(self.MGClibrary.parameters.values.keys())[0]
        for iType, aType in self.assemblytypes.items():
            # TODO check in numpy array
            if iType in self.config[t]:
                if hasattr(self, "AxialConfig"):
                    regs = set(self.AxialConfig.config_str[aType])
                else: # 2D object
                    regs = [aType]

                for r in regs:
                    if self.MGClibrary.data[param][r].isfiss():
                        fissile_types.append(iType)
                        break

        return fissile_types

    def get_fissile_SA(self, core, t=0):
        """Return number of fissile types in a core configuration at time t.

        Parameters
        ----------
        core : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        fissile_types = self.get_fissile_types(t=t)
        fissile_SA = []
        for iType in fissile_types:
            fissile_SA.extend(core.getassemblylist(iType, self.config[t]))
        return fissile_SA

    @property
    def nReg(self):
        return len(self.regions.keys())

    @staticmethod
    def multigroup_onto_fewgroup(multig, fewg):

        if isinstance(fewg, list):
            fewg = np.asarray(fewg)

        if isinstance(fewg, list):
            fewg = np.asarray(fewg)

        # ensure descending order
        fewg = fewg[np.argsort(-fewg)]
        H = len(multig)-1
        G = len(fewg)-1
        # sanity checks
        if G >= H:
            raise NEError(f'Collapsing failed: few-group structure should',
                          ' have less than {H} group')
        if multig[0] != fewg[0] or multig[-1] != fewg[-1]:
            raise NEError('Collapsing failed: few-group structure'
                          'boundaries do not match with multi-group'
                          'one')
        # map fewgroup onto multigroup
        few_into_multigrp = np.zeros((G+1,), dtype=int)
        for ig, g in enumerate(fewg):
            reldiff = abs(multig-g)/g
            idx = np.argmin(reldiff)
            if (reldiff[idx] > 1E-5):
                raise NEError(f'Group boundary n.{ig}, {g} MeV not present in fine grid!')
            else:
                few_into_multigrp[ig] = idx

        return few_into_multigrp

class MGClibrary():

    def __init__(self, MMGCdata, NE_regions, core, NE_geom):

        if "add_missing_MGC" in MMGCdata.keys():
            self.add_missing_MGC = MMGCdata["add_missing_MGC"]
        else:
            self.add_missing_MGC = 1

        if "fixdata" in MMGCdata.keys():
            self.fixdata = MMGCdata["fixdata"]
        else:
            self.fixdata = 1

        if "nxn" in MMGCdata.keys():
            self.use_nxn = MMGCdata["nxn"]
        else:
            self.use_nxn = False

        if "n_precursors" in MMGCdata.keys():
            self.n_prec = MMGCdata["n_precursors"]
        else:
            self.n_prec = 1

        isPH = True if 'PH' in MMGCdata.keys() else False

        self.energy_grid = MMGCdata
        # FIXME
        self.n_groups = self.energy_grid
        if "energy_grid_name" not in MMGCdata.keys():
            self.energy_grid_name = f'{self.MGClibrary.n_groups}G' 
        else:
            self.energy_grid_name = MMGCdata["energy_grid_name"]

        if isPH:
            self.get_PH_energy_grid(MMGCdata["PH"])

        write_coreutils_msg(f"Read and assign multi-group constants to NE object")
        self.get_material_data(MMGCdata, core, NE_geom, NE_regions)

    def get_MGC_path(self, lib_path):

        pattern = r"<par([0-9][0-9]*)>"
        path_dict_param = {}
        path_dict_no_param = {}

        for reader in lib_path.keys():
            for path in lib_path[reader]:

                param_match = re.search(pattern, path)
                if param_match:
                    number = param_match.group(1)
                    path = re.sub(r"<par([0-9][0-9]*)>", r"par\1", path)
                    N = int(number)
                    if N not in path_dict_param.keys():
                        path_dict_param[N] = {}

                if Path(path).exists():
                    file_list = os.listdir(path)
                else:
                    raise NEError(f"Path to group constant {path} in 'NEdata' does not exist.")

                if param_match:
                    path_dict_param[N][reader] = []
                else:
                    path_dict_no_param[reader] = []

                if len(file_list) >= 1:
                    for file in file_list:
                        if file.endswith(reader_ext[reader]):
                            if param_match:
                                path_dict_param[N][reader].append(Path(path).joinpath(file))
                            else:
                                path_dict_no_param[reader].append(Path(path).joinpath(file))
                else:
                    raise NEError(f"Path to group constant {path} in 'NEdata' is empty.")

        return path_dict_param, path_dict_no_param

    def get_material_data(self, NEdata, core, NE_geom, NE_regions):

        if "parameters" in NEdata.keys():
            par = NEdata["parameters"]
            self.parameters = Parameters(par["names"], par["units"], par["values"])
        else:
            self.MGC_parameters = None

        if "library_path" in NEdata.keys():
            gc_path_param, gc_path_all_param = self.get_MGC_path(NEdata["library_path"])
        else:
            raise NEError("Mandatory dictionary 'library_path' is missing from 'NEdata': cannot read group constants.")

        # sanity check on library_path
        if len(self.parameters.values.keys()) != len(gc_path_param.keys()):
            raise NEError("Mismatch between number of parameters and number of paths in 'library_path'.")

        if "P1consistent" not in NEdata.keys():
            self.P1consistent = 0
        else:
            self.P1consistent = NEdata["P1consistent"]
        
        if "nPrec" not in NEdata.keys():
            NEdata["nPrec"] = None

        if not hasattr(self, 'data'):
            self.data = {}

        # --- parse full data library
        if 'nemtab' in gc_path_all_param.keys():
            reader = 'nemtab'
            BU = 0.0 # FIXME take into account BU if in self.parameters
            for f in gc_path_all_param[reader]:
                param_values, param_combos, gc_in_dict_all_param = MGC_reader(reader, f)
                if hasattr(self, "parameters"):
                    # --- check parameters consistency
                    for par in self.parameters.names:
                        if par not in param_values.keys():
                            raise NEError(f"Missing parameter {par} in {reader} file {f}")
                    # --- ensure same values sorting
                    par_names_nemtab = list(param_values.keys())
                    idx_sort_combos = [i for i in range(len(self.parameters.values))]
                    idx_sort_nemtab = [-1]*len(self.parameters.names)
                    idx_sort = [i for i in range(len(par_names_nemtab))]

                    for idx, par in enumerate(self.parameters.names):
                        idx_sort_nemtab[idx] = par_names_nemtab.index(par)

                    if idx_sort != idx_sort_nemtab:
                        # sort parameters in each combos
                        param_combos_sorted = []
                        for combo in param_combos:
                            param_combos_sorted.append([combo[i] for i in idx_sort_nemtab])
                        # sort combos
                        idx_sort_combos = [0]*len(param_combos_sorted)
                        for k, lst in self.parameters.values.items():
                            matched = False
                            for idx, combo in enumerate(param_combos_sorted):
                                if combo == lst:
                                    idx_sort_combos[k] = idx
                                    matched = True
                            if not matched:
                                raise OSError(f"Parameter combination {lst} not found in {reader} file {f}")

                else:
                    # --- create parameters object
                    self.parameters = Parameters(param_values.keys(), [None]*len(param_values), param_combos)
                    idx_sort_combos = [i for i in range(len(self.parameters.values))]

                for iPar in idx_sort_combos:

                    if iPar not in self.data.keys():
                        self.data[iPar] = {}

                    data_name = gc_in_dict_all_param[BU][iPar]["data_name"]
                    self.data[iPar][data_name] = NEMaterial(data_in_dict=gc_in_dict_all_param[BU][iPar], energy_grid=self.energy_grid,
                                                            fixdata=self.MGClibrary.fixdata, P1consistent=self.P1consistent, use_nxn=self.use_nxn,
                                                            add_missing_MGC=self.add_missing_MGC)

        # --- parse parameter-wise data
        for iPar in self.parameters.values:
            if iPar not in self.data.keys():
                self.data[iPar] = {}

            for reader in gc_path_param[iPar].keys():
                if reader not in multi_material_readers:
                    for f in gc_path_param[iPar][reader]:
                        gc_in_dict = MGC_reader(reader, f)
                        self.data[iPar][gc_in_dict['data_name']] = NEMaterial(data_in_dict=gc_in_dict, energy_grid=self.energy_grid,
                                                                            fixdata=self.fixdata, P1consistent=self.P1consistent, use_nxn=self.use_nxn,
                                                                            add_missing_MGC=self.add_missing_MGC)
                else:
                    for f in gc_path_param[iPar][reader]:
                        gc_in_serpdict = MGC_reader(reader, f)
                        for data_in_dict in gc_in_serpdict:
                            if self.n_groups != len(data_in_dict["energy_grid"])-1:
                                raise NEError(f"Mismatch between the number of groups of the grid {self.energy_grid_name} and the energy grid in the Serpent _res files.")
                            elif not np.allclose(data_in_dict["energy_grid"], self.energy_grid):
                                raise NEError(f"Group boundaries mismatch between {self.energy_grid_name} and the energy grid in the MGC input files.")
                            else:
                                data_in_dict.pop("energy_grid")
                                self.data[iPar][data_in_dict['data_name']] = NEMaterial(data_in_dict=data_in_dict, energy_grid=self.energy_grid,
                                                                                        fixdata=self.fixdata, P1consistent=self.P1consistent, use_nxn=self.use_nxn,
                                                                                        add_missing_MGC=self.add_missing_MGC)

        # --- check if data is present for each region in NE_regions
        for iPar in self.data.keys():
            for reg in NE_regions:
                if reg not in self.data[iPar].keys():
                    raise NEError(f"Missing region {reg} in data library for the parameter combo n. {iPar}.")

        # --- HOMOGENISATION (if any)
        if core.dim != 2:
            if NE_geom.AxialConfig.homogenised:
                for iPar in self.data.keys():
                    for u0 in NE_geom.regions.values():
                        if "+" in u0: # homogenisation is needed
                            # identify SA type and subregions
                            strsplt = re.split(r"\d: ", u0, maxsplit=1)
                            NEty = strsplt[0].split("_n.")[0]
                            names = re.split(r" \+ ", strsplt[1])
                            # identify axial planes
                            idx_coarse = NE_geom.AxialConfig.config_str[NEty].index(u0)
                            z_coarse_lo = NE_geom.AxialConfig.zcuts[idx_coarse]
                            z_coarse_up = NE_geom.AxialConfig.zcuts[idx_coarse + 1]
                            # compute volumes
                            V_heter = np.zeros((len(names), ))
                            V_homog = np.zeros((len(names), ))
                            for iM, mixname in enumerate(names):
                                # fine region
                                idx_fine = NE_geom.AxialConfig.cuts[NEty].reg.index(mixname)
                                z_lo = NE_geom.AxialConfig.cuts[NEty].loz[idx_fine]
                                z_up = NE_geom.AxialConfig.cuts[NEty].upz[idx_fine]
                                V_heter[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_lo)
                                if z_lo >= z_coarse_lo and z_up <= z_coarse_up:
                                    V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_lo)
                                elif z_lo >= z_coarse_lo and z_up > z_coarse_up:
                                    V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_coarse_up-z_lo)
                                elif z_lo <= z_coarse_lo and z_up <= z_coarse_up:
                                    V_homog[iM] = core.Geometry.AssemblyGeometry.compute_volume(z_up-z_coarse_lo)
                                else:
                                    raise NEError("Error in homogenisation!")

                            # perform homogenisation
                            mat4hom = {}
                            for name in names:
                                mat4hom[name] = self.data[iPar][name]
                            vol4hom = {"homog": dict(zip(names, V_homog)), 
                                        "heter": dict(zip(names, V_heter))}
                            self.data[iPar][u0] = Homogenise(mat4hom, vol4hom, u0, self.fixdata, self.energy_grid, add_missing_MGC=self.add_missing_MGC)

    @property
    def energy_grid(self):
        return self._energy_grid

    @energy_grid.setter
    def energy_grid(self, NEargs):

        if 'energy_grid_name' in NEargs.keys():
            ename = NEargs['energy_grid_name']
        else:
            ename = None

        if 'energy_grid' in NEargs.keys():
            energy_grid = NEargs['energy_grid']
        else:
            energy_grid = ename

        # --- load user-defined energy grid
        if isinstance(energy_grid, (list, np.ndarray, tuple)):
            self._energy_grid = np.asarray(energy_grid)
        # --- load pre-defined energy group structure
        elif isinstance(energy_grid, (str, float, int)):
            pwd = Path(__file__).parent.parent.parent
            if 'COREutils'.lower() not in str(pwd).lower():
                raise NEError(f'Check COREutils tree for NEdata: {pwd}')
            else:
                pwd = pwd.joinpath('NEdata')
                if isinstance(energy_grid, str):
                    fgname = f'{energy_grid}.txt'
                    self._energy_grid_name = str(energy_grid)
                else:
                    fgname = f'{energy_grid}G.txt'
                    self.energy_grid_name = str(energy_grid)

                egridpath = pwd.joinpath('group_structures', fgname)
                self._energy_grid = np.loadtxt(egridpath)

        else:
            raise OSError(f'Unknown energy_grid \
                            {type(energy_grid)}')
        # --- ensure sorting
        if self._energy_grid[0] < self._energy_grid[1]:
            self._energy_grid = self._energy_grid[np.argsort(-self._energy_grid)]

    @property
    def n_groups(self):
        return self._n_groups

    @n_groups.setter
    def n_groups(self, energy_grid):
        self._n_groups = len(energy_grid) - 1

    @property
    def regions(self):
        iPar = list( self.data.keys() )[0]
        regions = list( self.data[iPar].keys() )

        return regions

    def get_PH_energy_grid(self, PHargs):
        if 'energy_grid_name' in PHargs.keys():
            ename = PHargs['energy_grid_name']
        else:
            ename = None

        if 'energy_grid' in PHargs.keys():
            energy_grid = PHargs['energy_grid']
        else:
            energy_grid = ename

        if isinstance(energy_grid, (list, np.ndarray, tuple)):
            self.nGrp = len(energy_grid)-1
            self.energy_grid_namePH = f'{self.nGrp}G' if ename is None else ename
            self.energygridPH = energy_grid
        elif isinstance(energy_grid, (str, float, int)):
            pwd = Path(__file__).parent.parent.parent
            if 'COREutils'.lower() not in str(pwd).lower():
                raise OSError(f'Check coreutils tree for PHdata: {pwd}')
            else:
                pwd = pwd.joinpath('PHdata')
                if isinstance(energy_grid, str):
                    fgname = f'{energy_grid}.txt'
                    self.energy_grid_namePH = str(energy_grid)
                else:
                    fgname = f'{energy_grid}G.txt'
                    self.energy_grid_namePH = str(energy_grid)

                egridpath = pwd.joinpath('group_structures', fgname)
                self.energygridPH = np.loadtxt(egridpath)
                self.nGrp = len(self.energygridPH)-1
        else:
            raise OSError(f'Unknown energy_grid \
                            {type(energy_grid)}')

        if self.energygridPH[0] < self.energygridPH[0]:
            self.energygridPH[np.argsort(-self.energygridPH)]

    def to_nemtab(self, destination_path=None, name_map=None):
        """Export MG library to files in the NEMTAB format.

        destination_path : str or Path-like, optional
            Path to which the NEMTAB files will be saved. If not provided, files will be saved in the current working directory.
        name_map : dict, optional
            Dictionary to map region names in the NE object to region names in the NEMTAB files. 
            If not provided, region names in the NE object will be used as they are in the NEMTAB files.

        Returns
        -------
        None
        """
        commchar = '*'
        # --- prepare common header for all files
        header = [commchar]
        if self.parameters is not None:
            parnames = list(self.parameters.names)

            if len(parnames) < 6:
                parnames += ['undef'] * ( 6 - len(parnames) )

            header.append(f"{commchar} {'    '.join(parnames)}")
            header.append(("    ".join([str(v) for v in self.parameters.n_values])))
            for iCom in self.data.keys():
                vals = []
                for iVal, v in enumerate(self.parameters.values[iCom]):
                    if isinstance(v, float):
                        vals.append(f"{v:1.5E}")
                    else:
                        raise NEError(f"Parameter value {v} in {parnames[iVal]} not supported in NEMTAB output!")

                header.append("   ".join(vals))

            header.append(commchar)

        else:
            header = [
                    commchar,
                    f'{commchar}   undef          undef          undef          undef          undef          undef          ',
                    '0              0              0              0              0              0',
                    commchar]

        header.append('* -------------------')
        header.append('* BURNUP   0.00 GWd/t')
        header.append('* -------------------')

        # write group-wise data
        data_list = {
                    'Diffcoef': 'di (diffusion coefficient)',
                    'Sigma_abs': 'ab (absorption cross-section)',
                    'nuSigma_fiss': 'nf (nu*fission cross-section)',
                    'fiss_energy*Sigma_fiss': 'kf (energy release*fission cross-section)',
                    'Sigma_fiss': 'fi (fission cross-section)',
                    'Sigma_tot': 'to (total cross-section)',
                    'S0': 'P0 Scattering',
                    'Sigma_transp': 'tr (transport cross-section)',
                    'chi_tot': 'ch (total fission emission spectrum)',
                    'chi_del': 'ch (delayed fission emission spectrum)',
                    'inv_vel': 'in (1/v)',
                    'lambda': 'la (decay constant)',
                    'beta': 'be (delayed neutron fraction)'
                    }

        iCom_del = 0 # parameter combo at which chi_del is saved

        for reg in self.regions:

            if name_map is not None and reg in name_map.keys():
                regname = name_map[reg]
            else:
                regname = reg

            lines = list(header)
            for key, nemtab_key in data_list.items():
                # add header
                if key != 'chi_del':
                    lines.append("\n".join([
                                commchar,
                                f"{commchar} {nemtab_key}",
                                commchar
                                ]))

                if key in ['S0', 'S1']:

                    # add group-wise data
                    for h in range(self.n_groups):
                        for g in range(self.n_groups):
                            lines.append(f"GROUP   {h + 1} ->   {g + 1}")

                            vals = []
                            for iCom in range(self.parameters.n_combos):
                                vals.append( self.data[iCom][reg].__dict__[key][g, h] )

                            val_str = " ".join([f"{v:1.5E}" for v in vals])

                            lines.append(f"  {val_str}")

                else:
                    
                    if key in ['chi_tot', 'inv_vel', 'lambda', 'beta']:
                        # add group-wise data
                        lines.append("GROUP      " + "           ".join( [f"{g + 1}" for g in range(self.n_groups)]) )
                        iCom = list( self.data.keys() )[0]
                        if key == 'inv_vel':
                            for reg_kp in self.regions:
                                mat0 = self.data[iCom][reg_kp]
                                if mat0.isfiss():
                                    break
                            vals = [mat0.__dict__[key][g] for g in range(self.n_groups)]
                        else:
                            if key in ['lambda', 'beta']:
                                vec_size = self.n_prec
                            else:
                                vec_size = self.n_groups
                            vals = [self.data[iCom][reg].__dict__[key][i] for i in range(vec_size)]

                        val_str = " ".join([f"{v:1.5E}" for v in vals])
                        lines.append(f"  {val_str}")
                    
                    elif key == 'chi_del':
                        # print separate ASCII file
                        chi_del_reg = np.zeros((self.n_groups, self.n_prec))
                        for p in range(self.n_prec):
                            chi_del_reg[:, p] = self.data[iCom_del][reg].__dict__[key][p, :]

                        fname = f"chi_del_{regname}.txt"

                        if destination_path is not None:
                            if isinstance(destination_path, str):
                                destination_path = Path(destination_path)
                            elif not isinstance(destination_path, Path):
                                raise NEError(f"Type of argument destination_path={destination_path} not valid. Must be string or Path-like object.")

                            if destination_path.exists():
                                fname = destination_path.joinpath(fname)

                        np.savetxt(fname, chi_del_reg)

                    else:
                        # add group-wise data
                        for g in range(self.n_groups):
                            lines.append(f"GROUP   {g + 1}")
                            
                            vals = []
                            for iCom in range(self.parameters.n_combos):
                                if key == 'fiss_energy*Sigma_fiss':
                                    key1, key2 = key.split('*')
                                    vals.append( 
                                                self.data[iCom][reg].__dict__[key1][g] * 1.602E-13 * # 1.602E-13 to be consistent with GRS scripts
                                                self.data[iCom][reg].__dict__[key2][g]
                                                )
                                else:
                                    vals.append( self.data[iCom][reg].__dict__[key][g] )

                            val_str = " ".join([f"{v:1.5E}" for v in vals])
                            lines.append(f"  {val_str}")

            lines.append("\n".join([
                        commchar,
                        "END"
                        ]))

            # dump to file
            fname = f"XS_{regname}.nemtab"
            if destination_path is not None:
                if isinstance(destination_path, str):
                    destination_path = Path(destination_path)
                elif not isinstance(destination_path, Path):
                    raise NEError(f"Type of argument destination_path={destination_path} not valid. Must be string or Path-like object.")

                if destination_path.exists():
                    fname = destination_path.joinpath(fname)

            with open(fname, "w") as f:
                lines = "\n".join(lines)
                f.write(lines)


class Parameters():
    """Define "Parameters" object.
    """
    def __init__(self, names, units, values):
        self.names = names
        self.units = units
        self.values = values

    @property
    def names(self):
        return self._names

    @names.setter
    def names(self, values):
        self._names = values

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, values):
        self._units = values

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, inpdict):
        self._values = {}
        for k in inpdict.keys():
            if k.startswith("par"):
                i = int(k.split("par")[1])
            elif isinstance(k, int):
                i = k
            else:
                raise OSError(f"Unknown parameter {k} in 'parameters' dict in the json input!")

            self._values[i] = inpdict[k]

    @property
    def n_param(self):
        return len(self.names)

    @property
    def n_combos(self):
        return len(self.values.keys())

    @property
    def n_values(self):
        mat_val = np.zeros((self.n_combos, self.n_param,), dtype=int)
        for i, v in enumerate(self.values.values()):
            mat_val[i, :] = v

        n_val = []
        for i in range(self.n_param):
            n_val.append(len(set(mat_val[:, i])))

        return n_val

class NEError(Exception):
    pass