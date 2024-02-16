import io
import numpy as np
from coreutils.tools.utils import fortranformatter as ff
from coreutils.frenetic.frenetic_namelists import FreneticNamelist, FreneticNamelistError


def writeBCdata(core):
    """
    Generate TH input data related to cooling zones.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.

    Returns
    -------
    ``None``
    """
    input_files = {'mdot.inp': 'massflowrate', 
                   'tempinl.inp': 'temperature', 
                   'pressout.inp': 'pressure',
                   }
    for inp in input_files.keys():
        what = input_files[inp]
        # generate input .inp
        f = io.open(inp, 'w', newline='\n')
        f.write(f"{len(core.TH.BCs[what]["time"])}, \n")
        isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
        N = int(core.nAss/6*isSym+1) if isSym else core.nAss
        values = core.TH.BCs[what]["values"]
        for it, t in enumerate(core.TH.BCs[what]["time"]):
            # loop over each assembly
            data = [t]
            data.extend(values[it, :].tolist())
            # write to file
            f.write(f'{ff(data)} \n')


def makeTHinput(core):
    """
    Make input.inp file.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object.

    Returns
    -------
    ``None``
    """
    frnnml = FreneticNamelist()
    f = io.open("input.inp", 'w', newline='\n')
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


def writeHTdata(core):
    """
    Generate TH input data.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.

    Returns
    -------
    ``None``
    """
    frnnml = FreneticNamelist()
    # FIXME this is a patch, in the future the user should choose these values
    nRadNode = core.FreneticNamelist["ADDTH"]["MaxNRadNode"]-2
    isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
    nr = [int(nRadNode*0.6), int(nRadNode*0.2), int(nRadNode*0.2)]
    N = int(core.nAss/6*isSym+1) if isSym else core.nAss
    for nType in core.TH.HTassemblytypes.keys():
        for nt, t in enumerate(core.TH.HTtime):
            # open new file
            f = io.open(f'HA_{nType:02d}_{nt+1:02d}.inp', 'w', newline='\n')
            for namelist in frnnml.files["THdatainput.inp"]:
                f.write(f"&{namelist}\n")
                for key, val in core.FreneticNamelist[f"HAType{nType}"][namelist].items():
                    # format value with FortranFormatter utility
                    if key in ['MaterHX', 'HeatGhX']:
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


