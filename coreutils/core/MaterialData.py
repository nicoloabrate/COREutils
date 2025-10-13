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

# names of the MGC attributes
sumxs = ['Sigma_tot', 'Sigma_abs', 'Sigma_rem', 'Sigma_rabs']
scatt_mat_keys = [*list(map(lambda z: "S"+str(z), range(8))),
              *list(map(lambda z: "Sp"+str(z), range(8)))]
indepdata = ['Sigma_capt', 'Sigma_fiss', 'S0', 'nu_fiss', 'chi_del', 'chi_pro']
basicdata = ['Sigma_fiss', 'nu_fiss', 'S0', 'Sp0', 'chi_tot', 'nuSigma_fiss']
kinetic_data = ['lambda', 'beta', 'nu_fiss_del', 'chi_del', 'chi_pro', 'inv_vel']
ene_data = ['kerma', 'fiss_energy']
alldata = list(set([*sumxs, *indepdata, *basicdata, *kinetic_data, *ene_data]))

# list for collapsing
collapse_xs = ['Sigma_fiss', 'Sigma_capt', *list(map(lambda z: "S"+str(z), range(0, 3))),
               *list(map(lambda z: "Sp"+str(z), range(0, 3))), 'inv_vel', 'Diffcoef', 'kerma']
collapse_xsf = ['nu_fiss', 'chi_del', 'chi_tot', 'chi_pro', 'fiss_energy']
delete_for_collapse = ['Sigma_abs', 'Sigma_rem', 'Sigma_tot']

# list for plotting
units = {'chi_del': '-', 'chi_tot': '-', 'chi_pro': '-', 'Sigma_tot': 'cm^{-1}',
         'Sigma_capt': 'cm^{-1}', 'Sigma_abs': 'cm^{-1}', 'Sigma_rabs': 'cm^{-1}', 
         'Sigma_fiss': 'cm^{-1}', 'S0': 'cm^{-1}', 'S1': 'cm^{-1}', 'Sp0': 'cm^{-1}', 'Sp1': 'cm^{-1}',
         'nuSigma_fiss': 'cm^{-1}', 'Sigma_rem': 'cm^{-1}', 'Sigma_transp': 'cm^{-1}',
         'fiss_energy': 'MeV', 'S': 'cm^{-1}', 'nu_fiss': '-', 'inv_vel': 's/cm',
         'Difflength': 'cm^2', 'Diffcoef': 'cm', 'flux': 'a.u.', 'kerma': 'J/cm'}
xslabels = {'chi_del': 'delayed Sigma_fiss. emission spectrum', 'chi_tot': 'total Sigma_fiss. emission spectrum',
            'chi_pro': 'prompt Sigma_fiss. emission spectrum', 'Sigma_tot': 'Total xs',
            'Sigma_capt': 'Capture xs', 'Sigma_abs': 'Absorption xs', 'Sigma_fiss': 'Fission xs',
            'nuSigma_fiss': 'Sigma_fiss. production xs', 'Sigma_rem': 'Removal xs', 'Sigma_transp': 'Transport xs',
            'fiss_energy': 'Sigma_fiss. energy', 'S': 'Scattering xs', 'nu_fiss': 'neutrons by fission',
            'inv_vel': 'Inverse velocity', 'Difflength': 'Diff. length', 'Diffcoef': 'Diff. coeff.',
            'flux': 'Flux spectrum', 'kerma': 'KERMA coefficient', 'Sigma_rabs': 'Reduced absorption',
            'S0': '0-th order scattering matrix', 'S1': '1st order scattering matrix',
            'Sp0': '0-th order production scattering matrix', 'Sp1': '1-st order production scattering matrix',}

# conversion dictionaries
# --- legacy json and txt
legacy2coreutils = {'Tot': 'Sigma_tot', 'Abs': 'Sigma_abs', 'Rem': 'Sigma_rem', 'Rabs': 'Sigma_rabs', 
                    'Capt': 'Sigma_capt', 'Fiss': 'Sigma_fiss', 'Nubar': 'nu_fiss', 'Diffcoef': 'Diffcoef',
                    'Chid': 'chi_del', 'Chip': 'chi_pro', 'Fiss': 'Sigma_fiss', 'S0': 'S0', 'SP0': 'Sp0', 'SP1': 'Sp1', 'SP2': 'Sp2',
                    'Chit': 'chi_tot',
                    'Nsf': 'nuSigma_fiss', 'lambda': 'lambda', 'FissEn': 'fiss_energy', 'Transp': 'Sigma_transp', 'Flx': 'flux',
                    'beta': 'beta', 'Invv': 'inv_vel', 'S1': 'S1', 'Sp1': 'Sp1', 'Kerma': 'kerma', 'Kappa': 'fiss_energy'}
# --- serpent
serpent2coreutils = {
                    'infTot': 'Sigma_tot', 'infAbs': 'Sigma_abs', 'infRemxs': 'Sigma_rem', 'infRabsxs': 'Sigma_rabs',
                    'infCapt': 'Sigma_capt', 'infFiss': 'Sigma_fiss', 'infS0': 'S0', 'infNubar': 'nu_fiss', 'infChid': 'chi_del',
                    'infChip': 'chi_pro', 'infSp0': 'Sp0', 'infChit': 'chi_tot', 'infNsf': 'nuSigma_fiss', 'lambda': 'lambda', 'beta': 'beta',
                    'infInvv': 'inv_vel', 'infFlx': 'flux', 'infDiffcoef': 'Diffcoef', 'infTranspxs': 'Sigma_transp',
                    'infKappa': 'fiss_energy', 'infS1': 'S1', 'infSp1': 'Sp1',}

serp_phot_keys = ['KermaPh', 'Rayleigh', 'Compton', 'PProduction', 'Photoelectric', 'nuPh', 'TotPhProd']

# --- nemtab
nemtab2coreutils = {"transport": "Sigma_transp" ,"absorption": "Sigma_abs" ,
                    "nuFission": "nuSigma_fiss" ,"kappaFission": "fiss_energy" ,
                    "P0": "S0" , "promptFissionSpectrum": "chi_tot", # not a bug: done to ensure consistency between FENNECS and FRENETIC codes in steady state
                    "inverseVelocity": "inv_vel" , "lambda": "lambda",
                    "beta": "beta"}

list_av_reader = ["serpent", "json", "txt", "nemtab", ] # "HDF5", "ecco"


def MGC_reader(reader, file):

    if reader == "json":
        data_in_dict = from_json(file)

    elif reader == "serpent":
        data_in_dict = from_serpent(file)

    elif reader == "txt":
        data_in_dict = from_txt(file)

    elif reader == "nemtab":
        data_in_dict = from_nemtab(file)

    # elif reader == "HDF5":
    #     data_in_dict = from_hdf5(file)

    # elif reader == "ecco":
    #     data_in_dict = from_ecco(file)

    else:
        raise OSError(f"Reader {reader} not available! Available formats: {list_av_reader}")

    return data_in_dict


