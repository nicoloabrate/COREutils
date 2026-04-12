import io
import os
import json
import logging
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from os.path import join
from shutil import move, copyfile, SameFileError, rmtree
from coreutils.tools.utils import fortranformatter as ff
from coreutils.tools.properties import *
from coreutils.tools.utils import fortranformatter # InputGeneratorError, 
# from coreutils.frenetic.FreneticInput import FreneticInput

from coreutils.tools.plot import RadialMap, AxialGeomPlot, SlabPlot
from .InpTH import writeHTdata, writeBCdata, makeTHinput
from .InpNE import writeConfig, makeNEinput, writemacro, writeNEdata
import coreutils.tools.h5 as myh5
from coreutils.frenetic.frenetic_namelists import FreneticNamelist, FreneticNamelistError

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

np.seterr(invalid='ignore')
logger = logging.getLogger(__name__)

logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
figfmt = ['png']


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
            nDiff = len(core.TH.HTdata.keys())
        except AttributeError:
            nDiff = len(core.NE.assemblytypes)
            # FIXME FIXME
            # logger.warn('nDiff variable set equal to the number of NE assemblies')

    except AttributeError as err:
        if "object has no attribute 'Map'" in str(err):  # assume 1D core
            nL, nR, nDiff, nH = 1, 1, 1, 1
            N = 1
            pitch = core.Geometry.AssemblyGeometry.pitch
        else:
            logger.error(err)

    isSym = core.FreneticNamelist['isSym']
    core.FreneticNamelist['nChan'] = int(nH/6*isSym+1) if isSym else nH
    core.FreneticNamelist['nL'] = nL
    core.FreneticNamelist['nR'] = nR
    core.FreneticNamelist['nDiff'] = nDiff
    core.FreneticNamelist['HexPitch'] = pitch/100
    core.FreneticNamelist['iTyCool'] = core.coolant
    lexag = np.nan
    if core.dim != 1:
        for latname, lat in core.Geometry.LatticeGeometry.items():
            if lat.wrapWidth > 0 and lat.nPins > 0:
                lexag = (pitch-2*lat.wrapWidth-2*lat.interassWidth)/3**0.5
                break
        if np.isnan(lexag):
            lexag = 0.001

    core.FreneticNamelist['LeXag'] = lexag/100 if core.dim != 1 else 0.001
    if np.isnan(core.FreneticNamelist['isNETH']):
        core.FreneticNamelist['isNETH'] = 2 if hasattr(core, "NE") and hasattr(core, "TH") and core.dim == 3 else 0
    core.FreneticNamelist['tEnd'] = core.TimeEnd if core.trans else 0.

    # unionise NE and TH configuration times in a single list
    TimeNETHConfig = []
    if hasattr(core, "NE"):
        TimeNETHConfig.extend(core.NE.time)
    if hasattr(core, "TH"):
        TimeNETHConfig.extend(core.TH.BCtime)

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

        if core.trans:
            core.FreneticNamelist['iRun'] = 2
        else:
            if np.isnan(core.FreneticNamelist['iRun']):
                core.FreneticNamelist['iRun'] = 1
                

        core.FreneticNamelist['nConf'] = len(core.NE.time)
        core.FreneticNamelist['nElez0'] = NZ
        core.FreneticNamelist['Meshz0'] = meshz
        core.FreneticNamelist['SplitZ'] = splitz
        if isinstance(core.FreneticNamelist['TimeProfNE'], list):
            core.FreneticNamelist['nTimeProfNE'] = len(core.FreneticNamelist['TimeProfNE'])
        # set power
        core.FreneticNamelist['power'] = core.power
        nGrp = 0 # TODO FIXME BUG
        if nGrp == 0:
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
        if np.isnan(core.FreneticNamelist['initTemp']):
            # get average heat in each HA
            nFissHA = len(core.NE.get_fissile_SA(core, t=0))
            qHA = core.power/nFissHA
            mdot = np.zeros((N,))
            Tinl = np.zeros((N,))
            for n in core.Map.fren2serp.keys():
                # get data in assembly
                if n > N:
                    break
                whichtype = core.getassemblytype(n, core.TH.BCconfig[0], isfren=True)
                whichtype = core.TH.BCassemblytypes[whichtype]
                Tinl[n-1] = core.TH.BCdata.temperatures[whichtype]
                mdot[n-1] = core.TH.BCdata.massflowrate[whichtype]

            # estimate outlet temp. with approx. energy balance
            if core.coolant == 'Pb':
                cp = LeadProp.specific_heat(Tinl)
            else:
                raise OSError(f"Properties not implemented for coolant {core.coolant}")

            dT = np.divide(qHA, mdot, out=np.zeros_like(mdot), where=mdot!=0)/cp
            Tout = Tinl+dT
            if (Tout-Tinl).max() < 0.5:
                logger.warning("Input power may be too small to heat the coolant!")
            # Pinl = rho*9.81*h+Pout
            core.FreneticNamelist['initTemp'] = (Tinl+Tout)/2

        #  assign THdata in ad hoc keys
        iType = 1
        for HTtype, HTdata in core.TH.HTdata.items():
            core.FreneticNamelist[f'HAType{iType}'] = {}
            HAdict = core.FreneticNamelist[f'HAType{iType}']
            iHA = [i for i in HTdata.iHA if i <= N]
            HAdict['iHA'] = iHA

            # TODO only one lattice axially, more should be considered
            GEtype = core.TH.HTtoGE[HTtype][0]
            latname = core.Geometry.AssemblyDefinition[GEtype].reg[0]
            lattice = core.Geometry.LatticeGeometry[latname]
            # TODO only one pin type per lattice, more should be considered
            # sanity check
            pinname = core.Geometry.LatticeType[latname][0]
            pin = core.Geometry.Pin[pinname]
            isHomog = len(pin.materials) < 3
            n = 2 if pin.isAnnular else 1
            nmat_min = 4 if core.Geometry.Pin[pinname].isAnnular else 3
            if len(core.Geometry.Pin[pinname].materials) < nmat_min:
                if len(core.Geometry.Pin[pinname].materials) == 1:
                    pass
                elif len(core.Geometry.Pin[pinname].materials) == 2 and core.Geometry.Pin[pinname].isAnnular:
                    pass
                else:
                    raise OSError(f"Gap or Cladding not specified in pin {pinname}!")

            HAdict['flagRadHomog'] = 1 if isHomog else 0
            HAdict['nFuelPin'] = lattice.nPins
            # FIXME TODO how to account for these? Maybe better to distinguish fissile-nonfissile
            HAdict['nNonHeatedPin'] = 0

            # --- geometry
            HAdict['diamFuelPin'] = 2*pin.radii.max()/100 # the name should be dPinX
            HAdict['diamFuelPinIn'] = 2*pin.radii[0]/100 if pin.isAnnular else 0.
            # FIXME TODO how to account for these? Maybe better to distinguish fissile-nonfissile
            HAdict['diamNonHeatedPin'] = 0.

            if isHomog:
                HAdict['thickGasGap'] = 0.
                HAdict['radOutClad'] = pin.radii.max()/100
                HAdict['radInnClad'] = pin.radii.max()/100
            else:
                HAdict['thickGasGap'] = (pin.radii[n]-pin.radii[n-1])/100
                n += 1
                HAdict['radOutClad'] = pin.radii[n]/100
                HAdict['radInnClad'] = pin.radii[n-1]/100

            if hasattr(lattice, 'wrapWidth'):
                HAdict['thickBiB'] = lattice.wrapWidth/100
                HAdict['thickChanClear'] = lattice.interassWidth/100
            else:
                HAdict['thickBiB'] = 0.
                HAdict['thickChanClear'] = 1E-6

            # FIXME TODO
            HAdict['lengthInBiB'] = 0.
            HAdict['lengthOutBiB'] = 0.

            # FIXME TODO
            HAdict['diamWire'] = 0.
            HAdict['pitchWire'] = 0.

            HAdict['pitchPin'] = lattice.pitch/100. # to ensure it is float

            # FIXME TODO
            HAdict['flagBiB'] = 0
            HAdict['pinGeomType'] = 1 if pin.isAnnular else 0
            # correlations
            HAdict['FrictPeakFact'] = float(HTdata.frictMult)
            HAdict['htcMultFact'] = float(HTdata.htcMult)
            HAdict['htcCorrType'] = HTdata.htcCorr
            HAdict['frictCorrType'] = HTdata.frictCorr
            HAdict['chanCouplingType'] = HTdata.chanCouplCorr

            # TODO TODO material
            HAdict['FuelMat'] = pin.materials[1] if pin.isAnnular else pin.materials[0]
            HAdict['NonFuelMat'] = "Default"

            if isHomog:
                HAdict['GapMat'] = "Default"
                HAdict['CladMat'] = "Default"
            else:
                HAdict['GapMat'] = pin.materials[2] if pin.isAnnular else pin.materials[1]
                HAdict['CladMat'] = pin.materials[3] if pin.isAnnular else pin.materials[2]

            if lattice.wrapMat is not None:
                HAdict['BiBMat'] = lattice.wrapMat
            else:
                HAdict['BiBMat'] = "Default"

            # FIXME the radial nodes subdivision is currently fixed here.
            # The user should have the possibility to choose it, but how
            # this can be done is not trivial and should be discussed
            matlst = [1, 0, 0]
            if not isHomog:
                matlst[1] = 2
                matlst[2] = 3

            HAdict['RadMatInd'] = matlst
            HAdict['RadHeatInd'] = [1, 0, 0]
            HAdict['iMatX'] = 1. # FIXME hardcoded value
            iType += 1

        eraseKeys = ["iHA", "nFuelPin", "nNonHeatedPin", "FuelMat", "diamFuelPin",
                     "diamFuelPinIn", "thickBiB", "thickChanClear", "FrictPeakFact", "htcMultFact", "BiBMat", 
                     "htcCorrType", "frictCorrType", "chanCouplingType", "flagRadHomog", "radOutClad", "radInnClad", "thickGasGap",
                     "lengthInBiB", "lengthOutBiB", "diamWire", "pitchWire", "diamNonHeatedPin", "pitchPin", 
                     "pinGeomType", "NonFuelMat", "CladMat", "GapMat", "RadMatInd", "RadHeatInd"]
        for key in eraseKeys:
            core.FreneticNamelist.pop(key)
    else:
        setToValue = ["iHA", "nFuelPin", "nNonHeatedPin", "FuelMat", "diamFuelPin", 'initTemp',
                      "diamFuelPinIn", "thickBiB", "thickChanClear", "FrictPeakFact", "htcMultFact", "pinGeomType",
                      "BiBMat", "htcCorrType", "frictCorrType", "chanCouplingType", "flagRadHomog", "radOutClad", "radInnClad", 
                      "thickGasGap", "diamNonHeatedPin", "pitchPin", "pinGeomType" "NonFuelMat" "CladMat" "GapMat" "RadMatInd",
                      "RadHeatInd", "lengthInBiB", "lengthOutBiB", "diamWire", "pitchWire", "pitchPin", 
                      "nElems", "xLengt", "NonFuelMat", "CladMat", "GapMat", "zLayer", "nLayer", "TimeProfTH",
                      "nTimeProfTH", "iMatX", "RadMatInd", "RadHeatInd"]
        for key in setToValue:
            core.FreneticNamelist[key] = -1

    # power: the variable powtot0 was substituted by pow0 to be consistent with the general analysis and with the rest of the files
    # if hasattr(core, "NE"):
    #     core.FreneticNamelist['pow0'] = 0.
    # else:
    #     core.FreneticNamelist['pow0'] = core.power if hasattr(core, "power") else np.nan
    #     core.FreneticNamelist['power'] = 0.

    # It is possible to use another alternative of the code in order to be aligned with the unit of measure: since we use pow0 (that is in W/m) and this file is for the power
    # expressed in W, we have to use the parameter of zmesh (present in the file TH.py) to obtain W/m already in the input file for the various cases:
    if hasattr(core, "NE"):
        core.FreneticNamelist['Pow0'] = 0.
    else:
        if hasattr(core, "power"):
            try:
               # Extract the value in meters (thanks to the division by 100 in TH.py at lines 161-168)
               channel_length = core.TH.zmesh[1]-core.TH.zmesh[0]
               if channel_length <= 0:
                   raise ValueError("Channel length calculated from zmesh is less than or equal to zero.")             
            except (AttributeError, TypeError, IndexError, KeyError) as e:
               raise RuntimeError(f"CRITICAL ERROR (InpGen): Impossible to determine the channel length from 'zmesh'. Check the JSON file. Error details: {e}")
            # Calculate the W/m and save the value:
            core.FreneticNamelist['Pow0'] = core.power / channel_length
            core.FreneticNamelist['power'] = 0.0
        else:
            core.FreneticNamelist['Pow0'] = np.nan
            core.FreneticNamelist['power'] = np.nan


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
            for iHTtype, HTtype in enumerate(core.TH.HTdata.keys()):
                hatype = f'HAType{iHTtype+1}'
                if hatype not in frnnml_full.keys():
                    frnnml_full[hatype] = {}
                frnnml_full[hatype][nml] = {}
                for s in lst:
                    frnnml_full[hatype][nml][s] = core.FreneticNamelist[hatype][s]

    return frnnml_full


