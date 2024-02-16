import os
import re
import json
import logging
import itertools
import h5py as h5
import numpy as np
import shutil as sh
import matplotlib.pyplot as plt

from pathlib import Path
from numpy.linalg import norm
from coreutils.core import Core
from matplotlib import rcParams
from copy import deepcopy as cp
from warnings import catch_warnings
from coreutils.tools.plot import RadialMap
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
rcParams['text.usetex']= True if sh.which('latex') else False

pwd = Path(__file__).parent
inp_json_map = pwd.joinpath("NEversion.json")

class NEoutput:
    """
    Class to read NE profiles computed by FRENETIC.
    """
    def __init__(self, path):
        """
        Initialise the class.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        self.casepath = path
        self.NEpath = os.path.join(path, 'NE')
        # looking for core.h5 file with core object
        self.core = Core(os.path.join(path, 'core.h5'))
        self.ngro = self.core.NE.nGro
        self.ngrp = self.core.NE.nGrp
        if "nPrec" in self.core.NE.NEdata.keys():
            if self.core.NE.NEdata["nPrec"] is None:
                self.npre = self.core.NE.nPre
            else:
                self.npre = self.core.NE.NEdata["nPrec"]
            self.nprp = self.core.NE.nPrp
        else:
            self.npre = self.core.NE.nPre
            self.nprp = self.core.NE.nPrp

        if hasattr(self.core, "FreneticNamelist"):
            isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
        else:
            isSym = 0

        self.nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss

        if self.core.dim != 2:
            self.nelz = self.core.NE.AxialConfig.splitz.sum()
        else:
            self.nelz = 1

        # get FRENETIC version map
        try:
            with open(inp_json_map) as f:
                try:
                    MapOutput = json.load(f)
                except json.JSONDecodeError as err:
                    print(err.args[0])
                    logging.critical(err.args[0])
                    raise NEOutputError(f"{err.args[0]} in {inp}")
        except FileNotFoundError:
            raise NEOutputError(f"File {inp_json_map} not found!")

        # get FRENETIC output version
        self.version = NEoutput.get_output_version(self.NEpath, MapOutput)
        if self.version not in MapOutput["MapVersion"].keys():
            if self.version != "0.0":
                raise NEOutputError(f"output version {self.version} not supported!")
            else:
                self.MapVersion = MapOutput["MapVersion"]["1.0"]
        else:
            self.MapVersion = MapOutput["MapVersion"][self.version]

        self.MapDerived = MapOutput["DerivedData"]

        vers = float(self.version)
        if vers <= 1.0:
            NEoutput._fill_deprec_vers_metadata(self.MapVersion, self.npre, self.ngro, self.nprp, self.ngrp)
        elif vers == 2.0:
            self.MapVersion["data"]["integralParameters"] = NEoutput.fill_intpar_dict(self.MapVersion["data"]["integralParameters"],
                                                                            self.npre, self.ngro, self.nprp, self.ngrp)
            self.HDF5_path = NEoutput.build_HDF5_path(self.MapVersion["data"])
            dupl_dist = NEoutput.get_duplicate_dset_names(self.MapVersion["data"]["distributions"])
            dupl_intp = NEoutput.get_duplicate_dset_names(self.MapVersion["data"]["integralParameters"])
            self.dupl = dupl_dist + dupl_intp + ["time"]
        else:
            pass

    def get(self, what, t=None, z=None, hex=None, pre=None,
            gro=None, metadata=False):
        """
        Get profile from output.

        Parameters
        ----------
        what: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default None.
        t: float or iterable, optional
            Time instant(s), by default None.
        z: float or iterable, optional
            Axial coordinate(s), by default None.
        pre: integer or iterable, optional
            Precursor families, by default None.
        gro: integer or iterable, optional
            Neutron (or photon) energy group(s), by default None.
        particles: string, optional
            The particle species analysed. It can be either "neutrons"
            or "photons".

        Returns
        -------
        profile: array
            Output profile requested.
        """
        # select getter method according to the output version
        if self.version == "0.0":
            if metadata:
                profile, descr, uom = self.get_txt(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)
            else:
                profile = self.get_txt(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)

        elif self.version == "1.0":
            if metadata:
                profile, descr, uom, color = self.get_v1(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)
            else:
                profile = self.get_v1(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)

        elif self.version == "2.0":
            derived_path = NEoutput.build_HDF5_path(self.MapDerived["data"])

            for path in derived_path:
                if what in path:
                    is_derived = True
                    break
                else:
                    is_derived = False

            if is_derived:
                if metadata:
                    profile, descr, uom, color = self.get_derived(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)
                else:
                    profile = self.get_derived(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)

            else:
                if metadata:
                    profile, descr, uom, color = self.get_v2(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)
                else:
                    profile = self.get_v2(what, t=t, z=z, hex=hex, pre=pre, gro=gro, metadata=metadata)

        else:
            raise NEOutputError(f"v{self.version} unknown!")

        if metadata:
            return profile, descr, uom, color
        else:
            return profile

    def get_xs(self, what, reg, gro=None, temp=(673,673)):
        """
        Get profile from output.

        Parameters
        ----------
        what: string
            Name of the variable to be parsed
        gro: integer or iterable, optional
            Neutron energy group(s), by default `None`.
        temp: tuple
            Tuple with fuel and coolant temperature featuring
            the data to be parsed, by default `None`.

        Returns
        -------
        profile: array
            Output profile requested.
        """
        Tf, Tc = temp[0], temp[1]
        xs_name = self.MapDerived["data"]["input_xs"][what]
        # --- open
        h5f = NEoutput.myh5open(self.NEpath, fname="NE_data.h5")
        
        reg_dict = dict(zip(self.core.NE.regions.values(),
        self.core.NE.regions.keys()))
        
        if isinstance(reg, str):
            id_reg = reg_dict[reg]
        elif isinstance(reg, int):
            id_reg = reg
        else:
            raise NEOutputError(f"Cannot parse argument of type {type(reg)}")
        
        h5path = "/".join([f"Tf_{Tf:02d}_Tc_{Tc:02d}", "/", f"{id_reg}", "/", xs_name])
        # --- parse the file
        xs = np.asarray(h5f[h5path])

        # --- close H5 file
        h5f.close()

        return xs

    def get_txt(self, what, t=None, z=None, hex=None, pre=None,
            gro=None, metadata=False):
        """
        Get profile from txt formatted output.

        Parameters
        ----------
        what: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default None.
        t: float or iterable, optional
            Time instant(s), by default None.
        z: float or iterable, optional
            Axial coordinate(s), by default None.
        pre: integer or iterable, optional
            Precursor families, by default None.
        gro: integer or iterable, optional
            Neutron/photon energy group(s), by default None.

        Returns
        -------
        profile: array
            Output profile requested.
        """
        tot = False
        if what in self.MapVersion["alias"].keys():
            what = self.MapVersion["alias"][what]
        elif what in self.MapDerived["data"]["distributions"]:
            if what == "tot_n_precursors":
                pre = np.arange(1, self.npre+1)
                what = "precurs"
                sum_dims = ["npre", "nelz", "nhex"]
                tot = True
            elif what == "tot_p_precursors":
                pre = np.arange(1, self.nprp+1)
                what = "precursp"
                sum_dims = ["nprp", "nelz", "nhex"]
                tot = True
            elif what == "radial_power":
                what = "powertot"
                sum_dims = ["nelz"]
                tot = True
                z = None # take all z
            elif what == "axial_power":
                what = "powertot"
                sum_dims = ["nhex"]
                tot = True
                hex = None # take all hex

        datapath = os.path.join(self.NEpath, "intpow.out")
        if not os.path.exists(datapath):
            raise NEOutputError(f"No output in directory {self.NEpath}")

        if what in self.MapVersion["data"]["distributions"]:
            if what == "timeDistr":
                # get time array from other output files
                # FIXME iterate over all possible .out
                datapath = os.path.join(self.NEpath, f"powertot.out")
                if not os.path.exists(datapath):
                    datapath = os.path.join(self.NEpath, f"powerfis.out")
                    if not os.path.exists(datapath):
                        datapath = os.path.join(self.NEpath, f"fluxdir.out")
                        if not os.path.exists(datapath):
                            raise NEOutputError(f"Cannot parse {what} from {self.NEpath}")

                times = np.loadtxt(datapath, comments="#", usecols=(0))
                return times
            else:
                datapath = os.path.join(self.NEpath, f"{what}.out")

            isintegral = False
            idx = self.MapVersion["data"]["distributions"].index(what)
            # check core h5 is present
            if self.core is None:
                raise NEOutputError(f'Cannot provide distributions. \
                                    No `core.h5` file in {self.casepath}')

            # --- PHASE-SPACE PARAMETERS
            if hasattr(self.core, "FreneticNamelist"):
                isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
            else:
                isSym = 0
            nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss

            if hex is not None:
                # make FRENETIC numeration consistent with python indexing
                if isinstance(hex, int):
                    hex = [hex-1]
                else:
                    hex = [h-1 for h in hex] if self.core.dim != 1 else [0]
            else:
                if self.core.dim == 1:
                    hex = [0]  # 0 instead of 1 for python indexing
                else:
                    hex = np.arange(0, nhex).tolist()

            # "t" refers to slicing
            if t is None:
                if len(self.core.NE.time) == 1:
                    t = [0]  # time instant, not python index!
            # "times" refers to all time instants
            nTimeConfig = len(self.core.NE.time)
            if nTimeConfig == 1:
                times = None
            else:  # parse time from h5 file
                times = np.loadtxt(datapath, comments="#", usecols=(0))
            # --- TIME AND AXIAL COORDINATE PARAMETERS
            gro, grp, pre, prp, idt, idz = self._shift_index(gro, pre,t, z, times=times, 
                                                            particles=particles)
            dimdict = {'iTime': idt, 'iAxNode': idz, 'iHexNode': hex, 'Group': gro,
                       'Family': pre}

            if t is not None:
                timesSnap = self.core.TimeSnap # TODO distinguish existence of snapshots in simulations

        else:  # integral data
            isintegral = True
            skip = 1  # +1 for time column
            notfound = True
            for k, v in self.MapVersion["data"]["integralParameters"].items():
                if what in v:
                    dictkey = k
                    fname = f'{dictkey}.out'
                    idx = v.index(what)+skip
                    notfound = False
                    break
                elif what == 'betaeff':
                    dictkey = k
                    if 'betaeff(1)' in v:
                        fname = 'intpar.out'
                        idx = []
                        for p in range(self.npre):
                            idx.append(v.index(f'betaeff({p+1})')+skip)
                        notfound = False
                        break
                elif what == 'time':
                    idx = skip-1
                    dictkey = 'intpar'
                    notfound = False

            if notfound:
                raise NEOutputError(f'{what} not found in data!')

        # --- PARSE PROFILE FROM H5 FILE
        datapath = os.path.join(self.NEpath, fname)
        profile = np.loadtxt(datapath, comments="#", usecols=(idx))

        if profile.ndim > 0:
            return profile[:]
        else:
            return profile

    def get_v1(self, what, t=None, z=None, hex=None, pre=None,
                gro=None, metadata=False, particles="neutrons"):
        """
        Get profile from output.

        Parameters
        ----------
        what: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default None.
        t: float or iterable, optional
            Time instant(s), by default None.
        z: float or iterable, optional
            Axial coordinate(s), by default None.
        pre: integer or iterable, optional
            Precursor families, by default None.
        gro: integer or iterable, optional
            Neutron energy group(s), by default None.
        grp: integer or iterable, optional
            Photon energy group(s), by default None.
        prp: integer or iterable, optional
            Photon precursor family, by default None.

        Returns
        -------
        profile: array
            Output profile requested.
        """
        tot = False
        if what in self.MapVersion["alias"].keys():
            what = self.MapVersion["alias"][what]
        elif what in self.MapDerived:
            if what == "tot_n_precursors":
                pre = np.arange(1, self.npre+1)
                what = "precurs"
                sum_dims = ["npre", "nelz", "nhex"]
                tot = True
            elif what == "tot_p_precursors":
                pre = np.arange(1, self.nprp+1)
                what = "precursp"
                sum_dims = ["nprp", "nelz", "nhex"]
                tot = True
            elif what == "radial_power":
                what = "powertot"
                sum_dims = ["nelz"]
                tot = True
                z = None # take all z
            elif what == "axial_power":
                what = "powertot"
                sum_dims = ["nhex"]
                tot = True
                hex = None # take all hex

        h5f = NEoutput.myh5open(self.NEpath)

        if what in self.MapVersion["data"]["distributions"]:
            if what == "timeDistr":
                times = cp(np.asarray(h5f["distributions"]["timeDistr"])[()])
                # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                times[0] = 0
                # --- close H5 file
                h5f.close()
                return times
            isintegral = False
            dictkey = "distributions"
            idx = self.MapVersion["data"]["distributions"].index(what)
            # check core h5 is present
            if self.core is None:
                raise NEOutputError(f'Cannot provide distributions. \
                                    No `core.h5` file in {self.casepath}')

            # --- PHASE-SPACE PARAMETERS
            if hasattr(self.core, "FreneticNamelist"):
                isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
            else:
                isSym = 0
            nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss

            if hex is not None:
                # make FRENETIC numeration consistent with python indexing
                if isinstance(hex, int):
                    hex = [hex-1]
                else:
                    hex = [h-1 for h in hex] if self.core.dim != 1 else [0]
            else:
                if self.core.dim == 1:
                    hex = [0]  # 0 instead of 1 for python indexing
                else:
                    hex = np.arange(0, nhex).tolist()

            # "t" refers to slicing
            if t is None:
                if len(self.core.NE.time) == 1:
                    t = [0]  # time instant, not python index!
            # "times" refers to all time instants
            nTimeConfig = len(self.core.NE.time)
            if nTimeConfig == 1:
                times = None
            else:  # parse time from h5 file
                times = cp(np.asarray(h5f[dictkey]["timeDistr"])[()])
                # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                times[0] = 0
            # --- TIME AND AXIAL COORDINATE PARAMETERS
            gro, pre, idt, idz = self._shift_index(gro, pre, t, z, times=times, particles=particles)
            dimdict = {'iTime': idt, 'iAxNode': idz, 'iHexNode': hex, 'Group': gro,
                       'Family': pre}

            if t is not None:
                timesSnap = self.core.TimeSnap # TODO distinguish existence of snapshots in simulations

        else:  # integral data
            isintegral = True
            skip = 1  # +1 for time column
            notfound = True
            for k, v in self.MapVersion["data"]["integralParameters"].items():
                if what in v:
                    dictkey = k
                    idx = v.index(what)+skip
                    notfound = False
                    break
                elif what == 'betaeff':
                    dictkey = k
                    if 'betaeff(1)' in v:
                        idx = []
                        for p in range(self.npre):
                            idx.append(v.index(f'betaeff({p+1})')+skip)
                        notfound = False
                        break
                elif what == 'time':
                    idx = skip-1
                    dictkey = 'intpar'
                    notfound = False

            if notfound:
                raise NEOutputError(f'{what} not found in data!')

        # --- PARSE PROFILE FROM H5 FILE
        if isintegral:
            if what == 'betaeff':
                betas = cp(np.array(h5f['integralParameters'][dictkey])[:, [idx]][:, 0, :])
                profile = betas.sum(axis=1)
            elif what == 'eigenvalue dir.' or what == 'eigenvalue adj.':
                profile = np.squeeze(h5f['integralParameters'][dictkey][:, [idx]])
            else:
                profile = h5f['integralParameters'][dictkey][:, [idx]][()]
        else:
            # parse specified time, assembly, axial node, group, prec. fam.
            dims = self.MapVersion['metadata']['distributions']['dim'][what]
            dimlst = []

            for d in dims:
                x = dimdict[d]
                if x is None:
                    x = 0 if x == 'iTime' else slice(None)
                dimlst.append(x)

            if what == "powertot":
                if what not in h5f[dictkey].keys():
                    ntim = len(np.asarray(h5f[dictkey]["timeDistr"]))
                    profile = np.zeros((ntim, self.nelz, self.nhex))
                    for p in ["powerfis", "powerneu", "powerpho"]:
                        if p in h5f[dictkey].keys():
                            powr = np.asarray(h5f[dictkey][p])
                        else:
                            powr = np.zeros((ntim, self.nelz, self.nhex))
                        profile += powr
            else:
                profile = np.asarray(h5f[dictkey][what])

            profile = profile[np.ix_(*dimlst)]

            if tot:
                dims = self.distrout_dim[what]
                for sum_dim in sum_dims:
                    sum_ax = dims.index(sum_dim)
                    if "power" in what:
                        if sum_dim == "nhex":
                            w = self.core.Geometry.AssemblyGeometry.area
                            profile = w*profile.sum(axis=sum_ax)
                        elif sum_dim == "nelz":
                            w = self.core.NE.AxialConfig.dz
                            profile = np.tensordot(profile, w, axes=([sum_ax], [0]))
                            profile = profile*self.core.Geometry.AssemblyGeometry.area
                        else:
                            raise NEOutputError(f"Cannot get {what} from data!")
                    else:
                        profile = profile.sum(axis=sum_ax)

                    dims = list(dims)
                    dims.remove(sum_dim)
                    dims = tuple(dims)

        # TODO: add metadata (and color) extraction

        # --- close H5 file
        h5f.close()
        if profile.ndim > 0:
            return profile[:]
        else:
            return profile

    def get_v2(self, what, t=None, z=None, hex=None, pre=None,
                gro=None, metadata=False):
        """
        Get profile from output.

        Parameters
        ----------
        what: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default None.
        t: float or iterable, optional
            Time instant(s), by default None.
        z: float or iterable, optional
            Axial coordinate(s), by default None.
        pre: integer or iterable, optional
            Precursor families, by default None.
        gro: integer or iterable, optional
            Neutron energy group(s), by default None.
        particles: string, optional
            The particle species analysed. It can be either "neutrons"
            or "photons".

        Returns
        -------
        profile: array
            Output profile requested.
        """
        # check alias or derived quantities
        if what in self.MapVersion["alias"].keys():
            what = self.MapVersion["alias"][what]

        # --- open
        h5f = NEoutput.myh5open(self.NEpath)

        # group content of each list. If duplicates, put them into a list
        if what in self.dupl:
            raise NEOutputError(f"More than one '{what}' dataset available. Add more details (e.g., particle, distributions/integralParameters)!")

        dsetpath = None
        for idx, path in enumerate(self.HDF5_path):
            if what in path:
                if "/" in what:
                    dset = what.split("/")[-1]
                    dset_in_path = path.split("/")[-1]
                else:
                    dset = what
                    dset_in_path = path.split("/")[-1]

                if dset == dset_in_path:
                    dsetpath = self.HDF5_path[idx]
                    break

        if dsetpath is None:
            raise NEOutputError(f"{what} not available in NEoutput v{self.version}")
        else:
            if "distributions/" in dsetpath:
                read_distr = True
                read_intpar = False
            elif "integralParameters/" in dsetpath:
                read_distr = False
                read_intpar = True
                # change dsetpath to accomodate for compound dset
                h5groups = dsetpath.split("/")
                if len(h5groups) > 2:
                    h5path = "/".join(h5groups[:-1])
                    dsetpath = h5f[h5path].fields(h5groups[-1])
                else:
                    h5path = dsetpath
            else:
                raise NEOutputError(f"{what} in NEoutput v{self.version} cannot be read!")

        # read
        if not read_intpar:
            if "time" not in what:
                # check core h5 is present
                if self.core is None:
                    raise NEOutputError(f'Cannot provide distributions. \
                                        No `core.h5` file in {self.casepath}')

                # --- PHASE-SPACE PARAMETERS
                if hasattr(self.core, "FreneticNamelist"):
                    isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
                else:
                    isSym = 0

                nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss
                if hex is not None:
                    # make FRENETIC numeration consistent with python indexing
                    if isinstance(hex, int):
                        hex = [hex-1]
                    else:
                        hex = [h-1 for h in hex] if self.core.dim != 1 else [0]
                else:
                    if self.core.dim == 1:
                        hex = [0]  # 0 instead of 1 for python indexing
                    else:
                        hex = np.arange(0, nhex).tolist()

                # "t" refers to slicing
                nTimeConfig = len(self.core.NE.time)
                if t is None:
                    if nTimeConfig == 1:
                        t = [0]  # time instant, not python index!
                # "times" refers to all time instants
                if nTimeConfig == 1:
                    times = None
                else:  # parse time from h5 file
                    times = np.asarray(h5f["distributions/time"])

                # --- TIME AND AXIAL COORDINATE PARAMETERS
                particles = "neutrons" if "neutrons" in dsetpath else "photons"
                gro, pre, idt, idz = self._shift_index(gro, pre, t, z, times=times, 
                                                        particles=particles)
                # FIXME select surface
                if self.core.dim == 1:
                    surf = np.arange(0, 2).tolist()
                elif self.core.dim == 2: 
                    surf = np.arange(0, 6).tolist()
                else:
                    surf = np.arange(0, 8).tolist()

                dimdict = {'iTime': idt, 'iAxNode': idz, 'iHexNode': hex, 'iSurf': surf}
                if particles == "neutrons":
                    dimdict['Group'] = gro
                    dimdict['Family'] = pre
                elif particles == "photons":
                    dimdict['GroupP'] = gro
                    dimdict['Family'] = pre

                if t is not None:
                    timesSnap = self.core.TimeSnap # TODO distinguish existence of snapshots in simulations

        else:  # integral data
            if dset != "time":
                # check core h5 is present
                if self.core is None:
                    raise NEOutputError(f'Cannot provide integralParameters. \
                                        No `core.h5` file in {self.casepath}')
                # "t" refers to slicing
                nTimeConfig = len(self.core.NE.time)
                # "times" refers to all time instants
                if nTimeConfig == 1:
                    times = None
                else:  # parse time from h5 file
                    if dset in self.MapVersion["data"]["integralParameters"]["static"]:
                        if self.core.trans:
                            times = None  # initial conditions
                        else:
                            times = self.core.NE.time
                    else:
                        times = np.asarray(h5f["integralParameters/time"])

                # get t index
                if times is not None:
                    if t is not None:
                        if isinstance(t, (list, np.ndarray)):
                            idt = [np.argmin(abs(ti-times)) for ti in t]
                        else:
                            idt = [np.argmin(abs(t-times))]
                    else:
                        idt = np.arange(0, len(times)).tolist()
                else:
                    idt = 0

        # --- PARSE PROFILE FROM H5 FILE
        if read_intpar:
            if dset != "time":
                profile = dsetpath[idt]
            else:
                profile = np.asarray(h5f[dsetpath])

        else:
            if dset != "time":
                # parse specified time, assembly, axial node, group, prec. fam.
                if dsetpath not in h5f:
                    raise NEOutputError(f"{dsetpath} not present in HDF5 output NE file!")
                else:
                    profile = np.asarray(h5f[dsetpath])

                dims = h5f[dsetpath].attrs['dimensions'][0].decode()
                dims = dims[1:-1].split(",")
                dimlst = []

                for d in dims:
                    x = dimdict[d]
                    if x is None:
                        x = 0 if x == 'iTime' else slice(None)
                    dimlst.append(x)

                profile = profile[np.ix_(*dimlst)]
            else:
                profile = np.asarray(h5f[dsetpath])

        # --- parse metadata (unit of measure and description)
        if read_intpar:
            description = h5f[h5path].attrs["description"][0].decode()
            uoms = h5f[h5path].attrs["unit of measure"][0].decode()
            uoms = uoms.split(",")
            for i, u in enumerate(uoms):
                if "(" in u:
                    u = u.split("(")[1]
                elif ")" in u:
                    u = u.split(")")[0]

                uoms[i] = u.replace(" ", "")
            # select uom
            mydict = self.MapVersion["data"]
            for g in h5groups:
                if isinstance(mydict, dict):
                    mydict = mydict[g]
                elif isinstance(mydict, list):
                    uom = uoms[mydict.index(g)]
        else:
            if metadata:
                description = h5f[dsetpath].attrs["description"][0].decode()
                uom = h5f[dsetpath].attrs["unit of measure"][0].decode()
                if "reaction_rate_density" not in path:
                    rel_path = path.split("/")[-1]
                    if "power_density" in path:
                        rel_path = "power_density/" + rel_path
                    color = self.MapVersion["metadata"]["colormap"][rel_path]
                else:
                    color = "Plasma"
        # --- close H5 file
        h5f.close()

        if metadata:

            if profile.ndim > 0:
                return profile[:], description, uom, color
            else:
                return profile, description, uom, color

        else:

            if profile.ndim > 0:
                return profile[:]
            else:
                return profile

    def get_derived(self, what, t=None, z=None, hex=None, pre=None,
                gro=None, metadata=False):
        """
        Get profile from output.

        Parameters
        ----------
        what: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default None.
        t: float or iterable, optional
            Time instant(s), by default None.
        z: float or iterable, optional
            Axial coordinate(s), by default None.
        pre: integer or iterable, optional
            Precursor families, by default None.
        gro: integer or iterable, optional
            Neutron energy group(s), by default None.
        particles: string, optional
            The particle species analysed. It can be either "neutrons"
            or "photons".

        Returns
        -------
        profile: array
            Output profile requested.
        """
        tot = False
        if what == "tot_n_precursors":
            pre = np.arange(1, self.npre+1)
            what = "precursors"
            sum_dims = ["Family", "iAxNode", "iHexNode"]
            tot = True
        elif what == "tot_p_precursors":
            pre = np.arange(1, self.nprp+1)
            what = "precursors"
            particles = "photons"
            sum_dims = ["Family", "iAxNode", "iHexNode"]
            tot = True
        elif what == "radial_power":
            # look for total power
            try:
                profile = self.get("power_density/total", z=None, t=t, hex=hex, gro=gro, pre=pre)
            except NEOutputError as err:
                if "not present in HDF5 output NE file!" in str(err):
                    # reconstruct total power
                    if t is None:
                        time = self.get("distributions/time")
                        ntim = len(time)
                    else:
                        if isinstance(t, list):
                            ntim = len(t)
                        else:
                            ntim = 1

                    if hex is None:
                        nhex = self.nhex
                    else:
                        if isinstance(hex, list):
                            nhex = len(hex)
                        else:
                            nhex = 1

                    profile = np.zeros((ntim, self.nelz, nhex))

                    for p in ["power_density/fission", "power_density/neutron_kerma", "power_density/photon_kerma"]:
                        try:
                            powr = self.get(p, z=None, t=t, hex=hex, gro=gro, pre=pre)
                        except NEOutputError:
                            powr = np.zeros((ntim, self.nelz, nhex))
                        profile += powr
                else:
                    raise NEOutputError(err)
            # integrate over the axial coordinate
            dz = self.core.NE.AxialConfig.dz
            profile = np.tensordot(profile, dz, axes=([1], [0]))
            profile = profile*self.core.Geometry.AssemblyGeometry.area
# FIXME TODO 
        # if tot:
        #     dims = self.distrout_dim[what]
        #     for sum_dim in sum_dims:
        #         sum_ax = dims.index(sum_dim)
        #         if "power" in what:
        #             if sum_dim == "nhex":
        #                 w = self.core.Geometry.AssemblyGeometry.area
        #                 profile = w*profile.sum(axis=sum_ax)
        #             elif sum_dim == "nelz":
        #                 w = self.core.NE.AxialConfig.dz
        #                 profile = np.tensordot(profile, w, axes=([sum_ax], [0]))
        #                 profile = profile*self.core.Geometry.AssemblyGeometry.area
        #             else:
        #                 raise NEOutputError(f"Cannot get {what} from data!")
        #         else:
        #             profile = profile.sum(axis=sum_ax)

        #         dims = list(dims)
        #         dims.remove(sum_dim)
        #         dims = tuple(dims)



        elif what == "axial_power":
            what = "power_density/total"
            sum_dims = ["iHexNode"]
            tot = True
            hex = None # take all hex
        elif what == "global_importance":
            neu_dens = self.get("neutron_density", t=t, z=z, hex=hex, pre=pre, gro=gro)
            flux_adj = self.get("neutrons/flux_adj", t=t, z=z, hex=hex, pre=pre, gro=gro)
            profile = neu_dens*flux_adj
        elif what == "neutron_density":
            flux = self.get("neutrons/flux", t=t, z=z, hex=hex, pre=pre, gro=gro)
            profile = np.zeros(flux.shape)
            # get velocity from macro.nml
            with open(os.path.join(self.NEpath, 'macro.nml'), 'r') as macronml:
                for l in macronml:
                    if 'veloc0' in l:
                        nvel = l.split(' = ')[1]
                        nvel = nvel.split(",")
                        nvel = [float(v.replace("d", "e")) for v in nvel[:-1]]

            if gro is None:
                for g in range(self.ngro):
                    profile[:, g, :, :] = flux[:, g, :, :]/nvel[g]
            else:
                profile[:, :, :, :] = flux/nvel[gro]

        if metadata:
            uom = self.MapDerived["metadata"]["uom"][what]
            description = self.MapDerived["metadata"]["description"][what]
            color = self.MapDerived["metadata"]["colormap"][what]
            if profile.ndim > 0:
                return profile[:], description, uom, color
            else:
                return profile, description, uom, color

        else:

            if profile.ndim > 0:
                return profile[:]
            else:
                return profile

    def eplot(self, eflx=None, t=None, z=None, hex=None, ax=None,
              pre=False, title=None, figname=None, egrid=False,
              lethargynorm=True, logx=True, logy=True, **kwargs, ):
        """
        Plot solution along energy for a certain portion of the phase space.

        Parameters
        ----------

        Returns
        -------
        None.

        """
        if logx and logy:
            loglog = True
        else:
            loglog = False

        E = self.core.NE.energygrid
        if eflx is None:
            raise OSError("TODO: implement automatic space integration")

        if lethargynorm:
            u = np.log(E[0]/E)
            eflx = eflx/np.diff(u)
        ax = ax or plt.gca()

        yr = np.zeros((len(eflx)+1,))
        yr[0] = eflx[0]
        yr[1:] = eflx

        plt.step(E, yr, where='pre', **kwargs)

        if loglog or logx:
            ax.set_xscale('log')
        if loglog or logy:
            ax.set_yscale('log')

        if egrid:
            for e in E:
                ax.axvline(e, c='k', lw=0.5, ls=':')

        plt.grid(axis='both', alpha=0.2)
        ax.set_xlabel('E [MeV]')
        if title is not None:
            plt.title(title)
        if figname:
            plt.tight_layout()
            plt.savefig(f"{figname}.pdf")

    def plot1D(self, what, gro=None, t=None, grp=None, pre=None, prp=None, ax=None,
               abscissas=None, z=None, hex=None, leglabels=None, figname=None, xlabel=None,
               xlims=None, ylims=None, ylabel=None, geometry=None, txtfmt=False,
               style='sty1D.mplstyle', legend=True, **kwargs):
        """
        Plot time/axial profile of integral param. or distribution in hex.

        Parameters
        ----------
        what : string
            Profile name according to FRENETIC namelist.
        zt : ndarray, optional
            Axial or time grid, by default None.
        figname : TYPE, optional
            Name assigned to the figure for saving, by default None.

        Returns
        -------
        None.
        """
        if style == 'sty1D.mplstyle':
            pwd = Path(__file__).parent.parent
            toolspath = Path.joinpath(pwd, "tools")
            if toolspath.exists():
                sty1D = str(Path.joinpath(pwd, "tools", style))
            else:
                raise NEOutputError(f"{toolspath} not found!")
        else:
            if not Path(style).exists():
                logging.info(f'{style} style sheet not found! \
                                Switching to default...')
            else:
                sty1D = style

        if what == "precursTot":
            pre = np.arange(1, self.npre+1)
            what = "precurs"
            sum_dims = ["npre", "nelz", "nhex"]
            tot = True
        elif what == "precurspTot":
            pre = np.arange(1, self.nprp+1)
            what = "precursp"
            sum_dims = ["nprp", "nelz", "nhex"]
            tot = True
        else:
            tot = False

        label = what
        if what in self.MapVersion['alias'].keys():
            what = self.MapVersion['alias'][what]

        # select unit of measure corresponding to profile
        plotvstime = True if t else False
        if t:
            t = None
        if what in self.MapVersion['data']['distributions']:
            isintegral = False
            idx = self.MapVersion['data']['distributions'].index(what)
            uom = self.MapVersion['metadata']['distributions']['uom'][what]
            dims = NEoutput.distrout_dim[what]
        else:  # integral data
            isintegral = True
            for k, v in self.MapVersion["data"]["integralParameters"].items():
                if what in v:
                    idx = v.index(what)
                    uom = self.MapVersion['metadata']['integralParameters']['uom'][what]
        # --- parse profile
        prof = self.get(what, gro=gro, hex=hex, t=t, z=z, pre=pre, prp=prp)
        # sum along axes, if total distribution is requested
        if tot:
            dims = self.distrout_dim[what]
            for sum_dim in sum_dims:
                sum_ax = dims.index(sum_dim)
                prof = prof.sum(axis=sum_ax)
                dims = list(dims)
                dims.remove(sum_dim)
                dims = tuple(dims)
            pre = None
            plotvstime = True
        # --- select independent variable
        # it can be time or axial coordinate
        nTimeConfig = len(self.core.NE.time)
        if nTimeConfig == 1:
            times = None # np.array([0])
        else:  # parse time from h5 file
            if not txtfmt:
                datapath = os.path.join(self.NEpath, "output.h5")
            if isintegral:
                if what != "precursTot":
                    times = self.get('time')
                else:
                    times = self.get('timeDistr')
                y = prof
            else:
                if txtfmt:
                    times = np.loadtxt(datapath, comments="#", usecols=(0))
                else:
                    times = cp(self.get('timeDistr')[()])
                    # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                    times[0] = 0
                if plotvstime:
                    t = times

        if t is None:
            t = [0]  # initial condition
        if isintegral and nTimeConfig == 1:
            raise NEOutputError("Cannot plot integral parameter in steady state!")

        ax = plt.gca() if ax is None else ax
        if isintegral:  # plot integral parameter
            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                handles = []
                handlesapp = handles.append
                if what in ['rho', 'reactivityn', 'betaeff']:
                    y *= 1E5
                if abscissas is not None:
                    x = abscissas
                else:
                    x = times
                lin1, = ax.plot(x, y, **kwargs)
                ax.set_xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    for k, v in self.MapVersion["data"]["integralParameters"].items():
                        if what in v:
                            idx = v.index(what)
                            uom = self.integralParameters_measure[k][idx]
                    ax.set_ylabel(fr"{what} {uom}")
                else:
                    ax.set_ylabel(ylabel)
        else:   # plot distribution
            if hex is None:
                hex = [0] # 1st hexagon (this is python index, not hex. number)

            # get python-wise index for slicing
            igro, ipre, idt, idz = self._shift_index(gro, pre, t, z, times=times)
            # map indexes from full- to sliced-array
            igro, ipre, idt, idz = self._to_index(igro, ipre, idt, idz)

            if nTimeConfig > 1 and plotvstime:  # plot against time
                x = times
                dim2plot = 'iTime'
                idx = dims.index('iTime')
                if xlabel is None:
                    xlabel = 'time [s]'
            else:  # plot time snapshots, if any, against axial coordinate
                x = self.core.NE.AxialConfig.AxNodes
                dim2plot = 'iAxNode'
                idx = dims.index('iAxNode')
                if xlabel is None:
                    xlabel = 'z-coordinate [cm]'

            # --- DEFINE SLICES
            dimdict = {'iTime': idt, 'iAxNode': idz, 'Group': igro,
                        'ngrp': igrp, 'Family': ipre, 'iHexNode': hex}
            usrdict = {'iTime': t, 'iAxNode': z, 'Group': gro,
                       'ngrp': grp, 'Family': pre, 'iHexNode': hex}
            dimlst = [None]*len(dims)
            for k in dims:
                i = dims.index(k)
                dimlst[i] = dimdict[k]
            # define multi-index
            tmp = dimlst.pop(idx)
            indexes = list(itertools.product(*dimlst))
            indexes = [list(tup) for tup in indexes]
            for i in range(len(indexes)):
                indexes[i].insert(idx, tmp)

            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                ax = plt.gca() if ax is None else ax
                handles = []
                handlesapp = handles.append
                ymin, ymax = np.inf, -np.inf
                # loop over dimensions to slice
                for i, s in enumerate(indexes):
                    y = prof[s[i]]  # .take(indices=d, axis=i)
                    label = self._build_label(s, dims, dim2plot, usrdict)
                    if abscissas is not None:
                        x = abscissas
                    lin1, = ax.plot(x, y, label=label, **kwargs)
                    handlesapp(lin1)
                    # track minimum and maximum
                    if ylims is None:
                        ymin = y.min() if y.min() < ymin else ymin
                        ymax = y.max() if y.max() > ymax else ymax

                if ylims is not None:
                    ymin = min(ylims)
                    ymax = max(ylims)

                plt.xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    if what in self.distributions:
                        isintegral = False
                        idx = self.distributions.index(what)
                        uom = self.distributions_measure[idx]
                    else:  # integral data
                        isintegral = True
                        for k, v in self.MapVersion["data"]["integralParameters"].items():
                            if what in v:
                                idx = v.index(what)
                                uom = self.integralParameters_measure[k][idx]

                    if rcParams['text.usetex']:
                        plt.ylabel(rf"{what} ${uom}$")
                    else:
                        plt.ylabel(f"{what} {uom}")
                else:
                    plt.ylabel(ylabel)

                # ax.set_ylim(ymin, ymax)
                ax.set_xlim(x.min(), x.max())

                legend_x = 0.50
                legend_y = 1.01
                ncol = 2 if len(indexes) < 4 else 4
                if leglabels is not None:
                    plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)
                else:
                    if legend:
                        plt.legend(bbox_to_anchor=(legend_x, legend_y),
                                loc='lower center', ncol=ncol)

                plt.tight_layout()
                # plt.show()
                if figname is not None:
                    ax.savefig(figname)

    def tplot1D(self, what, gro=None, pre=None, ax=None,
               abscissas=None, z=None, hex=None, leglabels=None, 
               figname=None, xlabel=None,
               xlims=None, ylims=None, ylabel=None, geometry=None,
               style='sty1D.mplstyle', norm=True, t_config=True, 
               legend=True, **kwargs):
        """
        Plot integral param. or distribution against time.

        Parameters
        ----------
        what : string
            Profile name according to FRENETIC namelist.
        zt : ndarray, optional
            Axial or time grid, by default None.
        figname : TYPE, optional
            Name assigned to the figure for saving, by default None.

        Returns
        -------
        None.
        """
        if style == 'sty1D.mplstyle':
            pwd = Path(__file__).parent.parent
            toolspath = Path.joinpath(pwd, "tools")
            if toolspath.exists():
                sty1D = str(Path.joinpath(pwd, "tools", style))
            else:
                raise NEOutputError(f"{toolspath} not found!")
        else:
            if not Path(style).exists():
                logging.info(f'{style} style sheet not found! \
                                Switching to default...')
            else:
                sty1D = style

        label = what
        if what in self.MapVersion["alias"].keys():
            what = self.MapVersion["alias"][what]

        # --- parse profile
        y, descr, uom = self.get(what, gro=gro, hex=hex, z=z, pre=pre, metadata=True)
        # --- select independent variable
        for idx, path in enumerate(self.HDF5_path):
            if what in path:
                if "/" in what:
                    dset = what.split("/")[-1]
                    dset_in_path = path.split("/")[-1]
                else:
                    dset = what
                    dset_in_path = path.split("/")[-1]

                if dset == dset_in_path:
                    dsetpath = self.HDF5_path[idx]
                    break
        root_group = dsetpath.split("/")[0]
        # integral or distribution?
        isintegral = root_group == "integralParameters"
        if isintegral:
            t = self.get("integralParameters/time")
        else:
            t = self.get("distributions/time")

        particles = "neutrons"
        if norm:
            lifetime0 = self.get(f"{particles}/effective_lifetime", t=0)
            t = t/lifetime0
            if xlabel is None:
                if rcParams['text.usetex']:
                    xlabel = fr"{particles} generations"
                else:
                    xlabel = fr"{particles} generations"

        else:
            # TODO foresee [micro s], [ms], ... [h]
            xlabel = f"time [s]"

        # nTimeConfig = len(self.core.NE.time)
        ax = plt.gca() if ax is None else ax
        if isintegral:  # plot integral parameter
            # plot against time
            with plt.style.context(sty1D):
                past_vers = float(self.version) <= 2.0
                if past_vers and what in ['rho', 'reactivityn', 'betaeff']:
                    y *= 1E5

                lin1, = ax.plot(t, y, **kwargs)
                ax.set_xlabel(xlabel)
                if ylabel is None:

                    if "/" in what:
                        dset = what.split("/")[-1]
                    else:
                        dset = what

                    if rcParams['text.usetex']:
                        ax.set_ylabel(rf"{dset} ${uom}$")
                    else:
                        ax.set_ylabel(f"{dset} {uom}")

                else:
                    ax.set_ylabel(ylabel)
        else:   # plot distribution
            if hex is None:
                hex = [0] # 1st hexagon (this is python index, not hex. number)

            # get python-wise index for slicing
            igro, ipre, idt, idz = self._shift_index(gro, pre, t, z, times=times)
            # map indexes from full- to sliced-array
            igro, ipre, idt, idz = self._to_index(igro, ipre, idt, idz)

            # --- DEFINE SLICES
            dimdict = {'iTime': idt, 'iAxNode': idz, 'Group': igro,
                        'ngrp': igrp, 'Family': ipre, 'iHexNode': hex}
            usrdict = {'iTime': t, 'iAxNode': z, 'Group': gro,
                       'ngrp': grp, 'Family': pre, 'iHexNode': hex}
            dimlst = [None]*len(dims)
            for k in dims:
                i = dims.index(k)
                dimlst[i] = dimdict[k]
            # define multi-index
            tmp = dimlst.pop(idx)
            indexes = list(itertools.product(*dimlst))
            indexes = [list(tup) for tup in indexes]
            for i in range(len(indexes)):
                indexes[i].insert(idx, tmp)

            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                ax = plt.gca() if ax is None else ax
                handles = []
                handlesapp = handles.append
                ymin, ymax = np.inf, -np.inf
                # loop over dimensions to slice
                for i, s in enumerate(indexes):
                    y = prof[s[i]]  # .take(indices=d, axis=i)
                    label = self._build_label(s, dims, dim2plot, usrdict)
                    if abscissas is not None:
                        x = abscissas
                    lin1, = ax.plot(x, y, label=label, **kwargs)
                    handlesapp(lin1)
                    # track minimum and maximum
                    if ylims is None:
                        ymin = y.min() if y.min() < ymin else ymin
                        ymax = y.max() if y.max() > ymax else ymax

                if ylims is not None:
                    ymin = min(ylims)
                    ymax = max(ylims)

                plt.xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    if what in self.distributions:
                        isintegral = False
                        idx = self.distributions.index(what)
                        uom = self.distributions_measure[idx]
                    else:  # integral data
                        isintegral = True
                        for k, v in self.MapVersion["data"]["integralParameters"].items():
                            if what in v:
                                idx = v.index(what)
                                uom = self.integralParameters_measure[k][idx]

                    if "/" in what:
                        dset = what.split("/")[-1]
                    else:
                        dset = what

                    if rcParams['text.usetex']:
                        plt.ylabel(rf"{dset} ${uom}$")
                    else:
                        plt.ylabel(f"{dset} {uom}")
                else:
                    plt.ylabel(ylabel)

                # ax.set_ylim(ymin, ymax)
                ax.set_xlim(x.min(), x.max())

                legend_x = 0.50
                legend_y = 1.01
                ncol = 2 if len(indexes) < 4 else 4
                if leglabels is not None:
                    plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)
                else:
                    if legend:
                        plt.legend(bbox_to_anchor=(legend_x, legend_y),
                                loc='lower center', ncol=ncol)

                plt.tight_layout()
                # plt.show()
                if figname is not None:
                    ax.savefig(figname)

    def zplot1D(self, what, gro=None, pre=None, ax=None,
               abscissas=None, t=None, hex=None, leglabels=None, 
               figname=None, xlabel=None,
               xlims=None, ylims=None, ylabel=None, geometry=None,
               style='sty1D.mplstyle', norm=True,
               legend=True, **kwargs):
        """
        Plot integral param. or distribution against axis.

        Parameters
        ----------
        what : string
            Profile name according to FRENETIC namelist.
        zt : ndarray, optional
            Axial or time grid, by default None.
        figname : TYPE, optional
            Name assigned to the figure for saving, by default None.

        Returns
        -------
        None.
        """
        if style == 'sty1D.mplstyle':
            pwd = Path(__file__).parent.parent
            toolspath = Path.joinpath(pwd, "tools")
            if toolspath.exists():
                sty1D = str(Path.joinpath(pwd, "tools", style))
            else:
                raise NEOutputError(f"{toolspath} not found!")
        else:
            if not Path(style).exists():
                logging.info(f'{style} style sheet not found! \
                                Switching to default...')
            else:
                sty1D = style

        label = what
        if what in self.MapVersion["alias"].keys():
            what = self.MapVersion["alias"][what]

        # --- parse profile
        y, descr, uom = self.get(what, gro=gro, hex=hex, t=t, pre=pre, metadata=True)
        # --- select independent variable
        for idx, path in enumerate(self.HDF5_path):
            if what in path:
                if "/" in what:
                    dset = what.split("/")[-1]
                    dset_in_path = path.split("/")[-1]
                else:
                    dset = what
                    dset_in_path = path.split("/")[-1]

                if dset == dset_in_path:
                    dsetpath = self.HDF5_path[idx]
                    break
        root_group = dsetpath.split("/")[0]

        if norm:
            z = z/z.max()
            if xlabel is None:
                xlabel = " normalised axial coordinate $[-]$"

        else:
            xlabel = f"axial coordinate [cm]"

        # nTimeConfig = len(self.core.NE.time)
        ax = plt.gca() if ax is None else ax

        if hex is None:
            hex = [0] # 1st hexagon (this is python index, not hex. number)

        # get python-wise index for slicing
        igro, ipre, idt, idz = self._shift_index(gro, pre, t, z, times=times)
        # map indexes from full- to sliced-array
        igro, ipre, idt, idz = self._to_index(igro, ipre, idt, idz)

        # --- DEFINE SLICES
        dimdict = {'iTime': idt, 'iAxNode': idz, 'Group': igro,
                    'ngrp': igrp, 'Family': ipre, 'iHexNode': hex}
        usrdict = {'iTime': t, 'iAxNode': z, 'Group': gro,
                    'ngrp': grp, 'Family': pre, 'iHexNode': hex}
        dimlst = [None]*len(dims)
        for k in dims:
            i = dims.index(k)
            dimlst[i] = dimdict[k]
        # define multi-index
        tmp = dimlst.pop(idx)
        indexes = list(itertools.product(*dimlst))
        indexes = [list(tup) for tup in indexes]
        for i in range(len(indexes)):
            indexes[i].insert(idx, tmp)

        # --- PLOT
        # plot against axial coordinate
        with plt.style.context(sty1D):
            ax = plt.gca() if ax is None else ax
            handles = []
            handlesapp = handles.append
            ymin, ymax = np.inf, -np.inf
            # loop over dimensions to slice
            for i, s in enumerate(indexes):
                y = prof[s[i]]  # .take(indices=d, axis=i)
                label = self._build_label(s, dims, dim2plot, usrdict)
                if abscissas is not None:
                    x = abscissas
                lin1, = ax.plot(x, y, label=label, **kwargs)
                handlesapp(lin1)
                # track minimum and maximum
                if ylims is None:
                    ymin = y.min() if y.min() < ymin else ymin
                    ymax = y.max() if y.max() > ymax else ymax

            if ylims is not None:
                ymin = min(ylims)
                ymax = max(ylims)

            plt.xlabel(xlabel)
            if ylabel is None:
                # select unit of measure corresponding to profile
                if what in self.distributions:
                    isintegral = False
                    idx = self.distributions.index(what)
                    uom = self.distributions_measure[idx]
                else:  # integral data
                    isintegral = True
                    for k, v in self.MapVersion["data"]["integralParameters"].items():
                        if what in v:
                            idx = v.index(what)
                            uom = self.integralParameters_measure[k][idx]

                if "/" in what:
                    dset = what.split("/")[-1]
                else:
                    dset = what

                if rcParams['text.usetex']:
                    plt.ylabel(rf"{dset} ${uom}$")
                else:
                    plt.ylabel(f"{dset} {uom}")
            else:
                plt.ylabel(ylabel)

            # ax.set_ylim(ymin, ymax)
            ax.set_xlim(x.min(), x.max())

            legend_x = 0.50
            legend_y = 1.01
            ncol = 2 if len(indexes) < 4 else 4
            if leglabels is not None:
                plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                        loc='lower center', ncol=ncol)
            else:
                if legend:
                    plt.legend(bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)

            plt.tight_layout()
            # plt.show()
            if figname is not None:
                ax.savefig(figname)

    def RadialMap(self, what, z=0, t=0, pre=0, gro=1, grp=0,
                  label=False, figname=None, hex=None,
                  usetex=False, fill=True, axes=None, cmap=None,
                  thresh=None, cbarLabel=True, xlabel=None, ylabel=None,
                  log=None, title=True, scale=1, fmt="%.2f", **kwargs):
        """
        Plot FRENETIC output on the x-y plane.

        Parameters
        ----------
        label : TYPE, optional
            DESCRIPTION, by default False.
        figname : TYPE, optional
            DESCRIPTION, by default None.
        fren : TYPE, optional
            DESCRIPTION, by default False.
        what : TYPE, optional
            DESCRIPTION, by default None.
        what : TYPE, optional
            DESCRIPTION, by default None.
        usetex : TYPE, optional
            DESCRIPTION, by default False.
        fill : TYPE, optional
            DESCRIPTION, by default True.
        axes : TYPE, optional
            DESCRIPTION, by default None.
        cmap : TYPE, optional
            DESCRIPTION, by default 'Spectral_r'.
        thresh : TYPE, optional
            DESCRIPTION, by default None.
        cbarLabel : TYPE, optional
            DESCRIPTION, by default None.
        xlabel : TYPE, optional
            DESCRIPTION, by default None.
        ylabel : TYPE, optional
            DESCRIPTION, by default None.
        loglog : TYPE, optional
            DESCRIPTION, by default None.
        logx : TYPE, optional
            DESCRIPTION, by default None.
        logy : TYPE, optional
            DESCRIPTION, by default None.
        title : TYPE, optional
            DESCRIPTION, by default None.
        scale : TYPE, optional
            DESCRIPTION, by default 1.
        fmt : TYPE, optional
            DESCRIPTION, by default "%.2f".
        **kwargs : TYPE
            DESCRIPTION.

        Raises
        ------
        IndexError
            DESCRIPTION.
        TypeError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        uom = ""
        descr = ""
        if hasattr(self.core, "FreneticNamelist"):
            isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
        else:
            isSym = 0
        nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss
        # check data type
        if isinstance(what, dict):  # comparison with FRENETIC and other vals.
            tallies = np.zeros((nhex, len(what.keys())))
            for i, k in enumerate(what.keys()):
                v2 = what[k]
                v1, descr, uom, color = self.get(k, hex=what, t=t, z=z, pre=pre, gro=gro, metadata=True)
                v1 = np.squeeze(v1)
                tmp = np.true_divide(norm(v1-v2), norm(v1))
                tmp[tmp == np.inf] = 0
                tmp = np.nan_to_num(tmp)
                tallies[:, i] = tmp*100

        # FIXME: is this really useful?

        # elif isinstance(what, list):  # list of output # TODO TO BE TESTED
        #     tallies = np.zeros((nhex, len(what)))
        #     for i, w in enumerate(what):
        #         _tmp = self.get(w, hex=what, t=t, z=z, 
        #                         pre=pre, gro=gro)
        #         tallies[:, i] = np.squeeze(_tmp)

        elif isinstance(what, str):  # single output
            tallies, descr, uom, color = self.get(what, t=t, z=z, pre=pre, gro=gro, metadata=True)
            tallies = np.squeeze(tallies)
        # elif isinstance(what, (np.ndarray)):
        #     tallies = what+0
        #     what = None
        else:
            raise TypeError('Input must be str, dict or list!')

        if cmap is None:
            cmap = color

        if title is True:
            timeSnap = self.core.TimeSnap
            idt = np.argmin(abs(t-timeSnap))

            if self.core.dim != 2:
                nodes = self.core.NE.AxialConfig.AxNodes
                idz = np.argmin(abs(z-nodes))
                title = 'z=%.2f [cm], t=%.2f [s]' % (nodes[idz], timeSnap[idt])
            else:
                nodes = np.array([0])
                idz = 0
                title = 't=%.2f [s]' % (timeSnap[idt])


        if cbarLabel is True:

            uom = uom.replace('**', '^')
            changes = ['-1', '-2', '-3']
            for c in changes:
                uom = uom.replace(c, '{%s}' % c)
            uom = uom.replace('*', '~')
            # uom = '$%s$' % uom if usetex is True else uom
            cbarLabel = r'%s $%s$' % (descr, uom)

        RadialMap(self.core, tallies=tallies, z=z, time=t, pre=pre, gro=gro,
                  label=label,
                  figname=figname,
                  which=hex,
                  fren=True,
                  whichconf='NE',
                  asstype=False,
                  dictname=None,
                  legend=False,
                  txtcol='k',
                  fill=False,
                  axes=axes,
                  cmap=cmap,
                  thresh=thresh,
                  cbarLabel=cbarLabel,
                  xlabel=xlabel,
                  ylabel=ylabel,
                  loglog=log,
                  logx=False, 
                  logy=False,
                  title=title,
                  scale=scale, 
                  fmt=fmt,
                #   numbers=False, 
                  **kwargs)

    def whereMaxSpectralRad(self, path, core, plot=True):

        with open(os.path.join(path, 'outputNE.log'), 'r') as f:
            for l in f:
                if '@ D3DMATI: MAXVAL(SPECTRAL NORM)' in l:
                    # parse IK, IG
                    num = l.split('(IK,IG)= ')[1]
                    IK, IG = num.split()
                    IK, IG = int(IK), int(IG)
                else:
                    IK, IG = None, None
        nElz = len(self.core.NE.AxialConfig.AxNodes) if self.core.dim != 2 else 1
        myIK = 0
        nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss
        for iz in range(0, nElz):
            for ih in range(1, nhex+1):
                if myIK == IK:
                    # TODO parse each time config.
                    hexty = self.core.getassemblytype(ih, config=core.NE.config[0], isfren=True)
                    hexty = self.core.NE.assemblytypes[hexty]
                    z = self.core.NE.AxialConfig.AxNodes[iz]
                    print(f'Max spectral norm in {hexty} SAs at z={z} cm')
                myIK = myIK+1

    def _shift_index(self, gro, pre, t, z, times=None, particles="neutrons"):
        """Convert input parameters to lists of indexes for slicing.

        Parameters
        ----------
        gro : int or list
            Number of energy groups for neutrons.
        pre : int or list
            Number of precursors for neutrons.
        particles: string, optional
            The particle species analysed. It can be either "neutrons"
            or "photons".

        Returns
        -------
        list
            gro, pre converted in listed indexes
        """
        if gro is not None:
            # make input iterables
            if isinstance(gro, int):
                gro = [gro]
            gro = [g-1 for g in gro]
        else:
            if particles == "neutrons":
                ngmax = self.core.NE.nGro
            elif particles == "photons":
                ngmax = self.core.NE.nGrp
            gro = np.arange(0, ngmax).tolist()

        if pre is not None:
            if isinstance(pre, int):
                pre = [pre]
            pre = [p-1 for p in pre]
        else:
            if particles == "neutrons":
                npmax = self.core.NE.nPre
            elif particles == "photons":
                npmax = self.core.NE.nPrp
            pre = np.arange(0, npmax).tolist()

        nodes = self.core.NE.AxialConfig.AxNodes if self.core.dim != 2 else np.array([0])
        if z is not None:
            if isinstance(z, (list, np.ndarray)):
                idz = [np.argmin(abs(zi-nodes)) for zi in z]
            else:
                idz = [np.argmin(abs(z-nodes))]
        else:
            idz = np.arange(0, len(nodes)).tolist()

        if times is not None:
            if t is not None:
                if isinstance(t, (list, np.ndarray)):
                    idt = [np.argmin(abs(ti-times)) for ti in t]
                else:
                    idt = [np.argmin(abs(t-times))]
            else:
                idt = np.arange(0, len(times)).tolist()
        else:
            idt = [0]

        return gro, pre, idt, idz

    def _to_index(self, gro, grp, pre, prp, t, z):
        """Map full-array indexes to sliced array indexes.

        Parameters
        ----------
        gro : list
            Indeces of energy groups for neutrons.
        grp : list
            Indeces of energy groups for photons.
        pre : list
            Indeces of precursors for neutrons.
        prp : list
            Indeces of precursors for photons.
        Returns
        -------
        list
            igro, igrp, ipre, iprp, idt, iz converted in listed indexes
        """
        if t is not None:
            idt = np.arange(0, len(t))
        else:
            idt = None

        if z is not None:
            idz = np.arange(0, len(z))
        else:
            idz = None

        if gro is not None:
            igro = np.arange(0, len(gro))
        else:
            igro = None

        if grp is not None:
            igrp = np.arange(0, len(grp))
        else:
            igrp = None

        if pre is not None:
            ipre = np.arange(0, len(pre))
        else:
            ipre = None

        if prp is not None:
            iprp = np.arange(0, len(prp))
        else:
            iprp = None

        return igro, igrp, ipre, iprp, idt, idz

    def _build_label(self, s, dims, dim2plot, usrdict):
        """Build legend label.

        Parameters
        ----------
        s : list
            Slice for the np.array.
        dims : list
            List of dimensions.
        dim2plot : string
            Dimension to be plotted.
        usrdict : dict
            Dict mapping dimension name and lists.

        Returns
        -------
        str
            Label for the plot.
        """
        label_dict = {'Group': 'g', 'ngrp': 'g',
                      'pre': 'p', 'prp': 'p', 'iHexNode': 'n'}
        dim2plot_dict = {'iTime': 't', 'iAxNode': 'z'}
        uom = {'iTime': 's', 'iAxNode': 'cm'}

        if plt.rcParams['text.usetex']:
            equal = "$=$"
        else:
            equal = "="

        label = []
        for i, k in enumerate(dims):
            if self.core.dim == 1 and k == 'iHexNode':
                continue
            if k not in ['iTime', 'iAxNode']:
                txt = usrdict[k][s[i]]
                txt = rf"{label_dict[k]}{equal}{txt}"
                label.append(txt)
            else:
                if k != dim2plot:
                    txt = usrdict[k][s[i]]
                    txt = rf"{dim2plot_dict[k]}{equal}{txt} {uom[k]}"
                    label.append(txt)

        return str(", ".join(label))

    @staticmethod
    def _fill_deprec_vers_metadata(MapVersion, npre, ngro, nprp, ngrp):
            # fill group and precursors entries
            try:
                # --- family-wise beta_eff
                lst = MapVersion['data']['integralParameters']['intpar']
                lst_uom = MapVersion['metadata']['integralParameters']['uom']['intpar']
                idy = lst.index('betaeff(')

                for i in range(npre):
                    lst.insert(idy, f'betaeff({i+1})')
                    uom = lst_uom[idy]
                    lst_uom.insert(idy, uom)
                    idy += 1
                # remove dummy entry
                idy = lst.index('betaeff(')
                lst.remove('betaeff(')
                del lst_uom[idy]
                # --- group-wise source_eff
                lst = MapVersion['data']['integralParameters']['intsrc']
                lst_uom = MapVersion['metadata']['integralParameters']['uom']['intsrc']
                idy = lst.index('gro=')
                for i in range(1,ngro+1):
                    lst.insert(idy, f'gro={i}')
                    uom = lst_uom['intsrc'][idy]
                    lst_uom.insert(idy, uom)
                    idy += 1

                idy = lst.index('gro=')
                lst.remove('gro=')
                del lst_uom[idy]
                # --- precursors-wise precursors amplitude
                lst = MapVersion['data']['integralParameters']['intamp']
                lst_uom = MapVersion['metadata']['integralParameters']['uom']['intamp']
                idy = lst.index('ceff(')
                for i in range(1, npre+1):
                    lst.insert(idy, f'ceff({i})')
                    uom = lst_uom[idy]
                    lst_uom.insert(idy, uom)
                    idy += 1

                idy = lst.index('ceff(')
                lst.remove('ceff(')
                del lst_uom[idy]

                # --- photon precursors-wise gamma_eff
                lst = MapVersion['data']['integralParameters']['intpar']
                lst_uom = MapVersion['metadata']['integralParameters']['uom']['intpar']
                idy = lst.index('gammaeff(')

                for i in range(nprp):
                    lst.insert(idy, f'gammaeff({i+1})')
                    uom = lst_uom[idy]
                    lst_uom.insert(idy, uom)
                    idy += 1
                # remove dummy entry
                idy = lst.index('gammaeff(')
                lst.remove('gammaeff(')
                del lst_uom[idy]

                # --- photon group-wise source
                lst = MapVersion['data']['integralParameters']['intsrc']
                lst_uom = MapVersion['metadata']['integralParameters']['uom']['intsrc']
                idy = lst.index('grp=')
                for i in range(1,ngrp+1):
                    lst.insert(idy, f'grp={i}')
                    uom = lst_uom['intsrc'][idy]
                    lst_uom.insert(idy, uom)
                    idy += 1

                idy = lst.index('grp=')
                lst.remove('grp=')
                del lst_uom[idy]

                # --- photon precursors-wise amplitude
                lst = MapVersion['data']['integralParameters']['intamp']
                lst_uom = MapVersion['metadata']['integralParameters']['uom']['intamp']
                idy = lst.index('geff(')
                for i in range(1, nprp+1):
                    lst.insert(idy, f'geff({i})')
                    uom = lst_uom[idy]
                    lst_uom.insert(idy, uom)
                    idy += 1

                idy = lst.index('geff(')
                lst.remove('geff(')
                del lst_uom[idy]

                return MapVersion

            except ValueError:
                pass

    @staticmethod
    def fill_intpar_dict(MapVersion, npre, ngro, nprp, ngrp):
            # fill group and precursors entries
            # --- amplitude
            lst = MapVersion['amplitude']

            idx =  lst["neutrons"].index("c_eff_*")
            lst["neutrons"].remove("c_eff_*")
            for p in range(1,npre+1):
                lst["neutrons"].append(f"c_eff_{p:02d}")
                idx += 1

            idx =  lst["photons"].index("g_eff_*")
            lst["photons"].remove("g_eff_*")
            for p in range(1,nprp+1):
                lst["photons"].append(f"g_eff_{p:02d}")
                idx += 1

            # --- kinetics
            lst = MapVersion['kinetics']

            idx =  lst["neutrons"].index("beta_eff_*")
            lst["neutrons"].remove("beta_eff_*")
            for p in range(1,npre+1):
                lst["neutrons"].append(f"beta_eff_{p:02d}")
                idx += 1

            idx =  lst["photons"].index("gamma_eff_*")
            lst["photons"].remove("gamma_eff_*")
            for p in range(1,nprp+1):
                lst["photons"].append(f"gamma_eff_{p:02d}")
                idx += 1

            # --- source
            lst = MapVersion['source']
            idx =  lst["neutrons"].index("source g=*")
            lst["neutrons"].remove("source g=*")
            for p in range(1,npre+1):
                lst["neutrons"].append(f"source g={p:02d}")
                idx += 1

            idx =  lst["photons"].index("source g=*")
            lst["photons"].remove("source g=*")
            for p in range(1,nprp+1):
                lst["photons"].append(f"source g={p:02d}")
                idx += 1

            return MapVersion

    @staticmethod
    def __loadtxt(fname):
        """
        Load the parameters and their names as dict.

        Parameters
        ----------
        fname : string
            Parameters file name

        Returns
        -------
        pdict: dict
            Dict whose keys are the parameters and whose values are the
            parameter values
        """
        lines = open(fname).read().split('\n')  # read all lines (they are always two)
        # discard comment, discard first empty key, split parameters names
        keys = (re.split("% |, ", lines[0]))[1:]
        vals = lines[1].split(" ")  # split values with " " delimiter
        pdict = dict(zip(keys, vals))  # create output dict
        return pdict

    @staticmethod
    def __wopen(h5name, ans=None):
        """
        Open the hdf5 file "h5name.hdf5" in "append" mode.

        Parameters
        ----------
        h5name : string
            File name

        Returns
        -------
        h5f : object
            h5py object

        """
        if os.path.isfile(h5name):
            print("File exists. Overwriting?")

            if ans is None:
                ans = input()

            elif isinstance(ans, str) is False:
                raise TypeError('ans argument type must be string!')

        else:  # if file do not exist, it creates it
            ans = "create"

        if ans == "yes" or ans == "y":
            os.remove(h5name)
            # open file in append mode
            h5f = h5.File(h5name, "a")
            return h5f
        elif ans == "create":
            # create file in append mode
            h5f = h5.File(h5name, "a")
            return h5f
        else:  # if answer is not positive, nothing is done
            return -1

    @staticmethod
    def __checkname(fname):
        """
        Check extension of filename and add if it is missed.

        Parameters
        ----------
        fname : string
            Input filename (optional extension).

        Raises
        ------
        OSError
            -File extension is wrong. Only HDF5 can be parsed

        Returns
        -------
        fname : string
            Filename and proper extension.

        """
        lst = fname.split(".")

        if len(lst) == 1:
            # add extension
            fname = "%s.hdf5" % fname
        else:
            if lst[-1] != "hdf5":
                lst[-1] = "hdf5"
                fname = ".".join(lst)
                raise FileNotFoundError("File extension is wrong. Only HDF5 can be parsed")

        return fname

    @staticmethod
    def myh5open(NEpath, fname="output_NE.h5"):
        try:
            h5path = os.path.join(NEpath, fname)
            # back compatibility with v1 of FRENETIC 
            # (commit n.8aaa49a23fcc8ffc01077c2c58facb66fd9aae0c on FRENETIC development)
            if not os.path.exists(h5path) and fname == "output_NE.h5":
                h5path = os.path.join(NEpath, "output.h5")
            h5f = h5.File(h5path, "r")
        except OSError as err:
            if 'Unable to open file' in str(err):
                if not os.path.exists(h5path):
                    raise OSError(f"No output in directory {NEpath}")
                else:
                    raise NEOutputError(f"{str(err)}\n{h5path} is probably corrupted!")
            else:
                raise OSError(str(err))
        return h5f

    @staticmethod
    def get_output_version(NEpath, MapOutput):
        try:
            h5f = NEoutput.myh5open(NEpath)
            # check version attribute
            h5f_attrs = h5f.attrs.keys()
            if "output version" in h5f_attrs:
                version = h5f.attrs["output version"][0].decode()
            else:
                version = "1.0"
        except OSError as err:
            if 'Unable to open file' in str(err):
                # look for txt files (deprecated format)
                intparf = MapOutput["1.0"]["data"]["integralParameters"].keys()
                dostrf = MapOutput["1.0"]["data"]["distributions"]
                txt_files = distrf + intparf
                for f in txt_files:
                    datapath = os.path.join(NEpath, f"{f}.out")
                    if os.path.exists(datapath):
                        version = "0.0"
                        break
                if not os.path.exists(datapath):
                    if not os.path.exists(h5path):
                        raise NEOutputError(f"No output in directory {NEpath}")
                    else:
                        raise NEOutputError(f"{str(err)}\n{h5path} is probably corrupted!")
            else:
                raise NEOutputError(err)

        return version

    @staticmethod
    def get_duplicate_dset_names(mydict, keys=None):
        dupl = []
        if keys is None:
            keys = []

        for k, v in mydict.items():
            if isinstance(v, list):
                for l in v:
                    if l not in keys:
                        keys.append(l)
                    else:
                        dupl.append(l)
            elif isinstance(v, dict):
                dupl2 = NEoutput.get_duplicate_dset_names(v, keys=keys)
                dupl.extend(dupl2)

        return dupl

    @staticmethod
    def is_h5path_valid(h5f, group, version):
        path = "/".join([h5f.name, group])
        if path in h5f:
            return True
        else:
            raise NEOutputError(f"`{path}` not found in NE output v{version}!")

    @staticmethod
    def build_HDF5_path(out_tree):
        HDF5_path = []
        # key = "distributions"
        for key, val in out_tree.items():

            if key == "input_xs":
                continue

            if isinstance(val, list):
                tmp_lst = ["/".join([key, l]) for l in val]
                HDF5_path.extend(tmp_lst)

            elif isinstance(val, dict):

                for k, v in val.items():

                    if k == "time":
                        HDF5_path.append("/".join([key, k]))
                    elif isinstance(v, list):
                        tmp_lst = ["/".join([k, l]) for l in v]
                    elif isinstance(v, dict):
                        lst = NEoutput.build_HDF5_path(v)
                        tmp_lst = []
                        for l in lst:
                            tmp_lst.append("/".join([k, l]))
                    else:
                        raise NEOutputError(f"object of type {type(v)} cannot be handled!")

                    tmp_lst = ["/".join([key, l]) for l in tmp_lst]
                    HDF5_path.extend(tmp_lst)


            else:

                raise NEOutputError(f"object of type {type(v)} cannot be handled!")

        return HDF5_path

class NEOutputError(Exception):
    pass