def from_json(path):
    """
    Read data from a json file.

    Parameters
    ----------
    path: str
        Path to json file.

    Returns
    -------
    data_in_dict: dict
        Dictionary containing the data read from the json file.

    """
    with open(path) as f:
        data_in_json = json.load(f)

    data_in_dict = {}
    for k, v in data_in_json.items():
        if k in legacy2coreutils.keys():
            k = legacy2coreutils[k]
        if isinstance(v, list):
            data_in_dict[k] = np.asarray(v)

    data_in_dict["data_name"] = path.name.split(".json")[0]
    data_in_dict["data_origin"] = "json"

    return data_in_dict


def _serpres_to_dict(serpres):
    """Transform :class:`serpentTools.ResultsReader` object 
        into a list of dictionaries, one for each universe stored in the _res file.

    Parameters
    ----------
    serpres : dict
        Dictionary of :class:`serpentTools.ResultsReader` objects.
    data_name : str
        Name of the material.

    Returns
    -------
    list_data_in_dict: list
        List of dictionaries containing the data read from the _res file.
    """
    list_data_in_dict = []
    lstapp = list_data_in_dict.append

    for data in serpres.universes.values():
        nE = len(data.infExp['infTot'])
        data_name = data.name
        data_in_dict = {}
        data_in_dict["data_name"] = data_name
        data_in_dict["data_origin"] = "serpent"
        data_in_dict["energy_grid"] = data.groups
        data_in_dict["energy_grid"][0] = 20
        data_in_dict["energy_grid"][-1] = 1e-11
        for serpkey, CUkey in serpent2coreutils.items():
            if serpkey in ["lambda", "beta"]:
                continue
            else:
                if serpkey.startswith('infS') or serpkey.startswith('infSp'):
                    vals = np.reshape(data.infExp[serpkey], (nE, nE), order='F')
                    rsd = np.reshape(data.infUnc[serpkey], (nE, nE), order='F')
                else:
                    vals = data.infExp[serpkey]
                    rsd = data.infUnc[serpkey]

            if rsd.size > 1:
                max_rsd = rsd.max().max()
                min_rsd = rsd.min().min()
                max_val = vals.max().max()
            else:
                max_rsd = rsd.max()
                min_rsd = rsd.min()
                min_val = vals.min()

            if max_rsd*100 > 1 or min_rsd <= 1E-12:
                g_max = np.argmax(rsd)
                g_min = np.argmin(rsd)
                if max_val >= 1E-12:
                    logger.warning(f'Serpent PRSD on {CUkey} : max={max_rsd*100:.1f} in g={g_max+1}, min={min_rsd*100:.1f} in g={g_min+1} in {data_name}.')

            data_in_dict[CUkey] = vals
            data_in_dict[f'{CUkey}_rsd'] = 2*rsd

        # kinetics parameters
        fwd_beta = serpres.resdata['fwdAnaBetaZero'][::2]
        fwd_beta_rsd = serpres.resdata['fwdAnaBetaZero'][1::2]

        data_in_dict['beta_tot'] = fwd_beta[0]
        data_in_dict['beta_tot_rsd'] = fwd_beta_rsd[0]
        if len(fwd_beta) > 1:
            data_in_dict['beta'] = fwd_beta[1:]
            data_in_dict['beta_rsd'] = fwd_beta_rsd[1:]
        else:
            data_in_dict['beta'] = np.array([data_in_dict['beta_tot']])
            data_in_dict['beta_rsd'] = np.array([data_in_dict['beta_tot_rsd']])
        # --- avoid issues with python lambda function
        lambdas = serpres.resdata['fwdAnaLambda'][::2]
        lambdas_rsd = serpres.resdata['fwdAnaLambda'][1::2]

        data_in_dict['lambda_tot'] = lambdas[0]
        data_in_dict['lambda_tot'] = lambdas_rsd[0]
        if len(lambdas) > 1:
            data_in_dict['lambda'] = lambdas[1:]
            data_in_dict['lambda_rsd'] = lambdas_rsd[1:]
        else:
            data_in_dict['lambda'] = np.array([data_in_dict['lambda_tot']])
            data_in_dict['lambda_rsd'] = np.array([data_in_dict['lambda_tot_rsd']])

        lstapp(data_in_dict)

    return list_data_in_dict


def _readserpentdet(self, serpdet, data_name, nE, nEPH):
    """Transform :class:`serpentTools.ResultsReader` object 
        into :class:``coreutils.NEMaterial`` object.

    Parameters
    ----------
    serpdet : dict
        Dictionary of :class:`serpentTools.DetectorsReader` objects.
    data_name : str
        Name of the material.
    nE: int
        Number of energy groups.
    nEPH: int
        Number of photon energy groups.

    Raises
    ------
    OSError
        If the material indicated by ``data_name`` is not available.
    OSError
        If the number of energy groups indicated by ``nE`` is not available.
    """
    data = None
    data_name = f"{data_name}__nkerma"

    for det in serpdet.values():
        if data_name in det.detectors.keys():
            det_data = det[data_name]
            if len(det_data.energy) != nE:
                raise OSError(f'{data_name} energy groups in _det do not match with \
                                input grid!')

            data = det_data.tallies

    if data is None:
        logger.warning(f'{data_name} data not available in Serpent files!')
    else:
        selfdic = self.__dict__

        selfdic["Kerma"] = data[::-1]
        rsd = det_data.errors

        if rsd.max()*100 > 1:
            g_max = np.argmax(rsd)
            logger.warning(f'Serpent PRSD of kerma = {rsd.max()*100} in group={g_max+1} in {data_name}.')

    # FIXME TODO work in progress
    if nEPH > 0:
        for mykey in serp_phot_keys:
            data_name = f"{data_name}__{mykey}"
            # loop over elements in this universe
            # TODO
            det_data = det[data_name]
            if len(det_data.energy) != nEPH:
                raise OSError(f'{data_name} PH energy groups in _det do not match with \
                                input grid!')

            data = det_data.tallies


