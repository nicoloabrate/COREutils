"""
Author: N. Abrate.

File: postprocess.py

Description: Class to read data from FRENETIC output files.
"""

import os
import re
import h5py as h5
import numpy as np
from numbers import Real
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
from coreutils.tools.plot import RadialMap
from matplotlib import rc


class PostProcess:
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

    distrout = ['fluxadj', 'fluxadjp', 'fluxdir', 'fluxdirp', 'powerfis',
                'powerneu', 'powerpho', 'powertot', 'precurs', 'precursp',
                'rrd_efis', 'rrd_fis', 'rrd_ker', 'rrd_kerp', 'rrd_lkg',
                'rrd_lkgp', 'rrd_nfis', 'rrd_sct', 'rrd_sctp', 'rrd_src',
                'rrd_srcp', 'rrd_tot', 'rrd_totp', 'tempcool', 'tempfuel']

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

    # sfruttare queste info per leggere e preallocare variabili
    distrout_dim = [('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim',  'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim',  'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'nelz', 'nhex'),
                    ('ntim', 'nelz', 'nhex'),
                    ('ntim', 'nelz', 'nhex'),
                    ('ntim', 'nelz', 'nhex'),
                    ('ntim', 'npre', 'nelz', 'nhex'),
                    ('ntim', 'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'ngro', 'nelz', 'nhex'),
                    ('ntim', 'ngrp', 'nelz', 'nhex'),
                    ('ntim', 'nelz', 'nhex'),
                    ('ntim', 'nelz', 'nhex')]

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

    distrout_uom = ['[-]', '[-]', '[cm**-2*s**-1]', '[cm**-2*s**-1]',
                    '[W*cm**-3]', '[W*cm**-3]', '[W*cm**-3]', '[W*cm**-3]',
                    '[cm**-3]', '[cm**-3]', '[W*cm**-3]', '[cm**-3*s**-1]',
                    '[W*cm**-3]', '[W*cm**-3]', '[cm**-3*s**-1]',
                    '[cm**-3*s**-1]', '[cm**-3*s**-1]', '[cm**-3*s**-1]',
                    '[cm**-3*s**-1]', '[cm**-3*s**-1]', '[cm**-3*s**-1]',
                    '[cm**-3*s**-1]', '[cm**-3*s**-1]', '[K]', '[K]']

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
        self.integralParameters = PostProcess.intout
        self.distributions = PostProcess.distrout
        self.integralParameters_measure = PostProcess.intout_uom
        self.distributions_descr = PostProcess.distrout_attr
        self.distributions_measure = PostProcess.distrout_uom
        self.output_path = path
        # parse number of groups and precursors
        macroxs0 = ['NGRO', 'NPRE', 'NGRP', 'NPRP']
        macroname = os.path.join(path, 'macro.nml')
        macronml = {}
        with open(macroname) as f:
            for line in f:
                for name in macroxs0:
                    if name in line:
                        x = line.split('=')[1]
                        macronml[name] = int(x)

                if line == '/\n':
                    break

        try:
            lst = self.integralParameters['intpar']
            idy = lst.index('betaeff(')
            for i in range(0, macronml['NPRE']):
                self.integralParameters['intpar'].insert(idy,
                                                         'betaeff(%d)' % i)
                uom = self.integralParameters_measure['intpar'][idy]
                self.integralParameters_measure['intpar'].insert(idy, uom)
                idy = idy + 1

            idy = self.integralParameters['intpar'].index('betaeff(')
            self.integralParameters['intpar'].remove('betaeff(')
            del self.integralParameters_measure['intpar'][idy]

            lst = self.integralParameters['intsrc']
            idy = lst.index('gro=')
            for i in range(0, macronml['NGRO']):
                self.integralParameters['intsrc'].insert(idy,
                                                         'gro=%d' % i)
                uom = self.integralParameters_measure['intsrc'][idy]
                self.integralParameters_measure['intsrc'].insert(idy, uom)
                idy = idy + 1

            idy = self.integralParameters['intsrc'].index('gro=')
            self.integralParameters['intsrc'].remove('gro=')
            del self.integralParameters_measure['intsrc'][idy]

            lst = self.integralParameters['intamp']
            idy = lst.index('ceff(')
            for i in range(0, macronml['NPRE']):
                self.integralParameters['intamp'].insert(idy,
                                                         'ceff(%d)' % i)
                uom = self.integralParameters_measure['intamp'][idy]
                self.integralParameters_measure['intamp'].insert(idy, uom)
                idy = idy + 1

            idy = self.integralParameters['intamp'].index('ceff(')
            self.integralParameters['intamp'].remove('ceff(')
            del self.integralParameters_measure['intamp'][idy]

        except ValueError:
            pass

    def get(self, which, hexa=None, time=None, z=None, pre=None,
            gro=None, grp=None, oldfmt=False, core=None):
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
        if which in self.distributions:
            isintegral = False
            dictkey = "distributions"
            fname = 'output.h5'
            idx = self.distributions.index(which)

            if hexa is not None:
                # make FRENETIC numeration consistent with python indexing
                hexa = [h-1 for h in hexa]

            if z is not None and time is not None and core is None:
                raise OSError('Core object is needed to plot this kind of data!')

            nodes = core.NEAxialConfig.AxNodes
            if z is not None:
                if isinstance(z, (list, np.ndarray)):
                    idz = [np.argmin(abs(zi-nodes)) for zi in z]
                else:
                    idz = np.argmin(abs(z-nodes))
            else:
                idz = np.arange(0, len(nodes)).tolist()

            if time is not None:
                times = core.TimeProf
                if isinstance(time, (list, np.ndarray)):
                    idt = [np.argmin(abs(t-times)) for t in time]
                else:
                    idt = np.argmin(abs(time-times))
            else:
                idt = None
            dimdict = {'ntim': idt, 'nelz': idz, 'nhex': hexa, 'ngro': gro,
                       'ngrp': grp, 'nprec': pre}

        else:  # integral data
            isintegral = True
            skip = 1  # +1 for time column
            notfound = True
            for k, v in self.integralParameters.items():

                if which in v:
                    dictkey = k
                    if oldfmt is True:
                        fname = '%s.out' % dictkey
                    else:
                        fname = 'output.h5'
                    idx = v.index(which)+skip
                    notfound = False

            if notfound:
                raise OSError('%s not found in data!' % which)

        # read file content
        datapath = os.path.join(self.output_path, fname)
        if oldfmt is True:
            profile = np.loadtxt(datapath, comments="#", usecols=(0, idx))

        else:
            fh5 = h5.File(datapath, "r")
            if isintegral:
                profile = fh5['integralParameters'][dictkey][:, [0, idx]]
            else:
                # parse specified time, assembly, axial node, group, prec. fam.
                idx = PostProcess.distrout.index(which)
                dims = PostProcess.distrout_dim[idx]
                dimlst = []

                for d in dims:
                    x = dimdict[d]
                    if x is None:
                        x = 0 if x == 'ntim' else slice(None)

                    dimlst.append(x)

                profile = np.asarray(fh5[dictkey][which])
                profile = profile[np.ix_(*dimlst)]

        return profile

    def plot1D(self, prof, which, xlabel=None, zt=None, leglabels=None,
               figname=None, ylabel=None):
        """
        Plot time/axial profile of integral parame. or distribution in hex.

        Parameters
        ----------
        prof : ndarray
            Physical profile. It may contain axial or time grid in the first
            column and as many columns as many profiles to be plotted.
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
        plt.style.use('seaborn-whitegrid')
        rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
        rc('text', usetex=True)

        nprof = prof.shape[1]
        skip = 0
        if nprof > 1 and zt is None:
            zt = prof[:, 0]
            skip = 1

        # plot profiles
        fig = plt.figure()
        handles = []
        handlesapp = handles.append

        for iP in range(0, nprof):
            lin1, = plt.plot(zt, prof[:, iP+skip], 'o', markersize=4)
            handlesapp(lin1)

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
            plt.ylabel("%s %s" % (which, uom))

        else:
            plt.ylabel(ylabel)

        if leglabels is not None:
            legend_x = 1
            legend_y = 0.5
            plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                       loc='center left', ncol=1)
            plt.show()

        if figname is not None:
            fig.savefig(figname, bbox_inches='tight', dpi=500)

    def RadialMap(self, core, what, z=0, time=0, pre=0, gro=0, grp=0,
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
            tallies = np.zeros((core.NAss, len(what.keys())))
            for i, k in enumerate(what.keys()):
                v2 = what[k]
                v1 = self.get(k, hexa=which, time=time,
                              z=z, pre=pre, gro=gro, grp=grp,
                              core=core)
                tmp = np.true_divide(norm(v1-v2), norm(v1))
                tmp[tmp == np.inf] = 0
                tmp = np.nan_to_num(tmp)
                tallies[:, i] = tmp*100

        elif isinstance(what, list):  # list of output
            tallies = np.zeros((core.NAss, len(what)))
            for i, w in enumerate(what):
                tallies[:, i] = self.get(w, hexa=which, time=time,
                                         z=z, pre=pre, gro=gro, grp=grp,
                                         core=core)

        elif isinstance(what, str):  # single output
            tallies = self.get(what, hexa=which, time=time, z=z,
                               pre=pre, gro=gro, grp=grp, core=core)
        else:
            raise TypeError('Input must be str, dict or list!')

        if title is True:
            nodes = core.NEAxialConfig.AxNodes
            idz = np.argmin(abs(z-nodes))

            times = core.TimeProf
            idt = np.argmin(abs(time-times))

            title = 'z=%.2f [cm], t=%.2f [s]' % (nodes[idz], times[idt])

        if cbarLabel is True:
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

        RadialMap(core, tallies=tallies, z=z, time=time, pre=pre, gro=gro,
                  grp=grp, label=False, figname=None, which=None, fren=False,
                  whichconf='NEconfig', asstype=False, dictname=None,
                  legend=False, txtcol='k', usetex=False, fill=False,
                  axes=None, cmap='Spectral_r', thresh=None,
                  cbarLabel=cbarLabel, xlabel=None, ylabel=None,
                  loglog=None, logx=None, logy=None, title=title,
                  scale=1, fmt="%.2f", numbers=False, **kwargs)

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


def get(data, which, hexa, time=None, z=None, pre=None,
        gro=None, grp=None, core=None, myslice=None):
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
    idx = PostProcess.distrout.index(which)
    dims = PostProcess.distrout_dim[idx]

    if core is not None:
        # check hexa, nelz and ntim consistency
        Taxis = dims.index('ntim')
        Zaxis = dims.index('nelz')
        Haxis = dims.index('nhex')
        masksize = list(data.shape)
        if data.shape[Haxis] < core.NAss:
            # map columns and hexagons
            hexa = [myslice['nhex'].index(h) for h in hexa]

    if z is not None and time is not None and core is None:
        raise OSError('Core object is needed to plot this kind of data!')

    nodes = core.NEAxialConfig.AxNodes
    if z is not None:
        if data.shape[Zaxis] < core.NEAxialConfig.AxNodes.shape[0]:
            nodes = myslice['nelz']

        if isinstance(z, (list, np.ndarray)):
            idz = [np.argmin(abs(zi-nodes)) for zi in z]
        else:
            idz = [np.argmin(abs(z-nodes))]
    else:
        if data.shape[Zaxis] < core.NEAxialConfig.AxNodes.shape[0]:
            NZ = len(myslice['nelz'])
        else:
            NZ = len(nodes)
        idz = np.arange(0, NZ).tolist()

    if time is not None:
        times = core.TimeProf
        if data.shape[Taxis] < len(times):
            times = myslice['ntim']
        if isinstance(time, (list, np.ndarray)):
            idt = [np.argmin(abs(t-times)) for t in time]
        else:
            idt = [np.argmin(abs(time-times))]
    else:
        idt = None
    dimdict = {'ntim': idt, 'nelz': idz, 'nhex': hexa, 'ngro': gro,
               'ngrp': grp, 'nprec': pre}

    # parse specified time, assembly, axial node, group, prec. fam.
    dimlst = []
    for d in dims:
        x = dimdict[d]
        if x is None:
            x = 0 if x == 'ntim' else slice(None)

        dimlst.append(x)

    profile = np.asarray(data)
    profile = profile[np.ix_(*dimlst)]

    return profile
