import os
import json
import numpy as np
import pandas as pd
import logging
import coreutils
import shutil as sh
import serpentTools as st
import matplotlib.pyplot as plt
from coreutils.tools.utils import uppcasedict, lowcasedict
from os import path
from pathlib import Path
from serpentTools import read
from serpentTools.settings import rc as rcst
from copy import deepcopy as copy
from matplotlib import rc
from os.path import join
from itertools import product
from collections import OrderedDict
from re import findall

logger = logging.getLogger(__name__)

usetex = True if sh.which('latex') else False

rc("font", **{"family": "sans-serif", "sans-serif": ["Helvetica"]})
rc("text", usetex=usetex)

scatt_keys = [*list(map(lambda z: "infS"+str(z), range(2))),
            *list(map(lambda z: "infSp"+str(z), range(2)))]
xsdf_keys = ['infTot', 'infAbs', 'infDiffcoef', 'infTranspxs', 'infCapt',
            'infRemxs', 'infFiss', 'infNsf', 'infRabsxs']
ene_keys = ['infNubar', 'infInvv', 'infKappa',  'infChit', 'infChip', 'infChid']

serp_keys = [*scatt_keys, *xsdf_keys, *ene_keys, 'infFlx']
serp_phot_keys = ['KermaPh', 'Rayleigh', 'Compton', 'PProduction', 'Photoelectric', 'nuPh', 'TotPhProd']

sumxs = ['Tot', 'Abs', 'Rem', 'Rabs']
indepdata = ['Capt', 'Fiss', 'S0', 'Nubar', 'Diffcoef', 'Chid', 'Chip']
basicdata = ['Fiss', 'Nubar', 'S0', 'Sp0', 'Chit', 'Nsf']
kinetics = ['lambda', 'beta']
alldata = list(set([*sumxs, *indepdata, *basicdata, *kinetics]))

collapse_xs = ['Fiss', 'Capt', *list(map(lambda z: "S"+str(z), range(0, 2))),
               *list(map(lambda z: "Sp"+str(z), range(0, 2))), 'Invv', 'Diffcoef', 'Kerma']
collapse_xsf = ['Nubar', 'Chid', 'Chit', 'Chip', 'FissEn']

units = {'Chid': '-', 'Chit': '-', 'Chip': '-', 'Tot': 'cm^{-1}',
        'Capt': 'cm^{-1}', 'Abs': 'cm^{-1}', 'Fiss': 'cm^{-1}',
        'NuSf': 'cm^{-1}', 'Rem': 'cm^{-1}', 'Transp': 'cm^{-1}',
        'FissEn': 'MeV', 'S': 'cm^{-1}', 'Nubar': '-', 'Invv': 's/cm',
        'Difflenght': 'cm', 'Diffcoef': 'cm', 'Flx': 'a.u.',
        'Kerma': 'J/cm'}

xslabels = {'Chid': 'delayed fiss. emission spectrum', 'Chit': 'total fiss. emission spectrum',
            'Chip': 'prompt fiss. emission spectrum', 'Tot': 'Total xs',
            'Capt': 'Capture xs', 'Abs': 'Absorption xs', 'Fiss': 'Fission xs',
            'NuSf': 'Fiss. production xs', 'Rem': 'Removal xs', 'Transp': 'Transport xs',
            'FissEn': 'Fiss. energy', 'S': 'Scattering xs', 'Nubar': 'neutrons by fission',
            'Invv': 'Inverse velocity', 'Difflenght': 'Diff. length', 'Diffcoef': 'Diff. coeff.',
            'Flx': 'Flux spectrum', 'Kerma': 'KERMA coefficient', 'Rabs': 'Reduced absorption'}

nemtab2coreutils = {"transport": "Transp" ,"absorption": "Abs" ,
                    "nuFission": "Nsf" ,"kappaFission": "FissEn" ,
                    "P0": "S0" ,
                    "promptFissionSpectrum": "Chit", # not a bug: done to ensure consistency between FENNECS and FRENETIC codes in steady state
                    "inverseVelocity": "Invv" , "lambda": "lambda",
                    "beta": "beta"}

def readSerpentRes(datapath, energygrid, T, beginswith,
                   egridname=False):
    """Read Serpent res file with the serpentTools package

    Parameters
    ----------
    datapath : str
        Absolute path to NE data
    energygrid: list
        List containing the energy group boundaries.
    T: tuple
        Temperatures of fuel and coolant, in this order.
    beginswith : str
        Prefix of whole name of the file to be read. It can be the name
        of the file, without extension.
    egridname: str
        Name of the energy grid.

    Returns
    -------
    res: dict
        dict of serpentTools parser object whose keys are the fuel and coolant temperatures.
    det: dict
        dict of serpentTools parser object for detectors whose keys are the fuel and coolant temperatures.

    Raises
    ------
    OSError
        If there is an issue with the NEdata default path inside ``coreutils``.
    OSError
        If ``serpent`` directory does not exist in the ``datapath`` path.

    """
    # -- serpentTools settings
    # st.settings.rc['xs.variableGroups'] = ['kinetics', 'xs', 'xs-prod',
    #                                        'gc-meta']

    missinT = False
    if T is not None:
        Tf, Tc = T

    nE = len(energygrid)-1
    egridname = egridname if egridname else f"{nE}G"
    pwd = Path(__file__).parent
    if not path.isdir(datapath):
        pwd = Path(__file__).parent.parent.parent
        if 'coreutils' not in str(pwd):
            raise OSError(f'Check coreutils tree for NEdata: {pwd}')
        # look into default NEdata dir
        logger.warning(f"{datapath} not found, looking in default tree...")
        datapath = str(pwd.joinpath('NEdata', f'{egridname}'))

    # look into serpent folder
    if Path(path.join(datapath, "serpent")).exists():
        spath = path.join(datapath, "serpent")
    else:
        raise OSError(f'"serpent" dir does not exist in {datapath}')
    # check for temperatures
    if T is not None:
        fname = f"{beginswith}_Tf_{Tf:g}_Tc_{Tc:g}"
        if Path(path.join(spath, f"Tf_{Tf:g}_Tc_{Tc:g}")).exists():
            spath = path.join(spath, f"Tf_{Tf:g}_Tc_{Tc:g}")
        elif Path(path.join(spath, f"Tc_{Tc:g}_Tf_{Tf:g}")).exists():
            spath.join(spath, f"Tc_{Tc:g}_Tf_{Tf:g}")
    else:
        fname = path.join(spath, beginswith)    

    if '_res.m' not in str(fname):
        basename = fname
        fname = f'{str(basename)}_res.m'
        dname = f'{str(basename)}_det0.m'
    else:
        fname = fname
        basename = fname.split("_res.m")[0]
        dname = f'{basename}_det0.m'

    fname = path.join(spath, fname)
    if Path(fname).exists():
        res = read(fname)
    else:
        res = None

    dname = path.join(spath, dname)
    if Path(dname).exists():
        det = read(dname)
    else:
        det = None

    return res, det


