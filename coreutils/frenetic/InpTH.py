import io
import logging
import numpy as np
from shutil import rmtree
from coreutils.tools.utils import fortranformatter as ff
from coreutils.frenetic.frenetic_namelists import FreneticNamelist, FreneticNamelistError

logger = logging.getLogger(__name__)

def _unlink_if_exists(filepath):
    if filepath.exists():
        filepath.unlink()
        logger.warning(f'Overwriting file {filepath.name}')


def _write_table(filepath, rows):
    with io.open(filepath, 'w', newline='\n') as f:
        for row in rows:
            f.write(f'{ff(row)} \n')


def _active_length(core):
    # FIXME check if zPowEnd and zPowStart are defined in TH
    if hasattr(core.TH, "axstep"):
        return float(np.sum(core.TH.axstep))
    return float(core.TH.zmesh[1]-core.TH.zmesh[0])


def _axial_steps(core):
    if hasattr(core.TH, "axstep"):
        return np.asarray(core.TH.axstep, dtype=float)
    n_z = int(core.TH.nVol)
    return np.ones((n_z,))*_active_length(core)/n_z


def writePowerData(core, path):
    """
    Generate TH power input data.

    COREutils stores power in W. FRENETIC input is written as linear power
    in W/m where the selected HeatingType needs spatially distributed values.
    """
    if not hasattr(core.TH, "Power") or core.TH.Power is None:
        return

    power = core.TH.Power
    powerpath = path.joinpath("power.inp")
    _unlink_if_exists(powerpath)

    if power["mode"] == "channels":
        length = _active_length(core)
        values = power["values"]/length
        rows = [[len(power["time"])]]
        for it, t in enumerate(power["time"]):
            rows.append([t]+values[it, :].tolist())
        _write_table(powerpath, rows)

    elif power["mode"] == "shape":
        dz = _axial_steps(core)
        shape = power["shape_factors"]/power["shape_factors"].sum()
        shape = shape/dz[:, np.newaxis]

        shapepath = path.joinpath("shape_factors.txt")
        _unlink_if_exists(shapepath)
        _write_table(shapepath, shape.tolist())

        rows = [[len(power["time"])]]
        for t, amplitude in zip(power["time"], power["amplitude"]):
            rows.append([t, amplitude])
        _write_table(powerpath, rows)

    elif power["mode"] == "variable_shape":
        dz = _axial_steps(core)
        values = power["values"]/dz[np.newaxis, :, np.newaxis]
        n_rows = len(power["time"])*values.shape[1]
        rows = [[n_rows]]
        for it, t in enumerate(power["time"]):
            for iz in range(values.shape[1]):
                rows.append([t]+values[it, iz, :].tolist())
        _write_table(powerpath, rows)

    else:
        raise FreneticNamelistError(f'Unknown power mode {power["mode"]}!')


def writeBCdata(core, path):
    """
    Generate TH input data related to cooling zones.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    path: pathlib object
        Path to file

    Returns
    -------
    ``None``
    """
    input_files = {'mdot.inp': 'massflowrate', 
                   'tempinl.inp': 'temperature', 
                   'pressout.inp': 'pressure',
                   }
    for inpname in input_files.keys():
        what = input_files[inpname]
        # generate input .inp
        n_time = len(core.TH.BCs[what]["time"])
        
        filepath = path.joinpath(inpname)
        if filepath.exists():
            rmtree(filepath)
            logger.warning(f'Overwriting file {inpname}')

        f = io.open(filepath, 'w', newline='\n')


        f.write(f"{n_time}, \n")
        isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
        N = int(core.nAss / 6 * isSym + 1) if isSym else core.nAss
        values = core.TH.BCs[what]["values"]
        for it, t in enumerate(core.TH.BCs[what]["time"]):
            # loop over each assembly
            data = [t]
            data.extend(values[it, :].tolist())
            # write to file
            f.write(f'{ff(data)} \n')


def makeTHinput(core, path):
    """
    Make input.inp file.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object.
    path: pathlib object
        Path to file

    Returns
    -------
    ``None``
    """
    frnnml = FreneticNamelist()
    inpname = "input.inp"
    filepath = path.joinpath(inpname)
    if filepath.exists():
        rmtree(filepath)
        logger.warning(f'Overwriting file {inpname}')

    f = io.open(filepath, 'w', newline='\n')
    for namelist in frnnml.files["THinput.inp"]:
        f.write(f"&{namelist}\n")
        for key, val in core.FreneticNamelist[namelist].items():
            # format value with FortranFormatter utility
            is_iterable = True if isinstance(val, (np.ndarray, list)) else False
            val = ff(val)
            # "vectorise" in Fortran input if needed
            if key in frnnml.vector_inp and not is_iterable:
                isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
                N = int(core.nAss/6*isSym+1) if isSym else core.nAss
                val = f"{N}*{val}"
            f.write(f"{key} = {val}\n")
        # write to file
        f.write("/\n")


def writeHTdata(core, path):
    """
    Generate TH input data.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    path: pathlib object
        Path to file

    Returns
    -------
    ``None``
    """
    frnnml = FreneticNamelist()
    # FIXME this is a patch, in the future the user should choose these values
    nRadNode = core.FreneticNamelist["NUMERICS0"]["MaxNRadNode"]-2
    isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
    nr = [int(nRadNode*0.6), int(nRadNode*0.2), int(nRadNode*0.2)]
    N = int(core.nAss/6*isSym+1) if isSym else core.nAss
    for nType in core.TH.HTassemblytypes.keys():
        for nt, t in enumerate(core.TH.HTtime):
            # open new file
            inpname = f'HA_{nType:02d}_{nt+1:02d}.inp'
            filepath = path.joinpath(inpname)
            if filepath.exists():
                rmtree(filepath)
                logger.warning(f'Overwriting file {inpname}')

            f = io.open(filepath, 'w', newline='\n')

            for namelist in frnnml.files["THdatainput.inp"]:
                f.write(f"&{namelist}\n")
                for key, val in core.FreneticNamelist[f"HAType{nType}"][namelist].items():
                    # format value with FortranFormatter utility
                    if key in ['RadMatInd', 'RadHeatInd']:
                        val = ff(val, nr)
                    else:
                        val = ff(val)
                    # "vectorise" in Fortran input if needed
                    if key in frnnml.vector_inp.keys():
                        if frnnml.vector_inp[key] == "nAss":
                            isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
                            length = int(core.nAss/6*isSym+1) if isSym else core.nAss
                        elif frnnml.vector_inp[key] == "nSides":
                            length = 6
                        else:
                            raise OSError("Unknown dim {frnnml.vector_inp[key]}!")
                        val = f"{length}*{val}"
                    f.write(f"{key} = {val}\n")
                # write to file
                f.write("/\n")
