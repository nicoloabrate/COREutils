"""
Author: N. Abrate.

File: InpGen.py

Description: Set of methods for generating FRENETIC input files.

"""

import os
from shutil import rmtree
from os.path import isfile, join
import numpy as np
import serpentTools as st
import h5py as h5
import coreutils.frenetic.InpTH as inpTH


def inpgen(core):

    # common_input.dat
    makecommoninput(core)
    # make directories neutronic, coolant, data


    # make NE input

    # make TH input
    if 'THconfig' in core.__dict__.keys():
        inpTH.writeTHdata(core)

    if 'CZconfig' in core.__dict__.keys():
        inpTH.writeCZdata(core)
    # generate case directory-tree

    # move files


def makecommoninput(core):
    """
    Make common_input.dat file.

    Parameters
    ----------
    core : obj
        Core object created with Core class.

    Returns
    -------
    ``None``
    """
    # parse number of hexagons per row
    NL = np.count_nonzero(core.Map.inp, axis=1)
    NL = NL[NL != 0]
    # parse number of rows
    NR = len(NL)
    # flip to be consistent with FRENETIC numeration
    if NL[0] < NL[-1]:
        NL = np.flipud(NL)
    # convert in strings
    NL = [str(i) for i in NL]
    # join strings
    NL = ','.join(NL)

    geomdata = {'$NH': core.NAss, '$NR': NR, '$NL': NL,
                '$NDIFF': len(core.THassemblytypes)}

    path = os.path.abspath(inpTH.__file__)
    path = os.path.join(path.split("InpTH.py")[0], "template_common_input.dat")

    with open(path) as tmp:  # open reference file
        with open("common_input.dat", 'w') as f:  # open new file
            for line in tmp:  # loop over lines in reference file
                for key, val in geomdata.items():  # loop over dict keys
                    if key in line:
                        line = line.replace(key, str(val))
                # write to file
                f.write(line)
