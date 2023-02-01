import io
import os
import git
import socket
import logging
import pathlib
import numpy as np
from os.path import join
from datetime import datetime
from shutil import move, copyfile, SameFileError
from . import templates
from coreutils.tools.utils import fortranformatter as ff
from coreutils.tools.plot import RadialMap, AxialGeomPlot, SlabPlot
import matplotlib.pyplot as plt
from .InpTH import writeTHdata, writeCZdata, makeTHinput
from .InpNE import writeConfig, makeNEinput, writemacro, writeNEdata
import coreutils.tools.h5 as myh5
from coreutils.frenetic.frenetic_namelists import FreneticNamelist, FreneticNamelistError

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

np.seterr(invalid='ignore')
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
figfmt = ['png']

repopath = pathlib.Path(__file__).resolve().parents[2]
repo = git.Repo(repopath)
sha = repo.head.object.hexsha  # commit id


def fillFreneticNamelist(core):
    """Fill FRENETIC kw dict with missing data, ensuring their consistency.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Object storing the information needed to fill the missing
        keys.

    Raises
    ------
    FreneticNamelistError
        If a keyword is not specified
    """
    # --- CI
    try:
        nL = np.count_nonzero(core.Map.inp, axis=1)
        nL = nL[nL != 0]
        # parse number of rows
        nR = len(nL)
        # flip to be consistent with FRENETIC numeration
        if nL[0] < nL[-1]:
            nL = (np.flipud(nL))
            nL = nL.tolist()

        pitch = core.AssemblyGeom.pitch
        nH = core.nAss
        try:
            nDiff = len(core.TH.assemblytypes)
        except AttributeError:
            nDiff = len(core.NE.assemblytypes)
            logging.warn('nDiff variable set equal to the number of NE assemblies')

    except AttributeError as err:
        if "object has no attribute 'Map'" in str(err):  # assume 1D core
            nL, nR, nDiff, nH = 1, 1, 1, 1
            pitch = core.AssemblyGeom.pitch
        else:
            print(err)

    core.FreneticNamelist['nChan'] = nH
    core.FreneticNamelist['nL'] = nL
    core.FreneticNamelist['nR'] = nR
    core.FreneticNamelist['nDiff'] = nDiff
    core.FreneticNamelist['HexPitch'] = pitch/100
    core.FreneticNamelist['LeXag'] = core.AssemblyGeom.edge if core.dim != 1 else 1.
    core.FreneticNamelist['isNETH'] = 2 if hasattr(core, "NE") and hasattr(core, "TH") and core.dim == 3 else 0
    core.FreneticNamelist['tEnd'] = core.TimeEnd if core.trans else 0.

    # unionise NE and TH configuration times in a single list
    TimeNETHConfig = []
    if hasattr(core, "NE"):
        TimeNETHConfig.extend(core.NE.time)
    if hasattr(core, "TH"):
        TimeNETHConfig.extend(core.TH.CZtime)

    TimeNETHConfig = list(set(TimeNETHConfig))

    # --- is NE
    core.FreneticNamelist['nDim'] = core.dim
    if hasattr(core, "NE"):
        if core.dim != 2:
            tmp = core.NE.AxialConfig.splitz
            NZ = len(core.NE.AxialConfig.zcuts)-1
            if isinstance(tmp, (int)):
                splitz = [tmp]*NZ
            elif isinstance(tmp, (list, np.ndarray)):
                splitz = tmp if len(tmp) > 1 else [tmp[0]]*NZ
            else:
                raise OSError(f'splitz in core.NEAxialsConfig.splitz cannot'
                            f'be of type {type(tmp)}')
            meshz = core.NE.AxialConfig.zcuts
        else:
            NZ = 1
            splitz = [1]
            meshz = [0., 0.]

        core.FreneticNamelist['iRun'] = 2 if core.trans else 1
        core.FreneticNamelist['nConf'] = len(core.NE.time)
        core.FreneticNamelist['nElez0'] = NZ
        core.FreneticNamelist['Meshz0'] = meshz
        core.FreneticNamelist['SplitZ'] = splitz
    else:
        core.FreneticNamelist['iRun'] = -1
        core.FreneticNamelist['nConf'] = -1
        core.FreneticNamelist['nElez0'] = -1
        core.FreneticNamelist['Meshz0'] = -1
        core.FreneticNamelist['SplitZ'] = -1

    # --- is TH
    if hasattr(core, "TH"):
        core.FreneticNamelist['nElems'] = core.TH.nVol
        core.FreneticNamelist['xLengt'] = core.TH.zmesh[1]-core.TH.zmesh[0]
        if hasattr(core.TH, "nVolRef"):
            core.FreneticNamelist['nElRef'] = core.TH.nVolRef
            core.FreneticNamelist['xBRefi'] = core.TH.zref[0]
            core.FreneticNamelist['xERefi'] = core.TH.zref[1]
            core.FreneticNamelist['iTyMsh'] = 1
        else:
            core.FreneticNamelist['iTyMsh'] = 0

        if np.isnan(core.FreneticNamelist['nLayer']):
            core.FreneticNamelist['zLayer'] = core.TH.zcoord
            core.FreneticNamelist['nLayer'] = core.TH.zcoord.shape[0]
        else:
            if np.isnan(core.FreneticNamelist['zLayer']):
                core.FreneticNamelist['zLayer'] = np.linspace(core.TH.zref[0], core.TH.zref[1], 
                                                              core.FreneticNamelist['nLayer'])

        if np.isnan(core.FreneticNamelist['nTimeProf']):
            core.FreneticNamelist['TimeProf'] = TimeNETHConfig
            core.FreneticNamelist['nTimeProf'] = len(core.FreneticNamelist['TimeProf'])
        #  assign THdata in ad hoc keys
        iType = 1
        for THtype, THdata in core.TH.THdata.items():
            core.FreneticNamelist[f'HAType{iType}'] = {}
            HAdict = core.FreneticNamelist[f'HAType{iType}']
            HAdict['iHA'] = THdata.iHA
            HAdict['iPinSolidX'] = THdata.isRadHomog
            HAdict['nFuelX'] = THdata.nHeatPins
            HAdict['nNonHeatedX'] = THdata.nNonHeatPins
            # geometry
            if hasattr(THdata, 'FuelRad'):
                HAdict['dFuelX'] = THdata.FuelRad[1]*2
                HAdict['dFuelInX'] = THdata.FuelRad[0]*2
            else:
                HAdict['dFuelX'] = 0.
                HAdict['dFuelInX'] = 0.

            if hasattr(THdata, 'NonFuelRad'):
                HAdict['DFuelNfX'] = THdata.NonFuelRad[1]*2
            else:
                HAdict['DFuelNfX'] = 0.

            if hasattr(THdata, 'GapRad'):
                HAdict['ThickGasX'] = THdata.GapRad[1]-THdata.GapRad[0]
            else:
                HAdict['ThickGasX'] = 0.

            if hasattr(THdata, 'CladRad'):
                HAdict['RCoX'] = THdata.CladRad[1]
                HAdict['RCiX'] = THdata.CladRad[0]
            else:
                HAdict['RCoX'] = 0.
                HAdict['RCiX'] = 0.

            if hasattr(THdata, 'WrapThick'):
                HAdict['ThickBoxX'] = THdata.WrapThick
                HAdict['ThickClearX'] = THdata.ThickClear
            else:
                HAdict['ThickBoxX'] = 0.
                HAdict['ThickClearX'] = 1E-6

            if hasattr(THdata, 'BibSides'):
                HAdict['InBoxInsideX'] = THdata.BibSides[0]
                HAdict['InBoxOutsideX'] = THdata.BibSides[1]
            else:
                HAdict['InBoxInsideX'] = 0.
                HAdict['InBoxOutsideX'] = 0.

            if hasattr(THdata, 'WireDiam'):
                HAdict['dWireX'] = THdata.WireDiam
                HAdict['pWireX'] = THdata.WirePitch
            else:
                HAdict['dWireX'] = 0.
                HAdict['pWireX'] = 0.

            if hasattr(THdata, 'FuelPitch'):
                HAdict['PtoPDistX'] = THdata.FuelPitch
            else:
                HAdict['PtoPDistX'] = 0.

            HAdict['iBiBX'] = THdata.isBiB
            HAdict['iCRadX'] = THdata.isAnn
            # correlations
            HAdict['FPeakX'] = float(THdata.frictMult)
            HAdict['QBoxX'] = float(THdata.htcMult)
            HAdict['iHpbPinX'] = THdata.htcCorr
            HAdict['iTyFrictX'] = THdata.frictCorr
            HAdict['iChCouplX'] = THdata.chanCouplCorr
            # material
            if hasattr(THdata, 'FuelPinMat'):
                HAdict['iFuelX'] = THdata.FuelPinMat
            else:
                HAdict['iFuelX'] = ""

            if hasattr(THdata, 'NonFuelPinMat'):
                HAdict['cNfX'] = THdata.NonFuelPinMat
            else:
                HAdict['cNfX'] = ""

            if hasattr(THdata, 'GapMat'):
                HAdict['iGapX'] = THdata.GapMat
            else:
                HAdict['iGapX'] = ""

            if hasattr(THdata, 'CladMat'):
                HAdict['iCladX'] = THdata.CladMat
            else:
                HAdict['iCladX'] = ""

            if hasattr(THdata, 'WrapMat'):
                HAdict['BoxMatX'] = THdata.WrapMat
            else:
                HAdict['BoxMatX'] = ""

            # FIXME the radial nodes subdivision is currently fixed here.
            # The user should have the possibility to choose it, but how
            # this can be done is not trivial and should be discussed
            matlst = [1, 0, 0]
            if hasattr(THdata, "GapMat"):
                matlst[1] = 2
            if hasattr(THdata, "CladMat"):
                matlst[2] = 3

            HAdict['MaterHX'] = matlst
            HAdict['HeatGhX'] = [1, 0, 0]
            HAdict['iMatX'] = 1. # FIXME hardcoded value
            iType += 1

        eraseKeys = ["iHA", "nFuelX", "nNonHeatedX", "iFuelX", "dFuelX",
                     "dFuelInX", "ThickBoxX", "ThickClearX", "FPeakX", "QBoxX", "BoxMatX", 
                     "iHpbPinX", "iTyFrictX", "iChCouplX", "iPinSolidX", "RCoX", "RCiX", "ThickGasX",
                     "InBoxInsideX", "InBoxOutsideX", "dWireX", "pWireX", "DFuelNfX", "PtoPDistX", 
                     "iCRadX", "cNfX", "iCladX", "iGapX", "MaterHX", "HeatGhX"]
        for key in eraseKeys:
            core.FreneticNamelist.pop(key)
    else:
        setToValue = ["iHA", "nFuelX", "nNonHeatedX", "iFuelX", "dFuelX",
                      "dFuelInX", "ThickBoxX", "ThickClearX", "FPeakX", "QBoxX",
                      "BoxMatX", "iHpbPinX", "iTyFrictX", "iChCouplX", "iPinSolidX", "RCoX", "RCiX", "ThickGasX", 
                      "DFuelNfX", "PtoPDistX", "iCRadX" "cNfX" "iCladX" "iGapX" "MaterHX" "HeatGhX", 
                      "InBoxInsideX", "InBoxOutsideX", "dWireX", "pWireX", "PtoPDistX", "nElems", "xLengt", 
                      "zLayer", "nLayer", "TimeProf", "nTimeProf", "iMatX", "MaterHX", "HeatGhX"]
        for key in setToValue:
            core.FreneticNamelist[key] = -1

    # --- final sanity check
    for k, v in core.FreneticNamelist.items():
        if "HAType" not in k:
            if isinstance(v, float):
                # check possible missing kw set to np.nan in FreneticNamelist class
                if np.isnan(v):
                    raise FreneticNamelistError(f"`{k}` keyword is not specified! Check input keywords in the .json file!")
        else:
            for kk, vv in v.items():
                if isinstance(vv, float):
                    # check possible missing kw set to np.nan in FreneticNamelist class
                    if np.isnan(vv):
                        raise FreneticNamelistError(f"`{kk}` keyword is not specified for {k}! Check input keywords in the .json file!")

    # --- arrange data in namelists
    frnnml_full = {}
    namelists = FreneticNamelist().namelists
    for nml, lst in namelists.items():
        if nml not in ["COMMONS", "THERMALHYDRAULIC"]:
            frnnml_full[nml] = {}
            for s in lst:
                frnnml_full[nml][s] = core.FreneticNamelist[s]
        else:
            for iTHtype, THtype in enumerate(core.TH.THdata.keys()):
                hatype = f'HAType{iTHtype+1}'
                if hatype not in frnnml_full.keys():
                    frnnml_full[hatype] = {}
                frnnml_full[hatype][nml] = {}
                for s in lst:
                    frnnml_full[hatype][nml][s] = core.FreneticNamelist[hatype][s]

    return frnnml_full


