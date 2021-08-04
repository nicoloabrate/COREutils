"""
Author: N. Abrate.

File: InpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import warnings
import numpy as np
from shutil import move, copyfile, SameFileError
from os.path import join
from . import templates
from coreutils.tools.utils import fortranformatter as ff
from .InpTH import writeTHdata, writeCZdata, makeTHinput
from .InpNE import writeConfig, makeNEinput, writemacro, writeNEdata
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


def inpgen(core, json, casename=None, templates=None, txtfmt=False):
    """
    Make FRENETIC NE/TH files if the required data are in core object.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    json : str
        Name of the ``.json`` input file.
    casename : str, optional
        File path where the case directory is located. Default is ``None``.
        In this case, the name of the FRENETIC case is 'case1'.
    templates : dict, optional
        File path where the template files are located. Default is ``None``.
        In this case, the default template is used.
    txtfmt : bool, optional
        Set ``True`` to print NE data also in txt format. Default is ``False``.

    Returns
    -------
    ``None``
    """
    # generate case directory-tree
    cwd = os.getcwd()
    if casename is None:
        casename = join(cwd, 'case1')

    if '.json' not in json:
        json = "%s.json" % json

    casepath = mkdir(casename)
    try:
        copyfile('%s' % json, join(casepath, '%s' % json))
    except SameFileError:
        os.remove(join(casepath, '%s' % json))
        print('Overwriting file {}'.format(json))
        copyfile('%s' % json, join(casepath, '%s' % json))

    templateTH, templateCZ, templateCI, templateNE = None, None, None, None
    if isinstance(templates, dict):
        if 'TH' in templates.keys():
            templateTH = templates['TH']

        if 'CZ' in templates.keys():
            templateCZ = templates['CZ']

        if 'NE' in templates.keys():
            templateNE = templates['NE']

        if 'CI' in templates.keys():
            templateCI = templates['CI']

    # make common input (common_input.dat)
    makecommoninput(core, templateCI)
    # move common_input
    try:
        move('common_input.dat', join(casepath, 'common_input.dat'))
    except SameFileError:
        os.remove(join(casepath, 'common_input.dat'))
        print('Overwriting file {}'.format(json))
        move('common_input.dat', join(casepath, 'common_input.dat'))
    # make NE input (config.dat, macro.nml)
    NE = True
    if 'config' in core.__dict__.keys():
        NE_1D = True
        tlast = max(core.config.keys())
    elif 'NEconfig' in core.__dict__.keys():
        NE_1D = False
    else:
        NE = False

    if NE:
        NEpath = mkdir("neutronic", casepath)
        # define number of axial cuts
        nFreAxReg = core.config[0].nLayers if NE_1D else len(core.NEAxialConfig.mycuts)-1
        nAssTypes = 1 if NE_1D else len(core.NEAxialConfig.cuts)  # len(core.config[tlast].regions)
        # define nmix (number of different regions)
        nmix = len(core.config[tlast].regions) if NE_1D else nFreAxReg*nAssTypes

        # --- write config.inp
        writeConfig(core, nFreAxReg, nAssTypes, NE_1D=NE_1D)

        # --- write input.dat
        makeNEinput(core, templateNE)

        # move NE files
        NEfiles = ['input.dat', 'config.inp']
        for f in NEfiles:
            try:
                move(f, join(NEpath, f))
            except SameFileError:
                os.remove(join(NEpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(NEpath, f))
    else:
        warnings.warn('input.dat and config.inp not written!')

    # write NE data
    if 'NEMaterialData' in core.__dict__.keys() or NE_1D:
        NEpath = mkdir("neutronic", casepath)
        # -- prepare data
        # get temperatures couples
        temp = [(300, 300)] if NE_1D else core.NEMaterialData.temp
        # get NG
        unifuel = None

        # FIXME: ask boss how to deal with it
        # reference temperatures defined as minima
        mincouple = min(temp, key=lambda t: (t[1]+t[0]))
        Tf, Tc = mincouple
        if NE_1D:
            regs = core.config[0].regionmap
            vel = 1/core.config[0].regions[regs[0]].Invv
            NG = len(vel)
            beta0 = core.config[0].regions[regs[0]].beta
            lambda0 = core.config[0].regions[regs[0]].__dict__['lambda']
            NP = core.config[0].regions[regs[0]].NPF#
            unimap = dict(zip(core.config[0].regions.keys(), range(len(core.config[0].regions))))
        else:
            for res in core.NEMaterialData.data[temp[0]]:
                for k in res.universes.keys():
                    NG = res.universes[k]._numGroups
                    if NG is None:  # workaround for serpentTools when _numGroups is None
                        NG = res.universes[k].infExp['infInvv'].shape[0]
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
        writemacro(core, nmix, NG, NP, vel, lambda0, beta0, nFreAxReg,
                   (Tf, Tc), unimap, NE_1D=NE_1D)

        # -- write NE_data.h5
        writeNEdata(core, NG, unimap, verbose=False, inf=True, txtfmt=txtfmt,
                    NE_1D=NE_1D)
        # move NE files
        NEfiles = ['macro.nml', 'NE_data.h5'] # 
        for f in NEfiles:
            try:
                move(f, join(NEpath, f))
            except SameFileError:
                os.remove(join(NEpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(NEpath, f))

        if NE_1D is False:
            move('diffdata.json', join(NEpath, 'diffdata.json'))

    else:
        warnings.warn('macro.nml and NE_data.h5 not written!')

    # make TH input (HA_*_*.txt)
    if 'THconfig' in core.__dict__.keys():
        THpath = mkdir("coolant", casepath)
        THdatapath = mkdir("data", THpath)
        writeTHdata(core, template=templateTH)
        # move TH data files
        pwd = os.getcwd()
        for f in os.listdir(pwd):
            if f.startswith("HA"):
                move(f, join(THdatapath, f))
    else:
        warnings.warn('HA_xx_xx.dat not written, data dir not created!')

    # make CZ input (mdot.txt, temp.txt, press.txt, filecool.txt)
    if 'CZconfig' in core.__dict__.keys():
        THpath = mkdir("coolant", casepath)
        # write CZ .txt data
        writeCZdata(core)
        # write input.dat
        makeTHinput(core, template=templateCZ)
        # move TH files
        THfiles = ['mdot.dat', 'press.dat', 'temp.dat', 'input.dat',
                   'filecool.dat']
        [move(f, join(THpath, f)) for f in THfiles]
    else:
        warnings.warn('mdot.dat, press.dat, temp.dat, input.dat not written!')


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
    tEnd : float, optional
        Final time instant for FRENETIC simulation. Default is ``None``.
    Returns
    -------
    ``None``
    """
    # parse number of hexagons per row
    try:
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
        NH = core.NAss
        PITCH = core.AssemblyGeom.pitch
        try:
            NDIFF = len(core.THassemblytypes)
        except AttributeError:
            NDIFF = len(core.NEassemblytypes)
            print('Warning: NDIFF variable set equal to the number of NE assemblies')

    except AttributeError as err:
        if "object has no attribute 'Map'" in str(err):  # assume 1D core
            NL, NR, NDIFF, NH = 1, 1, 1, 1
            PITCH = 1
        else:
            print(err)
    # check if coupled calculation is possible
    if all([i in core.__dict__.keys() for i in ['THconfig', 'NEconfig']]):
        isNETH = 2
    else:
        isNETH = 0

    data = {'$NH': NH, '$NR': NR, '$NL': NL, '$NDIFF': NDIFF,
            '$TEND': core.TimeEnd, '$ISNETH': isNETH,
            '$PITCH': PITCH/100}

    if template is None:
        tmp = pkg_resources.read_text(templates, 'template_common_input.dat')
        tmp = tmp.splitlines()
    else:
        with open(template, 'r') as f:
            temp_contents = f.read()
            tmp = temp_contents. splitlines()

    f = io.open('common_input.dat', 'w', newline='\n')

    for line in tmp:  # loop over lines in reference file
        for key, val in data.items():  # loop over dict keys
            if key in line:
                if key in ['$TEND', '$PITCH']:
                   val = ff(val, 'double')
                else:
                   val = str(val)
                
                line = line.replace(key, val)
        # write to file
        f.write(line)
        f.write('\n')


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
