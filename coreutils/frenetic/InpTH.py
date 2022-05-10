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
    # # generate filecool.dat
    # f = io.open('filecool.dat', 'w', newline='\n')
    # for nchan, chan in core.TH.CZassemblytypes.items():
    #     which = core.getassemblylist(nchan, core.TH.CZconfig[t], isfren=True)
    #     if which != []:
    #         # join assembly numbers in a single string
    #         which = [str(w) for w in which]
    #         which = ','.join(which)
    #         f.write("%s,\n" % which)

    # generate mdot.dat
    f = io.open('mdot.dat', 'w', newline='\n')
    f.write("%d," % len(core.TH.CZtime))
    for t in core.TH.CZtime:
        # loop over each assembly
        mflow = ["%s" % ff(t, 'double')]
        for n in core.Map.fren2serp.keys():
            # get mass flow rate
            whichtype = core.getassemblytype(n, core.TH.CZconfig[t], isfren=True)
            whichtype = core.TH.CZassemblytypes[whichtype]
            val = core.TH.CZMaterialData.massflowrates[whichtype]
            mflow.append("%s" % ff(val, 'double'))
        # write to file
        f.write("%s \n" % ",".join(mflow))

    # generate temp.dat
    f = io.open('temp.dat', 'w', newline='\n')
    f.write("%d," % len(core.TH.CZtime))
    for t in core.TH.CZtime:
        # loop over each assembly
        temp = ["%s" % ff(t, 'double')]
        for n in core.Map.fren2serp.keys():
            # get mass flow rate
            whichtype = core.getassemblytype(n, core.TH.config[t], isfren=True)
            whichtype = core.TH.CZassemblytypes[whichtype]
            val = core.TH.CZMaterialData.temperatures[whichtype]
            temp.append("%s" % ff(val, 'double'))
        # write to file
        f.write("%s \n" % ",".join(temp))

    # generate press.dat
    f = io.open('press.dat', 'w', newline='\n')
    f.write("%d," % len(core.TH.CZtime))
    for t in core.TH.CZtime:
        # loop over each assembly
        press = ["%s" % ff(t, 'double')]
        for n in core.Map.fren2serp.keys():
            # get mass flow rate
            whichtype = core.getassemblytype(n, core.TH.config[t], isfren=True)
            whichtype = core.TH.CZassemblytypes[whichtype]
            val = core.TH.CZMaterialData.pressures[whichtype]
            press.append("%s" % ff(val, 'double'))
        # write to file
        f.write("%s \n" % ",".join(press))


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
        for nt, t in enumerate(core.TH.time):
            which = core.getassemblylist(nchan, core.TH.config[t], isfren=True)
            # join assembly numbers in a single string
            which = [str(w) for w in which]
            which = ','.join(which)
            # --- print one file per each TH channel type
            newline = "IHA = %s, !int id number for HAs of this type" % which
            # open reference file
            if template is None:
                tmp = pkg_resources.read_text(templates, 'template_HA_01_01.dat')
                tmp = tmp.splitlines()
            else:
                with open(template, 'r') as f:
                    temp_contents = f.read()
                    tmp = temp_contents. splitlines()

            # open new file
            f = io.open('HA_%02d_%02d.dat' % (nchan, nt+1), 'w',
                        newline='\n')
            # loop over lines in reference file
            for line in tmp:
                if "IHA" in line:
                    line = line.replace(line, newline)
                # write to file
                f.write(line)
                f.write('\n')