def inpgen(core, json):
    """
    Make FRENETIC NE/TH files if the required data are in core object.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    json : str
        Absolute path of the ``.json`` input file.

    Returns
    -------
    ``None``
    """
    # generate case directory-tree
    cwd = os.getcwd()
    iwd = os.path.dirname(json)

    if '.json' not in json:
        json = f"{json}.json"
    
    json = pathlib.Path(json)
    casename = json.stem

    if not os.path.exists(iwd):
        raise OSError(f'{iwd} path does not exist!')

    casepath = mkdir(join(iwd, casename))
    AUXpath = mkdir("auxiliary", casepath)

    if hasattr(core, "NE"):
        AUXpathNE = mkdir("NE", AUXpath)

    if hasattr(core, "TH"):
        AUXpathTH = mkdir("TH", AUXpath)

    # --- echoing json to root directory
    try:
        copyfile(f'{json}', join(casepath, f'{json.name}'))
    except SameFileError:
        os.remove(join(casepath, f'{json.name}'))
        print(f'Overwriting file {json.name}')
        copyfile(f'{json}', join(casepath, f'{json.name}'))

    # --- add GIT info
    print_coreutils_info()
    move('coreutils_info.txt', join(AUXpath, 'coreutils_info.txt'))

    # --- save core object to root directory
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

    # --- COMMON INPUT (common_input.inp)
    makecommoninput(core)
    try:
        move('common_input.inp', join(casepath, 'common_input.inp'))
    except SameFileError:
        os.remove(join(casepath, 'common_input.inp'))
        print(f'Overwriting file {str(json)}')
        move('common_input.inp', join(casepath, 'common_input.inp'))

    # --- NE input (config.inp, macro.nml)
    if hasattr(core, "NE"):
        NE = True
        isNE1D = True if core.dim == 1 else False
    else:
        NE = False

    if NE:
        NEpath = mkdir("NE", casepath)
        # define nmix (number of different regions)
        nmix = len(core.NE.regions.keys())
        # --- write config.inp
        writeConfig(core)
        # --- write input.inp
        makeNEinput(core)

        # move NE files
        NEfiles = ['input.inp', 'config.inp']
        for f in NEfiles:
            try:
                move(f, join(NEpath, f))
            except SameFileError:
                os.remove(join(NEpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(NEpath, f))
    else:
        logging.warn('No NE object, so input.inp and config.inp not written!')

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
        writemacro(core, nmix, vel, lambda0, beta0,
                   (Tf, Tc), core.NE.regions, H5fmt=2)

        # -- write NE_data.h5
        writeNEdata(core, verbose=False, H5fmt=2, txt=0)
        # move NE files
        NEfiles = ['macro.nml', 'NE_data.h5']
        for f in NEfiles:
            try:
                move(f, join(NEpath, f))
            except SameFileError:
                os.remove(join(NEpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(NEpath, f))

        move('DiffLengthToNodeSize.json', join(AUXpathNE, 'DiffLengthToNodeSize.json'))

    else:
        logging.warn('macro.nml and NE_data.h5 not written!')

    TH = True if hasattr(core, "TH") else False

    # make TH input (HA_*_*.txt)
    if TH:
        THpath = mkdir("TH", casepath)
        THdatapath = mkdir("data", THpath)
        writeTHdata(core)
        # move TH data files
        pwd = os.getcwd()
        for f in os.listdir(pwd):
            if f.startswith("HA"):
                move(f, join(THdatapath, f))

        # make CZ input (mdot.txt, temp.txt, press.txt, filecool.txt)
        THpath = mkdir("TH", casepath)
        # write CZ .txt data
        writeCZdata(core)
        # write input.inp
        makeTHinput(core)
        # move TH files
        THfiles = ['mdot.inp', 'press.inp', 'temp.inp', 'input.inp']
        [move(f, join(THpath, f)) for f in THfiles]
    else:
        logging.warn('No TH configuration, so HA_xx_xx.inp not written and other data not created!')

    if NE:
        auxNE(core, AUXpathNE)
    if TH:
        auxTH(core, AUXpathTH)


def auxNE(core, AUXpathNE):
    """Generate NE auxiliary files.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    AUXpathNE : str
        Path to auxiliary NE directory.
    """
    plotNE = core.NE.plot if hasattr(core.NE, "plot") else None
    # plot configurations
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
    # --- plot core radial configuration
    if core.dim != 1:
        for fmt in figfmt:
            # assembly numbers
            figname = f'NE-rad-map.{fmt}'
            AUX_NE_plot.append(figname)
            RadialMap(core, label=True, fren=True, whichconf="NE", 
                        legend=True, asstype=True, figname=figname)
            # radial configurations
            for itime, t in enumerate(core.NE.time):
                figname = f'NE-rad-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                AUX_NE_plot.append(figname)
                RadialMap(core, time=t, label=True, fren=True, 
                            whichconf="NE", dictname=asslabel,
                            legend=True, asstype=True, figname=figname)
            # --- user-defined custom figures
            if "plot" in core.NE.__dict__.keys():
                if "radplot" in core.NE.plot.keys():
                    for iconf, conf in enumerate(core.NE.plot["radplot"]):
                        labeldict = None
                        asstype = True
                        figname = f'NE-rad-custom{iconf}.{fmt}'
                        AUX_NE_plot.append(figname)

                        if "sext" in conf:
                            whichSA = core.Map.getSAsextant(conf["sext"])
                        elif "whichSA" in conf:
                            whichSA = conf["whichSA"]
                        else:
                            whichSA = None

                        radtime = conf["time"] if "time" in conf else 0

                        if "labels" in conf:
                            if len(whichSA) != len(conf["labels"]):
                                print("Warning for plot: label numbers do not match with whichSA key!")
                            else:
                                labeldict = {}
                                for i, l in enumerate(conf["labels"]):
                                    for j in whichSA[i]:
                                        labeldict[j] = l
                                whichSA = None
                                asstype = False

                        RadialMap(core, time=radtime, label=True, fren=True, 
                                    whichconf="NE", dictname=labeldict, which=whichSA,
                                    legend=True, asstype=asstype, figname=figname)

    # --- plot core axial configurations
    if core.dim != 2:
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

    for fmt in figfmt:
        for itime, t in enumerate(core.NE.time):
            if core.dim == 1:
                figname = f'NE-slab-conf{itime}-t{1E3*t:g}_ms.{fmt}'
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

                figname = f'NE-ax-alltypes-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                AUX_NE_plot.append(figname)
                AxialGeomPlot(core, allassbly, time=t, fren=True, zcuts=True,
                            figname=figname, legend=True, floating=True)
                plt.close()

                figname = f'NE-ax-alltypes-splitz-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                AUX_NE_plot.append(figname)
                AxialGeomPlot(core, allassbly, time=t, fren=True, zcuts=True,
                                splitz=True, figname=figname, legend=True, floating=True)
                plt.close()

                # plot y=0 SAs
                figname = f'NE-ax-x0-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                AUX_NE_plot.append(figname)
                AxialGeomPlot(core, x0, time=t, fren=True, zcuts=True,
                            figname=figname, legend=True)
                plt.close()
                # plot x=0 SAs
                figname = f'NE-ax-y0-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                AUX_NE_plot.append(figname)
                AxialGeomPlot(core, y0, time=t, fren=True, zcuts=True,
                            figname=figname, legend=True, floating=True)
                plt.close()
                # plot along 1st sextant
                figname = f'NE-ax-sextI-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                AUX_NE_plot.append(figname)
                AxialGeomPlot(core, sextI, time=t, fren=True, zcuts=True,
                            figname=figname, legend=True, floating=True)
                plt.close()
                # custom plot
                if whichSA is not None:
                    figname = f'NE-ax-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    AxialGeomPlot(core, SAs, time=t, fren=True, zcuts=True,
                                figname=figname, legend=True)

    f = 'configurationsNE.xlsx'
    try:
        move(f, join(AUXpathNE, f))
    except SameFileError:
        os.remove(join(AUXpathNE, f))
        print('Overwriting file {}'.format(f))
        move(f, join(AUXpathNE, f))

    # move files in directory
    for f in AUX_NE_plot:
        try:
            move(f, join(AUXpathNE, f))
        except SameFileError:
            os.remove(join(AUXpathNE, f))
            print('Overwriting file {}'.format(f))
            move(f, join(AUXpathNE, f))


def auxTH(core, AUXpathTH):
    """Generate TH auxiliary files.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    AUXpathTH : str
        Path to auxiliary TH directory.
    """
    # plotTH = core.TH.plotTH
    # plot configurations
    if core.dim == 3:
        offset = core.Map.fren2serp[1]
        angle = np.radians(60)
        whichSA = None
        # if plotTH is not None:
        #     if 'offset' in plotTH.keys():
        #         offset = core.Map.fren2serp[plotTH['offset']]
        #     if 'angle' in plotTH.keys():
        #         angle = plotTH['angle']
        #     if 'offset' in plotTH.keys():
        #         whichSA = plotTH['whichSA']

    AUX_TH_plot = []
    # --- plot core radial configuration
    if core.dim != 1:
        for fmt in figfmt:
            for conftype in ['TH', 'CZ']:
                asslabel = core.TH.__dict__[f"{conftype}assemblytypes"]
                # assembly numbers
                figname = f'{conftype}-rad-map.{fmt}'
                AUX_TH_plot.append(figname)
                RadialMap(core, label=True, fren=True, whichconf=conftype, 
                            legend=True, asstype=True, figname=figname)
                # radial configurations
                for itime, t in enumerate(core.TH.__dict__[f"{conftype}time"]):
                    figname = f'{conftype}-rad-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_TH_plot.append(figname)
                    RadialMap(core, time=t, label=True, fren=True, 
                            whichconf=conftype, dictname=asslabel,
                            legend=True, asstype=True, figname=figname)


    # move files in directory
    for f in AUX_TH_plot:
        try:
            move(f, join(AUXpathTH, f))
        except SameFileError:
            os.remove(join(AUXpathTH, f))
            print('Overwriting file {}'.format(f))
            move(f, join(AUXpathTH, f))


def makecommoninput(core):
    """
    Make common_input.inp file.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.

    Returns
    -------
    ``None``
    """
    frnnml = FreneticNamelist()
    f = io.open('common_input.inp', 'w', newline='\n')

    for namelist in frnnml.files["common_input.inp"]:
        f.write(f"&{namelist}\n")
        for key, val in core.FreneticNamelist[namelist].items():
            # format value with FortranFormatter utility
            val = ff(val)
            # "vectorise" in Fortran input if needed
            if key in frnnml.vector_inp:
                val = f"{core.nAss}*{val}"
            # FIXME in the future there will be no need for (1, 1:nASS)
            if key.casefold() in ["nelref", "xbrefi", "xerefi"]:
                f.write(f"{key}(1, 1:{core.nAss}) = {val}\n")
            else:
                f.write(f"{key} = {val}\n")
        # write to file
        f.write("/\n")


def mkdir(dirname, indirs=None):
    """
    Make a new directory named dirname inside path.

    Parameters
    ----------
    dirname : string
        directory name
    indirs : list, optional
        List of directories where the new directory is created, by default
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


def print_coreutils_info():
    """Print information for reproducibility.

    Parameters
    ----------
    ``None``

    Returns
    -------
    ``None``
    """
    # datetime object containing current date and time
    now = datetime.now()
    mmddyyhh = now.strftime("%B %d, %Y %H:%M:%S")
    with open("coreutils_info.txt", "w") as f:
        f.write(f"FRENETIC input generated on with `coreutils`: \n")
        f.write(f"# -------------------------- \n")
        f.write(f"HOSTNAME: {socket.gethostname()} \n")
        try:
            f.write(f"USERNAME: {os.getlogin()} \n")
        except OSError:
            f.write(f"USERNAME: unknown \n")
        f.write(f"GIT_REPO_URL: {repo.remotes.origin.url} \n")
        f.write(f"GIT_COMMIT_ID: {sha} \n")
        f.write(f"GIT_BRANCH: {repo.active_branch} \n")
        f.write(f"DDYYMMHH: {mmddyyhh} \n")
        f.write(f"# -------------------------- \n")