def Homogenise(materials, volume, mixname, fixdata):
    """Homogenise multi-group parameters.

    Parameters
    ----------
    materials : dict
        Dict of ``NEMaterial`` objects to be mixed. The keys are the 
        name of the materials.
    volume : dict
        Dict containing the volume to mix material objects. The keys are the 
        name of the materials.
    mixname : str
        Name of the mixed material.

    Returns
    -------
    homogmat: ``NEMaterial``
        Object containing the homogenised material
    """
    collapse_xs = ['Fiss', 'Capt', *list(map(lambda z: "S"+str(z), range(2))),
                    *list(map(lambda z: "Sp"+str(z), range(2))), 'Invv', 'Transp', 'Kerma']
    collapse_xsf = ['Nubar', 'Chid', 'Chit', 'Chip', 'FissEn']
    inherit = ['NPF', 'nE', 'egridname', 'beta', 'beta_tot', 'energygrid',
               'lambda', 'lambda_tot', 'L', 'P1consistent', 'use_nxn', 'scat_n1n_exists']

    # compute normalisation constants
    for i, name in enumerate(materials.keys()):
        mat = materials[name]
        if i == 0:
            # instantiate new material
            homogmat = NEMaterial(init=True)
            setattr(homogmat, 'UniName', mixname)

            for attr in inherit:
                setattr(homogmat, attr, getattr(mat, attr))

            G = homogmat.nE
            TOTFLX = np.zeros((G, ))
            FISSRR = np.zeros((G, ))
            FISPRD = np.zeros((G, ))

        if mat.data_origin == 'Serpent':
            w = volume['homog'][name]/volume['heter'][name]
        else:
            w = volume['homog'][name]

        TOTFLX += w*mat.Flx  # total flux
        FISSRR += w*mat.Flx*mat.Fiss  # fiss. reaction rate
        FISPRD += w*mat.Flx*mat.Fiss*mat.Nubar  # fiss. production

    nMat = i
    setattr(homogmat, 'Flx', TOTFLX)

    for key in [*collapse_xs, *collapse_xsf]: # loop over data
        for i, name in enumerate(materials.keys()): # sum over sub-regions
            mat = materials[name].__dict__
            flx = materials[name].Flx

            if materials[name].data_origin == 'Serpent':
                w = volume['homog'][name]/volume['heter'][name]
            else:
                w = volume['homog'][name]

            # homogdata = np.dot(flux, data)/sum(flux)
            # --- cross section and inverse of velocity
            if key in collapse_xs:
                # if key in ["S1", "Sp0", "Sp1"]:
                #     if not hasattr(homogmat, key):
                #         continue

                if i == 0:
                    homogmat.__dict__[key] = w*mat[key]*flx
                else:
                    homogmat.__dict__[key] += w*mat[key]*flx

            elif key in collapse_xsf:
                if mat['Fiss'].max() <= 0:
                    notfiss = True
                else:
                    notfiss = False

                if key in ['Nubar', 'FissEn']:
                    if i == 0:
                        homogmat.__dict__[key] = w*mat[key]*flx*mat['Fiss']
                    elif notfiss:
                        continue
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx*mat['Fiss']
                elif key == 'Chid':
                    if i == 0:
                        homogmat.__dict__[key] = w*mat[key]*flx*mat['Nsf']
                    elif notfiss:
                        continue
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx*mat['Nsf']
                else:   # Chip and Chit
                    if i == 0:
                        homogmat.__dict__[key] = w*mat[key]*flx*mat['Nsf']
                    elif notfiss:
                        continue
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx*mat['Nsf']
            else:
                continue
    # normalise group constants
    hd = homogmat.__dict__
    for key in ['Nubar', 'FissEn']:
        tmp = np.divide(hd[key], FISSRR, where=FISSRR!=0)
        hd[key] = tmp
    for key in ['Chit', 'Chip', 'Chid']:
        tmp = np.divide(hd[key], FISPRD, where=FISPRD!=0)
        hd[key] = tmp
    for key, data in homogmat.__dict__.items():
        if key in collapse_xs:
            tmp = np.divide(data, TOTFLX, where=TOTFLX!=0)
            hd[key] = tmp

    homogmat.add_missing_xs()
    if fixdata:
        homogmat.repair_xs()

    return homogmat