def inpgen(core, jsonpath):
    """
    Make FRENETIC NE/TH files if the required data are in core object.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    jsonpath : str
        Absolute path of the ``.json`` input file.

    Returns
    -------
    ``None``
    """
    # --- Prepare FRENETIC input case tree
    logger.info(f"{''.join(['-']*50)}")
    logger.info("Preparing FRENETIC input case")
    logger.info(f"{''.join(['-']*50)}")

    iwd = Path(os.path.dirname(jsonpath))

    # generate case directory-tree
    if '.json' not in jsonpath:
        jsonpath = f"{jsonpath}.json"

    jsonpath = Path(jsonpath)
    casename = jsonpath.stem

    # create temporary directory
    tempfile.tempdir = Path(iwd)
    tmp_dirname = tempfile.mkdtemp(prefix=f"tmp_",suffix=f"_{casename}")
    logger.info(f"Storing FRENETIC input in temporary directory -> {tmp_dirname}")

    if not iwd.exists():
        raise OSError(f'{str(iwd)} path does not exist!')

    tmp_casepath = mkdir(iwd.joinpath(tmp_dirname))
    AUXpath = mkdir("auxiliary", tmp_casepath)

    AUXpathGE = mkdir("geometry", AUXpath)

    if hasattr(core, "NE"):
        AUXpathNE = mkdir("NE", AUXpath)

    if hasattr(core, "TH"):
        AUXpathTH = mkdir("TH", AUXpath)

    # --- echoing json to root directory
    try:
        copyfile(f'{jsonpath}', join(AUXpath, f'{jsonpath.name}'))
    except SameFileError:
        os.remove(join(tmp_casepath, f'{jsonpath.name}'))
        logger.warning(f'Overwriting file {jsonpath.name}')
        copyfile(f'{json}', join(AUXpath, f'{jsonpath.name}'))

    # --- save core object
    corefname = 'core.h5'
    grp_name = 'core'
    myh5.write(core, grp_name, tmp_casepath.joinpath(f'{corefname}'), chunks=True, 
               compression=True, overwrite=True, skip=['NE.data'])

    # --- COMMON INPUT (common_input.inp)
    makecommoninput(core, tmp_casepath)

    # --- NE input (config.inp, macro.nml)
    if hasattr(core, "NE"):
        NE = True
        isNE1D = True if core.dim == 1 else False
    else:
        NE = False

    if NE:
        NEpath = mkdir("NE", tmp_casepath)
        # define nmix (number of different regions)
        nmix = len(core.NE.regions.keys())
        # --- write config.inp
        writeConfig(core, NEpath)
        # --- write input.inp
        makeNEinput(core, NEpath)

        # write NE data
        if hasattr(core.NE.MGClibrary, 'data') or isNE1D:
            # -- prepare data
            par_names = core.NE.MGClibrary.parameters.names
            # get temperatures couples
            if par_names != ['Tc', 'Tf'] and par_names != ['Tf', 'Tc']:
                raise OSError("Cannot build the FRENETIC input for more than 2 parameters!")

            temp = core.NE.MGClibrary.parameters.values
            # get n_groups
            unifuel = None

            # reference temperatures defined as minima
            # FIXME TODO
            mincouple = temp[0]
            Tf, Tc = mincouple
            n_groups = core.NE.MGClibrary.n_groups
            NPRE = core.NE.MGClibrary.n_prec
            # --- get kinetic parameters (equal for each material)
            iCom = list( core.NE.MGClibrary.data.keys() )[0] # get 1st parameter combo as convention
            for iReg in core.NE.regions.keys():
                mat0 = core.NE.MGClibrary.data[iCom][core.NE.regions[iReg]]
                if mat0.isfiss():
                    break

            if not mat0.isfiss():
                raise OSError("U should not be here!")

            vel = 1/mat0.inv_vel
            if core.NE.MGClibrary.n_prec == 1:
                beta0 = [mat0.beta_tot]
                lambda0 = [mat0.__dict__['lambda_tot']]
            else:
                beta0 = mat0.beta
                lambda0 = mat0.__dict__['lambda']


            H5fmt = core.FreneticNamelist['CONTROL']['iHDF5Inp']

            if H5fmt == 0:
                txt = True
            else:
                txt = False

            # --- write macro.nml
            writemacro(core, NEpath, nmix, vel, lambda0, beta0, core.NE.regions, H5fmt)

            # -- write NE_data.h5
            writeNEdata(core, NEpath, H5fmt, txt, verbose=False, )

        else:
            logger.warn('No NE object: NE input not created!')

    TH = True if hasattr(core, "TH") else False

    # make TH input (HA_*_*.txt)
    if TH:
        THpath = mkdir("TH", tmp_casepath)
        HTdatapath = mkdir("data", THpath)
        writeHTdata(core, HTdatapath)
        # make BC input (mdot.txt, temp.txt, pressout.txt, filecool.txt)
        THpath = mkdir("TH", tmp_casepath)
        # write BC .txt data
        writeBCdata(core, THpath)
        # write input.inp
        makeTHinput(core, THpath)
    else:
        pass

    auxGE(core, AUXpathGE)
    if NE:
        auxNE(core, AUXpathNE)
    if TH:
        auxTH(core, AUXpathTH)

    move('coreutils.log', join(AUXpath, 'coreutils.log'))

    new_case_path = iwd.joinpath(casename)
    if new_case_path.exists():
        rmtree(new_case_path)
        logger.warning(f'Overwriting {str(new_case_path)}')

    move(tmp_casepath, new_case_path)


