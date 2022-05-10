"""
Author: N. Abrate.

File: MaterialData.py

Description: Class that define core material (NE/TH/PH) data.
"""
import os
import warnings
import coreutils
from os import path
from pathlib import Path
import serpentTools as st
from serpentTools import read
from serpentTools.settings import rc as rcst
import json
import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy as copy
from matplotlib import rc, checkdep_usetex

from os.path import join

usetex = checkdep_usetex(True)
rc("font", **{"family": "sans-serif", "sans-serif": ["Helvetica"]})
rc("text", usetex=usetex)

scatt_keys = [*list(map(lambda z: "infS"+str(z), range(2))),
            *list(map(lambda z: "infSp"+str(z), range(2)))]
xsdf_keys = ['infTot', 'infAbs', 'infDiffcoef', 'infTranspxs', 'infCapt',
            'infRemxs', 'infFiss', 'infNsf']
ene_keys = ['infNubar', 'infInvv', 'infKappa', 'infInvv',  'infChit',
            'infChip', 'infChid']

serp_keys = [*scatt_keys, *xsdf_keys, *ene_keys, 'infFlx']

sumxs = ['Tot', 'Abs', 'Remxs']
indepdata = ['Capt', 'Fiss', 'S0', 'Nubar', 'Diffcoef', 'Chid', 'Chip']
basicdata = ['Fiss', 'Nubar', 'S0', 'Chit']
kinetics = ['lambda', 'beta']
alldata = list(set([*sumxs, *indepdata, *basicdata, *kinetics]))

collapse_xs = ['Fiss', 'Capt', *list(map(lambda z: "S"+str(z), range(2))),
                *list(map(lambda z: "Sp"+str(z), range(2))), 'Invv']
collapse_xsf = ['Nubar', 'Chid', 'Chit', 'Chip', 'Kappa']

units = {'Chid': '-', 'Chit': '-', 'Chip': '-', 'Tot': 'cm^{-1}',
        'Capt': 'cm^{-1}', 'Abs': 'cm^{-1}', 'Fiss': 'cm^{-1}',
        'NuSf': 'cm^{-1}', 'Remxs': 'cm^{-1}', 'Transpxs': 'cm^{-1}',
        'Kappa': 'MeV', 'S': 'cm^{-1}', 'Nubar': '-', 'Invv': 's/cm',
        'Difflenght': 'cm^2', 'Diffcoef': 'cm', 'Flx': 'a.u.'}
xslabels = {'Chid': 'delayed fiss. emission spectrum', 'Chit': 'total fiss. emission spectrum',
            'Chip': 'prompt fiss. emission spectrum', 'Tot': 'Total xs',
            'Capt': 'Capture xs', 'Abs': 'Absorption xs', 'Fiss': 'Fission xs',
            'NuSf': 'Fiss. production xs', 'Remxs': 'Removal xs', 'Transpxs': 'Transport xs',
            'Kappa': 'Fiss. energy', 'S': 'Scattering xs', 'Nubar': 'neutrons by fission',
            'Invv': 'Inverse velocity', 'Difflenght': 'Diff. length', 'Diffcoef': 'Diff. coeff.',
            'Flx': 'Flux spectrum'}

def readSerpentRes(datapath, energygrid, T, beginswith,
                   egridname=False):
    """Read Serpent res file with Serpent tools

    Parameters
    ----------
    datapath : str
        Absolute path to NE data
    T : tuple or `None`
        Temperatures of fuel and coolant. If ``None``, temperature 
        dependence is ignored.
    beginswith : str
        Prefix of whole name of the file to be read. It can be the name
        of the file, without extension.

    Returns
    -------
    res
        dict of serpentTools parser object

    Raises
    ------
    OSError
        [description]
    OSError
        [description]
    OSError
        [description]
    """
    # -- serpentTools settings
    st.settings.rc['xs.variableGroups'] = ['kinetics', 'xs', 'xs-prod',
                                           'gc-meta']

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
        print(f"WARNING: {datapath} not found, looking in default tree...")
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
        fname = path.join(datapath, beginswith)    
    
    if '_res.m' not in str(fname):
        fname = f'{str(fname)}_res.m'
    else:
        fname = fname
        
    fname = path.join(spath, fname)
    if Path(fname).exists():
        res = read(fname)
    else:
        res = None

    return res


