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
from coreutils.tools.utils import MyDict, write_coreutils_msg
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import HTHexData
from coreutils.core.Geometry import Geometry, AxialConfig, AxialCuts
from coreutils.input.TH_input import *

logger = logging.getLogger(__name__)

n_digits_max = 14

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
        write_coreutils_msg(f"Set TH boundary conditions")

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
        write_coreutils_msg(f"Define time-dependent TH configurations and boundary conditions")

        configurations = {'HTconfig': HTconfig, 'BCconfig': BCconfig}
        for name, config in configurations.items():
            configtype = name.split('config')[0]
            if config is not None:
                for time in config.keys():

                    if "." in time:
                        n_digits = len(time.split(".")[1])
                        if n_digits > n_digits_max:
                            raise THError(f"Time {time} [s] has > {n_digits_max} digits after the decimal point! ")

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
        self.plot['SAcolors_BC'] = THargs["sacolors_bc"]
        self.plot['SAcolors_TH'] = THargs["sacolors_th"]
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

        self.Power = None
        if THargs.get("power") is not None:
            self.setPower(CI, THargs["power"])

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
                raise OSError(f"SA {SAtype} not defined in {configtype} config! Replacement cannot be performed!")
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

    def setPower(self, core, inp):
        """
        Define channel-wise or 3D TH power profiles.

        Internal values are stored in W. Conversion to FRENETIC linear power
        input is performed only when writing the TH files.
        """
        try:
            power = power_obj(**inp)
        except ValidationError as e:
            print("ValidationError. Check the .json input file!")
            raise THError(e.errors())

        mode = self._canonical_power_mode(power.mode)
        if mode == "channels":
            self.Power = self._build_channel_power(core, power)
        elif mode == "shape":
            self.Power = self._build_shape_power(core, power)
        elif mode == "variable_shape":
            self.Power = self._build_variable_shape_power(core, power)
        else:
            raise THError(f"Unknown power mode {power.mode}!")

    @staticmethod
    def _canonical_power_mode(mode):
        mode = mode.casefold().replace("-", "_")
        if mode in ["shape_time"]:
            return "variable_shape"
        return mode

    @staticmethod
    def _read_numeric_table(filepath, drop_count_header=True):
        filepath = Path(filepath).expanduser().resolve()
        rows = []
        try:
            with open(filepath) as f:
                for line in f:
                    line = line.split("#", 1)[0].strip()
                    if not line:
                        continue
                    raw = line.replace(",", " ").split()
                    rows.append([float(s.replace("d", "e").replace("D", "e")) for s in raw])
        except FileNotFoundError:
            raise THError(f"Power input file {filepath} not found!")

        if not rows:
            raise THError(f"Power input file {filepath} is empty!")

        if drop_count_header and len(rows[0]) == 1 and len(rows) > 1:
            n_rows = int(rows[0][0])
            if np.isclose(rows[0][0], n_rows) and n_rows == len(rows)-1:
                rows = rows[1:]

        n_cols = len(rows[0])
        if any(len(row) != n_cols for row in rows):
            raise THError(f"Inconsistent number of columns in {filepath}!")

        return np.asarray(rows, dtype=float)

    @staticmethod
    def _check_increasing_time(times, what):
        if len(times) > 1 and np.any(np.diff(times) <= 0):
            raise THError(f"Time values in {what} should be strictly increasing!")

    @staticmethod
    def _parse_power_func(func):
        def parse_profile(profile):
            if isinstance(profile, dict):
                profile = [profile]
            if not isinstance(profile, list) or len(profile) == 0:
                raise THError("Power func should be a non-empty list!")

            times = []
            values = []
            for point in profile:
                if not isinstance(point, dict) or len(point) != 1:
                    raise THError("Each power func entry should contain exactly one shape!")
                shape, data = next(iter(point.items()))
                if shape not in ["step", "linear"]:
                    raise THError(f"{shape} type not implemented for power!")
                try:
                    data = func_power(**data)
                except ValidationError as e:
                    raise THError(e.errors())
                times.append(data.time)
                values.append(data.value)

            times = np.asarray(times, dtype=float)
            values = np.asarray(values, dtype=float)
            TH._check_increasing_time(times, "power func")
            return times, values

        if isinstance(func, dict):
            return [parse_profile(func)]
        if not isinstance(func, list) or len(func) == 0:
            raise THError("Power func should be a non-empty list!")
        if all(isinstance(item, list) for item in func):
            return [parse_profile(profile) for profile in func]
        if all(isinstance(item, dict) for item in func):
            return [parse_profile(func)]
        raise THError("Power func should be a profile or a list of profiles!")

    def _load_power_profile(self, filepath):
        table = self._read_numeric_table(filepath)
        if table.shape[1] != 2:
            raise THError(f"Power profile file {filepath} should have two columns: time and value!")
        times = table[:, 0]
        values = table[:, 1]
        self._check_increasing_time(times, filepath)
        return times, values

    def _group_power_profiles(self, power, n_groups):
        if power.func is not None:
            profiles = self._parse_power_func(power.func)
        elif isinstance(power.filepath, list):
            if len(power.filepath) == 1:
                profiles = [self._load_power_profile(power.filepath[0])]
            elif len(power.filepath) == n_groups:
                profiles = [self._load_power_profile(filepath) for filepath in power.filepath]
            else:
                raise THError("Length of which and filepath is not consistent!")
        elif isinstance(power.filepath, str):
            profiles = [self._load_power_profile(power.filepath)]
        else:
            raise THError("Power mode requires func or filepath!")

        if len(profiles) == 1:
            profiles = profiles*n_groups
        elif len(profiles) != n_groups:
            raise THError("Length of which and power profiles is not consistent!")

        times0 = profiles[0][0]
        for times, _ in profiles[1:]:
            if times.shape != times0.shape or not np.allclose(times, times0):
                raise THError("All grouped power profiles should use the same time grid!")
        return profiles

    def _build_channel_power(self, core, power):
        n_ass = core.nAss
        if power.which is None:
            table = self._read_numeric_table(power.filepath)
            if table.shape[1] != n_ass+1:
                raise THError(f"channels power filepath should have {n_ass+1} columns: time plus nAss values!")
            times = table[:, 0]
            values = table[:, 1:]
            self._check_increasing_time(times, power.filepath)
        else:
            groups = power.which
            profiles = self._group_power_profiles(power, len(groups))
            times = profiles[0][0]
            values = np.zeros((len(times), n_ass))
            for channels, (_, profile_values) in zip(groups, profiles):
                for channel in channels:
                    if channel > n_ass:
                        raise THError(f"Channel {channel} exceeds nAss={n_ass}!")
                    values[:, channel-1] = profile_values

        if np.any(values < 0):
            raise THError("Power values should be non-negative!")

        return {
                "mode": "channels",
                "heatingtype": -1,
                "time": times,
                "values": values,
               }

    def _power_axial_nodes(self):
        if hasattr(self, "axstep"):
            return len(self.axstep)
        if hasattr(self, "nVol"):
            return self.nVol
        raise THError("Power shape modes require TH nelems and zmesh!")

    def _build_shape_power(self, core, power):
        n_ass = core.nAss
        n_z = self._power_axial_nodes()
        shape_path = power.shape_factor if power.shape_factor is not None else power.shape_factors
        shape = self._read_numeric_table(shape_path, drop_count_header=False)

        if shape.shape != (n_z, n_ass):
            msg = (f"shape_factors file should have nZ x nAss = {n_z} x {n_ass} values, "
                   f"got {shape.shape[0]} x {shape.shape[1]}!")
            raise THError(msg)
        if np.any(shape < 0):
            raise THError("shape_factors values should be non-negative!")
        if np.isclose(shape.sum(), 0.0):
            raise THError("shape_factors sum should be positive!")

        if power.func is not None:
            profiles = self._parse_power_func(power.func)
            if len(profiles) != 1:
                raise THError("shape power mode accepts one total-power profile A(t)!")
            times, amplitude = profiles[0]
        else:
            times, amplitude = self._load_power_profile(power.filepath)

        return {
                "mode": "shape",
                "heatingtype": 1,
                "time": times,
                "amplitude": amplitude,
                "shape_factors": shape,
               }

    def _build_variable_shape_power(self, core, power):
        n_ass = core.nAss
        n_z = self._power_axial_nodes()
        table = self._read_numeric_table(power.filepath)

        if table.shape[1] == n_ass*n_z+1:
            times = table[:, 0]
            self._check_increasing_time(times, power.filepath)
            values = table[:, 1:].reshape((table.shape[0], n_z, n_ass))
        elif table.shape[1] == n_ass+1:
            if table.shape[0] % n_z != 0:
                raise THError(f"variable 3D power file rows should be a multiple of nZ={n_z}!")
            n_times = table.shape[0]//n_z
            times = np.zeros((n_times,))
            values = np.zeros((n_times, n_z, n_ass))
            for it in range(n_times):
                block = table[it*n_z:(it+1)*n_z, :]
                if not np.allclose(block[:, 0], block[0, 0]):
                    raise THError("HeatingType=2 expects the same time repeated once for each axial slice!")
                times[it] = block[0, 0]
                values[it, :, :] = block[:, 1:]
            self._check_increasing_time(times, power.filepath)
        else:
            msg = (f"variable 3D power file should have either {n_ass*n_z+1} columns "
                   f"(compact) or {n_ass+1} columns (one row per axial slice)!")
            raise THError(msg)

        if np.any(values < 0):
            raise THError("Power values should be non-negative!")

        return {
                "mode": "variable_shape",
                "heatingtype": 2,
                "time": times,
                "values": values,
               }

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

            if p.func is not None:
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
            elif p.filepath is not None:
                raise THError("filepath in perturbBCs is validated but not implemented yet!")

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
