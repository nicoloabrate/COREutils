import os
import re
from copy import deepcopy as cp
from warnings import catch_warnings
import h5py as h5
import numpy as np
import itertools
import logging
from pathlib import Path
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
from coreutils.tools.plot import RadialMap
from coreutils.core import Core
from matplotlib import rcParams


class NEoutput:
    """
    Class to read NE profiles computed by FRENETIC.
    """

    # default keys for integral parameters (namelist)
    intout = {'errint': ['NC error', 'LE flux', 'LE shape', 'distortion',
                         'NC iterations', 'DTS iterations', 'DTR steps'],
              'errsol': ['n. outer', 'n. inn./out.', 'error keff',
                         'error flux', 'cpu time', 'comp. type'],
              'geometry': ['x-centre', 'y-centre', 'z-centre', 'volume',
                           'surf-xy', 'surf-z'],
              'intamp': ['amplituden', 'ceff(', '(dampn/dt)/ampn',
                         'amplitudep', '(dampp/dt)/ampp'],
              'inteig': ['eigenvalue dir.', 'eigenvalue adj.',
                         'reactivity'],
              'intpar': ['lifetimen', 'betaeff(', 'reactivityn', 'seffn',
                         'lifetimep', 'reactivityp', 'seffp', ],
              'intpow': ['power tot.', 'power fis.', 'power neu.',
                         'power pho.'],
              'intsrc': ['gro=', 'total', 'grp=', 'totalp']}

    distrout = ['timeDistr', 'fluxadj', 'fluxadjp', 'fluxdir', 'fluxdirp', 'powerfis',
                'powerneu', 'powerpho', 'powertot', 'precurs', 'precursp',
                'rrd_efis', 'rrd_fis', 'rrd_ker', 'rrd_kerp', 'rrd_lkg',
                'rrd_lkgp', 'rrd_nfis', 'rrd_sct', 'rrd_sctp', 'rrd_src',
                'rrd_srcp', 'rrd_tot', 'rrd_totp', 'tempcool', 'tempfuel']

    aliases = {'keff': 'eigenvalue dir.', 'k': 'eigenvalue dir.', 'flux': 'fluxdir',
               'keffa': 'eigenvalue adj.','adjoint': 'fluxadj', 'powerdens': 'powertot', 'rho': 'reactivityn',
               'intpowtot': 'power tot.', 'intpowneu': 'power neu.', 'intpowpho': 'power pho.',
               'intpowfis': 'power fis.'}

    post_process_keys = ['precursTot', 'precurspTot', 'power_radial', 'power_axial']

    distrout_attr = {'fluxadj': 'neutron adjoint flux',
                     'fluxadjp': 'photon adjoint flux',
                     'fluxdir': 'neutron direct flux',
                     'fluxdirp': 'photon direct flux',
                     'powerfis': 'fission power density',
                     'powerneu': 'KERMA power density',
                     'powerpho': 'photon power density',
                     'powertot': 'total power density',
                     'precurs': 'delayed neutron precursor concentrations',
                     'precursp': 'delayed photon precursor concentrations',
                     'rrd_efis': 'neutron fission energy production rate density',
                     'rrd_fis': 'neutron fission reaction rate density',
                     'rrd_ker': 'neutron kerma energy production rate density',
                     'rrd_kerp': 'photon kerma energy production rate density',
                     'rrd_lkg': 'neutron leakage rate density',
                     'rrd_lkgp': 'photon leakage rate density',
                     'rrd_nfis': 'neutron fission neutron production rate density',
                     'rrd_sct': 'neutron scattering reaction rate density',
                     'rrd_sctp': 'photon scattering reaction rate density',
                     'rrd_src': 'neutron source emission density',
                     'rrd_srcp': 'photon source emission density',
                     'rrd_tot': 'neutron total reaction rate density',
                     'rrd_totp': 'photon total reaction rate density',
                     'tempfuel': 'coolant temperature',
                     'tempcool': 'fuel temperature'}

    post_process_attr = {'precursTot': 'Total precursors conc.',
                         'precurspTot': 'Total photon precursors conc.',
                         'power_radial': 'Total power',
                         'power_axial': 'Linear power'}

    distrout_dim = {'fluxadj': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'fluxadjp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'fluxdir': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'fluxdirp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'powerfis': ('ntim', 'nelz', 'nhex'),
                    'powerneu': ('ntim', 'nelz', 'nhex'),
                    'powerpho': ('ntim', 'nelz', 'nhex'),
                    'powertot': ('ntim', 'nelz', 'nhex'),
                    'precurs': ('ntim', 'npre', 'nelz', 'nhex'),
                    'precursp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'rrd_efis': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_fis': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_ker': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_kerp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'rrd_lkg': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_lkgp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'rrd_nfis': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_sct': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_sctp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'rrd_src': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_srcp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'rrd_tot': ('ntim', 'ngro', 'nelz', 'nhex'),
                    'rrd_totp': ('ntim', 'ngrp', 'nelz', 'nhex'),
                    'tempfuel': ('ntim', 'nelz', 'nhex'),
                    'tempcool': ('ntim', 'nelz', 'nhex')}

    # default profiles unit of measures
    intout_uom = {'errint': ['[-]']*len(intout['errint']),
                  'errsol': ['[-]']*4+['[s]', '[-]'],
                  'geometry': ['[cm]']*3+['cm^3']+['[cm^2]']*2,
                  'intamp': ['[-]', '[-]', '[s^{-1}]', '[-]', '[s^{-1}]'],
                  'inteig': ['[-]']*3,
                  'intpar': ['[s]', '[-]', '[-]', '[s^{-1}]', '[s]', '[-]',
                             '[s^{-1}]', ],
                  'intpow': ['[W]']*4,
                  'intsrc': ['[s^{-1}]']*3}

    distrout_uom = ['[-]', '[-]', '[cm^{-2}s^{-1}]', '[cm^{-2} s^{-1}]',
                    '[Wcm^{-3}]', '[Wcm^{-3}]', '[W cm^{-3}]', '[W cm^{-3}]',
                    '[cm^{-3}]', '[cm^{-3}]', '[W cm^{-3}]', '[cm^{-3} s^{-1}]',
                    '[Wcm^{-3}]', '[W cm^{-3}]', '[cm^{-3} s^{-1}]',
                    '[cm^{-3} s^{-1}]', '[cm^{-3} s^{-1}]', '[cm^{-3} s^{-1}]',
                    '[cm^{-3} s^{-1}]', '[cm^{-3} s^{-1}]', '[cm^{-3} s^{-1}]',
                    '[cm^{-3} s^{-1}]', '[cm^{-3} s^{-1}]', '[K]', '[K]']

    post_process_uom = ['[cm^{-3} s^{-1}]', '[cm^{-3} s^{-1}]',
                        '[W]', '[W/m]']

    def __init__(self, path):
        """
        Initialise the class.

        Parameters
        ----------
        None.

        Returns
        -------
        None.
        """
        self.casepath = path
        self.NEpath = os.path.join(path, 'NE')
        # looking for core file
        self.core = Core(os.path.join(path, 'core.h5'))
        self.ngro = self.core.NE.nGro
        self.ngrp = self.core.NE.nGrp
        if "nPrec" in self.core.NE.NEdata.keys():
            self.npre = self.core.NE.NEdata["nPrec"]
            self.nprp = self.core.NE.nPrp
        else:
            self.npre = self.core.NE.nPre
            self.nprp = self.core.NE.nPrp

        self.nhex = self.core.nAss
        if self.core.dim != 2:
            self.nelz = self.core.NE.AxialConfig.splitz.sum()
        else:
            self.nelz = 1
        self.integralParameters = NEoutput.intout
        self.distributions = NEoutput.distrout
        self.integralParameters_measure = NEoutput.intout_uom
        self.distributions_descr = NEoutput.distrout_attr
        self.distributions_measure = NEoutput.distrout_uom
        try:
            lst = self.integralParameters['intpar']
            idy = lst.index('betaeff(')

            for i in range(self.npre):
                self.integralParameters['intpar'].insert(idy, f'betaeff({i+1})')
                uom = self.integralParameters_measure['intpar'][idy]
                self.integralParameters_measure['intpar'].insert(idy, uom)
                idy += 1

            idy = self.integralParameters['intpar'].index('betaeff(')
            self.integralParameters['intpar'].remove('betaeff(')
            del self.integralParameters_measure['intpar'][idy]

            lst = self.integralParameters['intsrc']
            idy = lst.index('gro=')
            for i in range(1,self.ngro+1):
                self.integralParameters['intsrc'].insert(idy, f'gro={i}')
                uom = self.integralParameters_measure['intsrc'][idy]
                self.integralParameters_measure['intsrc'].insert(idy, uom)
                idy += 1

            idy = self.integralParameters['intsrc'].index('gro=')
            self.integralParameters['intsrc'].remove('gro=')
            del self.integralParameters_measure['intsrc'][idy]

            lst = self.integralParameters['intamp']
            idy = lst.index('ceff(')
            for i in range(1, self.npre+1):
                self.integralParameters['intamp'].insert(idy, f'ceff({i})')
                uom = self.integralParameters_measure['intamp'][idy]
                self.integralParameters_measure['intamp'].insert(idy, uom)
                idy += 1

            idy = self.integralParameters['intamp'].index('ceff(')
            self.integralParameters['intamp'].remove('ceff(')
            del self.integralParameters_measure['intamp'][idy]

        except ValueError:
            pass

    def get(self, which, t=None, z=None, hex=None, pre=None,
            gro=None, grp=None, prp=None, oldfmt=False):
        """
        Get profile from output.

        Parameters
        ----------
        which: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default None.
        t: float or iterable, optional
            Time instant(s), by default None.
        z: float or iterable, optional
            Axial coordinate(s), by default None.
        pre: integer or iterable, optional
            Precursor families, by default None.
        gro: integer or iterable, optional
            Neutron energy group(s), by default None.
        grp: integer or iterable, optional
            Photon energy group(s), by default None.
        prp: integer or iterable, optional
            Photon precursor family, by default None.
        oldfmt: bool, optional
            Flag to read output in the old txt format. 
            Default is False.

        Returns
        -------
        profile: array
            Output profile requested.
        """
        # look for aliases, e.g., `keff` instead of `eigenvalue dir.`
        tot = False
        if which in self.aliases.keys():
            which = self.aliases[which]
        elif which in self.post_process_keys:
            if which == "precursTot":
                pre = np.arange(1, self.npre+1)
                which = "precurs"
                sum_dims = ["npre", "nelz", "nhex"]
                tot = True
            elif which == "precurspTot":
                pre = np.arange(1, self.nprp+1)
                which = "precursp"
                sum_dims = ["nprp", "nelz", "nhex"]
                tot = True
            elif which == "power_radial":
                which = "powertot"
                sum_dims = ["nelz"]
                tot = True
                z = None # take all z
            elif which == "power_axial":
                which = "powertot"
                sum_dims = ["nhex"]
                tot = True
                hex = None # take all hex

        if not oldfmt:
            try:
                h5path = os.path.join(self.NEpath, "output_NE.h5")
                # back compatibility with v1 of FRENETIC 
                # (commit n.8aaa49a23fcc8ffc01077c2c58facb66fd9aae0c on FRENETIC development)
                if not os.path.exists(h5path):
                    h5path = os.path.join(self.NEpath, "output.h5")
                fh5 = h5.File(h5path, "r")
            except OSError as err:
                if 'Unable to open file' in str(err):
                    oldfmt = True
                    datapath = os.path.join(self.NEpath, "intpow.out")
                    if not os.path.exists(datapath):
                        if not os.path.exists(h5path):
                            raise NEOutputError(f"No output in directory {self.NEpath}")
                        else:
                            print()
                            raise NEOutputError(f"{str(err)}\n{h5path} is probably corrupted!")
        else:
            # just to parse time, if needed
            datapath = os.path.join(self.NEpath, "intpow.out")
            if not os.path.exists(datapath):
                raise NEOutputError(f"No output in directory {self.NEpath}")

        if which in self.distributions:
            if which == "timeDistr":
                times = cp(np.asarray(fh5["distributions"]["timeDistr"])[()])
                # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                times[0] = 0
                # --- close H5 file
                fh5.close()
                return times
            isintegral = False
            dictkey = "distributions"
            idx = self.distributions.index(which)
            # check core h5 is present
            if self.core is None:
                raise NEOutputError(f'Cannot provide distributions. \
                                    No `core.h5` file in {self.casepath}')

            # --- PHASE-SPACE PARAMETERS
            if hasattr(self.core, "FreneticNamelist"):
                isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
            else:
                isSym = 0
            nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss

            if hex is not None:
                # make FRENETIC numeration consistent with python indexing
                if isinstance(hex, int):
                    hex = [hex-1]
                else:
                    hex = [h-1 for h in hex] if self.core.dim != 1 else [0]
            else:
                if self.core.dim == 1:
                    hex = [0]  # 0 instead of 1 for python indexing
                else:
                    hex = np.arange(0, nhex).tolist()

            # "t" refers to slicing
            if t is None:
                if len(self.core.NE.time) == 1:
                    t = [0]  # time instant, not python index!
            # "times" refers to all time instants
            nTimeConfig = len(self.core.NE.time)
            if nTimeConfig == 1:
                times = None
            else:  # parse time from h5 file
                if oldfmt:
                    times = np.loadtxt(datapath, comments="#", usecols=(0))
                else:
                    times = cp(np.asarray(fh5[dictkey]["timeDistr"])[()])
                    # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                    times[0] = 0
            # --- TIME AND AXIAL COORDINATE PARAMETERS
            gro, grp, pre, prp, idt, idz = self._shift_index(gro, grp, pre, prp, t, z, times=times)
            dimdict = {'ntim': idt, 'nelz': idz, 'nhex': hex, 'ngro': gro,
                       'ngrp': grp, 'npre': pre}

            if t is not None:
                timesSnap = self.core.TimeSnap # TODO distinguish existence of snapshots in simulations

        else:  # integral data
            isintegral = True
            skip = 1  # +1 for time column
            notfound = True
            for k, v in self.integralParameters.items():
                if which in v:
                    dictkey = k
                    if oldfmt:
                        fname = f'{dictkey}.out'
                    idx = v.index(which)+skip
                    notfound = False
                    break
                elif which == 'betaeff':
                    dictkey = k
                    if 'betaeff(1)' in v:
                        if oldfmt:
                            fname = 'intpar.out'
                        idx = []
                        for p in range(self.npre):
                            idx.append(v.index(f'betaeff({p+1})')+skip)
                        notfound = False
                        break
                elif which == 'time':
                    idx = skip-1
                    dictkey = 'intpar'
                    notfound = False

            if notfound:
                raise NEOutputError(f'{which} not found in data!')

        # --- PARSE PROFILE FROM H5 FILE
        if oldfmt:
            datapath = os.path.join(self.NEpath, fname)
            profile = np.loadtxt(datapath, comments="#", usecols=(0, idx))
        else:
            if isintegral:
                if which == 'betaeff':
                    betas = cp(np.array(fh5['integralParameters'][dictkey])[:, [idx]][:, 0, :])
                    profile = betas.sum(axis=1)
                elif which == 'eigenvalue dir.' or which == 'eigenvalue adj.':
                    profile = np.squeeze(fh5['integralParameters'][dictkey][:, [idx]])
                else:
                    profile = fh5['integralParameters'][dictkey][:, [idx]][()]
            else:
                # parse specified time, assembly, axial node, group, prec. fam.
                dims = NEoutput.distrout_dim[which]
                dimlst = []

                for d in dims:
                    x = dimdict[d]
                    if x is None:
                        x = 0 if x == 'ntim' else slice(None)
                    dimlst.append(x)

                if which == "powertot":
                    if which not in fh5[dictkey].keys():
                        ntim = len(np.asarray(fh5[dictkey]["timeDistr"]))
                        profile = np.zeros((ntim, self.nelz, self.nhex))
                        for p in ["powerfis", "powerneu", "powerpho"]:
                            if p in fh5[dictkey].keys():
                                powr = np.asarray(fh5[dictkey][p])
                            else:
                                powr = np.zeros((ntim, self.nelz, self.nhex))
                            profile += powr
                else:
                    profile = np.asarray(fh5[dictkey][which])

                profile = profile[np.ix_(*dimlst)]

                if tot:
                    dims = self.distrout_dim[which]
                    for sum_dim in sum_dims:
                        sum_ax = dims.index(sum_dim)
                        if "power" in which:
                            if sum_dim == "nhex":
                                w = self.core.Geometry.AssemblyGeometry.area
                                profile = w*profile.sum(axis=sum_ax)
                            elif sum_dim == "nelz":
                                w = self.core.NE.AxialConfig.dz
                                profile = np.tensordot(profile, w, axes=([sum_ax], [0]))
                                profile = profile*self.core.Geometry.AssemblyGeometry.area
                            else:
                                raise NEOutputError(f"Cannot get {which} from data!")
                        else:
                            profile = profile.sum(axis=sum_ax)

                        dims = list(dims)
                        dims.remove(sum_dim)
                        dims = tuple(dims)

        # --- close H5 file
        if not oldfmt:
            fh5.close()
        if profile.ndim > 0:
            return profile[:]
        else:
            return profile

    def eplot(self, eflx=None, t=None, z=None, hex=None, ax=None,
              pre=False, title=None, figname=None, egrid=False,
              lethargynorm=True, logx=True, logy=True, **kwargs, ):
        """
        Plot solution along energy for a certain portion of the phase space.

        Parameters
        ----------

        Returns
        -------
        None.

        """
        if logx and logy:
            loglog = True
        else:
            loglog = False

        E = self.core.NE.energygrid
        if eflx is None:
            raise OSError("TODO: implement automatic space integration")

        if lethargynorm:
            u = np.log(E[0]/E)
            eflx = eflx/np.diff(u)
        ax = ax or plt.gca()

        yr = np.zeros((len(eflx)+1,))
        yr[0] = eflx[0]
        yr[1:] = eflx

        plt.step(E, yr, where='pre', **kwargs)

        if loglog or logx:
            ax.set_xscale('log')
        if loglog or logy:
            ax.set_yscale('log')

        if egrid:
            for e in E:
                ax.axvline(e, c='k', lw=0.5, ls=':')

        plt.grid(which='both', alpha=0.2)
        ax.set_xlabel('E [MeV]')
        if title is not None:
            plt.title(title)
        if figname:
            plt.tight_layout()
            plt.savefig(f"{figname}.pdf")


    def plot1D(self, which, gro=None, t=None, grp=None, pre=None, prp=None, ax=None,
               abscissas=None, z=None, hex=None, leglabels=None, figname=None, xlabel=None,
               xlims=None, ylims=None, ylabel=None, geometry=None, oldfmt=False,
               style='sty1D.mplstyle', legend=True, **kwargs):
        """
        Plot time/axial profile of integral param. or distribution in hex.

        Parameters
        ----------
        which : string
            Profile name according to FRENETIC namelist.
        zt : ndarray, optional
            Axial or time grid, by default None.
        figname : TYPE, optional
            Name assigned to the figure for saving, by default None.

        Returns
        -------
        None.
        """
        if style == 'sty1D.mplstyle':
            pwd = Path(__file__).parent.parent
            toolspath = Path.joinpath(pwd, "tools")
            if toolspath.exists():
                sty1D = str(Path.joinpath(pwd, "tools", style))
            else:
                raise NEOutputError(f"{toolspath} not found!")
        else:
            if not Path(style).exists():
                logging.info(f'{style} style sheet not found! \
                                Switching to default...')
            else:
                sty1D = style

        if which == "precursTot":
            pre = np.arange(1, self.npre+1)
            which = "precurs"
            sum_dims = ["npre", "nelz", "nhex"]
            tot = True
        elif which == "precurspTot":
            pre = np.arange(1, self.nprp+1)
            which = "precursp"
            sum_dims = ["nprp", "nelz", "nhex"]
            tot = True
        else:
            tot = False

        label = which
        if which in self.aliases.keys():
            which = self.aliases[which]

        # select unit of measure corresponding to profile
        plotvstime = True if t else False
        if t:
            t = None
        if which in self.distributions:
            isintegral = False
            idx = self.distributions.index(which)
            uom = self.distributions_measure[idx]
            dims = NEoutput.distrout_dim[which]
        else:  # integral data
            isintegral = True
            for k, v in self.integralParameters.items():
                if which in v:
                    idx = v.index(which)
                    uom = self.integralParameters_measure[k][idx]
        # --- parse profile
        prof = self.get(which, gro=gro, hex=hex, t=t, z=z, grp=grp, pre=pre, prp=prp)
        # sum along axes, if total distribution is requested
        if tot:
            dims = self.distrout_dim[which]
            for sum_dim in sum_dims:
                sum_ax = dims.index(sum_dim)
                prof = prof.sum(axis=sum_ax)
                dims = list(dims)
                dims.remove(sum_dim)
                dims = tuple(dims)
            pre = None
            plotvstime = True
        # --- select independent variable
        # it can be time or axial coordinate
        nTimeConfig = len(self.core.NE.time)
        if nTimeConfig == 1:
            times = None # np.array([0])
        else:  # parse time from h5 file
            if not oldfmt:
                datapath = os.path.join(self.NEpath, "output.h5")
            if isintegral:
                if which != "precursTot":
                    times = self.get('time')
                else:
                    times = self.get('timeDistr')
                y = prof
            else:
                if oldfmt:
                    times = np.loadtxt(datapath, comments="#", usecols=(0))
                else:
                    times = cp(self.get('timeDistr')[()])
                    # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                    times[0] = 0
                if plotvstime:
                    t = times

        if t is None:
            t = [0]  # initial condition
        if isintegral and nTimeConfig == 1:
            raise NEOutputError("Cannot plot integral parameter in steady state!")

        ax = plt.gca() if ax is None else ax
        if isintegral:  # plot integral parameter
            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                handles = []
                handlesapp = handles.append
                if which in ['rho', 'reactivityn', 'betaeff']:
                    y *= 1E5
                if abscissas is not None:
                    x = abscissas
                else:
                    x = times
                lin1, = ax.plot(x, y, **kwargs)
                ax.set_xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    for k, v in self.integralParameters.items():
                        if which in v:
                            idx = v.index(which)
                            uom = self.integralParameters_measure[k][idx]
                    ax.set_ylabel(fr"{which} {uom}")
                else:
                    ax.set_ylabel(ylabel)
        else:   # plot distribution
            if hex is None:
                hex = [0] # 1st hexagon (this is python index, not hex. number)

            # get python-wise index for slicing
            igro, igrp, ipre, iprp, idt, idz = self._shift_index(gro, grp, pre,
                                                               prp, t, z, times=times)
            # map indexes from full- to sliced-array
            igro, igrp, ipre, iprp, idt, idz = self._to_index(igro, igrp, ipre, iprp,
                                                              idt, idz)

            if nTimeConfig > 1 and plotvstime:  # plot against time
                x = times
                dim2plot = 'ntim'
                idx = dims.index('ntim')
                if xlabel is None:
                    xlabel = 'time [s]'
            else:  # plot time snapshots, if any, against axial coordinate
                x = self.core.NE.AxialConfig.AxNodes
                dim2plot = 'nelz'
                idx = dims.index('nelz')
                if xlabel is None:
                    xlabel = 'z-coordinate [cm]'

            # --- DEFINE SLICES
            dimdict = {'ntim': idt, 'nelz': idz, 'ngro': igro,
                        'ngrp': igrp, 'npre': ipre, 'nhex': hex}
            usrdict = {'ntim': t, 'nelz': z, 'ngro': gro,
                       'ngrp': grp, 'npre': pre, 'nhex': hex}
            dimlst = [None]*len(dims)
            for k in dims:
                i = dims.index(k)
                dimlst[i] = dimdict[k]
            # define multi-index
            tmp = dimlst.pop(idx)
            indexes = list(itertools.product(*dimlst))
            indexes = [list(tup) for tup in indexes]
            for i in range(len(indexes)):
                indexes[i].insert(idx, tmp)

            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                ax = plt.gca() if ax is None else ax
                handles = []
                handlesapp = handles.append
                ymin, ymax = np.inf, -np.inf
                # loop over dimensions to slice
                for i, s in enumerate(indexes):
                    y = prof[s[i]]  # .take(indices=d, axis=i)
                    label = self._build_label(s, dims, dim2plot, usrdict)
                    if abscissas is not None:
                        x = abscissas
                    lin1, = ax.plot(x, y, label=label, **kwargs)
                    handlesapp(lin1)
                    # track minimum and maximum
                    if ylims is None:
                        ymin = y.min() if y.min() < ymin else ymin
                        ymax = y.max() if y.max() > ymax else ymax

                if ylims is not None:
                    ymin = min(ylims)
                    ymax = max(ylims)

                plt.xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    if which in self.distributions:
                        isintegral = False
                        idx = self.distributions.index(which)
                        uom = self.distributions_measure[idx]
                    else:  # integral data
                        isintegral = True
                        for k, v in self.integralParameters.items():
                            if which in v:
                                idx = v.index(which)
                                uom = self.integralParameters_measure[k][idx]

                    if rcParams['text.usetex']:
                        plt.ylabel(rf"{which} ${uom}$")
                    else:
                        plt.ylabel(f"{which} {uom}")
                else:
                    plt.ylabel(ylabel)

                # ax.set_ylim(ymin, ymax)
                ax.set_xlim(x.min(), x.max())

                legend_x = 0.50
                legend_y = 1.01
                ncol = 2 if len(indexes) < 4 else 4
                if leglabels is not None:
                    plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)
                else:
                    if legend:
                        plt.legend(bbox_to_anchor=(legend_x, legend_y),
                                loc='lower center', ncol=ncol)

                plt.tight_layout()
                # plt.show()
                if figname is not None:
                    ax.savefig(figname)

    def RadialMap(self, what, z=0, t=0, pre=0, gro=1, grp=0,
                  label=False, figname=None, hex=None,
                  usetex=False, fill=True, axes=None, cmap=None,
                  thresh=None, cbarLabel=True, xlabel=None, ylabel=None,
                  log=None, title=True, scale=1, fmt="%.2f", **kwargs):
        """
        Plot FRENETIC output on the x-y plane.

        Parameters
        ----------
        label : TYPE, optional
            DESCRIPTION, by default False.
        figname : TYPE, optional
            DESCRIPTION, by default None.
        fren : TYPE, optional
            DESCRIPTION, by default False.
        which : TYPE, optional
            DESCRIPTION, by default None.
        what : TYPE, optional
            DESCRIPTION, by default None.
        usetex : TYPE, optional
            DESCRIPTION, by default False.
        fill : TYPE, optional
            DESCRIPTION, by default True.
        axes : TYPE, optional
            DESCRIPTION, by default None.
        cmap : TYPE, optional
            DESCRIPTION, by default 'Spectral_r'.
        thresh : TYPE, optional
            DESCRIPTION, by default None.
        cbarLabel : TYPE, optional
            DESCRIPTION, by default None.
        xlabel : TYPE, optional
            DESCRIPTION, by default None.
        ylabel : TYPE, optional
            DESCRIPTION, by default None.
        loglog : TYPE, optional
            DESCRIPTION, by default None.
        logx : TYPE, optional
            DESCRIPTION, by default None.
        logy : TYPE, optional
            DESCRIPTION, by default None.
        title : TYPE, optional
            DESCRIPTION, by default None.
        scale : TYPE, optional
            DESCRIPTION, by default 1.
        fmt : TYPE, optional
            DESCRIPTION, by default "%.2f".
        **kwargs : TYPE
            DESCRIPTION.

        Raises
        ------
        IndexError
            DESCRIPTION.
        TypeError
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if hasattr(self.core, "FreneticNamelist"):
            isSym = self.core.FreneticNamelist["PRELIMINARY"]["isSym"]
        else:
            isSym = 0
        nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss
        # check data type
        if isinstance(what, dict):  # comparison with FRENETIC and other vals.
            tallies = np.zeros((nhex, len(what.keys())))
            for i, k in enumerate(what.keys()):
                v2 = what[k]
                v1 = self.get(k, hex=which, t=t, z=z, pre=pre, gro=gro, grp=grp)
                v1 = np.squeeze(v1)
                tmp = np.true_divide(norm(v1-v2), norm(v1))
                tmp[tmp == np.inf] = 0
                tmp = np.nan_to_num(tmp)
                tallies[:, i] = tmp*100

        elif isinstance(what, list):  # list of output # TODO TO BE TESTED
            tallies = np.zeros((nhex, len(what)))
            for i, w in enumerate(what):
                _tmp = self.get(w, hex=which, t=t, z=z, 
                                pre=pre, gro=gro, grp=grp)
                tallies[:, i] = np.squeeze(_tmp)

        elif isinstance(what, str):  # single output
            tallies = self.get(what, t=t, z=z, pre=pre, gro=gro, grp=grp)
            tallies = np.squeeze(tallies)
        elif isinstance(what, (np.ndarray)):
            tallies = what+0
            what = None
        else:
            raise TypeError('Input must be str, dict or list!')

        if title is True:
            timeSnap = self.core.TimeSnap
            idt = np.argmin(abs(t-timeSnap))

            if self.core.dim != 2:
                nodes = self.core.NE.AxialConfig.AxNodes
                idz = np.argmin(abs(z-nodes))
                title = 'z=%.2f [cm], t=%.2f [s]' % (nodes[idz], timeSnap[idt])
            else:
                nodes = np.array([0])
                idz = 0
                title = 't=%.2f [s]' % (timeSnap[idt])


        if cbarLabel is True:
            if what in self.distributions:
                idx = self.distributions.index(what)
                dist = self.distributions_descr[what]
                uom = self.distributions_measure[idx]
            elif what in self.post_process_keys:
                idx = self.post_process_keys.index(what)
                dist = self.post_process_attr[what]
                uom = self.post_process_uom[idx]
            else:
                if what is None:
                    idx = ""
                    dist = ""
                    uom = ""
                else:
                    raise NEOutputError(f"Cannot plot {what}!")

            uom = uom.replace('**', '^')
            changes = ['-1', '-2', '-3']
            for c in changes:
                uom = uom.replace(c, '{%s}' % c)
            uom = uom.replace('*', '~')
            # uom = '$%s$' % uom if usetex is True else uom
            cbarLabel = r'%s $%s$' % (dist, uom)

        # autoselect colormap
        if cmap is None:
            auto_cmap = {
                          'fluxadj': 'Spectral_r',
                          'fluxadjp': 'Spectral_r',
                          'fluxdir': 'Spectral_r',
                          'fluxdirp': 'Spectral_r',
                          'powerfis': 'inferno',
                          'powerneu': 'inferno',
                          'powerpho': 'inferno',
                          'powertot': 'inferno',
                          'power_radial': 'inferno',
                          'precurs': 'cividis',
                          'precursp': 'cividis',
                          'rrd_efis': 'plasma',
                          'rrd_fis': 'plasma',
                          'rrd_ker': 'plasma',
                          'rrd_kerp': 'plasma',
                          'rrd_lkg': 'plasma',
                          'rrd_lkgp': 'plasma',
                          'rrd_nfis': 'plasma',
                          'rrd_sct': 'plasma',
                          'rrd_sctp': 'plasma',
                          'rrd_src': 'plasma',
                          'rrd_srcp': 'plasma',
                          'rrd_tot': 'plasma',
                          'rrd_totp': 'plasma',
                          'tempfuel': 'coolwarm',
                          'tempcool': 'coolwarm'
                        }
            if what in auto_cmap.keys():
                cmap = auto_cmap[what]

        RadialMap(self.core, tallies=tallies, z=z, time=t, pre=pre, gro=gro, grp=grp, 
                  label=label,
                  figname=figname,
                  which=hex,
                  fren=True,
                  whichconf='NE',
                  asstype=False,
                  dictname=None,
                  legend=False,
                  txtcol='k',
                  fill=False,
                  axes=axes,
                  cmap=cmap,
                  thresh=thresh,
                  cbarLabel=cbarLabel,
                  xlabel=xlabel,
                  ylabel=ylabel,
                  loglog=log,
                  logx=False, 
                  logy=False,
                  title=title,
                  scale=scale, 
                  fmt=fmt,
                #   numbers=False, 
                  **kwargs)

    def whereMaxSpectralRad(self, path, core, plot=True):

        with open(os.path.join(path, 'outputNE.log'), 'r') as f:
            for l in f:
                if '@ D3DMATI: MAXVAL(SPECTRAL NORM)' in l:
                    # parse IK, IG
                    num = l.split('(IK,IG)= ')[1]
                    IK, IG = num.split()
                    IK, IG = int(IK), int(IG)
                else:
                    IK, IG = None, None
        nElz = len(self.core.NE.AxialConfig.AxNodes) if self.core.dim != 2 else 1
        myIK = 0
        nhex = int((self.core.nAss-1)/6*isSym)+1 if isSym else self.core.nAss
        for iz in range(0, nElz):
            for ih in range(1, nhex+1):
                if myIK == IK:
                    # TODO parse each time config.
                    hexty = self.core.getassemblytype(ih, config=core.NE.config[0], isfren=True)
                    hexty = self.core.NE.assemblytypes[hexty]
                    z = self.core.NE.AxialConfig.AxNodes[iz]
                    print(f'Max spectral norm in {hexty} SAs at z={z} cm')
                myIK = myIK+1

    def _shift_index(self, gro, grp, pre, prp, t, z,
                     times=None):
        """Convert input parameters to lists of indexes for slicing.

        Parameters
        ----------
        gro : int or list
            Number of energy groups for neutrons.
        grp : int or list
            Number of energy groups for photons.
        pre : int or list
            Number of precursors for neutrons.
        prp : int or list
            Number of precursors for photons.
        Returns
        -------
        list
            gro, grp, pre, prp converted in listed indexes
        """
        if gro is not None:
            # make input iterables
            if isinstance(gro, int):
                gro = [gro]
            gro = [g-1 for g in gro]
        else:
            gro = np.arange(0, self.core.NE.nGro).tolist()

        if grp is not None:
            if isinstance(grp, int):
                grp = [grp]
            grp = [g-1 for g in grp]
        else:
            grp = np.arange(0, self.core.NE.nGrp).tolist()

        if pre is not None:
            if isinstance(pre, int):
                pre = [pre]
            pre = [p-1 for p in pre]
        else:
            pre = np.arange(0, self.npre).tolist()

        if prp is not None:
            if isinstance(prp, int):
                prp = [prp]
            prp = [p-1 for p in prp]
        else:
            prp = np.arange(0, self.nprp).tolist()

        nodes = self.core.NE.AxialConfig.AxNodes if self.core.dim != 2 else np.array([0])
        if z is not None:
            if isinstance(z, (list, np.ndarray)):
                idz = [np.argmin(abs(zi-nodes)) for zi in z]
            else:
                idz = [np.argmin(abs(z-nodes))]
        else:
            idz = np.arange(0, len(nodes)).tolist()

        if times is not None:
            if t is not None:
                if isinstance(t, (list, np.ndarray)):
                    idt = [np.argmin(abs(ti-times)) for ti in t]
                else:
                    idt = [np.argmin(abs(t-times))]
            else:
                idt = np.arange(0, len(times)).tolist()
        else:
            idt = [0]

        return gro, grp, pre, prp, idt, idz

    def _to_index(self, gro, grp, pre, prp, t, z):
        """Map full-array indexes to sliced array indexes.

        Parameters
        ----------
        gro : list
            Indeces of energy groups for neutrons.
        grp : list
            Indeces of energy groups for photons.
        pre : list
            Indeces of precursors for neutrons.
        prp : list
            Indeces of precursors for photons.
        Returns
        -------
        list
            igro, igrp, ipre, iprp, idt, iz converted in listed indexes
        """
        if t is not None:
            idt = np.arange(0, len(t))
        else:
            idt = None

        if z is not None:
            idz = np.arange(0, len(z))
        else:
            idz = None

        if gro is not None:
            igro = np.arange(0, len(gro))
        else:
            igro = None

        if grp is not None:
            igrp = np.arange(0, len(grp))
        else:
            igrp = None

        if pre is not None:
            ipre = np.arange(0, len(pre))
        else:
            ipre = None

        if prp is not None:
            iprp = np.arange(0, len(prp))
        else:
            iprp = None

        return igro, igrp, ipre, iprp, idt, idz

    def _build_label(self, s, dims, dim2plot, usrdict):
        """Build legend label.

        Parameters
        ----------
        s : list
            Slice for the np.array.
        dims : list
            List of dimensions.
        dim2plot : string
            Dimension to be plotted.
        usrdict : dict
            Dict mapping dimension name and lists.

        Returns
        -------
        str
            Label for the plot.
        """
        label_dict = {'ngro': 'g', 'ngrp': 'g',
                      'pre': 'p', 'prp': 'p', 'nhex': 'n'}
        dim2plot_dict = {'ntim': 't', 'nelz': 'z'}
        uom = {'ntim': 's', 'nelz': 'cm'}

        if plt.rcParams['text.usetex']:
            equal = "$=$"
        else:
            equal = "="

        label = []
        for i, k in enumerate(dims):
            if self.core.dim == 1 and k == 'nhex':
                continue
            if k not in ['ntim', 'nelz']:
                txt = usrdict[k][s[i]]
                txt = rf"{label_dict[k]}{equal}{txt}"
                label.append(txt)
            else:
                if k != dim2plot:
                    txt = usrdict[k][s[i]]
                    txt = rf"{dim2plot_dict[k]}{equal}{txt} {uom[k]}"
                    label.append(txt)

        return str(", ".join(label))

    @staticmethod
    def __loadtxt(fname):
        """
        Load the parameters and their names as dict.

        Parameters
        ----------
        fname : string
            Parameters file name

        Returns
        -------
        pdict: dict
            Dict whose keys are the parameters and whose values are the
            parameter values
        """
        lines = open(fname).read().split('\n')  # read all lines (they are always two)
        # discard comment, discard first empty key, split parameters names
        keys = (re.split("% |, ", lines[0]))[1:]
        vals = lines[1].split(" ")  # split values with " " delimiter
        pdict = dict(zip(keys, vals))  # create output dict
        return pdict

    @staticmethod
    def __wopen(h5name, ans=None):
        """
        Open the hdf5 file "h5name.hdf5" in "append" mode.

        Parameters
        ----------
        h5name : string
            File name

        Returns
        -------
        fh5 : object
            h5py object

        """
        if os.path.isfile(h5name):
            print("File exists. Overwriting?")

            if ans is None:
                ans = input()

            elif isinstance(ans, str) is False:
                raise TypeError('ans argument type must be string!')

        else:  # if file do not exist, it creates it
            ans = "create"

        if ans == "yes" or ans == "y":
            os.remove(h5name)
            # open file in append mode
            fh5 = h5.File(h5name, "a")
            return fh5
        elif ans == "create":
            # create file in append mode
            fh5 = h5.File(h5name, "a")
            return fh5
        else:  # if answer is not positive, nothing is done
            return -1

    @staticmethod
    def __checkname(fname):
        """
        Check extension of filename and add if it is missed.

        Parameters
        ----------
        fname : string
            Input filename (optional extension).

        Raises
        ------
        OSError
            -File extension is wrong. Only HDF5 can be parsed

        Returns
        -------
        fname : string
            Filename and proper extension.

        """
        lst = fname.split(".")

        if len(lst) == 1:
            # add extension
            fname = "%s.hdf5" % fname
        else:
            if lst[-1] != "hdf5":
                lst[-1] = "hdf5"
                fname = ".".join(lst)
                raise FileNotFoundError("File extension is wrong. Only HDF5 can be parsed")

        return fname

class NEOutputError(Exception):
    pass