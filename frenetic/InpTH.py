"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
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
    with open("filecool.txt", 'w') as f:
        for nchan, chan in core.CZassemblytypes.items():
            which = core.getassemblylist(nchan, flagfren=True,
                                         whichconf="CZconfig")
            if which != []:
                # join assembly numbers in a single string
                which = [str(w) for w in which]
                which = ','.join(which)
                f.write("%s,\n" % which)

    # generate mdot.txt
    with open("mdot.txt", 'w') as f:
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
    with open("temp.txt", 'w') as f:
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
    with open("press.txt", 'w') as f:
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


def writeTHdata(core):
    """
    Generate TH input data. User is supposed to complete them manually.

    Parameters
    ----------
    core : obj
        Core object created with Core class.

    Returns
    -------
    ``None``
    """
    path = os.path.abspath(InpTH.__file__)
    path = os.path.join(path.split("InpTH.py")[0], "template_HA_01_01.dat")

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
                with open("HA_%02d_%02d.dat" % (nchan, nt+1), 'w') as f:
                    # loop over lines in reference file
                    for line in tmp:
                        if "IHA" in line:
                            line = line.replace(line, newline)
                        # write to file
                        f.write(line)