def Homogenise(materials, weights, mixname, P1consistent=False):
    """
    Homogenise multi-group parameters.

    Parameters
    ----------
    w : dict

    Returns
    -------
    
    """
    collapse_xs = ['Fiss', 'Capt', *list(map(lambda z: "S"+str(z), range(2))),
                    *list(map(lambda z: "Sp"+str(z), range(2))), 'Invv', 'Transpxs']
    collapse_xsf = ['Nubar', 'Chid', 'Chit', 'Chip', 'Kappa']
    inherit = ['NPF', 'nE', 'egridname', 'beta', 'beta_tot', 'energygrid',
               'lambda', 'lambda_tot', 'L']
    # compute normalisation constants
    for i, name in enumerate(materials.keys()):
        mat = materials[name]
        if i == 0:
            homogmat = NEMaterial(init=True)
            setattr(homogmat, 'UniName', mixname)
            for attr in inherit:
                setattr(homogmat, attr, getattr(mat, attr))
            G = homogmat.nE
            TOTFLX = np.zeros((G, ))
            FISSRR = np.zeros((G, ))
            FISPRD = np.zeros((G, ))
        w = weights[name]
        TOTFLX += w*mat.Flx  # total flux
        FISSRR += w*mat.Flx*mat.Fiss  # fiss. reaction rate
        FISPRD += w*mat.Flx*mat.Fiss*mat.Nubar  # fiss. production

    nMat = i
    setattr(homogmat, 'flx', TOTFLX)

    for key in [*collapse_xs, *collapse_xsf]: # loop over data
        for i, name in enumerate(materials.keys()): # sum over sub-regions
            mat = materials[name].__dict__
            flx = materials[name].Flx
            w = weights[name]
            # homogdata = np.dot(flux, data)/sum(flux)
            # --- cross section and inverse of velocity
            if key in collapse_xs:
                if i == 0:
                    homogmat.__dict__[key] = w*mat[key]*flx
                else:
                    homogmat.__dict__[key] += w*mat[key]*flx
            elif key in collapse_xsf:
                if mat['Fiss'].max() <= 0:
                    notfiss = True
                else:
                    notfiss = False

                if key in ['Nubar', 'Kappa']:
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
    for key in ['Nubar', 'Kappa']:
        tmp = np.divide(hd[key], FISSRR, where=FISSRR!=0)
        hd[key] = tmp
    for key in ['Chit', 'Chip', 'Chid']:
        tmp = np.divide(hd[key], FISPRD, where=FISPRD!=0)
        hd[key] = tmp
    for key, data in homogmat.__dict__.items():
        if key in collapse_xs:
            tmp = np.divide(data, TOTFLX, where=TOTFLX!=0)
            hd[key] = tmp

    homogmat.datacheck(P1consistent=P1consistent)
    return homogmat