def auxGE(core, AUXpathGE):
    """Generate GE auxiliary files.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    AUXpathGE : str
        Path to auxiliary NE directory.
    """
    # plot configurations
    if core.dim == 3:
        offset = core.Map.fren2serp[1]
        angle = np.radians(60)
        whichSA = None

    AUX_GE_plot = []
    asslabel = core.Geometry.assemblytypes

    if core.Geometry.plot["SAcolors"] is not None:
        colors_dict = {} 
        for idx, name  in core.Geometry.assemblytypes.items():
            colors_dict[idx] = core.Geometry.plot["SAcolors"][name]
    else:
        colors_dict = None

    # --- plot core radial configuration
    if core.Geometry.plot['radplot']:
        if core.dim != 1:
            for fmt in figfmt:
                # assembly numbers
                figname = AUXpathGE.joinpath(f'GE-rad-map.{fmt}')
                filepath = AUXpathGE.joinpath(figname)
                RadialMap(core, label=True, fren=True, whichconf="Geometry", 
                            legend=True, asstype=True, colors_dict=colors_dict,
                            figname=filepath)

        # radial configurations
        figname = AUXpathGE.joinpath(f'GE-rad-config.{fmt}')
        filepath = AUXpathGE.joinpath(figname)
        RadialMap(core, time=0, label=True, fren=True, 
                    whichconf="Geometry", dictname=asslabel,
                    legend=True, asstype=True, colors_dict=colors_dict,
                            figname=filepath)

