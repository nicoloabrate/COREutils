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
from coreutils.tools.properties import *
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
        nL = core.Map.nonZeroCols
        # parse number of rows
        nR = len(nL)
        # flip to be consistent with FRENETIC numeration
        if nL[0] < nL[-1]:
            nL = (np.flipud(nL))
            nL = nL.tolist()

        pitch = core.Geometry.AssemblyGeometry.pitch
        nH = core.nAss
        isSym = core.FreneticNamelist['isSym']
        N = int(core.nAss/6*isSym+1) if isSym else core.nAss
        try:
            nDiff = len(core.TH.THdata.keys())
        except AttributeError:
            nDiff = len(core.NE.assemblytypes)
            logging.warn('nDiff variable set equal to the number of NE assemblies')

    except AttributeError as err:
        if "object has no attribute 'Map'" in str(err):  # assume 1D core
            nL, nR, nDiff, nH = 1, 1, 1, 1
            N = 1
            pitch = core.Geometry.AssemblyGeometry.pitch
        else:
            logging.error(err)

    isSym = core.FreneticNamelist['isSym']
    core.FreneticNamelist['nChan'] = int(nH/6*isSym+1) if isSym else nH
    core.FreneticNamelist['nL'] = nL
    core.FreneticNamelist['nR'] = nR
    core.FreneticNamelist['nDiff'] = nDiff
    core.FreneticNamelist['HexPitch'] = pitch/100
    lexag = np.nan
    for latname, lat in core.Geometry.LatticeGeometry.items():
        if lat.wrapWidth > 0 and lat.nPins > 0:
            lexag = (pitch-2*lat.wrapWidth-2*lat.interassWidth)/3**0.5
            break
    core.FreneticNamelist['LeXag'] = lexag/100 if core.dim != 1 else 0.001
    if np.isnan(core.FreneticNamelist['isNETH']):
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
        if isinstance(core.FreneticNamelist['TimeProfNE'], list):
            core.FreneticNamelist['nTimeProfNE'] = len(core.FreneticNamelist['TimeProfNE'])
        # set power
        core.FreneticNamelist['power'] = core.power
        if core.NE.nGrp == 0:
            core.FreneticNamelist['ioPowerp'] = 0
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
                core.FreneticNamelist['zLayer'] = np.linspace(core.TH.zmesh[0], core.TH.zmesh[1], 
                                                              core.FreneticNamelist['nLayer'])

        if np.isnan(core.FreneticNamelist['nTimeProfTH']):
            core.FreneticNamelist['TimeProfTH'] = TimeNETHConfig
            core.FreneticNamelist['nTimeProfTH'] = len(core.FreneticNamelist['TimeProfTH'])

        # smart initialisation
        if np.isnan(core.FreneticNamelist['temIni']):
            # get average heat in each HA
            nFissHA = len(core.NE.get_fissile_SA(core, t=0))
            qHA = core.power/nFissHA
            mdot = np.zeros((N,))
            Tinl = np.zeros((N,))
            for n in core.Map.fren2serp.keys():
                # get data in assembly
                if n > N:
                    break
                whichtype = core.getassemblytype(n, core.TH.CZconfig[0], isfren=True)
                whichtype = core.TH.CZassemblytypes[whichtype]
                Tinl[n-1] = core.TH.CZdata.temperatures[whichtype]
                mdot[n-1] = core.TH.CZdata.massflowrates[whichtype]

            # estimate outlet temp. with approx. energy balance
            if core.coolant == 'Pb':
                cp = LeadProp.specific_heat(Tinl)
            else:
                raise OSError(f"Properties not implemented for coolant {core.coolant}")

            dT = np.divide(qHA, mdot, out=np.zeros_like(mdot), where=mdot!=0)/cp
            Tout = Tinl+dT
            if (Tout-Tinl).max() < 0.5:
                logging.warning("Input power may be too small to heat the coolant!")
            # Pinl = rho*9.81*h+Pout
            core.FreneticNamelist['temIni'] = (Tinl+Tout)/2

        #  assign THdata in ad hoc keys
        iType = 1
        for THtype, THdata in core.TH.THdata.items():
            core.FreneticNamelist[f'HAType{iType}'] = {}
            HAdict = core.FreneticNamelist[f'HAType{iType}']
            iHA = [i for i in THdata.iHA if i <= N]
            HAdict['iHA'] = iHA

            # TODO only one lattice axially, more should be considered
            GEtype = core.TH.THtoGE[THtype][0]
            latname = core.Geometry.AssemblyType[GEtype].reg[0]
            lattice = core.Geometry.LatticeGeometry[latname]
            # TODO only one pin type per lattice, more should be considered
            pinname = core.Geometry.LatticeType[latname][0]
            pin = core.Geometry.Pin[pinname]
            isHomog = len(pin.materials) < 3
            n = 2 if pin.isAnnular else 1

            HAdict['iRadHom'] = 1 if isHomog else 0
            HAdict['nFuelX'] = lattice.nPins
            # FIXME TODO how to account for these? Maybe better to distinguish fissile-nonfissile
            HAdict['nNonHeatedX'] = 0

            # --- geometry
            HAdict['dFuelX'] = 2*pin.radii.max()/100 # the name should be dPinX
            HAdict['dFuelInX'] = 2*pin.radii[0]/100 if pin.isAnnular else 0.
            # FIXME TODO how to account for these? Maybe better to distinguish fissile-nonfissile
            HAdict['dFuelNfX'] = 0.

            if isHomog:
                HAdict['ThickGasX'] = 0.
                HAdict['RCoX'] = pin.radii.max()/100
                HAdict['RCiX'] = pin.radii.max()/100
            else:
                HAdict['ThickGasX'] = (pin.radii[n]-pin.radii[n-1])/100
                n += 1
                HAdict['RCoX'] = pin.radii[n]/100
                HAdict['RCiX'] = pin.radii[n-1]/100

            if hasattr(lattice, 'wrapWidth'):
                HAdict['ThickBoxX'] = lattice.wrapWidth/100
                HAdict['ThickClearX'] = lattice.interassWidth/100
            else:
                HAdict['ThickBoxX'] = 0.
                HAdict['ThickClearX'] = 1E-6

            # FIXME TODO
            HAdict['InBoxInsideX'] = 0.
            HAdict['InBoxOutsideX'] = 0.

            # FIXME TODO
            HAdict['dWireX'] = 0.
            HAdict['pWireX'] = 0.

            HAdict['PtoPDistX'] = lattice.pitch/100. # to ensure it is float

            # FIXME TODO
            HAdict['iBiBX'] = 0
            HAdict['iCRadX'] = 1 if pin.isAnnular else 0
            # correlations
            HAdict['FPeakX'] = float(THdata.frictMult)
            HAdict['QBoxX'] = float(THdata.htcMult)
            HAdict['iHpbPinX'] = THdata.htcCorr
            HAdict['iTyFrictX'] = THdata.frictCorr
            HAdict['iChCouplX'] = THdata.chanCouplCorr

            # TODO TODO material
            HAdict['iFuelX'] = pin.materials[1] if pin.isAnnular else pin.materials[0]
            HAdict['NonFuelMat'] = "Default"

            if isHomog:
                HAdict['iGapX'] = "Default"
                HAdict['iCladX'] = "Default"
            else:
                HAdict['iGapX'] = pin.materials[2] if pin.isAnnular else pin.materials[1]
                HAdict['iCladX'] = pin.materials[3] if pin.isAnnular else pin.materials[2]

            if lattice.wrapMat is not None:
                HAdict['BoxMatX'] = lattice.wrapMat
            else:
                HAdict['BoxMatX'] = "Default"

            # FIXME the radial nodes subdivision is currently fixed here.
            # The user should have the possibility to choose it, but how
            # this can be done is not trivial and should be discussed
            matlst = [1, 0, 0]
            if not isHomog:
                matlst[1] = 2
                matlst[2] = 3

            HAdict['MaterHX'] = matlst
            HAdict['HeatGhX'] = [1, 0, 0]
            HAdict['iMatX'] = 1. # FIXME hardcoded value
            iType += 1

        eraseKeys = ["iHA", "nFuelX", "nNonHeatedX", "iFuelX", "dFuelX",
                     "dFuelInX", "ThickBoxX", "ThickClearX", "FPeakX", "QBoxX", "BoxMatX", 
                     "iHpbPinX", "iTyFrictX", "iChCouplX", "iRadHom", "RCoX", "RCiX", "ThickGasX",
                     "InBoxInsideX", "InBoxOutsideX", "dWireX", "pWireX", "dFuelNfX", "PtoPDistX", 
                     "iCRadX", "NonFuelMat", "iCladX", "iGapX", "MaterHX", "HeatGhX"]
        for key in eraseKeys:
            core.FreneticNamelist.pop(key)
    else:
        setToValue = ["iHA", "nFuelX", "nNonHeatedX", "iFuelX", "dFuelX", 'temIni',
                      "dFuelInX", "ThickBoxX", "ThickClearX", "FPeakX", "QBoxX", "iCRadX",
                      "BoxMatX", "iHpbPinX", "iTyFrictX", "iChCouplX", "iRadHom", "RCoX", "RCiX", 
                      "ThickGasX", "dFuelNfX", "PtoPDistX", "iCRadX" "NonFuelMat" "iCladX" "iGapX" "MaterHX",
                      "HeatGhX", "InBoxInsideX", "InBoxOutsideX", "dWireX", "pWireX", "PtoPDistX", 
                      "nElems", "xLengt", "NonFuelMat", "iCladX", "iGapX", "zLayer", "nLayer", "TimeProfTH",
                      "nTimeProfTH", "iMatX", "MaterHX", "HeatGhX"]
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
    inpfiles = FreneticNamelist().files
    NEnml = inpfiles["NEinput.inp"]
    THnml = inpfiles["THinput.inp"]+inpfiles["THdatainput.inp"]

    for nml, lst in namelists.items():

        if not hasattr(core, "NE"):
            if nml in NEnml:
                continue
        if not hasattr(core, "TH"):
            if nml in THnml:
                continue

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
        copyfile(f'{json}', join(AUXpath, f'{json.name}_echo'))
    except SameFileError:
        os.remove(join(casepath, f'{json.name}_echo'))
        logging.warning(f'Overwriting file {json.name}_echo')
        copyfile(f'{json}', join(AUXpath, f'{json.name}_echo'))

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
        logging.warning(f'Overwriting file {corefname}')
        copyfile(f'{corefname}', join(casepath, f'{corefname}'))

    # --- COMMON INPUT (common_input.inp)
    makecommoninput(core)
    try:
        move('common_input.inp', join(casepath, 'common_input.inp'))
    except SameFileError:
        os.remove(join(casepath, 'common_input.inp'))
        logging.warning(f'Overwriting file {str(json)}')
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
                logging.warning('Overwriting file {}'.format(f))
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
        if core.NE.NEdata["nPrec"] is None:
            beta0 = mat0.beta
            lambda0 = mat0.__dict__['lambda']
        elif core.NE.NEdata["nPrec"] == 1:
            beta0 = [mat0.beta_tot]
            lambda0 = [mat0.__dict__['lambda_tot']]
        else:
            raise OSError("Cannot deal with 'nPrec'!=1!")
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
                logging.warning('Overwriting file {}'.format(f))
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

        # make CZ input (mdot.txt, temp.txt, pressout.txt, filecool.txt)
        THpath = mkdir("TH", casepath)
        # write CZ .txt data
        writeCZdata(core)
        # write input.inp
        makeTHinput(core)
        # move TH files
        THfiles = ['mdot.inp', 'pressout.inp', 'tempinl.inp', 'input.inp']
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
    # plot configurations
    if core.dim == 3:
        offset = core.Map.fren2serp[1]
        angle = np.radians(60)
        whichSA = None

    AUX_NE_plot = []
    asslabel = core.NE.assemblytypes
    # --- plot core radial configuration
    if core.NE.plot['radplot']:
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
                                    logging.warning("plot: label numbers do not match with whichSA key!")
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
    if core.NE.plot['axplot']:
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

    if core.NE.worksheet:
        f = 'configurationsNE.xlsx'
        try:
            move(f, join(AUXpathNE, f))
        except SameFileError:
            os.remove(join(AUXpathNE, f))
            logging.warning('Overwriting file {}'.format(f))
            move(f, join(AUXpathNE, f))

    # move files in directory
    for f in AUX_NE_plot:
        try:
            move(f, join(AUXpathNE, f))
        except SameFileError:
            os.remove(join(AUXpathNE, f))
            logging.warning('Overwriting file {}'.format(f))
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
    # plot configurations
    if core.dim == 3:
        offset = core.Map.fren2serp[1]
        angle = np.radians(60)
        whichSA = None

    AUX_TH_plot = []
    # --- plot core radial configuration
    if core.TH.plot['radplot']:
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
            logging.warning('Overwriting file {}'.format(f))
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
    isSym = core.FreneticNamelist["PRELIMINARY"]['isSym']
    N = int(core.nAss/6*isSym+1) if isSym else core.nAss
    for namelist in frnnml.files["common_input.inp"]:
        f.write(f"&{namelist}\n")
        for key, val in core.FreneticNamelist[namelist].items():
            # format value with FortranFormatter utility
            val = ff(val)
            # "vectorise" in Fortran input if needed
            if key in frnnml.vector_inp:
                val = f"{N}*{val}"
            # FIXME in the future there will be no need for (1, 1:nASS)
            if key.casefold() in ["nelref", "xbrefi", "xerefi"]:
                f.write(f"{key}(1, 1:{N}) = {val}\n")
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