def from_txt(fname):
    """
    Parse the material data from a .txt file.

    Macro-group constants are parsed from a formatted file with column-wise
    data separated by headers beginning with "#" and the name of the data:
        * Sigma_tot: total cross section [cm^-1]
        * Sigma_transp: transport cross section [cm^-1]
                    It is defined as total_xs-avg_direction*scattering_xs
                    according to P1 approximation.
        * Diffcoef: diffusion coefficient [cm]
                    It is defined as 1/(3*Sigma_transp).
        * Sigma_abs: absorption cross section [cm^-1]
                It is the sum of Sigma_capt and Sigma_fiss cross sections.
        * Sigma_capt: capture cross section [cm^-1]
        * Sigma_fiss: fission cross section [cm^-1]
        * Sigma_rem: removal cross section [cm^-1]
                It is the sum of Sigma_abs and group-removal.
        * chi_tot: total emission spectrum [-]
        * chi_pro: prompt emission spectrum [-]
        * chi_del: delayed emission spectrum [-]
        * nuSigma_fiss: fission production cross section [cm^-1]
        * nu_fiss: neutron multiplicities [-]
        * fiss_energy: average fission deposited heat [MeV]
        * inv_vel: particle inverse velocity [s/cm]
        * S0, S1, S2,... : scattering matrix cross section [cm^-1]
        * Sp0, Sp1, Sp2,... : scattering production matrix cross section
                            [cm^-1]
        * beta: delayed neutron fractions [-]
        * lambda: precursors families decay constant [-]

    Parameters
    ----------
    fname : string
        Material data file name.

    Returns
    -------
    data_in_dict: dict
        Dictionary containing the data read from the .txt file.

    """
    data_in_dict = {}
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

            if key.startswith('S') or key.startswith('Sp'):
                # multi-line data (scattering matrix)
                if matrix is None:
                    matrix = np.asarray(data)
                else:
                    matrix = np.c_[matrix, data]

                if key in legacy2coreutils.keys():
                    key = legacy2coreutils[key]

                if matrix.shape == (G, G):
                    data_in_dict[key] = matrix.T
                elif matrix.shape == (G, ):
                    data_in_dict[key] = matrix
            else:
                # single-line data (scattering matrix)
                if key in legacy2coreutils.keys():
                    key = legacy2coreutils[key]
                data_in_dict[key] = np.asarray(data)

    data_in_dict["data_name"] = fname.name.split(".txt")[0]
    data_in_dict["data_origin"] = "txt"

    return data_in_dict


def from_nemtab(path):
    """
    Read data from json file.

    Parameters
    ----------
    path: str
        Path to json file.

    Returns
    -------
    data_in_dict: dict
        Dictionary containing the data read from the .XS file in NEMTAB format.
    """
    with open(path) as f:
        flines = f.readlines()

    data_name = path.name.split(".XS")[0]

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
                    grps = findall(r'\d+', line)
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
                grps = findall(r'\d+', line)
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
                    BU = float(findall(r'\d+', line)[0])
                    gconst[BU] = OrderedDict()
                    for i_combo in range(n_combos):
                        gconst[BU][i_combo] = {}
                        gconst[BU][i_combo]["data_name"] = data_name
                    i_data_type = -1
                elif "-" not in line:
                    data_type = line.split()[1]
                    core_data_type = nemtab2coreutils[data_type]
                    for i_combo in range(n_combos):
                        if data_type == "P0":
                            gconst[BU][i_combo][core_data_type] = -np.ones((G, G))
                        else:
                            if data_type in ["promptFissionSpectrum", "inverseVelocity"]:
                                gconst[BU][i_combo][core_data_type] = -np.ones((G,))
                            elif data_type in ["beta", "lambda"]:
                                gconst[BU][i_combo][core_data_type] = -np.ones((F,))
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
                            gconst[BU][i_combo][core_data_type][g-1] = data
                            g += 1

                        elif data_type in ["promptFissionSpectrum", "inverseVelocity"]:
                            gconst[BU][i_combo][core_data_type][g-1] = data
                            g += 1
                        else:
                            gconst[BU][i_combo][core_data_type][g-1] = data
                            i_combo += 1

    return param_values, param_combos, gconst


def from_serpent(filepath):
    """Read Serpent res file with the serpentTools package

    Parameters
    ----------
    filepath : str
        Absolute path to NE data

    Returns
    -------
    res: dict
        dict of serpentTools parser object whose keys are the fuel and coolant temperatures.

    """
    # -- serpentTools settings
    # st.settings.rc['xs.variableGroups'] = ['kinetics', 'xs', 'xs-prod',
    #                                        'gc-meta']
    res = st.read(filepath)
    data_in_serpdict = _serpres_to_dict(res)

    return data_in_serpdict


def Homogenise(materials, volume, mixname, fixdata, energy_grid, add_missing_MGC=True):
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
    collapse_xs = ['Sigma_fiss', 'Sigma_capt', *list(map(lambda z: "S"+str(z), range(2))),
                    *list(map(lambda z: "Sp"+str(z), range(2))), 'inv_vel', 'Sigma_transp', 'Kerma']
    collapse_xsf = ['nu_fiss', 'chi_del', 'chi_tot', 'chi_pro', 'fiss_energy']
    inherit = ['NPF', 'beta', 'beta_tot', 'lambda', 'lambda_tot', 'L', 'P1consistent', 'use_nxn', 'scat_n1n_exists']

    # compute normalisation constants
    for i, name in enumerate(materials.keys()):
        mat = materials[name]
        if i == 0:
            # instantiate new material
            homogmat = NEMaterial(init=True)
            setattr(homogmat, 'data_name', mixname)

            for attr in inherit:
                if not hasattr(mat, attr):
                    continue
                else:
                    setattr(homogmat, attr, getattr(mat, attr))

            G = len(energy_grid) - 1

            TOTFLX = np.zeros((G, ))
            FISSRR = np.zeros((G, ))
            FISPRD = np.zeros((G, ))

        if mat.data_origin == 'Serpent':
            w = volume['homog'][name]/volume['heter'][name]
        else:
            w = volume['homog'][name]

        TOTFLX += w*mat.flux  # total flux
        FISSRR += w*mat.flux*mat.Sigma_fiss  # Sigma_fiss. reaction rate
        FISPRD += w*mat.flux*mat.Sigma_fiss*mat.nu_fiss  # Sigma_fiss. production

    nMat = i
    setattr(homogmat, 'flux', TOTFLX)

    for key in [*collapse_xs, *collapse_xsf]: # loop over data
        for i, name in enumerate(materials.keys()): # sum over sub-regions
            mat = materials[name].__dict__
            flx = materials[name].flux

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
                if hasattr(materials[name], key):
                    if i == 0:
                        homogmat.__dict__[key] = w*mat[key]*flx
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx
                else:
                    continue
            elif key in collapse_xsf:
                if mat['Sigma_fiss'].max() <= 0:
                    notfiss = True
                else:
                    notfiss = False

                if key in ['nu_fiss', 'fiss_energy']:
                    if i == 0:
                        homogmat.__dict__[key] = w*mat[key]*flx*mat['Sigma_fiss']
                    elif notfiss:
                        continue
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx*mat['Sigma_fiss']
                elif key == 'chi_del':
                    if i == 0:
                        homogmat.__dict__[key] = np.zeros((homogmat.NPF, G))
                    elif notfiss:
                        continue
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx*mat['nuSigma_fiss']
                else:   # chi_pro and chi_tot
                    if i == 0:
                        homogmat.__dict__[key] = w*mat[key]*flx*mat['nuSigma_fiss']
                    elif notfiss:
                        continue
                    else:
                        homogmat.__dict__[key] += w*mat[key]*flx*mat['nuSigma_fiss']
            else:
                continue
    # normalise group constants
    hd = homogmat.__dict__
    for key in ['nu_fiss', 'fiss_energy']:
        tmp = np.divide(hd[key], FISSRR, where=FISSRR!=0)
        hd[key] = tmp
    for key in ['chi_tot', 'chi_pro', 'chi_del']:
        if FISPRD.sum() > 0:
            tmp = np.divide(hd[key], FISPRD, where=FISPRD!=0)
            hd[key] = tmp
        else:
            hd[key] = tmp
    for key, data in homogmat.__dict__.items():
        if key in collapse_xs:
            tmp = np.divide(data, TOTFLX, where=TOTFLX!=0)
            hd[key] = tmp

    hd["Diffcoef"] = 1/(3*hd["Sigma_transp"])

    if add_missing_MGC:
        homogmat.add_missing_MGC(energy_grid=energy_grid)

    if fixdata:
        homogmat.repair_MGC()

    return homogmat