class NEMaterial():
    """Create material regions with multi-group constants.

    Parameters
    ----------
    UniName: str
        Universe name.
    energygrid: iterable
        Energy group structure containing nE+1 group boundaries where nE is the
        number of energy groups.
    datapath: str, optional
        Path to the file containing the data, by default ``None``. If ``None``,
        data are taken from the local database.
    egridname : str, optional
        Name of the energy group structure, by default ``None``.
    h5file: object
        h5 group from .h5 files.
    reader: str``
        Type or reader. It can be ``'serpent'``, ``'json'`` or ``'txt'``.
    serpres: :class:`serpentTools.ResultsReader`
        Object created parsing the _res.m Serpent file with ``serpentTools``
    basename : bool or str
        if not ``False``, base name is used to compose the filenames, which 
        needs to be in the form <basename>_Tf_XXX_Tc_XXX. 
    temp: tuple
        if ``basename`` is not None, directories in the form 
        "Tf_{}_Tc_{}" are searched  and "Tf_{}_Tc_{}" suffix 
        is attached to the file name
    fixdata: bool, optional
        Flag to check and ensure data consistency, by default ``True``.
    init: bool, optional
        Flag to initialise the object as empty, by default ``False``

    Attributes
    ----------
    nE: int
        Number of energy groups.
    egridname: str
        Name of the energy grid.
    energygrid: list
        List of energy group boundaries.
    UniName: str
        Name of the material.
    NPF: int
        Number of neutron precursors families.
    L: int
        Scattering anisotropy order
    Tot: np.array
        1D array of length ``nE`` with the total cross section in cm^-1.
    Abs: np.array
        1D array of length ``nE`` with the absorption cross section in cm^-1.
    Capt: np.array
        1D array of length ``nE`` with the capture cross section in cm^-1.
    Fiss: np.array
        1D array of length ``nE`` with the fission cross section in cm^-1.
    Rem: np.array
        1D array of length ``nE`` with the removal cross section in cm^-1.
    Transp: np.array
        1D array of length ``nE`` with the transport cross section in cm^-1.
    NuSf: np.array
        1D array of length ``nE`` with the fission production cross section in cm^-1.
    Diffcoef: np.array
        1D array of length ``nE`` with the diffusion coefficient in cm.
    Difflength: np.array
        1D array of length ``nE`` with the diffusion length in cm.
    S0: np.array
        2D array of size ``(nE, nE)`` with the scattering matrix cross section in cm^-1.
    Chit: np.array
        1D array of size ``nE`` with the total fission emission spectrum.
    Chip: np.array
        1D array of size ``nE`` with the prompt fission emission spectrum.
    Chid: np.array
        1D array of size ``nE`` with the delayed fission emission spectrum.
    Nubar: np.array
        1D array of size ``nE`` with the number of neutrons emitted by fission.
    Invv: np.array
        1D array of size ``nE`` with the inverse of the neutron velocity in s/cm.
    lambda: np.array
        1D array of size ``NPF`` with the decay constants of the precursors.
    beta: np.array
        1D array of size ``NPF`` with the delayed neutron fracitons.
    Flx: np.array
        1D array of size ``nE`` with the flux energy spectrum in arbitrary units.

    
    """

    def __init__(self, UniName=None, energygrid=None, datapath=None,
                 egridname=None, h5file=None, reader='json', serpres=None,
                 serpdet=None, basename=False, temp=False, fixdata=True,
                 init=False, energygridPH=None, use_nxn=False, P1consistent=False):

        if h5file:
            if isinstance(h5file, dict):
                for k, v in h5file.items():
                    if type(v) is bytes:
                        v = v.decode()
                    self.__dict__[k] = v
            elif isinstance(h5file, str):
                raise OSError('To do')
            else:
                msg = f"h5file must be dict or str, not {type(h5file)}"
                raise TypeError(msg)
        else:
            if init:
                return

            if temp:
                Tf, Tc = temp
            nE = len(energygrid)-1
            egridname = egridname if egridname else f"{nE}G"
            pwd = Path(__file__).parent

            if serpres is None:
                self.data_origin = "serpent"
                if datapath is None:
                    pwd = Path(__file__).parent.parent.parent
                    if 'coreutils' not in str(pwd):
                        raise OSError(f'Check coreutils tree for NEdata: {pwd}')
                    # look into default NEdata dir
                    datapath = str(pwd.joinpath('NEdata', f'{egridname}'))
                    filename = UniName
                elif not path.isdir(datapath):
                    pwd = Path(__file__).parent.parent.parent
                    if 'coreutils' not in str(pwd):
                        raise OSError(f'Check coreutils tree for NEdata: {pwd}')
                    filename = copy(datapath)
                    datapath = str(pwd.joinpath('NEdata', f'{egridname}'))
                else:
                    filename = basename

                if reader == 'json':
                    # look into json folder
                    if Path(path.join(datapath, "json")).exists():
                        jpath = path.join(datapath, "json")
                    else:
                        jpath = datapath

                    if '.json' not in str(filename):
                        filename_ext = f'{str(filename)}.{reader}'
                    else:
                        filename_ext = filename

                    # check for temperatures
                    if temp:
                        dirTfTc = f"Tf_{Tf:g}_Tc_{Tc:g}"
                        dirTcTf = f"Tc_{Tc:g}_Tf_{Tf:g}"

                        if Path(path.join(jpath, dirTfTc)).exists():
                            jpath = path.join(jpath, dirTfTc)
                        elif Path(path.join(jpath, dirTcTf)).exists():
                            jpath = path.join(jpath, dirTcTf)

                    fname = path.join(jpath, filename_ext)

                    # if '.json' not in str(filename):
                    #     fname = f'{str(filename)}.{reader}'
                    # else:
                    #     fname = filename

                    if Path(fname).exists():
                        self._readjson(fname)
                        self.data_origin = "json"
                    else:
                        logger.debug(f'{fname} not found!')
                        reader = 'nemtab'

                if reader == 'nemtab':
                    self.data_origin = "NEMTAB"
                    # look into NemTab folder
                    if Path(path.join(datapath, "nemtab")).exists():
                        tpath = path.join(datapath, "nemtab")
                    else:
                        tpath = datapath

                    fname = path.join(tpath, filename)

                    if '.XS' not in str(fname):
                        fname_ext = f'{str(fname)}.XS'
                    else:
                        fname_ext = filename

                    fname = path.join(tpath, fname_ext)
                    if Path(fname).exists():
                        param, param_combos, data, G = data_nemtab = self._readnemtab(fname)
                        if G != nE:
                            raise OSError(f"Inconsistent number of groups for {fname}:{G}!={nE}")
                        # temporary patch: just take the 1st combination
                        P1, P2 = param_combos[0]
                        if P1 > P2:
                            Tf = P1
                            Tc = P2
                        else:
                            Tf = P2
                            Tc = P1
                        # assign basic constants
                        for key, val in data[0.0][0].items():
                            if key == "Abs" and use_nxn:
                                self.__dict__["Rabs"] = val
                            elif key == "S0" and use_nxn:
                                self.__dict__["Sp0"] = val
                            else:
                                self.__dict__[key] = val
                        # assign kinetic parameters
                        for key in data[0.0].keys():
                            if isinstance(key, str):
                                self.__dict__[key] = data[0.0][key]
                        self.Chip = self.Chit*1
                        # PATCH: add fictitious Fiss XS (keeping ESigF constant)
                        Ef = 200.0*1.602176634E-13  # J
                        self.Fiss = self.FissEn/Ef
                        self.FissEn = np.asarray([Ef/1.602176634E-13]*G)
                        check = self.FissEn*self.Fiss
                        # WATCH OUT Sp0+Rabs treatment?
                    else:
                        logger.debug(f'{fname} not found!')
                        reader = 'txt'

                if reader == 'txt':
                    self.data_origin = "txt"
                    # look into txt folder
                    if Path(path.join(datapath, "txt")).exists():
                        tpath = path.join(datapath, "txt")
                    else:
                        tpath = datapath

                    if temp:
                        dirTfTc = f"Tf_{Tf:g}_Tc_{Tc:g}"
                        dirTcTf = f"Tc_{Tc:g}_Tf_{Tf:g}"
                        if Path(path.join(tpath, dirTfTc)).exists():
                            spath = path.join(tpath, dirTfTc, filename)
                        elif Path(path.join(tpath, dirTcTf)).exists():
                            path.join(tpath, dirTcTf, filename)

                    else:
                        fname = path.join(tpath, filename)
                    
                    if '.txt' not in str(fname):
                        fname_ext = f'{str(fname)}.{reader}'
                    else:
                        fname_ext = filename

                    fname = path.join(tpath, fname_ext)
                    if Path(fname).exists():
                        self._readtxt(fname, nE)
                    else:
                        raise OSError(f'{fname} not found!')
            else:
                self._readserpentres(serpres, UniName, nE, egridname)
                self.data_origin = "Serpent"
                if energygridPH is None:
                    nEPH = 0
                else:
                    nEPH = len(energygridPH) - 1
                self._readserpentdet(serpdet, UniName, nE, nEPH)

            self.nE = nE
            # FIXME TODO
            self.egridname = egridname
            self.energygrid = energygrid

            if energygridPH is not None:
                self.egridnamePH = egridnamePH
                self.energygridPH = energygridPH
                self.nEPH = len(self.energygridPH) - 1

            self.UniName = UniName
            self.P1consistent = P1consistent
            self.use_nxn = use_nxn

            try:
                self.NPF = (self.beta).size
            except AttributeError:
                logger.info('Kinetic parameters not available!')
                self.NPF = 1

            # --- complete data and perform sanity check
            L = 0
            datastr = list(self.__dict__.keys())
            # //2 since there are 'S' and 'Sp'
            S = sum('S' in s for s in datastr)//2
            self.L = S if S > L else L  # get maximum scattering order

            self.add_missing_xs()

            if fixdata:
                self.repair_xs()

    def _readjson(self, path):
        """
        Read data from json file.

        Parameters
        ----------
        path: str
            Path to json file.

        Returns
        -------
        None.

        """
        with open(path) as f:
            data = json.load(f)
        for k, v in data.items():
            if isinstance(v, list):
                self.__dict__[k] = np.asarray(v)
            else:
                self.__dict__[k] = v

        return None

    def _readserpentres(self, serpres, UniName, nE, egridname):
        """Transform :class:`serpentTools.ResultsReader` object 
            into :class:``coreutils.NEMaterial`` object.

        Parameters
        ----------
        serpres : dict
            Dictionary of :class:`serpentTools.ResultsReader` objects.
        UniName : str
            Name of the material.
        nE: int
            Number of energy groups.
        egridname: str
            Name of the energy grid.

        Raises
        ------
        OSError
            If the material indicated by ``UniName`` is not available.
        OSError
            If the number of energy groups indicated by ``nE`` is not available.
        """        
        data = None
        for res in serpres.values():
            try:
                data = res.getUniv(UniName, 0, 0, 0)
            except KeyError:
                continue

        if data is None:
            raise OSError(f'{UniName} data not available in Serpent files!')

        if len(data.infExp['infAbs']) != nE:
            raise OSError(f'{UniName} energy groups do not match with \
                          input grid!')

        selfdic = self.__dict__
        for my_key in serp_keys:
            if my_key.startswith('infS') or my_key.startswith('infSp'):
                vals = np.reshape(data.infExp[my_key], (nE, nE), order='F')
                rsd = np.reshape(data.infUnc[my_key], (nE, nE), order='F')
            else:
                vals = data.infExp[my_key]
                rsd = data.infUnc[my_key]

            if rsd.size > 1:
                max_rsd = rsd.max().max()
            else:
                max_rsd = rsd.max()

            if max_rsd*100 > 1:
                g_max = np.argmax(rsd)
                logger.warning(f'Serpent PRSD of {my_key} = {max_rsd*100:.1f} in group={g_max+1} in {UniName}.')

            if 'Kappa' in my_key:
                selfdic['FissEn'] = vals
            else:
                new_key = my_key.split('inf')[1]
                if "xs" in new_key:
                    new_key = new_key.split('xs')[0]
                selfdic[new_key] = vals

        # kinetics parameters
        selfdic['beta'] = res.resdata['fwdAnaBetaZero'][::2]
        selfdic['beta_tot'] = selfdic['beta'][0]
        if len(selfdic['beta']) > 1:
            selfdic['beta'] = selfdic['beta'][1:]
        else:
            selfdic['beta'] = np.array([selfdic['beta_tot']])
        # this to avoid confusion with python lambda function
        selfdic['lambda'] = res.resdata['fwdAnaLambda'][::2]
        selfdic['lambda_tot'] = selfdic['lambda'][0]
        if len(selfdic['lambda']) > 1:
            selfdic['lambda'] = selfdic['lambda'][1:]
        else:
            selfdic['lambda'] = np.array([selfdic['lambda_tot']])

    def _readserpentdet(self, serpdet, UniName, nE, nEPH):
        """Transform :class:`serpentTools.ResultsReader` object 
            into :class:``coreutils.NEMaterial`` object.

        Parameters
        ----------
        serpdet : dict
            Dictionary of :class:`serpentTools.DetectorsReader` objects.
        UniName : str
            Name of the material.
        nE: int
            Number of energy groups.
        nEPH: int
            Number of photon energy groups.

        Raises
        ------
        OSError
            If the material indicated by ``UniName`` is not available.
        OSError
            If the number of energy groups indicated by ``nE`` is not available.
        """
        data = None
        data_name = f"{UniName}__nkerma"

        for det in serpdet.values():
            if data_name in det.detectors.keys():
                det_data = det[data_name]
                if len(det_data.energy) != nE:
                    raise OSError(f'{UniName} energy groups in _det do not match with \
                                    input grid!')

                data = det_data.tallies

        if data is None:
            logger.warning(f'{UniName} data not available in Serpent files!')
        else:
            selfdic = self.__dict__

            selfdic["Kerma"] = data[::-1]
            rsd = det_data.errors

            if rsd.max()*100 > 1:
                g_max = np.argmax(rsd)
                logger.warning(f'Serpent PRSD of kerma = {rsd.max()*100} in group={g_max+1} in {UniName}.')

        # FIXME TODO work in progress
        if nEPH > 0:
            for mykey in serp_phot_keys:
                data_name = f"{UniName}__{mykey}"
                # loop over elements in this universe
                # TODO
                det_data = det[data_name]
                if len(det_data.energy) != nEPH:
                    raise OSError(f'{UniName} PH energy groups in _det do not match with \
                                    input grid!')

                data = det_data.tallies

    def _readtxt(self, fname, nE):
        """
        Parse the material data from a .txt file.

        Macro-group constants are parsed from a formatted file with column-wise
        data separated by headers beginning with "#" and the name of the data:
            * Tot: total cross section [cm^-1]
            * Transp: transport cross section [cm^-1]
                        It is defined as total_xs-avg_direction*scattering_xs
                        according to P1 approximation.
            * Diffcoef: diffusion coefficient [cm]
                        It is defined as 1/(3*Transp).
            * Abs: absorption cross section [cm^-1]
                   It is the sum of Capt and Fiss cross sections.
            * Capt: capture cross section [cm^-1]
            * Fiss: fission cross section [cm^-1]
            * Rem: removal cross section [cm^-1]
                    It is the sum of Abs and group-removal.
            * Chit: total emission spectrum [-]
            * Chip: prompt emission spectrum [-]
            * Chid: delayed emission spectrum [-]
            * Nsf: fission production cross section [cm^-1]
            * Nubar: neutron multiplicities [-]
            * FissEn: average fission deposited heat [MeV]
            * Invv: particle inverse velocity [s/cm]
            * S0, S1, S2,... : scattering matrix cross section [cm^-1]
            * Sp0, Sp1, Sp2,... : scattering production matrix cross section
                                [cm^-1]
            * beta: delayed neutron fractions [-]
            * lambda: precursors families decay constant [-]

        Parameters
        ----------
        fname : string
            Material data file name.
        nE : int
            Number of energy groups.

        Returns
        -------
        None.

        """
        selfdic = self.__dict__
        G = None

        lines = open(fname).read().split('\n')

        for il, line in enumerate(lines):

            if line.startswith('#'):
                key = (line.split('#')[1]).strip()
                matrix = None

            elif line == '':
                continue

            else:

                data = np.asarray([float(val) for val in line.split()])
                if G is None:
                    G = len(data)

                if G != nE:
                    raise OSError('Number of groups in line %g is not \
                                  consistent!', il)

                if key.startswith('S') or key.startswith('Sp'):
                    # multi-line data (scattering matrix)
                    if matrix is None:
                        matrix = np.asarray(data)
                    else:
                        matrix = np.c_[matrix, data]

                    if matrix.shape == (G, G):
                        selfdic[key] = matrix.T
                    elif matrix.shape == (G, ):
                        selfdic[key] = matrix
                else:
                    # single-line data (scattering matrix)
                    selfdic[key] = np.asarray(data)

    def _readnemtab(self, path):
        """
        Read data from json file.

        Parameters
        ----------
        path: str
            Path to json file.

        Returns
        -------
        None.

        """
        with open(path) as f:
            flines = f.readlines()

        init = True
        G = -1
        F = -1
        # get preliminary parameters
        for iline, line in enumerate(flines):
            # parse info on file structure
            if iline == 0:
                parameters_name = tuple(line.split()[1:])
                n_param = len(parameters_name)
            elif iline == 1:
                n_pts_per_param = [int(n) for n in line.split()]
                n_combos = np.prod(n_pts_per_param)
                param_values = OrderedDict()
                param_list = []
                i_count = 0

            if iline > 1:
                # assign parameters
                if i_count < n_param:
                    param_values[parameters_name[i_count]] = [float(p) for p in line.split()]
                    param_list.append([float(p) for p in line.split()])
                    i_count += 1
                elif i_count == n_param and init:
                    init = False
                    param_combos = []
                    # compute combinations
                    param_combos = tuple([p[::-1] for p in product(*param_list[::-1])])
                    gconst = {}
                    data_start_line = iline

                if not init:

                    if line == "* \n" or line == "*\n":
                        continue
                    elif "* GROUP" in line:
                        # parse group number
                        grps = findall("\d+", line)
                        if len(grps) == 1:
                            g = int(grps[0])
                        elif len(grps) == 2:
                            g = int(grps[0])
                            g1 = int(grps[1])
                        else:
                            g = 0
                            if len(grps) != G:
                                F = int(grps[-1])
                    elif line.startswith("* "):
                        if "BURNUP" in line:
                            i_data_type = -1
                        elif "-" not in line:
                            # parse the data type (transport, absorption,...)
                            data_type = line.split()[1]
                            if i_data_type == 0 and G < 0:
                                G = g + 0
                            if "lambda" == data_type and g > 0:
                                F = g + 0
                                break

                            i_data_type += 1
                    elif "END" in line:
                        continue

        for iline, line in enumerate(flines[data_start_line: ]):
            if not init:

                if line == "* \n" or line == "*\n":
                    continue
                elif "* GROUP" in line:
                    i_combo = 0
                    # parse group number
                    grps = findall("\d+", line)
                    if len(grps) == 1:
                        g = int(grps[0])
                    elif len(grps) == 2:
                        g = int(grps[0])
                        g1 = int(grps[1])
                    else:
                        g = 1
                elif "* " in line:
                    if "BURNUP" in line:
                        # parse burnup level
                        BU = float(findall("\d+", line)[0])
                        gconst[BU] = OrderedDict()
                        for i_combo in range(n_combos):
                            gconst[BU][i_combo] = {}
                        i_data_type = -1
                    elif "-" not in line:
                        data_type = line.split()[1]
                        core_data_type = nemtab2coreutils[data_type]
                        for i_combo in range(n_combos):
                            if data_type == "P0":
                                gconst[BU][i_combo][core_data_type] = -np.ones((G, G))
                            else:
                                if data_type in ["promptFissionSpectrum", "inverseVelocity"]:
                                    gconst[BU][core_data_type] = -np.ones((G,))
                                elif data_type in ["beta", "lambda"]:
                                    gconst[BU][core_data_type] = -np.ones((F,))
                                else:
                                    gconst[BU][i_combo][core_data_type] = -np.ones((G,))
                        i_combo = 0
                        i_data_type += 1
                elif "END" in line:
                    continue
                else:
                    data_lst = [float(v) for v in line.split()]
                    for data in data_lst:
                        if data_type == "P0":
                            gconst[BU][i_combo][core_data_type][g1-1, g-1] = data
                            i_combo += 1

                        else:
                            if data_type in ["beta", "lambda"]:
                                gconst[BU][core_data_type][g-1] = data
                                g += 1

                            elif data_type in ["promptFissionSpectrum", "inverseVelocity"]:
                                gconst[BU][core_data_type][g-1] = data
                                g += 1
                            else:
                                gconst[BU][i_combo][core_data_type][g-1] = data
                                i_combo += 1

        return param_values, param_combos, gconst, G

    def patch_nemtab(self):
        print("Applying the patch for NemTab format...")


    def getxs(self, key, pos1=None, pos2=None):
        """Get material data (for a certain energy group, if needed).

        Parameters
        ----------
        key : str
            User selected nuclear data.
        pos1 : int, optional
            Departure energy group for scattering matrix. If not provided,
            data over all the energy groups are returned.
            The default is ``None``.
        pos2 : int, optional
            Arrival energy group for scattering matrix. If not provided,
            data over all the energy groups are returned.
            The default is ``None``.

        Returns
        -------
        vals : numpy.ndarray
            1-D ``numpy.ndarray`` with G/NPF (groups) rows.

        """
        if pos1 is None and pos2 is None:
            try:
                vals = self.__dict__[key]
            except KeyError:
                if key.startswith('S') or key.startswith('Sp'):
                    # set higher moments to zero if not available
                    vals = self.__dict__['S0']*0
                else:
                    raise OSError(f'{key} data not available!')
        else:
            if key.startswith('S') or key.startswith('Sp'):
                if pos2 is None:
                    raise OSError('Two coordinates needed for %s data' % key)
                else:
                    vals = self.__dict__[key][pos1, pos2]
            else:
                vals = self.__dict__[key][pos1]

        return vals

    def plot(self, what, depgro=False, family=1, ax=None, figname=None,
             normalise=True, **kwargs):
        """Plot multi-group data from the object.

        Parameters
        ----------
        what : str
            Data to be plotted.
        depgro : int, optional
            Departure energy group, by default ``False``. This argument is needed to plot
            the scattering cross section.
        family : int, optional
            Number of neutron precursor family, by default 1
        ax : `matplotlib.axes.Axes`, optional
            Ax on which to plot the data, by default `None`. If not provided,
            a new figure is created.
        figname : str, optional
            Figure name with its extension, by default ``None``
        normalise : bool, optional
            Normalisation flag, by default ``True``

        Raises
        ------
        OSError
            If the ``depgro`` argument is not provided when the data to be plotted
            is the scattering matrix.
        """        
        E = self.energygrid
        ax = ax or plt.gca()
        xs = self.__dict__[what]
        whatlabel = xslabels[what]
        if 'S' in what:
            if depgro:
                xs = xs[depgro, :]
                whatlabel = f'{xslabels[what]} from g={depgro}'
            else:
                raise OSError('Material.plot: depgro variable needed!')
        elif what == 'Chid':
            xs = xs[family-1, :]
        elif what == 'Flx':
            if normalise:
                u = np.log(self.energygrid/self.energygrid[0])
                xs = xs/np.diff(-u)


        if 'Chi' in what:
            xs = xs/xs.dot(-np.diff(E))

        if 'S' in what:
            uom = units['S']
        else:
            uom = units[what]

        if 'Flx' in what and normalise:
            whatlabel = 'Flux per unit lethargy'

        if usetex:
            uom = f'$\\rm {uom}$'

        if 'label' not in kwargs.keys():
            kwargs['label'] = what

        plt.stairs(xs, edges=E, baseline=None, **kwargs)
        ax.set_xlabel('E [MeV]')
        ax.set_ylabel(f'{whatlabel} [{uom}]')
        ax.set_xscale('log')
        if what not in ['Nubar', 'Chid', 'Chip', 'Chit']:
            ax.set_yscale('log')

        plt.grid(which='both', alpha=0.2)
        if figname:
            plt.tight_layout()
            plt.savefig(f"{figname}.png")

    def perturb(self, what, howmuch, depgro=None, fixdata=True):
        """Perturb material composition.

        Parameters
        ----------
        what : str
            Type of perturbation. If ``what="density"``, the density of the 
            material is perturbed, otherwise the other data can be perturbed by
            indicating the data. For instance, ``what="Fiss"`` or ``what="Nubar"``.
        howmuch : list or float
            Magnitude of the perturbation. If list, its length must be equal to
            ``nE``, and the perturbation is applied to each group. If it is a float,
            the perturbation is applied to the material density. 
        depgro : int, optional
            Departure energy group, by default ``False``. This argument is needed to perturb
            the scattering cross section.
        fixdata: bool, optional
            Flag to check and ensure data consistency, by default ``True``.

        Returns
        -------
        None.

        """
        if what == 'density':
            densdata = ['Capt', 'Fiss', *list(map(lambda z: "S"+str(z), range(self.L))),
                        *list(map(lambda z: "Sp"+str(z), range(self.L)))]
            if howmuch < 0:
                raise OSError('Cannot apply negative density perturbations!')
            for xs in densdata:
                self.__dict__[xs][:] = self.__dict__[xs][:]*howmuch
        else:
            depgro = depgro-1 if depgro is not None else depgro
            for g in range(self.nE):
                # no perturbation
                if howmuch[g] == 0:
                    continue

                mydic = self.__dict__
                if what in indepdata:
                    # update perturbed parameter
                    if depgro is None:
                        delta = mydic[what][g]*howmuch[g]
                        mydic[what][g] = mydic[what][g]+delta
                    else:  # select departure group for scattering matrix
                        delta = mydic[what][depgro]*howmuch[depgro]
                        mydic[what][depgro] = mydic[what][depgro]+delta

                    # select case to ensure data consistency
                    if what == 'Fiss':
                        self.Nsf[g] = self.Nubar[g]*mydic[what][g]
                    elif what == 'Nubar':
                        self.Nsf[g] = self.Fiss[g]*mydic[what][g]
                        # computesumxs = False
                    elif what.startswith('Chi'):
                        if what in ['Chit']:
                            mydic[what] = mydic[what]*(1+delta)
                        else:
                            raise OSError('Delayed/prompt spectra \
                                           perturbation still missing!')
                    elif what == 'Diffcoef':
                        # Hp: change in diffcoef implies change in capture
                        delta = 1/(3*mydic[what][g])-self.Transp[g]
                    elif what == 'S0':
                        # change higher moments, if any
                        for ll in range(self.L): # FIXME
                            R = (mydic[what][g]/mydic[what][g]-delta)
                            key = 'S%d' % ll
                            mydic[key][depgro][g] = mydic[key][depgro][g]*R

                else:
                    if fixdata:
                        raise OSError(f'{what} cannot be perturbed \
                                      directly!')
                    else:
                        # update perturbed parameter
                        if depgro is None:
                            delta = mydic[what][g]*howmuch[g]
                            mydic[what][g] = mydic[what][g]+delta
                        else:  # select departure group for scattering matrix
                            delta = mydic[what][depgro]*howmuch[g]
                            mydic[what][depgro] = mydic[what][depgro]+delta

        if fixdata:
            self.repair_xs()

    def repair_xs(self):
        """Ensure data consistency.

        Parameters
        ----------
        ``None``.

        Returns
        -------
        ``None``.

        """
        datadic = self.__dict__
        datavail = copy(list(datadic.keys()))

        # ensure non-zero total XS
        self.bad_data = False
        if np.count_nonzero(self.Tot) != self.Tot.shape[0]:
            self.bad_data = True
            # ensure that capt matches tot where tot is zero
            self.Capt[self.Tot <= 0] = 1E-5
            # modify Tot accordingly
            self.Tot[self.Tot <= 0] = 1E-5

        # TODO propose a quick fix for bad_data True
        self.Nsf = self.Fiss*self.Nubar
        self.Abs = self.Fiss + self.Capt
        if np.count_nonzero(self.Abs == 0) > 0:
            raise OSError

        if self.use_nxn:
            InScatt = np.diag(self.Sp0)
            sTOT = self.Sp0.sum(axis=0) if len(self.Sp0.shape) > 1 else self.Sp0
            if hasattr(self, 'Sp1'):
                sTOT1 = self.Sp1.sum(axis=0) if len(self.Sp1.shape) > 1 else self.Sp1
            else:
                sTOT1 = np.zeros(sTOT.shape)
            # if not np.array_equal(self.Rabs, self.Abs):
            #     if min(self.Rabs) < 0:
            #         self.Rabs = self.Abs
            #     self.Capt = self.Rabs - self.Fiss
        else:
            InScatt = np.diag(self.S0)
            sTOT = self.S0.sum(axis=0) if len(self.S0.shape) > 1 else self.S0
            sTOT1 = self.S1.sum(axis=0) if len(self.S1.shape) > 1 else self.S1

        # --- compute diffusion coefficient and transport xs
        if self.P1consistent:
            # --- compute transport xs (derivation from P1)
            self.Transp = self.Tot-sTOT1
            self.Diffcoef = 1/(3*self.Transp)
        else:
            self.Transp[self.Transp <= 1E-8] = 1E-8
            self.Diffcoef = 1/(3*self.Transp)

        self.Rem = self.Tot - InScatt

        self.DiffLength = np.sqrt(self.Diffcoef / self.Rem)

        self.MeanFreePath = 1 / self.Tot.max()

        # self.Fiss[self.Fiss <= 5E-7] = 0

        isFiss = self.Fiss.max() > 0

        if isFiss:
            self.Chit /= self.Chit.sum()

        kincons = True
        for s in kinetics:
            if s not in datavail:
                kincons = False
                self.__dict__[s] = [0]

        if kincons:
            if isFiss:
                if len(self.Chid.shape) == 1:
                    # each family has same emission spectrum
                    # FIXME FIXME check Serpent RSD and do correction action
                    self.Chid[self.Chid <= 1E-4] = 0
                    self.Chid /= self.Chid.sum()
                    self.Chid = np.asarray([self.Chid]*self.NPF)
                elif self.Chid.shape != (self.NPF, self.nE):
                    raise NEMaterialError(f'Delayed fiss. spectrum should be \
                                    ({self.NPF}, {self.nE})')

                # FIXME FIXME check Serpent RSD and do correction action
                self.Chip[self.Chip <= 1E-4] = 0

                try:
                    for g in range(0, self.nE):
                        chit = (1-self.beta.sum())*self.Chip[g] + \
                                np.dot(self.beta, self.Chid[:, g])
                        if abs(self.Chit[g]-chit) > 1E-3:
                            raise NEMaterialError()
                except NEMaterialError:
                    logger.warning(f'Fission spectra or delayed fractions'
                                    f' in {self.UniName} not consistent! '
                                    'Forcing consistency acting on chi-prompt...')
                else:
                    self.Chip = (self.Chit-np.dot(self.beta, self.Chid))/(1-self.beta.sum())
                    for g in range(0, self.nE):
                        chit = (1-self.beta.sum())*self.Chip[g] + \
                                np.dot(self.beta, self.Chid[:, g])
                        if abs(self.Chit[g]-chit) > 1E-4:
                            raise NEMaterialError("Normalisation failed!")

            # ensure pdf normalisation
            if isFiss:
                self.Chip /= self.Chip.sum()
                for p in range(self.NPF):
                    self.Chid[p, :] /= self.Chid[p, :].sum()

    def add_missing_xs(self):
        """Add missing group constants.

        Parameters
        ----------
        ``None``.

        Returns
        -------
        ``None``.

        """
        # TODO if not existing, compute the flux assuming an infinite medium
        E = self.energygrid
        datadic = self.__dict__
        datavail = copy(list(datadic.keys()))
        # --- check basic reactions existence
        for s in basicdata:
            if s not in datavail:
                if (s == 'Nsf' and 'Nubar' in datavail) or (s == 'Nubar' and 'Fiss' in datavail and 'Nubar') or (s == 'Fiss' and 'Nubar' in datavail):
                    continue
                elif (s == 'S0' and 'Sp0' in datavail) or (s == 'Sp0' and 'S0' in datavail):
                    continue
                else:
                    msg = f'{s} is missing in {self.UniName} data!'
                    logger.error(msg)
                    raise OSError(msg)

        # --- compute fission production cross section
        if hasattr(self, 'Nubar') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Nsf'):
                self.Nsf = self.Fiss*self.Nubar
                logger.warning(f"'Nsf' defined from available 'Nubar' and 'Fiss' for {self.UniName}.")
        elif hasattr(self, 'Nsf') and hasattr(self, 'Nubar'):
            if not hasattr(self, 'Fiss'):
                if max(self.Nubar) > 0:
                    self.Fiss = self.Nsf / self.Nubar
                    logger.warning(f"'Fiss' defined from available 'Nubar' and 'Nsf' for {self.UniName}.")
                else:
                    self.Fiss = np.zeros((nE, ))
                    logger.warning(f"'Fiss' set to zero for {self.UniName}.")
        elif hasattr(self, 'Nsf') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Nubar'):
                if min(self.Fiss) > 0: 
                    self.Nubar = self.Nsf / self.Fiss
                    logger.warning(f"'Nubar' defined from available 'Nsf' and 'Fiss' for {self.UniName}.")
                else:
                    self.Nubar = copy(self.Fiss)
                    logger.warning(f"'Nubar' set to zero for {self.UniName}.")
        else:
            raise OSError('To compute fission data at least two out of the three data "Nsf","Nubar" and "Fiss" are required')

        # --- add scattering matrices
        if not hasattr(self, 'Sp0'):
            self.Sp0 = self.S0
            logger.warning(f"'Sp0' set equal to 'S0' for {self.UniName}.")

            if self.use_nxn:
                self.use_nxn = False
                logger.info(f"(n,xn) scattering reactions not considered for {self.UniName} since no Sp0 in input!")

        if not hasattr(self, 'S0'):
            self.scat_n1n_exists = 0
            self.S0 = self.Sp0
            logger.warning(f"'Sp0' set equal to 'S0' for {self.UniName}.")
        else:
            self.scat_n1n_exists = 1

        if self.scat_n1n_exists:
            InScatt = np.diag(self.S0)
            sTOT = self.S0.sum(axis = 0) if len(self.S0.shape) > 1 else self.S0

        # --- compute missing sum reactions
        if hasattr(self, 'Capt') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Abs'):
                self.Abs = self.Fiss + self.Capt
                logger.warning(f"'Abs' defined from available 'Fiss' and 'Capt' for {self.UniName}.")

        elif hasattr(self, 'Abs') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Capt'):
                self.Capt = self.Abs - self.Fiss
                logger.warning(f"'Capt' defined from available 'Fiss' and 'Abs' for {self.UniName}.")

        elif hasattr(self, 'Abs') and hasattr(self, 'Capt'):
            if not hasattr(self, 'Fiss'):
                self.Fiss = self.Abs - self.Capt
                logger.warning(f"'Fiss' defined from available 'Capt' and 'Abs' for {self.UniName}.")

        elif hasattr(self, 'Rabs') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Capt'):
                self.Capt = self.Rabs - self.Fiss
                logger.warning(f"'Capt' defined from available 'Fiss' and 'Rabs' for {self.UniName}.")

        elif hasattr(self, 'Rabs') and hasattr(self, 'Capt'):
            if not hasattr(self, 'Fiss'):
                self.Fiss = self.Rabs - self.Capt
                logger.warning(f"'Fiss' defined from available 'Capt' and 'Rabs' for {self.UniName}.")

        elif hasattr(self, 'Rem') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Abs'):
                self.Abs = self.Rem - sTOT + InScatt
                logger.warning(f"'Abs' defined from available 'Rem' and 'Fiss' for {self.UniName}.")

            if not hasattr(self, 'Capt'):
                self.Capt = self.Abs - self.Fiss
                logger.warning(f"'Capt' defined from available 'Rem' and 'Fiss' for {self.UniName}.")

        elif hasattr(self, 'Rem') and hasattr(self, 'Capt'):
            if not hasattr(self, 'Abs'):
                self.Abs = self.Rem - sTOT + InScatt
                logger.warning(f"'Abs' defined from available 'Rem' and 'Fiss' for {self.UniName}.")

            if not hasattr(self, 'Fiss'):
                self.Fiss = self.Abs - self.Capt
                logger.warning(f"'Fiss' defined from available 'Rem' and 'Capt' for {self.UniName}.")

        elif hasattr(self, 'Tot') and hasattr(self, 'Fiss'):
            if not hasattr(self, 'Capt'):
                self.Capt = self.Tot - sTOT - self.Fiss
                logger.warning(f"'Capt' defined from available 'Fiss' and 'Tot' for {self.UniName}.")

            if not hasattr(self, 'Abs'):
                self.Abs = self.Fiss + self.Capt
                logger.warning(f"'Abs' defined from available 'Capt' and 'Fiss' for {self.UniName}.")

        # --- add missing data
        if not hasattr(self, 'Rabs'):
            self.Rabs = self.Abs
            logger.warning(f"'Rabs' set equal to 'Abs' for {self.UniName}.")

        if not hasattr(self, 'Abs'):
            self.Abs = self.Rabs
            logger.warning(f"'Abs' set equal to 'Rabs' for {self.UniName}.")

        if not hasattr(self, 'Rem'):
            if self.scat_n1n_exists:
                self.Rem = self.Abs + sTOT - InScatt
                logger.warning(f"'Rem' defined from available 'Abs' and 'S0' for {self.UniName}.")
            else:
                logger.warning(f"'Rem' not defined because 'S0' is missing for {self.UniName}.")

        if not hasattr(self, 'Tot'):
            if self.scat_n1n_exists:
                self.Tot = self.Abs + sTOT
                logger.warning(f"'Tot' defined from available 'Abs' and 'S0' for {self.UniName}.")
            elif self.use_nxn:
                self.Tot = self.Rabs +  self.Sp0.sum(axis = 0)
                logger.warning(f"'Tot' defined from available 'Rabs' and 'Sp0' for {self.UniName}.")

        if not hasattr(self, 'S1'):
            # # estimate mu0
            # mu0 = (self.Tot - self.Transp)/(self.S0.sum(axis = 0))
            # self.S1 = (mu0*self.S0.T).T
            # tot = self.Tot - self.S1.sum(axis = 0)
            self.S1 = self.S0

        # ensure non-zero total XS
        self.bad_data = False
        if np.count_nonzero(self.Tot) != self.Tot.shape[0]:
            self.bad_data = True

        if not hasattr(self, "Invv"):
            if not hasattr(self, "fine_energygrid"):
                avgE = 1/2*(E[:-1]+E[1:])*1.602176634E-13  # J
                v = np.sqrt(2*avgE/1.674927351e-27)
                self.Invv = 1/(v*100)  # s/cm
                logger.warning(f"'Invv' defined from the average kinetic energy in group g for {self.UniName}.")

        # --- compute diffusion coefficient and transport xs
        if not hasattr(self, 'Transp'):
            if hasattr(self, 'Diffcoef'):
                self.Transp = 1/(3*self.Diffcoef)
                logger.warning(f"'Transp' defined from available 'Diffcoef' for {self.UniName}.")

            else:
                if hasattr(self, 'S1') and self.P1consistent:
                    self.Transp = self.Tot-self.S1.sum(axis=0)
                    logger.warning(f"'Transp' defined from available 'Tot' and 'S1' for {self.UniName}.")

                else:
                    # assuming isotropic scattering
                    self.Transp = self.Tot
                    logger.warning(f"'Transp' defined from available 'Diffcoef' for {self.UniName}.")

        if not hasattr(self, 'Diffcoef'):
            self.Diffcoef = 1/(3*self.Transp)

        # --- compute diffusion length
        if not hasattr(self, 'DiffLength'):
            if not hasattr(self, 'Rem'):
                self.DiffLength = np.sqrt(self.Diffcoef / self.Abs)
            else:
                self.DiffLength = np.sqrt(self.Diffcoef / self.Rem)
        # --- compute mean free path
        if not hasattr(self, 'MeanFreePath'):
            self.MeanFreePath = 1/self.Tot.max()
        # --- ensure consistency kinetic parameters (if fissile medium)
        isFiss = self.Fiss.max() > 0
        if not hasattr(self, "FissEn"):
            if isFiss:
                self.FissEn = np.asarray([200]*self.nE)
            else:
                self.FissEn = np.asarray([0]*self.nE)

        if not hasattr(self, "Chit"):
            if isFiss:
                raise OSError(f"'Chit' is missing from data {self.UniName}")
            else:
                self.Chit = np.zeros((self.nE, ))

        kincons = True
        for s in kinetics:
            if s not in datavail:
                kincons = False
                self.__dict__[s] = np.zeros((self.NPF,))
                self.__dict__[f"{s}_tot"] = np.zeros((self.NPF,))

        if kincons:
            if not hasattr(self, "beta"):
                if isFiss:
                    raise OSError(f"'beta' is missing for {self.UniName}")
                else:
                    self.beta = np.zeros((self.NPF,))

            if not hasattr(self, "lambda"):
                if isFiss:
                    raise OSError(f"'lambda' is missing for {self.UniName}")
                else:
                    self.__dict__["lambda"] = np.zeros((self.NPF,))

            if not hasattr(self,"beta_tot"):
                self.beta_tot = self.beta.sum()
            if not hasattr(self, "lambda_tot"):
                # FIXME # TODO
                self.__dict__["lambda_tot"] = np.mean(self.__dict__["lambda"])

            if not hasattr(self, "Chip"):
                if isFiss:
                    if hasattr(self, "Chid"):
                        self.Chip = (self.Chit-np.dot(self.beta, self.Chid))/(1-self.beta.sum())
                    else:
                        raise OSError(f"'Chip' is missing from data {self.UniName}")
                else:
                    self.Chip = np.zeros((self.nE, ))

            if not hasattr(self, "Chid"):
                if isFiss:
                    self.Chid = (self.Chit-self.Chip*(1-self.beta.sum()))/(self.beta.sum())
                else:
                    self.Chid = np.zeros((self.NPF, self.nE))

        if not hasattr(self, "Kerma"):
            self.Kerma = np.zeros((self.nE, ))

        if not hasattr(self, "Flx"):
            # FIXME: an improved option can be estimating the flux axial prof. with analytical profiles
            # e.g. cos(Bz) if self.Fiss != 0 or exp(-z/L)+exp(+z/L) if self.Fiss = 0
            self.Flx = np.ones((self.nE, ))

    def to_json(self, fname=None):
        """Dump object to json file.

        Parameters
        ----------
        fname: str, optional
            Filename, by default ``None``.

        Returns
        -------
        None.

        """
        if fname is None:
            f'{self.UniName}_{self.egridname}.json'
        tmp = {}
        with open(fname, 'w') as f:

            for k, v in self.__dict__.items():
                if isinstance(v, (np.ndarray)):
                    tmp[k] = v.tolist()
                else:
                    tmp[k] = v

            json.dump(tmp, f, sort_keys=True, indent=10)

    def collapse(self, fewgrp, spectrum=None, egridname=None, fixdata=True):
        """Collapse in energy the multi-group data.

        Parameters
        ----------
        fewgrp : iterable
            Few-group structure to perform the collapsing.
        spectrum: array, optional
            Spectrum to perform the energy collapsing, by default ``None``. If ``None``,
            the ``Flx`` attribute is used as a weighting spectrum.
        egridname: str, optional
            Name of the energy grid, by default ``None``.

        Raises
        ------
        OSError
            Collapsing failed: weighting flux missing in {}.

        Returns
        -------
        None.

        """
        if spectrum is not None:
            flx = spectrum
        else:
            if not hasattr(self, 'Flx'):
                raise OSError('Collapsing failed: weighting flux missing in '
                              f'{self.UniName}')
            else:
                flx = self.Flx

        multigrp = self.energygrid
        # few_into_multigrp = multigroup_onto_fewgroup(multi_g_grid, few_g_grid[str(case)])
        if isinstance(fewgrp, list):
            fewgrp = np.asarray(fewgrp)
        # ensure descending order
        fewgrp = fewgrp[np.argsort(-fewgrp)]
        H = len(multigrp)-1
        G = len(fewgrp)-1
        # sanity checks
        if G >= H:
            raise NEMaterialError(f'Collapsing failed: few-group structure should',
                          ' have less than {H} group')
        if multigrp[0] != fewgrp[0] or multigrp[-1] != fewgrp[-1]:
            raise NEMaterialError('Collapsing failed: few-group structure'
                                'boundaries do not match with multi-group'
                                'one')
        # map fewgroup onto multigroup
        few_into_multigrp = np.zeros((G+1,), dtype=int)
        # multigrp_bin = np.zeros((H+1,), dtype=int)
        for ig, g in enumerate(fewgrp):
            reldiff = abs(multigrp-g)/g
            idx = np.argmin(reldiff)
            if (reldiff[idx] > 1E-5):
                raise NEMaterialError(f'Group boundary n.{ig}, {g} MeV not present in fine grid!')
            else:
                few_into_multigrp[ig] = idx
                # multigrp_bin[idx] = 1

        collapsed = {}
        collapsed['Flx'] = np.zeros((G, ))

        # manage reduced absorption collapsing
        if hasattr(self, "Rabs"):
            # collapse the (n,xn) cross section
            xs_abs_nxn = self.Abs - self.Rabs
            collapsed["Rabs"] = np.zeros((G, ))

        for g in range(G):
            # select fine groups in g
            G1, G2 = fewgrp[g], fewgrp[g+1]
            iS = few_into_multigrp[g]
            iE = few_into_multigrp[g+1]
            # compute flux in g
            NC = flx[iS:iE].sum()
            collapsed['Flx'][g] = NC
            # --- collapse
            for key, v in self.__dict__.items():
                # --- cross section and inverse of velocity
                if key in collapse_xs:
                    # --- preallocation
                    dims = (G, G) if 'S' in key else (G, )
                    if g == 0:
                        collapsed[key] = np.zeros(dims)

                    if len(dims) == 1:
                        if key == 'Diffcoef':
                            v = self.Transp
                            v = 1/3/v
                        collapsed[key][g] = np.divide(flx[iS:iE].dot(v[iS:iE]), NC, where=NC!=0)
                    else:
                        # --- scattering
                        for g2 in range(G):  # arrival group
                            I1, I2 = fewgrp[g2], fewgrp[g2+1]
                            iS2 = few_into_multigrp[g2]
                            iE2 = few_into_multigrp[g2+1]
                            s = v[iS:iE, iS2:iE2].sum(axis=0)
                            NCS = flx[iS2:iE2].sum()
                            collapsed[key][g][g2] = np.divide(flx[iS2:iE2].dot(s), NCS, where=NCS!=0)
                            iS2 = iE2
                # --- fission-related data
                elif key in collapse_xsf:
                    if self.Fiss.max() <= 0:
                        if key == 'Chid':
                            collapsed[key] = np.zeros((self.NPF, G))
                        else:
                            collapsed[key] = np.zeros((G, ))
                        continue
                    fissrate = flx[iS:iE]*self.Fiss[iS:iE]
                    FRC = fissrate.sum()
                    if key == 'Chid':
                        if g == 0:
                            collapsed[key] = np.zeros((self.NPF, G))
                        for p in range(self.NPF):
                            collapsed[key][p, g] = v[p, iS:iE].sum()
                    else:
                        if g == 0:
                            collapsed[key] = np.zeros((G, ))

                        if key in ['Chit', 'Chip']:
                            collapsed[key][g] = v[iS:iE].sum()
                        else:
                            collapsed[key][g] = np.divide(fissrate.dot(v[iS:iE]), FRC, where=FRC!=0)
                else:
                    continue

            # --- reduced absorption
            if hasattr(self, "Rabs"):
                xs_abs_nxn_g = np.divide(flx[iS:iE].dot(xs_abs_nxn[iS:iE]), NC, where=NC!=0)
                collapsed["Rabs"][g] = collapsed["Capt"][g] + collapsed["Fiss"][g] - xs_abs_nxn_g

            iS = iE

        collapsed['Transp'] = 1/(3*collapsed['Diffcoef'])
        self.P1consistent = False # to "preserve" diffcoef
        # overwrite data
        self.fine_energygrid = self.energygrid+0
        self.energygrid = fewgrp
        self.nE = G
        self.egridname = egridname if egridname else f'{G}G'
        for key in self.__dict__.keys():
            if key in collapsed.keys():
                self.__dict__[key] = collapsed[key]

        self.add_missing_xs()
        # ensure data consistency
        if fixdata:
            self.repair_xs()

    def isfiss(self):
        """Assess whether the material is fissile"""
        return self.Fiss.max() > 0 and self.Nubar.max() > 0


class HTHexData():
    """Assign TH material data to the reactor core.

    Parameters
    ----------
    which: list
        List of assemblies assigned to the current type.
    inpdict: dict


    Attributes
    ----------
    iHA: list
        List of assemblies assigned to the current type.
    frictMult: float
        Friction factor multiplier
    htcMult: float
        Heat Transfer Coefficient multiplier
    htcCorr: str
        Heat Transfer Coefficient correlation
    frictCorr: str
        Friction factors correlations
    chanCouplCorr: str
        Correlation for coupling channels
    """
    def __init__(self, which, inpdict):
        inpdict = lowcasedict(inpdict)
        # assign assemblies to type 
        self.iHA = which
        # TH correlations
        self.frictMult = 1
        self.htcMult = 1
        self.htcCorr = inpdict["htc_corr"]
        self.frictCorr = inpdict["frict_corr"]
        self.chanCouplCorr = inpdict["chan_coupling_corr"]


class NEMaterialError(Exception):
    pass


class THDataError(Exception):
    pass