class NEMaterial():
    """Create material regions with multi-group constants."""

    def __init__(self, uniName=None, energygrid=None, datapath=None,
                 egridname=None, h5file=None, reader='json', serpres=None,
                 basename=False, temp=False, datacheck=True, init=False, P1consistent=False):
        """
        Initialise object.

        Parameters
        ----------
        uniName : str
            Universe name.
        energygrid : iterable
            Energy group structure.
        datapath : str, optional
            Path to the file containing the data. If ``None``,
            data are taken from the local database.
            The default is None.
        egridname : str, optional
            Name of the energy group structure. The default is ``None``.
        h5file: object
            h5 group from .h5 files.
        reader : str
            Type or reader. It can be 'serpent', 'json' or 'txt'.
        serpres : object
            Object created parsing the _res.m Serpent file with 
            serpentTools
        basename : bool or str
            if not ``False``, base name is used to compose the filenames, which 
            needs to be in the form <basename>_Tf_XXX_Tc_XXX. 
        temp : tuple
            if ``basename`` is not None, directories in the form 
            "Tf_{}_Tc_{}" are searched  and "Tf_{}_Tc_{}" suffix 
            is attached to the file name
        
        Raises
        ------
        OSError
            DESCRIPTION.

        Returns
        -------
        None.

        """
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
                if datapath is None:
                    pwd = Path(__file__).parent.parent.parent
                    if 'coreutils' not in str(pwd):
                        raise OSError(f'Check coreutils tree for NEdata: {pwd}')
                    # look into default NEdata dir
                    datapath = str(pwd.joinpath('NEdata', f'{egridname}'))
                    filename = uniName
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
                    # check for temperatures
                    if temp:
                        dirTfTc = f"Tf_{Tf}_Tc_{Tc}"
                        dirTcTf = f"Tc_{Tc}_Tf_{Tf}"                                   
                        if Path(path.join(jpath, dirTfTc)).exists():
                            jpath = path.join(jpath, dirTfTc, filename)
                        elif Path(path.join(jpath, dirTcTf)).exists():
                            path.join(jpath, dirTcTf, filename)

                        # if dirTcTf not in filename and dirTfTc not in filename:
                    else:
                        fname = path.join(jpath, filename)
                    
                    if '.json' not in str(filename):
                        fname = f'{str(filename)}.{reader}'
                    else:
                        fname = filename

                    fname = path.join(jpath, fname)
                    if Path(fname).exists():
                        self._readjson(fname)
                    else:
                        print(f'{fname} not found!')
                        reader = 'txt'

                if reader == 'txt':
                    # look into txt folder
                    if Path(path.join(datapath, "txt")).exists():
                        tpath = path.join(datapath, "txt")
                    else:
                        tpath = datapath

                    if temp:
                        dirTfTc = f"Tf_{Tf}_Tc_{Tc}"
                        dirTcTf = f"Tc_{Tc}_Tf_{Tf}"                                   
                        if Path(path.join(tpath, dirTfTc)).exists():
                            spath = path.join(tpath, dirTfTc, filename)
                        elif Path(path.join(tpath, dirTcTf)).exists():
                            path.join(tpath, dirTcTf, filename)

                    else:
                        fname = path.join(tpath, filename)    
                    
                    if '.txt' not in str(fname):
                        fname = f'{str(fname)}.{reader}'
                    else:
                        fname = filename

                    fname = path.join(tpath, fname)
                    if Path(fname).exists():
                        self._readtxt(fname, nE)
                    else:
                        raise OSError(f'{fname} not found!')
            else:
                self._readserpentres(serpres, uniName, nE, egridname)
            
            self.nE = nE
            self.egridname = egridname
            self.energygrid = energygrid
            self.UniName = uniName

            try:
                self.NPF = (self.beta).size
            except AttributeError:
                print('Kinetic parameters not available!')
                self.NPF = 1

            # --- complete data and perform sanity check
            L = 0
            datastr = list(self.__dict__.keys())
            # //2 since there are 'S' and 'Sp'
            S = sum('S' in s for s in datastr)//2
            self.L = S if S > L else L  # get maximum scattering order
            if datacheck:
                self.datacheck(P1consistent=P1consistent)

    def _readjson(self, path):
        """
        Read data from json file.

        Parameters
        ----------
        filename : str
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

    def _readserpentres(self, serpres, uniName, nE, egridname):

        data = None
        for res in serpres.values():
            try:
                data = res.getUniv(uniName, 0, 0, 0)
            except KeyError:
                continue

        if data is None:
            raise OSError(f'{uniName} data not available in Serpent files!')

        if len(data.infExp['infAbs']) != nE:
            raise OSError(f'{uniName} energy groups do not match with \
                          input grid!')

        selfdic = self.__dict__
        for my_key in serp_keys:

            if my_key.startswith('infS') or my_key.startswith('infSp'):
                vals = np.reshape(data.infExp[my_key], (nE, nE), order='F')
            else:
                vals = data.infExp[my_key]

            selfdic[my_key.split('inf')[1]] = vals

        # kinetics parameters
        selfdic['beta'] = res.resdata['fwdAnaBetaZero'][::2]
        selfdic['beta_tot'] = selfdic['beta'][0]
        selfdic['beta'] = selfdic['beta'][1:]
        # this to avoid confusion with python lambda function
        selfdic['lambda'] = res.resdata['fwdAnaLambda'][::2]
        selfdic['lambda_tot'] = selfdic['lambda'][0]
        selfdic['lambda'] = selfdic['lambda'][1:]

    def _readtxt(self, fname, nE):
        """
        Parse the material data from a .txt file.

        Macro-group constants are parsed from a formatted file with column-wise
        data separated by headers beginning with "#" and the name of the data:
            * Tot: total cross section [cm^-1]
            * Transpxs: transport cross section [cm^-1]
                        It is defined as total_xs-avg_direction*scattering_xs
                        according to P1 approximation.
            * Diffcoef: diffusion coefficient [cm]
                        It is defined as 1/(3*Transpxs).
            * Abs: absorption cross section [cm^-1]
                   It is the sum of Capt and Fiss cross sections.
            * Capt: capture cross section [cm^-1]
            * Fiss: fission cross section [cm^-1]
            * Remxs: removal cross section [cm^-1]
                    It is the sum of Abs and group-removal.
            * Chit: total emission spectrum [-]
            * Chip: prompt emission spectrum [-]
            * Chid: delayed emission spectrum [-]
            * Nsf: fission production cross section [cm^-1]
            * Nubar: neutron multiplicities [-]
            * Kappa: average fission deposited heat [MeV]
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

    def getxs(self, key, pos1=None, pos2=None):
        """
        Get material data (for a certain energy group, if needed).

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

    def plot(self, what, dep_group=None, family=1, ax=None, figname=None,
             normalise=True, **kwargs):

        E = self.energygrid
        ax = ax or plt.gca()
        xs = self.__dict__[what]
        whatlabel = xslabels[what]
        if 'S' in what:
            if dep_group:
                xs = xs[dep_group, :]
                whatlabel = f'{xslabels[what]} from g={dep_group}'
            else:
                raise OSError('Material.plot: dep_group variable needed!')
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

    def perturb(self, what, howmuch, depgro=None, sanitycheck=True, P1consistent=False):
        """

        Perturb material composition.

        Parameters
        ----------
        what : TYPE
            DESCRIPTION.
        howmuch : TYPE
            DESCRIPTION.

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
                        delta = 1/(3*mydic[what][g])-self.Transpxs[g]
                    elif what == 'S0':
                        # change higher moments, if any
                        for ll in range(self.L): # FIXME
                            R = (mydic[what][g]/mydic[what][g]-delta)
                            key = 'S%d' % ll
                            mydic[key][depgro][g] = mydic[key][depgro][g]*R

                else:
                    if sanitycheck:
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

        if sanitycheck:
            # force normalisation
            if abs(self.Chit.sum() - 1) > 1E-4:
                if np.any(self.Chit == 0) :
                    pass
                else:
                    self.Chit = self.Chit/self.Chit.sum()

            self.datacheck(P1consistent=P1consistent)

    def datacheck(self, P1consistent=False):
        """
        Check data consistency and add missing data.

        Returns
        -------
        None.

        """
        E = self.energygrid
        datadic = self.__dict__
        datavail = copy(list(datadic.keys()))
        # check basic reactions existence
        for s in basicdata:
            if s not in datavail:
                raise OSError(f'{s} is missing in {self.UniName} data!')
        # --- compute in-group scattering
        InScatt = np.diag(self.S0)
        sTOT = self.S0.sum(axis=0) if len(self.S0.shape) > 1 else self.S0
        # --- compute fission production cross section
        self.Nsf = self.Fiss*self.Nubar
        # --- compute missing sum reactions
        if 'Capt' in datavail:
            self.Abs = self.Fiss+self.Capt
        elif 'Abs' in datavail:
            self.Capt = self.Abs-self.Fiss
        elif 'Tot' in datavail:
            self.Capt = self.Tot-sTOT-self.Fiss
            self.Abs = self.Fiss+self.Capt

        self.Remxs = self.Abs+sTOT-InScatt
        self.Tot = self.Remxs+InScatt
        # ensure non-zero total XS
        self.Tot[self.Tot <= 0] = 1E-8
        if 'Invv' not in datavail:
            avgE = 1/2*(E[:-1]+E[1:])*1.602176634E-13  # J
            v = np.sqrt(2*avgE/1.674927351e-27)
            self.Invv = 1/(v*100)  # s/cm

        # --- compute diffusion coefficient and transport xs
        if P1consistent:
            if 'S1' in datavail:
                # --- compute transport xs (derivation from P1)
                self.Transpxs = self.Tot-self.S1.sum(axis=0)
                # mu0 = self.S1/self.S0
                self.Diffcoef = 1/(3*self.Transpxs)
            elif 'Diffcoef' in datavail:
                self.Transpxs = 1/(3*self.Diffcoef)
            elif 'Transpxs' in datavail:
                self.Transpxs[self.Transpxs <= 0] = 1E-8
                self.Diffcoef = 1/(3*self.Transpxs)
            else:
                self.Transpxs = self.Tot
                self.Diffcoef = 1/(3*self.Transpxs)
        else:
            # --- compute diffusion coefficient and transport xs
            if 'Transpxs' in datavail:
                self.Transpxs[self.Transpxs <= 1E-8] = 1E-8
                self.Diffcoef = 1/(3*self.Transpxs)
            elif 'Diffcoef' in datavail:
                self.Transpxs = 1/(3*self.Diffcoef)
            else:
                self.Transpxs = self.Tot
                self.Diffcoef = 1/(3*self.Transpxs)
        # --- compute diffusion length
        self.Remxs[self.Remxs <= 0] = 1E-8 # avoid huge diff. coeff. and length
        self.DiffLength = np.sqrt(self.Diffcoef/self.Remxs)
        # --- compute mean free path
        self.MeanFreePath = 1/self.Tot.max()
        # --- ensure consistency kinetic parameters (if fissile medium)
        self.Fiss[self.Fiss <= 5E-7] = 0
        isFiss = self.Fiss.max() > 0
        if isFiss:
            # FIXME FIXME check Serpent RSD and do correction action
            # self.Chit[self.Chit <= 1E-4] = 0
            if abs(self.Chit.sum() - 1) > 1E-4:
                print(f'Total fission spectra in {self.UniName} not normalised!'
                      'Forcing normalisation...')
            # ensure pdf normalisation
            self.Chit /= self.Chit.sum()
            if "Kappa" not in self.__dict__.keys():
                self.Kappa = np.array([200]*self.nE)
        else:
            self.Kappa = np.array([0]*self.nE)

        kincons = True
        for s in kinetics:
            if s not in datavail:
                kincons = False
                self.__dict__[s] = [0]

        if kincons:
            try:
                self.beta_tot = self.beta.sum()

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
                            if abs(self.Chit[g]-chit) > 1E-4:
                                raise NEMaterialError()
                    except NEMaterialError:
                        print(f'Fission spectra or delayed fractions'
                              f' in {self.UniName} not consistent! '
                              'Forcing consistency acting on chi-prompt...')
                    else:
                        self.Chip = (self.Chit-np.dot(self.beta, self.Chid))/(1-self.beta.sum())
                        for g in range(0, self.nE):
                            chit = (1-self.beta.sum())*self.Chip[g] + \
                                    np.dot(self.beta, self.Chid[:, g])
                            if abs(self.Chit[g]-chit) > 1E-4:
                                raise NEMaterialError("Normalisation failed!")
                else:
                    self.Chit = np.zeros((self.nE, ))
                    self.Chip = np.zeros((self.nE, ))
                    self.Chid = np.zeros((self.NPF, self.nE))

            except AttributeError as err:
                if 'Chid' in str(err) or 'Chip' in str(err):
                    self.Chid = np.asarray([self.Chit]*self.NPF)
                    self.Chip = self.Chit
                else:
                    print(err)

            # ensure pdf normalisation
            if isFiss:
                self.Chip /= self.Chip.sum()
                for p in range(self.NPF):
                    self.Chid[p, :] /= self.Chid[p, :].sum()
        else:
            if isFiss:
                self.Chip = self.Chit
                self.Chid = self.Chit
            else:
                self.Chit = np.zeros((self.nE, ))
                self.Chip = np.zeros((self.nE, ))
                self.Chid = np.zeros((self.NPF, self.nE))
  
    def void(self, keepXS=None, sanitycheck=True):
        """
        Make region void except for some group-wise user-specified reaction.

        Parameters
        ----------
        what : str
            DESCRIPTION.
        where : ndarray
            DESCRIPTION.
        howmuch : float
            DESCRIPTION.
        system : object
            DESCRIPTION.

        Returns
        -------
        None.

        """
        # add anisotropic XS
        for ll in range(self.L):
            new = f'S{ll}'
            newP = f'Sp{ll}'
            if new not in alldata:
                alldata.append(new)
            if newP not in alldata:
                alldata.append(newP)

        allkeys = False
        if isinstance(keepXS, dict):
            if 'all' in keepXS['reaction']:
                allkeys = True
                keepXS['reaction'] = []

        mydic = self.__dict__
        for what in mydic.keys():
            if allkeys:
                keepXS['reaction'].append(what)
            if what in alldata:
                if isinstance(keepXS, dict):
                    # keep or reject whole reaction channel
                    if what in keepXS['reaction']:
                        if 'energy' in keepXS.keys():
                            if keepXS['energy'] == 'all':
                                pass
                            else:
                                for g in range(self.nE):
                                    if g+1 not in keepXS['energy']:
                                        mydic[what][g] = 0
                    else:
                        mydic[what][:] = 0
                else:
                    mydic[what][:] = 0

    def to_json(self, fname=None):
        """
        Dump object to json file.

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

    def collapse(self, fewgrp, spectrum=None, egridname=None, P1consistent=False):
        """
        Collapse in energy the multi-group data.

        Parameters
        ----------
        fewgrp : iterable
            Few-group structure to perform the collapsing.

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
            if 'Flx' not in self.__dict__.keys():
                raise OSError('Collapsing failed: weighting flux missing in'
                              f'{self.UniName}')
            else:
                flx = self.Flx

        multigrp = self.energygrid
        if isinstance(fewgrp, list):
            fewgrp = np.asarray(fewgrp)
        # ensure descending order
        fewgrp = fewgrp[np.argsort(-fewgrp)]
        H = len(multigrp)-1
        G = len(fewgrp)-1
        # sanity check
        if G > H:
            raise OSError(f'Collapsing failed: few-group structure should \
                          have less than {H} group')
        if multigrp[0] != fewgrp[0] or multigrp[0] != fewgrp[0]:
            raise OSError('Collapsing failed: few-group structure  \
                          boundaries do not match with multi-group \
                          one')
        for ig, g in enumerate(fewgrp):
            if g not in multigrp:
                raise OSError(f'Group boundary n.{ig}, {g} MeV not present in fine grid!')

        iS = 0
        collapsed = {}
        collapsed['Flx'] = np.zeros((G, ))
        for g in range(G):
            # select fine groups in g
            G1, G2 = fewgrp[g], fewgrp[g+1]
            iE = np.argwhere(np.logical_and(multigrp[iS:] < G1,
                                            multigrp[iS:] >= G2))[-1][0]+iS
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
                        collapsed[key][g] = flx[iS:iE].dot(v[iS:iE])/NC
                    else:
                        # --- scattering
                        iS2 = 0
                        for g2 in range(G):  # arrival group
                            I1, I2 = fewgrp[g2], fewgrp[g2+1]
                            iE2 = np.argwhere(np.logical_and
                                              (multigrp[iS2:] < I1,
                                               multigrp[iS2:] >= I2))
                            iE2 = iE2[-1][0]+iS2
                            s = v[iS:iE, iS2:iE2].sum(axis=0)
                            NCS = flx[iS2:iE2].sum()
                            collapsed[key][g][g2] = flx[iS2:iE2].dot(s)/NCS
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

                        if 'Chi' in key:
                            collapsed[key][g] = v[iS:iE].sum()
                        else:
                            collapsed[key][g] = fissrate.dot(v[iS:iE])/FRC
                else:
                    continue
            iS = iE
        collapsed['Diffcoef'] = 1/(3*collapsed['Transpxs'])
        # overwrite data
        self.energygrid = fewgrp
        self.nE = G
        self.egridname = egridname if egridname else f'{G}G'
        for key in self.__dict__.keys():
            if key in collapsed.keys():
                self.__dict__[key] = collapsed[key]
        # ensure data consistency
        self.datacheck(P1consistent=P1consistent)


