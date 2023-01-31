import io
from . import templates
from coreutils.tools.utils import fortranformatter as ff
from coreutils.frenetic.frenetic_namelists import FreneticNamelist, FreneticNamelistError


def writeCZdata(core):
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
    input_files = {'mdot.dat': 'massflowrates', 
                   'temp.dat': 'temperatures', 
                   'press.dat': 'pressures'}
    for inp in input_files.keys():
        # generate input .dat
        f = io.open(inp, 'w', newline='\n')
        f.write(f"{len(core.TH.CZtime)},")
        for t in core.TH.CZtime:
            # loop over each assembly
            data = [t]
            for n in core.Map.fren2serp.keys():
                # get data in assembly
                whichtype = core.getassemblytype(n, core.TH.CZconfig[t], isfren=True)
                whichtype = core.TH.CZassemblytypes[whichtype]
                val = core.TH.CZData.__dict__[input_files[inp]][whichtype]
                data.append(val)
            # write to file
            f.write(f'{ff(data)} \n')


def makeTHinput(core):
    """
    Make input.dat file.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object.

    Returns
    -------
    ``None``
    """
    frnnml = FreneticNamelist()
    f = io.open("input.dat", 'w', newline='\n')
    for namelist in frnnml.files["THinput.dat"]:
        f.write(f"&{namelist}\n")
        for key, val in core.FreneticNamelist[namelist].items():
            # format value with FortranFormatter utility
            val = ff(val)
            # "vectorise" in Fortran input if needed
            if key in frnnml.vector_inp:
                val = f"{core.nAss}*{val}"
            f.write(f"{key} = {val}\n")
        # write to file
        f.write("/\n")


def writeTHdata(core):
    """
    Generate TH input data. User is supposed to complete them manually.

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
    nr = [int(nRadNode*0.6), int(nRadNode*0.2), int(nRadNode*0.2)]
    for nType in core.TH.THassemblytypes.keys():
        for nt, t in enumerate(core.TH.THtime):
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
                            length = core.nAss
                        elif frnnml.vector_inp[key] == "nSides":
                            length = 6
                        else:
                            raise OSError("Unknown dim {frnnml.vector_inp[key]}!")
                        val = f"{length}*{val}"
                    f.write(f"{key} = {val}\n")
                # write to file
                f.write("/\n")