class NEMaterial():
    """Create material regions with multi-group constants.

    Parameters
    ----------
    data_name: str
        Universe name.
    energy_grid: iterable
        Energy group structure containing nE+1 group boundaries where nE is the
        number of energy groups.
    datapath: str, optional
        Path to the file containing the data, by default ``None``. If ``None``,
        data are taken from the local database.
    energy_grid_name : str, optional
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
    energy_grid_name: str
        Name of the energy grid.
    energy_grid: list
        List of energy group boundaries.
    data_name: str
        Name of the material.
    NPF: int
        Number of neutron precursors families.
    L: int
        Scattering anisotropy order
    Sigma_tot: np.array
        1D array of length ``nE`` with the total cross section in cm^-1.
    Sigma_abs: np.array
        1D array of length ``nE`` with the absorption cross section in cm^-1.
    Sigma_capt: np.array
        1D array of length ``nE`` with the capture cross section in cm^-1.
    Sigma_fiss: np.array
        1D array of length ``nE`` with the fission cross section in cm^-1.
    Sigma_rem: np.array
        1D array of length ``nE`` with the removal cross section in cm^-1.
    Sigma_transp: np.array
        1D array of length ``nE`` with the transport cross section in cm^-1.
    NuSf: np.array
        1D array of length ``nE`` with the fission production cross section in cm^-1.
    Diffcoef: np.array
        1D array of length ``nE`` with the diffusion coefficient in cm.
    Difflength: np.array
        1D array of length ``nE`` with the diffusion length in cm.
    S0: np.array
        2D array of size ``(nE, nE)`` with the scattering matrix cross section in cm^-1.
    chi_tot: np.array
        1D array of size ``nE`` with the total fission emission spectrum.
    chi_pro: np.array
        1D array of size ``nE`` with the prompt fission emission spectrum.
    chi_del: np.array
        1D array of size ``nE`` with the delayed fission emission spectrum.
    nu_fiss: np.array
        1D array of size ``nE`` with the number of neutrons emitted by fission.
    inv_vel: np.array
        1D array of size ``nE`` with the inverse of the neutron velocity in s/cm.
    lambda: np.array
        1D array of size ``NPF`` with the decay constants of the precursors.
    beta: np.array
        1D array of size ``NPF`` with the delayed neutron fracitons.
    flux: np.array
        1D array of size ``nE`` with the flux energy spectrum in arbitrary units.

    
    """

    def __init__(self, data_in_dict=None, energy_grid=None, add_missing_MGC=True,
                 fixdata=True, init=False, use_nxn=False, P1consistent=False):

        # if h5file:
        #     if isinstance(h5file, dict):
        #         for k, v in h5file.items():
        #             if type(v) is bytes:
        #                 v = v.decode()
        #             self.__dict__[k] = v
        #     elif isinstance(h5file, str):
        #         raise OSError('To do')
        #     else:
        #         msg = f"h5file must be dict or str, not {type(h5file)}"
        #         raise TypeError(msg)
        if init:
            return
        else:
            for k, v in data_in_dict.items():
                self.__dict__[k] = v
        # FIXME 
        # if reader == 'nemtab':
            # fname = path.join(tpath, fname_ext)
            # if Path(fname).exists():
            #     param, param_combos, data, G = data_nemtab = self.from_nemtab(fname)
            #     if G != nE:
            #         raise OSError(f"Inconsistent number of groups for {fname}:{G}!={nE}")
            #     # temporary patch: just take the 1st combination
            #     P1, P2 = param_combos[0]
            #     if P1 > P2:
            #         Tf = P1
            #         Tc = P2
            #     else:
            #         Tf = P2
            #         Tc = P1
            #     # assign basic constants
            #     for key, val in data[0.0][0].items():
            #         if key == "Sigma_abs" and use_nxn:
            #             self.__dict__["Sigma_rabs"] = val
            #         elif key == "S0" and use_nxn:
            #             self.__dict__["Sp0"] = val
            #         else:
            #             self.__dict__[key] = val
            #     # assign kinetic parameters
            #     for key in data[0.0].keys():
            #         if isinstance(key, str):
            #             self.__dict__[key] = data[0.0][key]
            #     self.chi_pro = self.chi_tot*1
            #     # PATCH: add fictitious Sigma_fiss XS (keeping ESigF constant)
            #     Ef = 200.0*1.602176634E-13  # J
            #     self.Sigma_fiss = self.fiss_energy/Ef
            #     self.fiss_energy = np.asarray([Ef/1.602176634E-13]*G)
            #     check = self.fiss_energy*self.Sigma_fiss
            #     # WATCH OUT Sp0+Sigma_rabs treatment?

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

        if add_missing_MGC:
            # TODO FIXME add "add_missing MGC" to self
            self.add_missing_MGC(energy_grid=energy_grid)

        if fixdata:
            self.repair_MGC()


    def get_MGC(self, key, pos1=None, pos2=None):
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
        E = self.energy_grid
        ax = ax or plt.gca()
        xs = self.__dict__[what]
        whatlabel = xslabels[what]
        if 'S' in what:
            if depgro:
                xs = xs[depgro, :]
                whatlabel = f'{xslabels[what]} from g={depgro}'
            else:
                raise OSError('Material.plot: depgro variable needed!')
        elif what == 'chi_del':
            xs = xs[family-1, :]
        elif what == 'flux':
            if normalise:
                u = np.log(self.energy_grid/self.energy_grid[0])
                xs = xs/np.diff(-u)


        if 'Chi' in what:
            xs = xs/xs.dot(-np.diff(E))

        if 'S' in what:
            uom = units['S']
        else:
            uom = units[what]

        if 'flux' in what and normalise:
            whatlabel = 'Flux per unit lethargy'

        if usetex:
            uom = f'$\\rm {uom}$'

        if 'label' not in kwargs.keys():
            kwargs['label'] = what

        plt.stairs(xs, edges=E, baseline=None, **kwargs)
        ax.set_xlabel('E [MeV]')
        ax.set_ylabel(f'{whatlabel} [{uom}]')
        ax.set_xscale('log')
        if what not in ['nu_fiss', 'chi_del', 'chi_pro', 'chi_tot']:
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
            indicating the data. For instance, ``what="Sigma_fiss"`` or ``what="nu_fiss"``.
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
            densdata = ['Sigma_capt', 'Sigma_fiss', *list(map(lambda z: "S"+str(z), range(self.L))),
                        *list(map(lambda z: "Sp"+str(z), range(self.L)))]
            if howmuch < 0:
                raise OSError('Cannot apply negative density perturbations!')
            for xs in densdata:
                self.__dict__[xs][:] = self.__dict__[xs][:]*howmuch
        else:
            depgro = depgro - 1 if depgro is not None else depgro
            if self.__dict__[what].shape == 1:
                G = len(self.__dict__[what])
            else:
                G = self.__dict__[what].shape[0]
            for g in range(G):
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
                    if what == 'Sigma_fiss':
                        self.nuSigma_fiss[g] = self.nu_fiss[g]*mydic[what][g]
                    elif what == 'nu_fiss':
                        self.nuSigma_fiss[g] = self.Sigma_fiss[g]*mydic[what][g]
                        # computesumxs = False
                    elif what.startswith('Chi'):
                        if what in ['chi_tot']:
                            mydic[what] = mydic[what]*(1+delta)
                        else:
                            raise OSError('Delayed/prompt spectra \
                                           perturbation still missing!')
                    elif what == 'Diffcoef':
                        # Hp: change in diffcoef implies change in capture
                        delta = 1/(3*mydic[what][g])-self.Sigma_transp[g]
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
            self.repair_MGC()

    def repair_MGC(self):
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
        if np.count_nonzero(self.Sigma_tot) != self.Sigma_tot.shape[0]:
            self.bad_data = True
            # ensure that Sigma_capt matches tot where tot is zero
            self.Sigma_capt[self.Sigma_tot <= 0] = 1E-5
            # modify Sigma_tot accordingly
            self.Sigma_tot[self.Sigma_tot <= 0] = 1E-5

        # TODO propose a quick fix for bad_data True
        self.nuSigma_fiss = self.Sigma_fiss*self.nu_fiss
        self.Sigma_abs = self.Sigma_fiss + self.Sigma_capt
        if np.count_nonzero(self.Sigma_abs == 0) > 0:
            raise OSError(f"0 in Sigma_abs for {self.data_name}!")

        if self.use_nxn:
            InScatt = np.diag(self.Sp0)
            sTOT = self.Sp0.sum(axis=0) if len(self.Sp0.shape) > 1 else self.Sp0
            if hasattr(self, 'Sp1'):
                sTOT1 = self.Sp1.sum(axis=0) if len(self.Sp1.shape) > 1 else self.Sp1
            else:
                sTOT1 = np.zeros(sTOT.shape)
            # if not np.array_equal(self.Sigma_rabs, self.Sigma_abs):
            #     if min(self.Sigma_rabs) < 0:
            #         self.Sigma_rabs = self.Sigma_abs
            #     self.Sigma_capt = self.Sigma_rabs - self.Sigma_fiss
        else:
            InScatt = np.diag(self.S0)
            sTOT = self.S0.sum(axis=0) if len(self.S0.shape) > 1 else self.S0
            sTOT1 = self.S1.sum(axis=0) if len(self.S1.shape) > 1 else self.S1

        # --- compute diffusion coefficient and transport xs
        if self.P1consistent:
            # --- compute transport xs (derivation from P1)
            self.Sigma_transp = self.Sigma_tot-sTOT1
            self.Diffcoef = 1/(3*self.Sigma_transp)
        else:
            self.Sigma_transp[self.Sigma_transp <= 1E-8] = 1E-8
            self.Diffcoef = 1/(3*self.Sigma_transp)

        self.Sigma_rem = self.Sigma_tot - InScatt

        self.DiffLength = np.sqrt(self.Diffcoef / self.Sigma_rem)

        self.MeanFreePath = 1 / self.Sigma_tot.max()

        # self.Sigma_fiss[self.Sigma_fiss <= 5E-7] = 0

        isFiss = self.Sigma_fiss.max() > 0

        if isFiss:
            self.chi_tot /= self.chi_tot.sum()

        kincons = True
        for s in kinetic_data:
            if s not in datavail:
                kincons = False
                self.__dict__[s] = [0]

        if kincons:
            if isFiss:
                if len(self.chi_del.shape) == 1:
                    # each family has same emission spectrum
                    # FIXME FIXME check Serpent RSD and do correction action
                    self.chi_del[self.chi_del <= 1E-4] = 0
                    self.chi_del /= self.chi_del.sum()
                    self.chi_del = np.asarray([self.chi_del]*self.NPF)
                elif self.chi_del.shape != (self.NPF, len(self.Sigma_tot)):
                    raise NEMaterialError(f'Delayed Sigma_fiss. spectrum should be \
                                    ({self.NPF}, {len(self.Sigma_tot)})')

                # FIXME FIXME check Serpent RSD and do correction action
                self.chi_pro[self.chi_pro <= 1E-4] = 0

                try:
                    for g in range(len(self.Sigma_tot)):
                        chit = (1-self.beta.sum())*self.chi_pro[g] + \
                                np.dot(self.beta, self.chi_del[:, g])
                        if abs(self.chi_tot[g]-chit) > 1E-3:
                            raise NEMaterialError()
                except NEMaterialError:
                    logger.warning(f'Fission spectra or delayed fractions'
                                    f' in {self.data_name} not consistent! '
                                    'Forcing consistency acting on chi-prompt...')
                else:
                    self.chi_pro = (self.chi_tot-np.dot(self.beta, self.chi_del))/(1-self.beta.sum())
                    for g in range(len(self.Sigma_tot)):
                        chit = (1-self.beta.sum())*self.chi_pro[g] + \
                                np.dot(self.beta, self.chi_del[:, g])
                        if abs(self.chi_tot[g]-chit) > 1E-4:
                            raise NEMaterialError("Normalisation failed!")

            # ensure pdf normalisation
            if isFiss:
                self.chi_pro /= self.chi_pro.sum()
                for p in range(self.NPF):
                    if self.chi_del[p, :].sum() > 0:
                        self.chi_del[p, :] /= self.chi_del[p, :].sum()

    def add_missing_MGC(self, energy_grid=None):
        """Add missing group constants.

        Parameters
        ----------
        ``None``.

        Returns
        -------
        ``None``.

        """
        # TODO if not existing, compute the flux assuming an infinite medium
        datadic = self.__dict__
        datavail = copy(list(datadic.keys()))
        # --- check basic reactions existence
        for s in basicdata:
            if s not in datavail:
                if (s == 'nuSigma_fiss' and 'nu_fiss' in datavail) or (s == 'nu_fiss' and 'Sigma_fiss' in datavail and 'nu_fiss') or (s == 'Sigma_fiss' and 'nu_fiss' in datavail):
                    continue
                elif (s == 'S0' and 'Sp0' in datavail) or (s == 'Sp0' and 'S0' in datavail):
                    continue
                else:
                    msg = f'{s} is missing in {self.data_name} data!'
                    logger.error(msg)
                    raise OSError(msg)

        # --- compute fission production cross section
        if hasattr(self, 'nu_fiss') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'nuSigma_fiss'):
                self.nuSigma_fiss = self.Sigma_fiss*self.nu_fiss
                logger.warning(f"'nuSigma_fiss' defined from available 'nu_fiss' and 'Sigma_fiss' for {self.data_name}.")
        elif hasattr(self, 'nuSigma_fiss') and hasattr(self, 'nu_fiss'):
            if not hasattr(self, 'Sigma_fiss'):
                if max(self.nu_fiss) > 0:
                    self.Sigma_fiss = self.nuSigma_fiss / self.nu_fiss
                    logger.warning(f"'Sigma_fiss' defined from available 'nu_fiss' and 'nuSigma_fiss' for {self.data_name}.")
                else:
                    self.Sigma_fiss = np.zeros((len(self.nu_fiss), ))
                    logger.warning(f"'Sigma_fiss' set to zero for {self.data_name}.")
        elif hasattr(self, 'nuSigma_fiss') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'nu_fiss'):
                if min(self.Sigma_fiss) > 0: 
                    self.nu_fiss = self.nuSigma_fiss / self.Sigma_fiss
                    logger.warning(f"'nu_fiss' defined from available 'nuSigma_fiss' and 'Sigma_fiss' for {self.data_name}.")
                else:
                    self.nu_fiss = copy(self.Sigma_fiss)
                    logger.warning(f"'nu_fiss' set to zero for {self.data_name}.")
        else:
            raise OSError('To compute fission data at least two out of the three data "nuSigma_fiss","nu_fiss" and "Sigma_fiss" are required')

        # --- add scattering matrices
        if not hasattr(self, 'Sp0'):
            self.Sp0 = self.S0
            logger.warning(f"'Sp0' set equal to 'S0' for {self.data_name}.")

            if self.use_nxn:
                self.use_nxn = False
                logger.info(f"(n,xn) scattering reactions not considered for {self.data_name} since no Sp0 in input!")

        if not hasattr(self, 'S0'):
            self.scat_n1n_exists = 0
            self.S0 = self.Sp0
            logger.warning(f"'Sp0' set equal to 'S0' for {self.data_name}.")
        else:
            self.scat_n1n_exists = 1

        if self.scat_n1n_exists:
            InScatt = np.diag(self.S0)
            sTOT = self.S0.sum(axis = 0) if len(self.S0.shape) > 1 else self.S0

        # --- compute missing sum reactions
        if hasattr(self, 'Sigma_capt') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'Sigma_abs'):
                self.Sigma_abs = self.Sigma_fiss + self.Sigma_capt
                logger.warning(f"'Sigma_abs' defined from available 'Sigma_fiss' and 'Sigma_capt' for {self.data_name}.")

        elif hasattr(self, 'Sigma_abs') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'Sigma_capt'):
                self.Sigma_capt = self.Sigma_abs - self.Sigma_fiss
                logger.warning(f"'Sigma_capt' defined from available 'Sigma_fiss' and 'Sigma_abs' for {self.data_name}.")

        elif hasattr(self, 'Sigma_abs') and hasattr(self, 'Sigma_capt'):
            if not hasattr(self, 'Sigma_fiss'):
                self.Sigma_fiss = self.Sigma_abs - self.Sigma_capt
                logger.warning(f"'Sigma_fiss' defined from available 'Sigma_capt' and 'Sigma_abs' for {self.data_name}.")

        elif hasattr(self, 'Sigma_rabs') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'Sigma_capt'):
                self.Sigma_capt = self.Sigma_rabs - self.Sigma_fiss
                logger.warning(f"'Sigma_capt' defined from available 'Sigma_fiss' and 'Sigma_rabs' for {self.data_name}.")

        elif hasattr(self, 'Sigma_rabs') and hasattr(self, 'Sigma_capt'):
            if not hasattr(self, 'Sigma_fiss'):
                self.Sigma_fiss = self.Sigma_rabs - self.Sigma_capt
                logger.warning(f"'Sigma_fiss' defined from available 'Sigma_capt' and 'Sigma_rabs' for {self.data_name}.")

        elif hasattr(self, 'Sigma_rem') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'Sigma_abs'):
                self.Sigma_abs = self.Sigma_rem - sTOT + InScatt
                logger.warning(f"'Sigma_abs' defined from available 'Sigma_rem' and 'Sigma_fiss' for {self.data_name}.")

            if not hasattr(self, 'Sigma_capt'):
                self.Sigma_capt = self.Sigma_abs - self.Sigma_fiss
                logger.warning(f"'Sigma_capt' defined from available 'Sigma_rem' and 'Sigma_fiss' for {self.data_name}.")

        elif hasattr(self, 'Sigma_rem') and hasattr(self, 'Sigma_capt'):
            if not hasattr(self, 'Sigma_abs'):
                self.Sigma_abs = self.Sigma_rem - sTOT + InScatt
                logger.warning(f"'Sigma_abs' defined from available 'Sigma_rem' and 'Sigma_fiss' for {self.data_name}.")

            if not hasattr(self, 'Sigma_fiss'):
                self.Sigma_fiss = self.Sigma_abs - self.Sigma_capt
                logger.warning(f"'Sigma_fiss' defined from available 'Sigma_rem' and 'Sigma_capt' for {self.data_name}.")

        elif hasattr(self, 'Sigma_tot') and hasattr(self, 'Sigma_fiss'):
            if not hasattr(self, 'Sigma_capt'):
                self.Sigma_capt = self.Sigma_tot - sTOT - self.Sigma_fiss
                logger.warning(f"'Sigma_capt' defined from available 'Sigma_fiss' and 'Sigma_tot' for {self.data_name}.")

            if not hasattr(self, 'Sigma_abs'):
                self.Sigma_abs = self.Sigma_fiss + self.Sigma_capt
                logger.warning(f"'Sigma_abs' defined from available 'Sigma_capt' and 'Sigma_fiss' for {self.data_name}.")

        # --- add missing data
        if not hasattr(self, 'Sigma_rabs'):
            self.Sigma_rabs = self.Sigma_abs
            logger.warning(f"'Sigma_rabs' set equal to 'Sigma_abs' for {self.data_name}.")

        if not hasattr(self, 'Sigma_abs'):
            self.Sigma_abs = self.Sigma_rabs
            logger.warning(f"'Sigma_abs' set equal to 'Sigma_rabs' for {self.data_name}.")

        if not hasattr(self, 'Sigma_rem'):
            if self.scat_n1n_exists:
                self.Sigma_rem = self.Sigma_abs + sTOT - InScatt
                logger.warning(f"'Sigma_rem' defined from available 'Sigma_abs' and 'S0' for {self.data_name}.")
            else:
                logger.warning(f"'Sigma_rem' not defined because 'S0' is missing for {self.data_name}.")

        if not hasattr(self, 'Sigma_tot'):
            if self.scat_n1n_exists:
                self.Sigma_tot = self.Sigma_abs + sTOT
                logger.warning(f"'Sigma_tot' defined from available 'Sigma_abs' and 'S0' for {self.data_name}.")
            elif self.use_nxn:
                self.Sigma_tot = self.Sigma_rabs +  self.Sp0.sum(axis = 0)
                logger.warning(f"'Sigma_tot' defined from available 'Sigma_rabs' and 'Sp0' for {self.data_name}.")

        if not hasattr(self, 'S1'):
            # # estimate mu0
            # mu0 = (self.Sigma_tot - self.Sigma_transp)/(self.S0.sum(axis = 0))
            # self.S1 = (mu0*self.S0.T).T
            # tot = self.Sigma_tot - self.S1.sum(axis = 0)
            self.S1 = self.S0

        # ensure non-zero total XS
        self.bad_data = False
        if np.count_nonzero(self.Sigma_tot) != self.Sigma_tot.shape[0]:
            self.bad_data = True

        if not hasattr(self, "inv_vel"):
            # if not hasattr(self, "fine_energygrid"):
            if energy_grid is None:
                raise OSError(f"'inv_vel' is missing from data {self.data_name} and no energy grid provided.")
            else:
                avgE = 1/2 * (energy_grid[:-1] + energy_grid[1:]) * 1.602176634E-13  # J
                v = np.sqrt(2 * avgE / 1.674927351e-27)
                self.inv_vel = 1/(v * 100)  # s/cm
                logger.warning(f"'inv_vel' defined from the average kinetic energy in group g for {self.data_name}.")

        # --- compute diffusion coefficient and transport xs
        if not hasattr(self, 'Sigma_transp'):
            if hasattr(self, 'Diffcoef'):
                self.Sigma_transp = 1/(3*self.Diffcoef)
                logger.warning(f"'Sigma_transp' defined from available 'Diffcoef' for {self.data_name}.")

            else:
                if hasattr(self, 'S1') and self.P1consistent:
                    self.Sigma_transp = self.Sigma_tot-self.S1.sum(axis=0)
                    logger.warning(f"'Sigma_transp' defined from available 'Sigma_tot' and 'S1' for {self.data_name}.")

                else:
                    # assuming isotropic scattering
                    self.Sigma_transp = self.Sigma_tot
                    logger.warning(f"'Sigma_transp' defined from available 'Diffcoef' for {self.data_name}.")

        if not hasattr(self, 'Diffcoef'):
            self.Diffcoef = 1/(3*self.Sigma_transp)

        # --- compute diffusion length
        # if not hasattr(self, 'DiffLength'):
        #     if not hasattr(self, 'Sigma_rem'):
        #         self.DiffLength = np.sqrt(self.Diffcoef / self.Sigma_abs)
        #     else:
        #         self.DiffLength = np.sqrt(self.Diffcoef / self.Sigma_rem)
        # --- compute mean free path
        if not hasattr(self, 'MeanFreePath'):
            if self.Sigma_tot.max() <= 0:
                idg = np.argmax(self.Sigma_tot)
                logger.warning(f"max(Sigma_tot)=0 for {self.data_name} in {idg}.")
                self.MeanFreePath = 1E15
            else:
                self.MeanFreePath = 1/self.Sigma_tot.max()
        # --- ensure consistency kinetic parameters (if fissile medium)
        isFiss = self.Sigma_fiss.max() > 0
        if not hasattr(self, "fiss_energy"):
            if isFiss:
                self.fiss_energy = np.asarray([200]*len(self.nu_fiss))
            else:
                self.fiss_energy = np.asarray([0]*len(self.Sigma_abs))

        if not hasattr(self, "chi_tot"):
            if isFiss:
                raise OSError(f"'chi_tot' is missing from data {self.data_name}")
            else:
                self.chi_tot = np.zeros((len(self.Sigma_abs), ))

        kincons = True
        for s in kinetic_data:
            if s not in datavail:
                kincons = False
                self.__dict__[s] = np.zeros((self.NPF,))
                # FIXME this produces "nu_fiss_del_tot" which is meaningless
                self.__dict__[f"{s}_tot"] = np.zeros((self.NPF,))

        if kincons:
            if not hasattr(self, "beta"):
                if isFiss:
                    raise OSError(f"'beta' is missing for {self.data_name}")
                else:
                    self.beta = np.zeros((self.NPF,))

            if not hasattr(self, "lambda"):
                if isFiss:
                    raise OSError(f"'lambda' is missing for {self.data_name}")
                else:
                    self.__dict__["lambda"] = np.zeros((self.NPF,))

            if not hasattr(self,"beta_tot"):
                self.beta_tot = self.beta.sum()
            if not hasattr(self, "lambda_tot"):
                # FIXME # TODO
                self.__dict__["lambda_tot"] = np.mean(self.__dict__["lambda"])

            if not hasattr(self, "chi_pro"):
                if isFiss:
                    if hasattr(self, "chi_del"):
                        self.chi_pro = (self.chi_tot-np.dot(self.beta, self.chi_del))/(1-self.beta.sum())
                    else:
                        raise OSError(f"'chi_pro' is missing from data {self.data_name}")
                else:
                    self.chi_pro = np.zeros((len(self.Sigma_abs), ))

            if not hasattr(self, "chi_del"):
                if isFiss:
                    self.chi_del = (self.chi_tot-self.chi_pro*(1-self.beta.sum()))/(self.beta.sum())
                else:
                    self.chi_del = np.zeros((self.NPF, len(self.Sigma_abs)))

        if not hasattr(self, "kerma"):
            self.kerma = np.zeros((len(self.Sigma_abs), ))

        if not hasattr(self, "flux"):
            # FIXME: an improved option can be estimating the flux axial prof. with analytical profiles
            # e.g. cos(Bz) if self.Sigma_fiss != 0 or exp(-z/L)+exp(+z/L) if self.Sigma_fiss = 0
            self.flux = np.ones((len(self.Sigma_abs), ))

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
            f'{self.data_name}_{self.energy_grid_name}.json'
        tmp = {}
        with open(fname, 'w') as f:

            for k, v in self.__dict__.items():
                if isinstance(v, (np.ndarray)):
                    tmp[k] = v.tolist()
                else:
                    tmp[k] = v

            json.dump(tmp, f, sort_keys=True, indent=10)

    def collapse(self, fewgrp_grid, multigrp_grid, spectrum=None, fixdata=True,
                add_missing_MGC=True):
        """Collapse in energy the multi-group data.

        Parameters
        ----------
        fewgrp_grid : iterable
            Few-group structure to perform the collapsing.
        spectrum: array, optional
            Spectrum to perform the energy collapsing, by default ``None``. If ``None``,
            the ``flux`` attribute is used as a weighting spectrum.
        energy_grid_name: str, optional
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
            flux = spectrum
        else:
            if not hasattr(self, 'flux'):
                raise OSError('Collapsing failed: weighting flux missing in '
                              f'{self.data_name}')
            else:
                flux = self.flux

        # few_into_multigrp = multigroup_onto_fewgroup(multi_g_grid, few_g_grid[str(case)])
        if isinstance(fewgrp_grid, list):
            fewgrp_grid = np.asarray(fewgrp_grid)
        # ensure descending order
        fewgrp_grid = fewgrp_grid[np.argsort(-fewgrp_grid)]
        H = len(multigrp_grid)-1
        G = len(fewgrp_grid)-1
        # sanity checks
        if G >= H:
            raise NEMaterialError(f'Collapsing failed: few-group structure should',
                          ' have less than {H} group')
        if multigrp_grid[0] != fewgrp_grid[0] or multigrp_grid[-1] != fewgrp_grid[-1]:
            raise NEMaterialError('Collapsing failed: few-group structure'
                                'boundaries do not match with multi-group'
                                'one')
        # map fewgroup onto multigroup
        few_into_multigrp = np.zeros((G+1,), dtype=int)
        # multigrp_bin = np.zeros((H+1,), dtype=int)
        for ig, g in enumerate(fewgrp_grid):
            reldiff = abs(multigrp_grid-g)/g
            idx = np.argmin(reldiff)
            if (reldiff[idx] > 1E-5):
                raise NEMaterialError(f'Group boundary n.{ig}={g} MeV of the collapsing grid not present in the fine grid!')
            else:
                few_into_multigrp[ig] = idx
                # multigrp_bin[idx] = 1

        collapsed = {}
        collapsed['flux'] = np.zeros((G, ))

        # manage reduced absorption collapsing
        if hasattr(self, "Sigma_rabs"):
            # collapse the (n,xn) cross section
            xs_abs_nxn = self.Sigma_abs - self.Sigma_rabs
            collapsed["Sigma_rabs"] = np.zeros((G, ))

        for g in range(G):
            # select fine groups in g
            G1, G2 = fewgrp_grid[g], fewgrp_grid[g+1]
            iS = few_into_multigrp[g]
            iE = few_into_multigrp[g+1]
            # compute flux in g
            NC = flux[iS:iE].sum()
            collapsed['flux'][g] = NC
            # --- collapse
            for key, v in self.__dict__.items():
                # --- cross section and inverse of velocity
                if key in collapse_xs:
                    # --- preallocation
                    if key in scatt_mat_keys:
                        dims = (G, G)
                    else:
                        dims = (G, )

                    if g == 0:
                        collapsed[key] = np.zeros(dims)

                    if len(dims) == 1:
                        if key == 'Diffcoef':
                            v = self.Sigma_transp
                            v = 1/3/v
                        collapsed[key][g] = np.divide(flux[iS:iE].dot(v[iS:iE]), NC, where=NC!=0)
                    else:
                        # --- scattering
                        for g2 in range(G):  # arrival group
                            I1, I2 = fewgrp_grid[g2], fewgrp_grid[g2+1]
                            iS2 = few_into_multigrp[g2]
                            iE2 = few_into_multigrp[g2+1]
                            s = v[iS:iE, iS2:iE2].sum(axis=0)
                            NCS = flux[iS2:iE2].sum()
                            collapsed[key][g][g2] = np.divide(flux[iS2:iE2].dot(s), NCS, where=NCS!=0)
                            iS2 = iE2
                # --- fission-related data
                elif key in collapse_xsf:
                    if self.Sigma_fiss.max() <= 0:
                        if key == 'chi_del':
                            collapsed[key] = np.zeros((self.NPF, G))
                        else:
                            collapsed[key] = np.zeros((G, ))
                        continue
                    fissrate = flux[iS:iE]*self.Sigma_fiss[iS:iE]
                    FRC = fissrate.sum()
                    if key == 'chi_del':
                        if g == 0:
                            collapsed[key] = np.zeros((self.NPF, G))
                        for p in range(self.NPF):
                            # TODO FIXME
                            if len(v.shape) > 1:
                                collapsed[key][p, g] = v[p, iS:iE].sum()
                            else:
                                collapsed[key][p, g] = v[iS:iE].sum()
                    else:
                        if g == 0:
                            collapsed[key] = np.zeros((G, ))

                        if key in ['chi_tot', 'chi_pro']:
                            collapsed[key][g] = v[iS:iE].sum()
                        else:
                            collapsed[key][g] = np.divide(fissrate.dot(v[iS:iE]), FRC, where=FRC!=0)
                else:
                    continue

            # --- reduced absorption
            if hasattr(self, "Sigma_rabs"):
                xs_abs_nxn_g = np.divide(flux[iS:iE].dot(xs_abs_nxn[iS:iE]), NC, where=NC!=0)
                collapsed["Sigma_rabs"][g] = collapsed["Sigma_capt"][g] + collapsed["Sigma_fiss"][g] - xs_abs_nxn_g

            iS = iE

        collapsed['Sigma_transp'] = 1/(3*collapsed['Diffcoef'])
        self.P1consistent = False # to "preserve" diffcoef
        # overwrite data
        for key in self.__dict__.keys():
            if key in collapsed.keys():
                self.__dict__[key] = collapsed[key]

        # clean data scored over the fine-group grid
        self_keys = list(self.__dict__.keys())
        for key in self_keys:
            if key in delete_for_collapse:
                del self.__dict__[key]

        if add_missing_MGC:
            self.add_missing_MGC(energy_grid=fewgrp_grid)

        # ensure data consistency
        if fixdata:
            self.repair_MGC()

    def isfiss(self):
        """Assess whether the material is fissile"""
        return self.Sigma_fiss.max() > 0 and self.nu_fiss.max() > 0
    

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