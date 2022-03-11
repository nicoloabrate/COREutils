"""
Author: N. Abrate.

File: output.py

Description: Class to read data from FRENETIC output files.
"""

from ast import alias
import os
import re
from warnings import catch_warnings
import h5py as h5
import numpy as np
import itertools
from pathlib import Path
from numbers import Real
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
    Class to read profiles computed by FRENETIC.
    """

    # default keys for integral parameters (namelist)
    intout = {'errint': ['NC error', 'LE flux', 'LE shape', 'distortion',
                         'NC iterations', 'DTF iterations', 'DTR steps'],
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
              'intsrc': ['gro=', 'total', 'totalp']}

    distrout = ['timeDistr', 'fluxadj', 'fluxadjp', 'fluxdir', 'fluxdirp', 'powerfis',
                'powerneu', 'powerpho', 'powertot', 'precurs', 'precursp',
                'rrd_efis', 'rrd_fis', 'rrd_ker', 'rrd_kerp', 'rrd_lkg',
                'rrd_lkgp', 'rrd_nfis', 'rrd_sct', 'rrd_sctp', 'rrd_src',
                'rrd_srcp', 'rrd_tot', 'rrd_totp', 'tempcool', 'tempfuel']

    aliases = {'keff': 'eigenvalue dir.', 'k': 'eigenvalue dir.', 'flux': 'fluxdir',
               'adjoint': 'fluxadj', 'powerdens': 'powertot', 'rho': 'reactivityn',
               'intpowtot': 'power tot.', 'intpowneu': 'power neu.', 'intpowpho': 'power pho.',
               'intpowfis': 'power fis.'}

    distrout_attr = ['neutron adjoint flux', 'photon adjoint flux',
                     'neutron direct flux', 'photon direct flux',
                     'total fission power density',
                     'total neutron power density',
                     'total photon power density',
                     'total thermal power density',
                     'delayed neutron precursor concentrations',
                     'delayed photon precursor concentrations',
                     'neutron fission energy production rate density',
                     'neutron fission reaction rate density',
                     'neutron kerma energy production rate density',
                     'photon kerma energy production rate density',
                     'neutron leakage rate density',
                     'photon leakage rate density',
                     'neutron fission neutron production rate density',
                     'neutron scattering reaction rate density',
                     'photon scattering reaction rate density',
                     'neutron source emission density',
                     'photon source emission density',
                     'neutron total reaction rate density',
                     'photon total reaction rate density',
                     'coolant temperature', 'fuel temperature']

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
        self.THpath = os.path.join(path, 'TH')
        # look for core file
        self.core = Core(os.path.join(path, 'core.h5'))

        self.integralParameters = NEoutput.intout
        self.distributions = NEoutput.distrout
        self.integralParameters_measure = NEoutput.intout_uom
        self.distributions_descr = NEoutput.distrout_attr
        self.distributions_measure = NEoutput.distrout_uom
        try:
            lst = self.integralParameters['intpar']
            idy = lst.index('betaeff(')
            for i in range(self.core.NE.nPre):
                self.integralParameters['intpar'].insert(idy, f'betaeff({i+1})')
                uom = self.integralParameters_measure['intpar'][idy]
                self.integralParameters_measure['intpar'].insert(idy, uom)
                idy += 1

            idy = self.integralParameters['intpar'].index('betaeff(')
            self.integralParameters['intpar'].remove('betaeff(')
            del self.integralParameters_measure['intpar'][idy]

            lst = self.integralParameters['intsrc']
            idy = lst.index('gro=')
            for i in range(self.core.NE.nGro):
                self.integralParameters['intsrc'].insert(idy, f'gro={i}')
                uom = self.integralParameters_measure['intsrc'][idy]
                self.integralParameters_measure['intsrc'].insert(idy, uom)
                idy += 1

            idy = self.integralParameters['intsrc'].index('gro=')
            self.integralParameters['intsrc'].remove('gro=')
            del self.integralParameters_measure['intsrc'][idy]

            lst = self.integralParameters['intamp']
            idy = lst.index('ceff(')
            for i in range(self.core.NE.nPre):
                self.integralParameters['intamp'].insert(idy, f'ceff({i})')
                uom = self.integralParameters_measure['intamp'][idy]
                self.integralParameters_measure['intamp'].insert(idy, uom)
                idy += 1

            idy = self.integralParameters['intamp'].index('ceff(')
            self.integralParameters['intamp'].remove('ceff(')
            del self.integralParameters_measure['intamp'][idy]

        except ValueError:
            pass

    def get(self, which, hex=None, t=None, z=None, pre=None,
            gro=None, grp=None, prp=None, oldfmt=False):
        """
        Get profile from output.

        Parameters
        ----------
        path : TYPE
            DESCRIPTION.
        which : TYPE
            DESCRIPTION.

        Returns
        -------
        None
        """
        # look for aliases, e.g., `keff` instead of `eigenvalue dir.`
        if which in self.aliases.keys():
            which = self.aliases[which]

        if not oldfmt:
            datapath = os.path.join(self.NEpath, "output.h5")
            fh5 = h5.File(datapath, "r")
        else:
            # just to parse time, if needed
            datapath = os.path.join(self.NEpath, "intpow")

        if which in self.distributions:
            if which == 'timeDistr':
                return np.asarray(fh5["distributions"]["timeDistr"])
            isintegral = False
            dictkey = "distributions"
            fname = 'output.h5'
            idx = self.distributions.index(which)
            # check core h5 is present
            if self.core is None:
                raise OSError(f'Cannot provide distributions. \
                               No `core.h5` file in {self.casepath}')    
            else:
                core = self.core
            # identify if NE or TH
            NE = True if hasattr(self.core, "name") else False

            # --- PHASE-SPACE PARAMETERS
            if hex is not None:
                # make FRENETIC numeration consistent with python indexing
                hex = [h-1 for h in hex] if self.core.dim != 1 else [0]
            else:
                if self.core.dim == 1:
                    hex = [0]  # 0 instead of 1 for python indexing
            # "t" refers to slicing
            if t is None:
                if len(self.core.NE.time) == 1:
                    t = [0]
            # "times" refers to all time instants
            nTime = len(self.core.NE.time)
            if nTime == 1:
                times = None
                istrans = False
            else:  # parse time from h5 file
                istrans = True                
                if oldfmt:
                    times = np.loadtxt(datapath, comments="#", usecols=(0))
                else:
                    times = np.asarray(fh5[dictkey]["timeDistr"])
            # --- TIME AND AXIAL COORDINATE PARAMETERS
            gro, grp, pre, prp, idt, idz = self._shift_index(gro, grp, pre, prp, t, z, times=times)
            dimdict = {'ntim': idt, 'nelz': idz, 'nhex': hex, 'ngro': gro,
                       'ngrp': grp, 'nprec': pre}
            nodes = self.core.NE.AxialConfig.AxNodes
            if t is not None:
                times = self.core.TimeSnap

        else:  # integral data
            isintegral = True
            skip = 1  # +1 for time column
            notfound = True
            for k, v in self.integralParameters.items():
                if which in v:
                    dictkey = k
                    if oldfmt:
                        fname = f'{dictkey}.out'
                    else:
                        fname = 'output.h5'
                    idx = v.index(which)+skip
                    notfound = False

            if notfound:
                raise OSError(f'{which} not found in data!')

        # --- PARSE PROFILE FROM H5 FILE
        if oldfmt:
            profile = np.loadtxt(datapath, comments="#", usecols=(0, idx))
        else:
            fh5 = h5.File(datapath, "r")
            if isintegral:
                profile = fh5['integralParameters'][dictkey][:, [0, idx]]
            else:
                # parse specified time, assembly, axial node, group, prec. fam.
                dims = NEoutput.distrout_dim[which]
                dimlst = []

                for d in dims:
                    x = dimdict[d]
                    if x is None:
                        x = 0 if x == 'ntim' else slice(None)

                    dimlst.append(x)

                profile = np.asarray(fh5[dictkey][which])
                profile = profile[np.ix_(*dimlst)]

        return profile

    def plot1D(self, which, gro=None, t=None, grp=None, pre=None, prp=None,
               z=None, hex=None, leglabels=None, figname=None, xlabel=None, 
               ylabel=None, geometry=None, oldfmt=False, style='sty1D.mplstyle',
               **kwargs):
        """
        Plot time/axial profile of integral parame. or distribution in hex.

        Parameters
        ----------
        which : string
            Profile name according to FRENETIC namelist.
        zt : ndarray, optional
            Axial or time grid. The default is None.
        figname : TYPE, optional
            Name assigned to the figure for saving. The default is None.

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
                raise OSError(f"{toolspath} not found!")
        else:
            if not Path(style).exists():
                print(f'Warning: {style} style sheet not found! \
                    Switching to default...')
            else:
                sty1D = style

        label = which
        if which in self.aliases.keys():
            which = self.aliases[which]

        # select unit of measure corresponding to profile
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
        prof = self.get(which, gro=gro, t=t, z=z, grp=grp, pre=pre, prp=prp)
        # --- select independent variable
        # it can be time or axial coordinate
        nTime = len(self.core.NE.time)
        if nTime == 1:
            times = None # np.array([0])
            istrans = False
        else:  # parse time from h5 file
            istrans = True
            if not oldfmt:
                datapath = os.path.join(self.NEpath, "output.h5")
                fh5 = h5.File(datapath, "r")
            if isintegral:
                x = prof[:, 0]
                y = prof[:, 1]
            else:
                if oldfmt:
                    times = np.loadtxt(datapath, comments="#", usecols=(0))
                else:
                    times = np.asarray(fh5["distributions"]["timeDistr"])
            # time = [None]
        if t is None:
            t = [0]
        if isintegral and nTime == 1:
            raise OSError("Cannot plot integral parameter in steady state!")

        if isintegral:  # plot integral parameter
            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                fig = plt.figure()
                handles = []
                handlesapp = handles.append
                if which in ['rho', 'reactivityn']:
                    y *= 1E5
                lin1, = plt.plot(x, y, **kwargs)
                plt.xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    for k, v in self.integralParameters.items():
                        if which in v:
                            idx = v.index(which)
                            uom = self.integralParameters_measure[k][idx]
                    plt.ylabel(fr"{which} {uom}")
                else:
                    plt.ylabel(ylabel)
        else:   # plot distribution         
            if hex is None:
                hex = [0]
            # get python-wise index for slicing
            igro, igrp, ipre, iprp, idt, idz = self._shift_index(gro, grp, pre, 
                                                               prp, t, z, times=times)
            # map indexes from full- to sliced-array
            igro, igrp, ipre, iprp, idt, idz = self._to_index(igro, igrp, ipre, iprp, 
                                                              idt, idz)

            if nTime > 1 and len(t) == nTime:  # plot against time
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
                        'ngrp': igrp, 'nprec': ipre, 'nhex': hex}
            usrdict = {'ntim': t, 'nelz': z, 'ngro': gro,
                       'ngrp': grp, 'nprec': pre, 'nhex': hex}
            dimlst = [None]*len(dims)
            ndim = 1
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
                fig = plt.figure()
                axes = plt.gca()
                handles = []
                handlesapp = handles.append
                ymin, ymax = np.inf, -np.inf
                # loop over dimensions to slice
                for i, s in enumerate(indexes):
                    y = prof[s]  # .take(indices=d, axis=i)
                    label = self._build_label(s, dims, dim2plot, usrdict)
                    lin1, = plt.plot(x, y, label=label, **kwargs)
                    handlesapp(lin1)
                    # track minimum and maximum
                    ymin = y.min() if y.min() < ymin else ymin
                    ymax = y.max() if y.max() > ymax else ymax

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

                axes.set_ylim(ymin, ymax)
                axes.set_xlim(x.min(), x.max())

                legend_x = 0.50
                legend_y = 1.01
                ncol = 2 if len(indexes) < 4 else 4
                if leglabels is not None:
                    plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)
                else:
                    plt.legend(bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)
                    
                plt.tight_layout()
                # plt.show()
                if figname is not None:
                    fig.savefig(figname)

    def RadialMap(self, core, what, z=0, t=0, pre=0, gro=0, grp=0,
                  label=False, figname=None, which=None,
                  usetex=False, fill=True, axes=None, cmap='Spectral_r',
                  thresh=None, cbarLabel=True, xlabel=None, ylabel=None,
                  loglog=None, logx=None, logy=None, title=True,
                  scale=1, fmt="%.2f", numbers=False, **kwargs):
        """
        Plot FRENETIC output on the x-y plane.

        Parameters
        ----------
        label : TYPE, optional
            DESCRIPTION. The default is False.
        figname : TYPE, optional
            DESCRIPTION. The default is None.
        fren : TYPE, optional
            DESCRIPTION. The default is False.
        which : TYPE, optional
            DESCRIPTION. The default is None.
        what : TYPE, optional
            DESCRIPTION. The default is None.
        usetex : TYPE, optional
            DESCRIPTION. The default is False.
        fill : TYPE, optional
            DESCRIPTION. The default is True.
        axes : TYPE, optional
            DESCRIPTION. The default is None.
        cmap : TYPE, optional
            DESCRIPTION. The default is 'Spectral_r'.
        thresh : TYPE, optional
            DESCRIPTION. The default is None.
        cbarLabel : TYPE, optional
            DESCRIPTION. The default is None.
        xlabel : TYPE, optional
            DESCRIPTION. The default is None.
        ylabel : TYPE, optional
            DESCRIPTION. The default is None.
        loglog : TYPE, optional
            DESCRIPTION. The default is None.
        logx : TYPE, optional
            DESCRIPTION. The default is None.
        logy : TYPE, optional
            DESCRIPTION. The default is None.
        title : TYPE, optional
            DESCRIPTION. The default is None.
        scale : TYPE, optional
            DESCRIPTION. The default is 1.
        fmt : TYPE, optional
            DESCRIPTION. The default is "%.2f".
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
        # check data type
        if isinstance(what, dict):  # comparison with FRENETIC and other vals.
            tallies = np.zeros((self.core.NAss, len(what.keys())))
            for i, k in enumerate(what.keys()):
                v2 = what[k]
                v1 = self.get(k, hex=which, t=t,
                              z=z, pre=pre, gro=gro, grp=grp,
                              core=core)
                tmp = np.true_divide(norm(v1-v2), norm(v1))
                tmp[tmp == np.inf] = 0
                tmp = np.nan_to_num(tmp)
                tallies[:, i] = tmp*100

        elif isinstance(what, list):  # list of output
            tallies = np.zeros((self.core.NAss, len(what)))
            for i, w in enumerate(what):
                tallies[:, i] = self.get(w, hex=which, t=t,
                                         z=z, pre=pre, gro=gro, grp=grp,
                                         core=core)

        elif isinstance(what, str):  # single output
            tallies = self.get(what, hex=which, t=t, z=z,
                               pre=pre, gro=gro, grp=grp, core=core)
        else:
            raise TypeError('Input must be str, dict or list!')

        if title:
            nodes = self.core.NE.AxialConfig.AxNodes
            idz = np.argmin(abs(z-nodes))

            times = self.core.TimeSnap
            idt = np.argmin(abs(t-times))

            title = 'z=%.2f [cm], t=%.2f [s]' % (nodes[idz], times[idt])

        if cbarLabel:
            idx = self.distributions.index(what)
            dist = self.distributions_descr[idx]
            uom = self.distributions_measure[idx]
            uom = uom.replace('**', '^')
            changes = ['-1', '-2', '-3']
            for c in changes:
                uom = uom.replace(c, '{%s}' % c)
            uom = uom.replace('*', '~')
            # uom = '$%s$' % uom if usetex is True else uom
            cbarLabel = r'%s $%s$' % (dist, uom)

        RadialMap(core, tallies=tallies, z=z, time=t, pre=pre, gro=gro,
                  grp=grp, label=False, figname=None, which=None, fren=False,
                  whichconf='NEconfig', asstype=False, dictname=None,
                  legend=False, txtcol='k', usetex=False, fill=False,
                  axes=None, cmap='Spectral_r', thresh=None,
                  cbarLabel=cbarLabel, xlabel=None, ylabel=None,
                  loglog=None, logx=None, logy=None, title=title,
                  scale=1, fmt="%.2f", numbers=False, **kwargs)

    def whereMaxSpectralRad(path, core, plot=True):
    
        with open(os.path.join(path, 'neutronic', 'outputNE.log'), 'r') as f:
            for l in f:
                if '@ D3DMATI: MAXVAL(SPECTRAL NORM)' in l:
                    # parse IK, IG
                    num = l.split('(IK,IG)= ')[1]
                    IK, IG = num.split()
                    IK, IG = int(IK), int(IG)
        nElz = len(self.core.NE.AxialConfig.AxNodes)
        myIK = 0
        for iz in range(0, nElz):
            for ih in range(1, self.core.NAss+1):
                if myIK == IK:
                    hexty = self.core.getassemblytype(ih, isfren=True)
                    hexty = self.core.NE.assemblytypes[hexty]
                    print(ih)
                    z = self.core.NE.AxialConfig.AxNodes[iz]
                    print('Max spectral norm in {} SAs at z={} cm'.format(hexty, z))
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
                gro = [gro-1]
            gro = [g-1 for g in gro]
        else:
            gro = np.arange(0, self.core.NE.nGro).tolist()
        if grp is not None:
            if isinstance(grp, int):
                grp = [grp-1]
            grp = [g-1 for g in grp]
        if pre is not None:
            if isinstance(pre, int):
                pre = [pre-1]
            pre = [p-1 for p in pre]
        if prp is not None:
            if isinstance(prp, int):
                prp = [prp-1]
            prp = [p-1 for p in prp]

        nodes = self.core.NE.AxialConfig.AxNodes
        if z is not None:
            if isinstance(z, (list, np.ndarray)):
                idz = [np.argmin(abs(zi-nodes)) for zi in z]
            else:
                idz = np.argmin(abs(z-nodes))
        else:
            idz = np.arange(0, len(nodes)).tolist()

        if times is not None:
            if t is not None:
                if isinstance(t, (list, np.ndarray)):
                    idt = [np.argmin(abs(ti-times)) for ti in t]
                else:
                    idt = np.argmin(abs(t-times))
            else:
                idt = np.arange(0, len(times)).tolist()
        else:
            idt = [0]

        return gro, grp, pre, prp, idt, idz

    def _to_index(self, gro, grp, pre, prp, t, z):
        """Map full-array indexes to sliced array indexes.

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
        
        label_dict = {'ngro': 'g', 'ngrp': 'g',
                      'pre': 'p', 'prp': 'p', 'nhex': 'n='}
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
                raise OSError("File extension is wrong. Only HDF5 can be parsed")

        return fname