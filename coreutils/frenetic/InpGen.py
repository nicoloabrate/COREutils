"""
Author: N. Abrate.

File: InpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import logging
import pathlib
import numpy as np
from shutil import move, copyfile, SameFileError
from os.path import join
from . import templates
from coreutils.tools.utils import fortranformatter as ff
from coreutils.tools.plot import RadialMap, AxialGeomPlot, SlabPlot
import matplotlib.pyplot as plt
from .InpTH import writeTHdata, writeCZdata, makeTHinput
from .InpNE import writeConfig, makeNEinput, writemacro, writeNEdata
import coreutils.tools.h5 as myh5
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

figfmt = ['png', 'pdf']

def inpgen(core, json, casename=None, templates=None, plotNE=None, whichSA=None,
           H5fmt=2):
    """
    Make FRENETIC NE/TH files if the required data are in core object.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    json : str
        Absolute path of the ``.json`` input file.
    casename : str, optional
        File path where the case directory is located. Default is ``None``.
        In this case, the name of the FRENETIC case is 'case1'.
    templates : dict, optional
        File path where the template files are located. Default is ``None``.
        In this case, the default template is used.
    H5fmt : bool, optional
        Set ``True`` to print NE data also in txt format. Default is ``False``.

    Returns
    -------
    ``None``
    """
    # generate case directory-tree
    cwd = os.getcwd()
    iwd = os.path.dirname(json)
    if casename is None:
        casename = join(cwd, 'case1')

    if '.json' not in json:
        json = f"{json}.json"

    if not os.path.exists(iwd):
        raise OSError(f'{iwd} path does not exist!')

    casepath = mkdir(join(iwd, casename))
    AUXpath = mkdir("auxiliary", casepath)
    # --- save json to root directory
    jsonname = pathlib.Path(json).name
    try:
        copyfile(f'{json}', join(casepath, f'{jsonname}'))
    except SameFileError:
        os.remove(join(casepath, f'{jsonname}'))
        print(f'Overwriting file {jsonname}')
        copyfile(f'{json}', join(casepath, f'{jsonname}'))
    # --- save core object to root directory
    # core.to_h5('core')
    corefname = 'core.h5'
    grp_name = 'core'
    myh5.write(core, grp_name, corefname, chunks=True, compression=True,
               overwrite=True, skip=['NE.data'])
    try:
        copyfile(f'{corefname}', join(casepath, f'{corefname}'))
    except SameFileError:
        os.remove(join(casepath, f'{corefname}'))
        print(f'Overwriting file {corefname}')
        copyfile(f'{corefname}', join(casepath, f'{corefname}'))

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
    
    if hasattr(core, "NE"):
        NE = True
        isNE1D = True if core.dim == 1 else False
    else:
        NE = False

    if NE:
        NEpath = mkdir("NE", casepath)
        # define number of axial cuts
        nFreAxReg = len(core.NE.AxialConfig.zcuts)-1
        nAssTypes = 1 if isNE1D else len(core.NE.AxialConfig.cuts)  # len(core.config[tlast].regions)
        # define nmix (number of different regions)
        nmix = len(core.NE.regions.keys())

        # --- write config.inp
        writeConfig(core, nFreAxReg, nAssTypes)

        # --- write input.dat
        makeNEinput(core, template=templateNE, H5fmt=H5fmt)

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
        logging.warn('No NE object, so input.dat and config.inp not written!')

    # write NE data
    if hasattr(core.NE, 'data') or isNE1D:
        NEpath = mkdir("NE", casepath)
        # -- prepare data
        # get temperatures couples
        temp = core.TfTc
        # get NGRO
        unifuel = None

        # reference temperatures defined as minima
        mincouple = min(temp, key=lambda t: (t[1]+t[0]))
        Tf, Tc = mincouple
        NGRO = core.NE.nGro
        NPRE = core.NE.nPre
        # --- get kinetic parameters (equal for each material)
        mat0 = core.NE.data[temp[0]][core.NE.regions[1]]
        vel = 1/mat0.Invv
        beta0 = mat0.beta
        lambda0 = mat0.__dict__['lambda']

        # --- write macro.nml
        writemacro(core, nmix, vel, lambda0, beta0, nFreAxReg,
                   (Tf, Tc), core.NE.regions, H5fmt=H5fmt)

        # -- write NE_data.h5
        writeNEdata(core, verbose=False, H5fmt=H5fmt)
        # move NE files
        NEfiles = ['macro.nml', 'NE_data.h5']
        for f in NEfiles:
            try:
                move(f, join(NEpath, f))
            except SameFileError:
                os.remove(join(NEpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(NEpath, f))

        move('meanfreepath_difflength.json', join(AUXpath, 'meanfreepath_difflength.json'))

    else:
        logging.warn('macro.nml and NE_data.h5 not written!')

    # make TH input (HA_*_*.txt)
    if 'THconfig' in core.__dict__.keys():
        THpath = mkdir("TH", casepath)
        THdatapath = mkdir("data", THpath)
        writeTHdata(core, template=templateTH)
        # move TH data files
        pwd = os.getcwd()
        for f in os.listdir(pwd):
            if f.startswith("HA"):
                move(f, join(THdatapath, f))
    else:
        logging.warn('No TH configuration, so HA_xx_xx.dat not written and data dir not created!')

    # make CZ input (mdot.txt, temp.txt, press.txt, filecool.txt)
    if 'CZconfig' in core.__dict__.keys():
        THpath = mkdir("TH", casepath)
        # write CZ .txt data
        writeCZdata(core)
        # write input.dat
        makeTHinput(core, template=templateCZ)
        # move TH files
        THfiles = ['mdot.dat', 'press.dat', 'temp.dat', 'input.dat',
                   'filecool.dat']
        [move(f, join(THpath, f)) for f in THfiles]
    else:
        logging.warn('No CZconfig, so mdot.dat, press.dat, temp.dat, input.dat not written!')


    # plot configurations
    if NE:
        if core.dim == 3:
            offset = core.Map.fren2serp[1]
            angle = np.radians(60)
            whichSA = None
            if plotNE is not None:
                if 'offset' in plotNE.keys():
                    offset = core.Map.fren2serp[plotNE['offset']]
                if 'angle' in plotNE.keys():
                    angle = plotNE['angle']
                if 'offset' in plotNE.keys():
                    whichSA = plotNE['whichSA']

        AUX_NE_plot = []
        asslabel = core.NE.assemblytypes
        if core.dim != 1:
            for fmt in figfmt:
                # --- radial map (assembly numbers)
                figname = f'NE-rad-map.{fmt}'
                AUX_NE_plot.append(figname)
                RadialMap(core, label=True, fren=True, whichconf="NE", 
                          legend=True, asstype=True, figname=figname)
                # --- radial configurations
                for itime, t in enumerate(core.NE.time):
                    figname = f'NE-rad-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    RadialMap(core, time=t, label=True, fren=True, 
                              whichconf="NE", dictname=asslabel,
                              legend=True, asstype=True, figname=figname)

        if core.dim != 1:
            x0 = []
            y0 = []
            sextI = []

            x0y0 = core.Map.serpcentermap[offset]

            for n, xy in core.Map.serpcentermap.items():
                n = core.Map.serp2fren[n]
                if abs(xy[1]) < 1E-4:
                    x0.append(n)
                if abs(xy[0]) < 1E-4:
                    y0.append(n)
                if abs(np.tan(angle) - (xy[1]-x0y0[1])/(xy[0]-x0y0[0])) < 1E-4:
                    sextI.append(n)
        else:
            SAs = None
        # plot core Axial configuration
        for fmt in figfmt:
            for itime, t in enumerate(core.NE.time):
                if core.dim == 1:
                    figname = f'NEslab-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    SlabPlot(core, time=t, figname=figname, )
                    plt.close()
                elif core.dim == 3:
                    # --- default plot
                    # plot one SA per each kind at each time
                    # add one assembly per type
                    allassbly = []
                    config = core.NE.config[t]
                    lst = np.unique(config.flatten())
                    for l in lst:
                        if l != 0:
                            a = core.getassemblylist(l, config, isfren=True)
                            allassbly.append(min(a))
                    allassbly.sort()
                    figname = f'NEax-alltypes-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    AxialGeomPlot(core, allassbly, time=t, fren=True, zcuts=True,
                                figname=figname, legend=True, floating=True)
                    plt.close()
                    # plot y=0 SAs
                    figname = f'NEax-x0-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    AxialGeomPlot(core, x0, time=t, fren=True, zcuts=True,
                                figname=figname, legend=True)
                    plt.close()
                    # plot x=0 SAs
                    figname = f'NEax-y0-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    AxialGeomPlot(core, y0, time=t, fren=True, zcuts=True,
                                figname=figname, legend=True, floating=True)
                    plt.close()
                    # plot along 1st sextant
                    figname = f'NEax-sextI-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    AxialGeomPlot(core, sextI, time=t, fren=True, zcuts=True,
                                figname=figname, legend=True, floating=True)
                    plt.close()
                    # custom plot
                    if whichSA is not None:
                        figname = f'NEax-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                        AUX_NE_plot.append(figname)
                        AxialGeomPlot(core, SAs, time=t, fren=True, zcuts=True,
                                    figname=figname, legend=True)
                else:
                    raise OSError(f'Cannot use this kind of plot for {core.dim}D cores!')
        f = 'configurations.xlsx'
        try:
            move(f, join(AUXpath, f))
        except SameFileError:
            os.remove(join(AUXpath, f))
            print('Overwriting file {}'.format(f))
            move(f, join(AUXpath, f))

        # move files in directory
        for f in AUX_NE_plot:
            try:
                move(f, join(AUXpath, f))
            except SameFileError:
                os.remove(join(AUXpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(AUXpath, f))

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
            NDIFF = len(core.TH.assemblytypes)
        except AttributeError:
            NDIFF = len(core.NE.assemblytypes)
            logging.warn('NDIFF variable set equal to the number of NE assemblies')

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