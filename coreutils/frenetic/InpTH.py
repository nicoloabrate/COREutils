"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
from . import templates
from coreutils.tools.utils import fortranformatter as ff
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


def writeCZdata(core):
    """
    Generate TH input data related to cooling zones.

    Parameters
    ----------
    core : obj
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
            data = [f"{t:.8e}"]
            for n in core.Map.fren2serp.keys():
                # get data in assembly
                whichtype = core.getassemblytype(n, core.TH.CZconfig[t], isfren=True)
                whichtype = core.TH.CZassemblytypes[whichtype]
                val = core.TH.CZMaterialData.__dict__[input_files[inp]][whichtype]
                data.append(f"{val:1.8e}")
            # write to file
            f.write(f'{",".join(data)} \n')

def makeTHinput(core, template=None):
    """
    Make input.dat file.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    template : str, optional
        File path where the template file is located. Default is ``None``.
        In this case, the default template is used.

    Returns
    -------
    ``None``
    """
    geomdata = {'$NHEX': core.NAss, '$NPROF': len(core.TimeSnap),
                '$TPROF': core.TimeSnap}

    if template is None:
        tmp = pkg_resources.read_text(templates, 'template_THinput.dat')
        tmp = tmp.splitlines()
    else:
        with open(template, 'r') as f:
            temp_contents = f.read()
            tmp = temp_contents. splitlines()

    f = io.open("input.dat", 'w', newline='\n')

    for line in tmp:  # loop over lines in reference file
        for key, val in geomdata.items():  # loop over dict keys
            if key in line:
                if key == '$TPROF':
                    tProf = [ff(t, 'double') for t in val]
                    val = ','.join(tProf)
                else:
                    val = str(val)
                line = line.replace(key, val)
        # write to file
        f.write(line)
        f.write('\n')


def writeTHdata(core, template=None):
    """
    Generate TH input data. User is supposed to complete them manually.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    template : str, optional
        File path where the template file is located. Default is ``None``.
        In this case, the default template is used.

    Returns
    -------
    ``None``
    """
    for nchan, chan in core.TH.THassemblytypes.items():
        # loop over time
        for nt, t in enumerate(core.TH.THtime):
            which = core.getassemblylist(nchan, core.TH.THconfig[t], isfren=True)
            # join assembly numbers in a single string
            which = [str(w) for w in which]
            which = ','.join(which)
            # --- print one file per each TH channel type
            newline = f"IHA = {which}, !int id number for HAs of this type"
            # open reference file
            if template is None:
                tmp = pkg_resources.read_text(templates, 'template_HA_01_01.dat')
                tmp = tmp.splitlines()
            else:
                with open(template, 'r') as f:
                    temp_contents = f.read()
                    tmp = temp_contents. splitlines()

            # open new file
            f = io.open(f'HA_{nchan:02d}_{nt+1:02d}.dat', 'w', newline='\n')
            # loop over lines in reference file
            for line in tmp:
                if "IHA" in line:
                    line = line.replace(line, newline)
                # write to file
                f.write(line)
                f.write('\n')