def auxNE(core, AUXpathNE):
    """Generate NE auxiliary files.

    Parameters
    ----------
    core : :class:`coreutils.core.Core`
        Core object created with Core class.
    AUXpathNE : pathlib object
        Path to auxiliary NE directory.
    """
    # plot configurations
    if core.dim == 3:
        offset = core.Map.fren2serp[1]
        angle = np.radians(60)
        whichSA = None

    AUX_NE_plot = []
    asslabel = core.NE.assemblytypes

    if core.NE.plot['radplot'] and core.NE.plot["SAcolors"] is not None:
        colors_dict = {} 
        for idx, name  in core.NE.assemblytypes.items():
            colors_dict[idx] = core.NE.plot["SAcolors"][name]
    else:
        colors_dict = None

    # --- plot core radial configuration
    if core.NE.plot['radplot']:
        if core.dim != 1:
            for fmt in figfmt:
                # assembly numbers
                figname = f'NE-rad-map.{fmt}'
                filepath = AUXpathNE.joinpath(figname)
                RadialMap(core, label=True, fren=True, whichconf="NE", 
                            legend=True, asstype=True, colors_dict=colors_dict,
                            figname=filepath)
                # radial configurations
                for itime, t in enumerate(core.NE.time):
                    figname = f'NE-rad-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    filepath = AUXpathNE.joinpath(figname)
                    RadialMap(core, time=t, label=True, fren=True, 
                                whichconf="NE", dictname=asslabel,
                                colors_dict=colors_dict, legend=True, asstype=True, 
                                figname=filepath)
                # --- user-defined custom figures
                if "plot" in core.NE.__dict__.keys():
                    if isinstance(core.NE.plot['radplot'], list):
                        for iconf, conf in enumerate(core.NE.plot["radplot"]):
                            labeldict = None
                            asstype = True
                            figname = f'NE-rad-custom{iconf}.{fmt}'
                            filepath = AUXpathNE.joinpath(figname)
                            if "sext" in conf:
                                whichSA = core.Map.getSAsextant(conf["sext"])
                            elif "whichSA" in conf:
                                whichSA = conf["whichSA"]
                            else:
                                whichSA = None

                            radtime = conf["time"] if "time" in conf else 0

                            if "labels" in conf:
                                if len(whichSA) != len(conf["labels"]):
                                    logger.warning("plot: label numbers do not match with whichSA key!")
                                else:
                                    labeldict = {}
                                    for i, l in enumerate(conf["labels"]):
                                        for j in whichSA[i]:
                                            labeldict[j] = l
                                    whichSA = None
                                    asstype = False

                            RadialMap(core, time=radtime, label=True, fren=True, 
                                    whichconf="NE", dictname=labeldict, which=whichSA,
                                    legend=True, colors_dict=colors_dict, asstype=asstype, figname=filepath)

    # --- plot core axial configurations
    if core.NE.plot['axplot']:
        if core.dim == 3:
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
                    figname = f'NE-slab-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    filepath = AUXpathNE.joinpath(figname)
                    SlabPlot(core, time=t, figname=filepath)
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

                    figname = f'NE-ax-alltypes-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    filepath = AUXpathNE.joinpath(figname)
                    AxialGeomPlot(core, allassbly, time=t, fren=True, zcuts=True,
                                figname=filepath, legend=True, floating=True)
                    plt.close()

                    # plot all assemblies at t with FRENETIC axial nodes over the reference axial geometry
                    figname = f'NE-ax-alltypes-splitz-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    filepath = AUXpathNE.joinpath(figname)
                    AUX_NE_plot.append(figname)
                    AxialGeomPlot(core, allassbly, time=t, fren=True, zcuts=True,
                                assembly_name=True, splitz=True, figname=filepath,
                                legend=True, floating=True)
                    plt.close()

                    # plot all assemblies at t with FRENETIC axial nodes over the homogenised axial geometry
                    if core.NE.AxialConfig.homogenised:
                        figname = f'NE-ax-alltypes-splitz-homog-config{itime}-t{1E3*t:g}_ms.{fmt}'
                        filepath = AUXpathNE.joinpath(figname)
                        AxialGeomPlot(core, allassbly, time=t, fren=True, zcuts=True,
                                      assembly_name=True, showhomog=True,
                                      splitz=True, figname=filepath, legend=True, floating=True)
                        plt.close()

                    # plot y=0 SAs
                    figname = f'NE-ax-x0-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    filepath = AUXpathNE.joinpath(figname)
                    AxialGeomPlot(core, x0, time=t, fren=True, zcuts=True,
                                figname=filepath, legend=True)
                    plt.close()
                    # # plot x=0 SAs
                    # figname = f'NE-ax-y0-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    # filepath = AUXpathNE.joinpath(figname)
                    # AxialGeomPlot(core, y0, time=t, fren=True, zcuts=True,
                    #             figname=filepath, legend=True, floating=True)
                    # plt.close()
                    # # plot along 1st sextant
                    # figname = f'NE-ax-sextI-config{itime}-t{1E3*t:g}_ms.{fmt}'
                    # filepath = AUXpathNE.joinpath(figname)
                    # AxialGeomPlot(core, sextI, time=t, fren=True, zcuts=True,
                    #             figname=filepath, legend=True, floating=True)
                    # plt.close()
                    # custom plot
                    if whichSA is not None:
                        figname = f'NE-ax-config{itime}-t{1E3*t:g}_ms.{fmt}'
                        filepath = AUXpathNE.joinpath(figname)
                        AxialGeomPlot(core, SAs, time=t, fren=True, zcuts=True,
                                    figname=filepath, legend=True)


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
                for conftype in ['HT', 'BC']:
                    asslabel = core.TH.__dict__[f"{conftype}assemblytypes"]
                    # assembly numbers
                    figname = f'{conftype}-rad-map.{fmt}'
                    filepath = AUXpathTH.joinpath(figname)
                    RadialMap(core, label=True, fren=True, whichconf=conftype, 
                                legend=True, asstype=True, figname=filepath)
                    # radial configurations
                    for itime, t in enumerate(core.TH.__dict__[f"{conftype}time"]):
                        figname = f'{conftype}-rad-config{itime}-t{1E3*t:g}_ms.{fmt}'
                        filepath = AUXpathTH.joinpath(figname)
                        RadialMap(core, time=t, label=True, fren=True, 
                                whichconf=conftype, dictname=asslabel,
                                legend=True, asstype=True, figname=filepath)


    # move files in directory
    for f in AUX_TH_plot:
        try:
            move(f, join(AUXpathTH, f))
        except SameFileError:
            os.remove(join(AUXpathTH, f))
            logger.warning('Overwriting file {}'.format(f))
            move(f, join(AUXpathTH, f))


def makecommoninput(core, path):
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
    filepath = Path(path).joinpath('common_input.inp')

    if filepath.exists():
        os.remove(str(filepath))
        logger.warning(f'Overwriting file {str(filepath)}')

    f = io.open(filepath, 'w', newline='\n')
    isSym = core.FreneticNamelist["PRELIMINARY"]['isSym']
    N = int(core.nAss/6*isSym+1) if isSym else core.nAss
    for namelist in frnnml.files["common_input.inp"]:
        f.write(f"&{namelist}\n")
        for key, val in core.FreneticNamelist[namelist].items():
            # format value with FortranFormatter utility
            val = fortranformatter(val)
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

    return Path(path)


