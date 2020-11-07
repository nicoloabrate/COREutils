"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import coreutils.frenetic.InpTH as InpTH


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
    # generate filecool.txt
    f = io.open('filecool.txt', 'w', newline='\n')
    for nchan, chan in core.CZassemblytypes.items():
        which = core.getassemblylist(nchan, flagfren=True,
                                     whichconf="CZconfig")
        if which != []:
            # join assembly numbers in a single string
            which = [str(w) for w in which]
            which = ','.join(which)
            f.write("%s,\n" % which)

    # generate mdot.txt
    f = io.open('mdot.txt', 'w', newline='\n')
    f.write("%d, \n" % len(core.CZtime))
    for t in core.CZtime:
        # loop over each assembly
        mflow = []
        for n in core.Map.fren2serp.keys():
            # get mass flow rate
            whichtype = core.getassemblytype(n, flagfren=True,
                                             whichconf="CZconfig")
            whichtype = core.CZassemblytypes[whichtype]
            val = core.CZMaterialData.massflowrates[whichtype]
            mflow.append("%.6e" % val)
        # write to file
        f.write("%s \n" % ",".join(mflow))

    # generate temp.dat
    f = io.open('temp.txt', 'w', newline='\n')
    f.write("%d, \n" % len(core.CZtime))
    for t in core.CZtime:
        # loop over each assembly
        temp = []
        for n in core.Map.fren2serp.keys():
            # get mass flow rate
            whichtype = core.getassemblytype(n, flagfren=True,
                                             whichconf="CZconfig")
            whichtype = core.CZassemblytypes[whichtype]
            val = core.CZMaterialData.temperatures[whichtype]
            temp.append("%.6e" % val)
        # write to file
        f.write("%s \n" % ",".join(temp))

    # generate press.dat
    f = io.open('press.txt', 'w', newline='\n')
    f.write("%d, \n" % len(core.CZtime))
    for t in core.CZtime:
        # loop over each assembly
        press = []
        for n in core.Map.fren2serp.keys():
            # get mass flow rate
            whichtype = core.getassemblytype(n, flagfren=True,
                                             whichconf="CZconfig")
            whichtype = core.CZassemblytypes[whichtype]
            val = core.CZMaterialData.pressures[whichtype]
            press.append("%.6e" % val)
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

    geomdata = {'$NHEX': core.NAss}

    if template is None:
        path = os.path.abspath(InpTH.__file__)
        path = os.path.join(path.split("InpTH.py")[0], "template_THinput.dat")
    else:
        path = template

    with open(path) as tmp:  # open reference file
        f = io.open("input.dat", 'w', newline='\n')
        # with open() as f:  # open new file
        for line in tmp:  # loop over lines in reference file
            for key, val in geomdata.items():  # loop over dict keys
                if key in line:
                    line = line.replace(key, str(val))
            # write to file
            f.write(line)


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
    if template is None:
        path = os.path.abspath(InpTH.__file__)
        path = os.path.join(path.split("InpTH.py")[0], "template_HA_01_01.dat")
    else:
        path = template

    for nchan, chan in core.THassemblytypes.items():
        # loop over time
        for nt, t in enumerate(core.THtime):
            which = core.getassemblylist(nchan, time=t, flagfren=True,
                                         whichconf="THconfig")
            # join assembly numbers in a single string
            which = [str(w) for w in which]
            which = ','.join(which)
            # --- print one file per each TH channel type
            newline = "IHA = %s, !int id number for HAs of this type" % which
            # open reference file
            with open(path) as tmp:
                # open new file
                f = io.open('HA_%02d_%02d.dat' % (nchan, nt+1), 'w',
                            newline='\n')
                # loop over lines in reference file
                for line in tmp:
                    if "IHA" in line:
                        line = line.replace(line, newline)
                    # write to file
                    f.write(line)