class NEMix(NEMaterial):
    # TODO check this actually works!
    """Create regions mixing other materials."""

    def __init__(self, *, universes, densities=None, energygrid, datapath=None,
                 egridname=None, reader='json', mixname=None, P1consistent=False):
        """
        Initialise object.

        Parameters
        ----------
        uniName : str
            Universe name.
        energygrid : iterable
            Energy group structure.
        datapath : str, optional
            Path to the file containing the data. If None,
            data are taken from the local database.
            The default is None.
        egridname : str, optional
            Name of the energy group structure. The default is None.

        Raises
        ------
        OSError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        nE = len(energygrid)-1
        egridname = egridname if egridname else f"{nE}G"

        if densities is not None:
            if len(universes) != len(densities):
                raise OSError('Number of regions and number of densities mismatch')
        else:
            densities = np.ones(len(universes))

        idx = 0
        nMat = len(universes)
        materials = dict(zip(universes, densities))
        xsf = {}
        fissionprod = np.zeros((nE, nMat))
        totfissxs = np.zeros((nE, ))
        betatot = np.zeros((nMat, ))
        beta = []
        for k, v in materials.items():
            xsf[k] = {}
            if datapath is not None:
                kpath = datapath[k]
            else:
                kpath = None

            mat = NEMaterial(uniName=k, energygrid=energygrid, datapath=kpath,
                           egridname=egridname, reader=reader)
            # density multiplication and summation
            for s in mat.__dict__.keys():
                if s in collapse_xs:
                    if idx == 0:
                        self.__dict__[s] = densities[idx]*mat.__dict__[s]
                    else:
                        self.__dict__[s] += densities[idx]*mat.__dict__[s]

            fissionprod[:, idx] = mat.Nubar*mat.Fiss
            totfissxs += mat.Fiss
            xsf[k]['Fiss'] = mat.Fiss
            for s in collapse_xsf:
                xsf[k][s] = mat.__dict__[s]
                self.__dict__[s] = np.zeros(mat.__dict__[s].shape)

            if 'beta' in mat.__dict__.keys():
                NPF = mat.NPF
                self.beta = np.zeros((NPF, ))
                self.Chid = np.zeros((NPF, nE))
                beta.append(mat.beta)
            if 'lambda' in mat.__dict__.keys():
                self.__dict__['lambda'] = np.zeros((mat.NPF, ))
                xsf[k]['lambda'] = mat.__dict__['lambda']

            idx += 1

        beta = np.asarray(beta)
        if self.Fiss.max() > 0:
            for i, k in enumerate(materials.keys()):
                fiss = xsf[k]['Fiss']
                nuba = xsf[k]['Nubar']
                # mix Nubar
                self.Nubar += fiss*nuba
                # mix emission spectra            
                self.Chit += xsf[k]['Chit']*np.sum(fiss*nuba)
                if beta.max() > 0:
                    self.beta += beta[i, :]*np.sum(fiss*nuba)
                    betatot[i] = beta[i, :].sum()
                    self.Chip += xsf[k]['Chip']*np.sum(fiss*nuba*(1-betatot[i]))
                    for f in range(NPF):
                        self.Chid[f, :] += xsf[k]['Chid'][f, :]*np.sum(fiss*nuba*beta[i, f])
                if 'lambda' in xsf[k].keys():
                    self.__dict__['lambda'] = xsf[k]['lambda']
                # mix fission heat

            self.Nubar = self.Nubar/totfissxs
            self.beta = self.beta/fissionprod.sum()
            self.Chit = self.Chit/fissionprod.sum()
            self.Chip = self.Chip/(fissionprod*(1-betatot)).sum()
            # FIXME Fission energy is missing!
            for f in range(NPF):
                self.Chid[f, :] = self.Chid[f, :]/(fissionprod*beta[:, f]).sum()
      
        # # TODO FIXME
        # if self.Fiss.max() > 0:
        #     for s in collapse_xsf:
        #         nu = mat.__dict__['Nubar'] if 'Chi' in s else 1
        #         self.__dict__[s] = self.__dict__[s]/np.sum(mat.__dict__['Fiss']*nu)

        if mixname is None:
            mixname = '_'.join(universes)

        self.nE = nE
        self.egridname = egridname
        self.energygrid = energygrid
        self.UniName = mixname

        try:
            self.NPF = (self.beta).size
        except AttributeError:
            print('Kinetic parameters not available!')
            self.NPF = None

        # --- complete data and perform sanity check
        L = 0
        datastr = list(self.__dict__.keys())
        # //2 since there are 'S' and 'Sp'
        S = sum('S' in s for s in datastr)//2
        self.L = S if S > L else L  # get maximum scattering order
        self.datacheck(P1consistent=P1consistent)


class CZMaterialData:
    """
    Assign material data TH to reactor core.

    Attributes
    ----------
    THdata : dict
        Dictionary storing objects with macro-group constants parsed by
        serpentTools.
    THtemp : list
        List with tuples (Tf, Tc).

    Methods
    -------
    ``None``
    """

    def __init__(self, mflow, pressures, temperatures, CZassemblynames):
        """
        Initialise object.

        Parameters
        ----------
        mflow: list
            List with mass flow rates, one for each cooling zone.
        pressures: list
            List with pressures, one for each cooling zone.
        temperatures: list
            List with temperatures, one for each cooling zone.
        CZassemblynames: list
            List with cooling zone names, sorted consistently with the
            physical parameter lists.

        Returns
        -------
        ``None``
        """
        # check length consistency
        if mflow is not None:
            if len(mflow) != len(CZassemblynames):
                raise OSError("The number of mass flow rates must match" +
                              "with the number of the cooling zones!")
            else:
                self.massflowrates = dict(zip(CZassemblynames, mflow))

        if temperatures is not None:
            if len(temperatures) != len(CZassemblynames):
                raise OSError("The number of temperatures must match" +
                              "with the number of the cooling zones!")
            else:
                self.temperatures = dict(zip(CZassemblynames, temperatures))

        if pressures is not None:
            if len(pressures) != len(CZassemblynames):
                raise OSError("The number of pressures must match" +
                              "with the number of the cooling zones!")
            else:
                self.pressures = dict(zip(CZassemblynames, pressures))

class NEMaterialError(Exception):
    pass