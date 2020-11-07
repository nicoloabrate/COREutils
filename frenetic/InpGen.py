"""
Author: N. Abrate.

File: InpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import warnings
import numpy as np
from shutil import move
from os.path import join
import coreutils.frenetic.InpTH as inpTH
import coreutils.frenetic.InpNE as inpNE


def inpgen(core, casename=None):
    """
    Make FRENETIC NE/TH files if the required data are in core object.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    casename : str, optional
        File path where the case directory is located. Default is ``None``.
        In this case, the name of the FRENETIC case is 'case1'.

    Returns
    -------
    ``None``
    """
    # generate case directory-tree
    if casename is None:
        casename = join(os.getcwd(), 'case1')

    casepath = mkdir(casename)
    pwd = os.path.abspath(inpTH.__file__)
    pwd = pwd.split("InpTH.py")[0]
    # make common input (common_input.dat)
    makecommoninput(core)
    # move common_input
    move('common_input.dat', casepath)

    # make NE input (config.dat, macro.nml)
    if 'NEconfig' in core.__dict__.keys():
        NEpath = mkdir("NE", casepath)
        # define number of axial cuts
        nFreAxReg = len(core.NEAxialConfig.mycuts)-1
        nAssTypes = len(core.NEAxialConfig.cuts)
        # define nmix (number of different regions)
        nmix = nFreAxReg*nAssTypes

        # --- write config.inp
        inpNE.writeConfig(core, nFreAxReg, nAssTypes)

        # --- write input.dat
        inpNE.makeNEinput(core)

        # move NE files
        NEfiles = ['input.dat', 'config.inp']
        [move(f, NEpath) for f in NEfiles]
    else:
        warnings.warn('input.dat and config.inp not written!')

    # write NE data
    if 'NEMaterialData' in core.__dict__.keys():
        NEpath = mkdir("NE", casepath)
        # -- prepare data
        # get temperatures couples
        temp = core.NEMaterialData.temp
        # get NG
        unifuel = None

        # FIXME: ask boss how to deal with it
        # reference temperatures defined as minima
        mincouple = min(temp, key=lambda t: (t[1]+t[0]))
        Tf, Tc = mincouple
        for res in core.NEMaterialData.data[temp[0]]:
            for k in res.universes.keys():
                NG = res.universes[k]._numGroups
                if res.universes[k].infExp['infNubar'][0] > 0:
                    unifuel = k
                    break

            if unifuel is not None:
                break

        # --- get decay constants and physical delayed fractions
        # 0th position is total lambda
        lambda0 = res.resdata['fwdAnaLambda'][2::2]  # ::2 to avoid rel std
        beta0 = res.resdata['fwdAnaBetaZero'][2::2]  # ::2 to avoid rel std
        # get number of precursors
        NP = int(len(lambda0))

        # --- define univ dict to map where a certain universe is stored
        unimap = {}
        # loop over all files
        for nf, res in enumerate(core.NEMaterialData.data[temp[0]]):
            # loop over all universe inside each file
            for k in res.universes.keys():
                unimap[k[0]] = nf

        # FIXME: homogenise over whole reactor?
        if unifuel is not None:
            vel = 1/res.universes[unifuel].infExp['infInvv']
        else:
            raise OSError("Fuel (fissile) region missing in universe list!")

        # --- write macro.nml
        inpNE.writemacro(core, nmix, NG, NP, vel, lambda0, beta0, nFreAxReg,
                         (Tf, Tc), unimap)

        # -- write NE_data.h5
        inpNE.writeNEdata(core, NG, unimap, verbose=False,
                          inf=True, asciifmt=False, homogenise=True)
        # move NE files
        NEfiles = ['macro.nml', 'NE_data.h5']
        [move(f, NEpath) for f in NEfiles]

    else:
        warnings.warn('macro.nml and NE_data.h5 not written!')

    # make TH input (HA_*_*.txt)
    if 'THconfig' in core.__dict__.keys():
        THpath = mkdir("TH", casepath)
        THdatapath = mkdir("data", THpath)
        inpTH.writeTHdata(core)
        # move TH data files
        pwd = os.getcwd()
        for f in os.listdir(pwd):
            if f.startswith("HA"):
                move(f, THdatapath)
    else:
        warnings.warn('HA_xx_xx.dat not written, data dir not created!')

    # make CZ input (mdot.txt, temp.txt, press.txt, filecool.txt)
    if 'CZconfig' in core.__dict__.keys():
        THpath = mkdir("TH", casepath)
        # write CZ .txt data
        inpTH.writeCZdata(core)
        # write input.dat
        inpTH.makeTHinput(core)
        # move TH files
        THfiles = ['mdot.txt', 'press.txt', 'temp.txt', 'input.dat',
                   'filecool.txt']
        [move(f, THpath) for f in THfiles]
    else:
        warnings.warn('mdot.txt, press.txt, temp.txt, input.dat not written!')


def makecommoninput(core, template=None):
    """
    Make common_input.dat file.

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

    if template is None:
        path = os.path.abspath(inpTH.__file__)
        path = os.path.join(path.split("InpTH.py")[0],
                            "template_common_input.dat")
    else:
        path = template

    with open(path) as tmp:  # open reference file
        f = io.open('common_input.dat', 'w', newline='\n')
        for line in tmp:  # loop over lines in reference file
            for key, val in geomdata.items():  # loop over dict keys
                if key in line:
                    line = line.replace(key, str(val))
            # write to file
            f.write(line)


def mkdir(dirname, indirs=None):
    """
    Make a new directory named dirname inside path.

    Parameters
    ----------
    dirname : string
        directory name
    indirs : list, optional
        List of directories where the new directory is created. Default is
        ``None``

    Returns
    -------
    path : str
        Path of created directory
    """
    if indirs is None:
        path = dirname
    else:
        if isinstance(indirs, list) is False:
            indirs = [indirs]
        for i, p in enumerate(indirs):
            if i == 0:
                path = p
            else:
                path = join(path, p)
        path = join(path, dirname)

    os.makedirs((path), exist_ok=True)

    return path
