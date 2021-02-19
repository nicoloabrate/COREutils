"""
Author: N. Abrate.

File: postprocess.py

Description: Class to read data from FRENETIC output files.
"""

import os
import re
import time as t
import h5py as h5
import numpy as np
import matplotlib.pyplot as plt

from os.path import isfile, join
from matplotlib import rc

# TODO:
# per conti parametrici, si scrive una classe del tipo IOwrapper che salvi in matrici (poi
# salvate in hdf5, se necessario) di output e parametri. Questo script dovra' leggere
# in maniera automatica file da piu' cartelle con nomi simili (per ora i nomi contengono i
# parametri, poi magari ci sara' il parsing dei file di input)


class PostProcess:
    """
    Class to read profiles computed by FRENETIC.
    """

    # leggili dall'input!
    (nelz, ntim, ngro, ngrp, nhex, npre) = (1, 1, 1, 1, 1, 1)
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
        self.integralParameters = ParseFrenOut.intout
        self.distributions = ParseFrenOut.distrout
        self.integralParameters_measure = ParseFrenOut.intout_uom
        self.distributions_descr = ParseFrenOut.distrout_attr
        self.distributions_measure = ParseFrenOut.distrout_uom

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

    def get(self, path, which, hexa=None, time=None, z=None, pre=None,
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
        if hexa is not None:
            # make FRENETIC numeration consistent with python indexing
            hexa = [h-1 for h in hexa]  

        dimdict = {'ntim': time, 'nelz': z, 'nhex': hexa, 'ngro': gro, 'ngrp':
                   grp, 'nprec': pre}

        if which in self.distributions:
            isintegral = False
            dictkey = "distributions"
            fname = 'output.h5'
            idx = self.distributions.index(which)

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
        datapath = os.path.join(path, fname)
        if oldfmt is True:
            profile = np.loadtxt(datapath, comments="#", usecols=(0, idx))

        else:
            fh5 = h5.File(datapath, "r")
            if isintegral:
                profile = fh5['integralParameters'][dictkey][:, [0, idx]]
            else:
                # parse specified time, assembly, axial node, group, prec. fam.
                idx = ParseFrenOut.distrout.index(which)
                dims = ParseFrenOut.distrout_dim[idx]
                dimlst = []
    
                for d in dims:
                    x = dimdict[d]
                    if x is None:
                        x = 0 if x == 'ntim' else slice(None)
    
                    dimlst.append(x)
  
                profile = np.asarray(fh5[dictkey][which])
                profile = profile[dimlst]

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

    def RadialMap(self, core, what= time=0, label=False, dictname=None, figname=None,
                  fren=False, which=None, what=None, asstype=False, usetex=False,
                  fill=True, axes=None, cmap='Spectral_r', thresh=None,
                  cbarLabel=None, xlabel=None, ylabel=None, loglog=None,
                  logx=None, logy=None, title=None, scale=1, fmt="%.2f",
                  numbers=False, **kwargs):
        """
        Plot FRENETIC output on the x-y plane.
    
        Parameters
        ----------
        label : TYPE, optional
            DESCRIPTION. The default is False.
        dictname : TYPE, optional
            DESCRIPTION. The default is None.
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
        # set default font and TeX interpreter
        rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
        rc('text', usetex=usetex)
    
        Nass = core.Map.type.size
        # array of assembly type
        typelabel = np.reshape(core.Config[time], (Nass, 1))
        maxtype = int(max(typelabel))
        coretype = range(0, maxtype+1)  # define
    
        kwargs.setdefault("ec", "k")
        kwargs.setdefault("linewidth", 0.5)
        kwargs.setdefault("lw", 0.5)
        kwargs.setdefault("alpha", 1)
        fontsize = kwargs.get("fontsize", 4)
        # delete size from kwargs to use it in pathces
        if 'fontsize' in kwargs:
            del kwargs['fontsize']
    
        else:  # cont. <- if type(fill) is bool
    
            orientation = 0
    
            patches = []
            patchesapp = patches.append
            errbar = False
            # check data type is correct
            if type(what) is dict:
                # check keys
                if 'tallies' in what.keys():
                    tallies = what['tallies']
    
                if 'errors' in what.keys():
                    errors = what['errors']
                    errbar = True
    
            elif type(what) is np.ndarray:
                tallies = what
                # check on data shape
                try:
                    # associate tallies to Serpent assemblies numeration
                    Nx, Ny = tallies.shape
                    assnum = np.arange(1, Nx*Ny+1)
                    # flattening sq. or hex. lattice by rows
                    tallies = dict(zip(assnum, tallies.flatten('C')))
                except ValueError:
                    # TODO (possible enhancement: plot ND array slicing)
                    raise IndexError('Only 2D arrays are currently supported!')
    
            else:
                raise TypeError('Data must be dict or numpy array!')
    
            # TODO: place these lines somewhere where tallies is array for automatic formatting
            # peak = np.max(np.max(tallies))
            # if abs(peak) > 999:
            #     fmt = ".2e"
            # else:
            #     fmt = ".2f"
    
        # open figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
    
        # check which variable
        if which is None:
            which = (core.Map.serpcentermap).keys()
    
        elif which is not None:
            if fren is True:
                which = [core.Map.fren2serp[k] for k in which]
            # FIXME!
            # else:
            #     tmp = list((core.serpcentermap).keys())
            #     which = [tmp[k] for k in which]
    
        for key, coord in (core.Map.serpcentermap).items():
    
            # check key is in which list
            if key not in which:
                continue
    
            x, y = coord
            # scale coordinate
            coord = (x*scale, y*scale)

            # define assembly patch
            asspatch = RegularPolygon(coord, core.AssemblyGeom.numedges, L*scale,
                                      orientation=orientation, **kwargs)
            patchesapp(asspatch)
            # define value to be plotted
            #if fren is False:  # Serpent numeration
            # FIXME: per ora "valuesapp(tallies[key])" viene messo sotto per evitare che sia tutto disordinato
            #valuesapp(tallies[key])
            #else:  # Frenetic numeration
               # keyF = core.serp2fren[key]
               # valuesapp(tallies[keyF])
    
        # plot physics, if any
        if physics is True:
            # values = np.asarray(values)
            patches = np.asarray(patches, dtype=object)
            if which is None:
                coord = np.array(list(core.Map.serpcentermap.values()))
            else:
                coord, values = [], []
                for k in which:
                    coord.append(core.Map.serpcentermap[k])
                    values.append(tallies[k])
    
                coord = np.asarray(coord)
                values = np.asarray(values)
    
            normalizer = normalizerFactory(values, None, False, coord[:, 0]*scale,
                                           coord[:, 1]*scale)
            pc = PatchCollection(patches, cmap=cmap, **kwargs)
            formatPlot(ax, loglog=loglog, logx=logx, logy=logy,
                       xlabel=xlabel or "X [cm]",
                       ylabel=ylabel or "Y [cm]", title=title)
            pc.set_array(values)
            pc.set_norm(normalizer)
            ax.add_collection(pc)
            addColorbar(ax, pc, cbarLabel=cbarLabel)
    
        # add labels on top of the polygons
        for key, coord in (core.Map.serpcentermap).items():
            # check key is in "which" list
            if key not in which:
                continue
    
            x, y = coord
            # plot text inside assemblies
            if dictname is None:
                if label is True:  # plot assembly number
                    if physics is False:
                        if fren is True:  # FRENETIC numeration
                            txt = str(core.Map.serp2fren[key])  # translate keys
                        else:
                            txt = str(key)
    
                    else:
                        # define value to be plotted
                        if numbers is False:
                            if fren is False:  # Serpent numeration
                                txt = fmt % tallies[key]
    
                            else:  # Frenetic numeration
                                txt = fmt % tallies[key]  # core.serp2fren[key]
    
                            if errbar is True:
                                txt = "%s \n %.2f%%" % (txt, errors[key]*100)
                        else:
                            if fren is True:  # FRENETIC numeration
                                txt = str(core.Map.serp2fren[key])  # translate keys
                            else:
                                txt = str(key)
    
                    plt.text(x*scale, y*scale, txt, ha='center',
                             va='center', size=fontsize)
    
            else:
                if asstype is True:  # plot assembly type
                    txt = dictname[typelabel[key-1, 0]]
                    plt.text(x*scale, y*scale, txt, ha='center', va='center',
                             size=fontsize)
    
                # FIXME: must be a better way to do this avoiding asstype, maybe.
                # change "dictname" because maybe we want tuples to have overlappings (phytra fig)
                # write other labels
                else:
                    atype = core.getassemblytype(key, time=time)
                    x, y = core.Map.serpcentermap[key]
                    txt = dictname[atype]
                    plt.text(x*scale, y*scale, txt, ha='center',
                             va='center', size=fontsize)
    
        ax.axis('equal')
        if xlabel is None and ylabel is None:
            plt.axis('off')
    
        # save figure
        if figname is not None:
            fig.savefig(figname, bbox_inches='tight', dpi=250)
    
    
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

