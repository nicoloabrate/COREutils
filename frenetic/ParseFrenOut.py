"""
Author: N. Abrate.

File: ParseFrenOut.py

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


class ParseFrenOut:
    """
    Class to read ParseFrenOut profiles exported from Ansys Fluent.

    Attributes
    ----------
    snapshots : ndarray
        snapshot matrix
    param : ndarray
        parameters matrix
    snapshotmap: List
        list of lists mapping snapshot matrix
    coordmap : list
        list of lists mapping coordinates
    param_names : list
        list of parameter names
    flag2D : bool
        flag to understand if 2D or 3D simulations

    Methods
    -------
    load(datapath, flag2D=False):
        Store the content of hdf5 file in "datapath" in an object.
    plot1D(xyz, face, prof, cases, figname=None):
        Plot CFD profile over a certain coordinate of a source-box face.
    plot2D(face, prof, case, adim=False, figname=None):
        Plot CFD profiles map over a source-box face.
    subplot2D(face, prof, case, adim=False, figname=None):
        Plot CFD profiles map over a source-box face.
    compareplot1D(xyz, face, prof, case, interpol, figname=None):
        Compare high-fidelity solution and reduced order model interpolation.
    getXYZ(face, prof, case):
        Get X, Y and Z coordinates from ParseFrenOut face.
    write(datapath, flag2D=False):
        Read Fluent output files and write them in HDF5 file.
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
            gro=None, grp=None, oldfmt=False):
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
                profile = fh5['integralParameters'][dictkey][0, idx]
            else:
                # parse specified time, assembly, axial node, group, prec. fam.
                dims = ParseFrenOut.distrout_dim
                dimlst = []
    
                for d in dims:
                    x = dimdict[d]
                    if x is None:
                        x = 0 if x == 'ntim' else slice(None)
    
                    dimlst.append(x)
    
                profile = fh5[dictkey][which][dimlst]

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

    def compareplot1D(self, xyz, face, prof, case, interpol, figname=None):
        """
        Compare high-fidelity solution and reduced order model interpolation.

        Parameters
        ----------
        xyz : string
            Spatial coordinate the profile is plotted with respect with.
        face : string
            Face the profile is plotted with respect with.
        prof : string
            Physical profile.
        case : int
            Identification number of the case.
        interpol : ndarray
            Interpolated profile.
        figname : TYPE, optional
            Name assigned to the figure for saving. The default is None.

        Returns
        -------
        None.

        """
        plt.style.use('seaborn-whitegrid')
        rc('text', usetex=True)

        fig = plt.figure()

        v = self.__dict__[xyz]  # get spatial coordinate

        iFace = self.facekey.index(face)
        iProf = self.profilekey.index(prof)

        # take coordinates from the snapshot map
        iS, iE = self.snapshotmap[iFace][iProf]
        # take coordinates from the coordinate map
        iCS, iCE = self.coordmap[iFace]

        lin1, = plt.plot(v[iCS:iCE+1], self.snapshots[iS:iE+1, case],
                         'o', markersize=4)
        lin2, = plt.plot(v[iCS:iCE+1], interpol[iS:iE+1],
                         'o', markersize=4)

        handles = (lin1, lin2)
        labels = ("CFD", "ROM")

        titledict = dict(zip(self.param_names, self.param[:, case]))
        tit = ', '.join("{!s}={!r}".format(key, val)
                        for (key, val) in titledict.items())
        plt.title(tit)

        plt.xlabel(" ".join((xyz, "[m]")))

        # select unit of measure for ylabel
        if self.flag2D is False:
            um_ind = self.inp_prof_key3D.index(prof)
            um = self.unit_meas_3D[um_ind]
        else:
            um_ind = self.inp_prof_key2D.index(prof)
            um = self.unit_meas_2D[um_ind]

        if prof == "ch4":
            prof = "$\\rm{CH_4}$"

        plt.ylabel("%s %s" % (prof, um))

        legend_x = 1
        legend_y = 0.5
        plt.legend(handles, labels, bbox_to_anchor=(legend_x, legend_y),
                   loc='center left', ncol=1)
        plt.show()

        if figname is not None:
            fig.savefig(figname, bbox_inches='tight', dpi=500)

    @classmethod
    def write(cls, datapath, fname=None, ans=None, flag2D=False):
        """
        Read Fluent output files and write them in HDF5 file.

        Parameters
        ----------
        cls : ParseFrenOut class
            ParseFrenOut class.
        datapath : string
            Path where data are stored.
        fname : string
            Name for HDF5 file. The default is None, so the filename given
            is the same of the directory containing the profiles.
        ans : string
            Answer for choosing file overwriting. Default is None, so I/O with
            user is required.
        flag2D : bool or int, optional
            Flag for 2D profiles. The default is None.

        Raises
        ------
        OSError
            -Number of profiles and parameters does not match
            -Identification number of profiles and parameters does not match

        Returns
        -------
        None
        """
        if flag2D is False:
            facekeys = cls.inp_face_key3D
            profilekeys = cls.inp_prof_key3D
            unit_meas = cls.unit_meas_3D
        else:
            facekeys = cls.inp_face_key2D
            profilekeys = cls.inp_prof_key2D
            unit_meas = cls.unit_meas_2D

        if fname is None:
            h5name = datapath + ".hdf5"
        else:
            h5name = ParseFrenOut.__checkname(fname)

        fh5 = ParseFrenOut.__wopen(h5name, ans=ans)

        if fh5 == -1:
            return print("File not overwritten.")

        print("Writing profiles and parameters in hdf5 file...")
        tstart = t.time()

        proffiles = [f for f in sorted(os.listdir(datapath))
                     if isfile(join(datapath, f))
                     if f.startswith('sbprofiles_')]

        paramfiles = [f for f in sorted(os.listdir(datapath))
                      if isfile(join(datapath, f))
                      if f.startswith('sbparam_')]

        if len(proffiles) != len(paramfiles):
            print("Number of profile files and number of parameter files do not match!")
            raise OSError("Please check files in %s" % datapath)

        for iFile, profname in enumerate(proffiles):
            num1 = profname.split(".")[0]
            num1 = num1.split("_")[1]

            num2 = paramfiles[iFile].split(".")[0]
            num2 = num2.split("_")[1]

            if num1 != num2:
                raise OSError("Profile and parameter file id numbers mismatch!")

        # loop over input files (Fluent output)
        for iFile, f in enumerate(proffiles):
            fid, ext = f.split(".")
            fid = fid.split("_")[1]

            fh5.create_group(fid)

            pname = os.path.join(datapath, paramfiles[iFile])

            pdict = ParseFrenOut.__loadtxt(pname)

            for k, v in pdict.items():
                fh5[fid].attrs[k] = float(v)

            fname = os.path.join(datapath, f)
            findlines = open(fname).read().split('\n')

            NP = [int((findlines[0].split(' '))[2].split(')')[0])]
            Nold = 0
            for iP in range(0, len(facekeys)-1):
                # span the list to find the number of points inside each face
                N = Nold+(2+NP[iP])*len(profilekeys)+2
                Nstr = findlines[N].split(' ')[2]
                NP.append(int((Nstr.split(')')[0])))  # store number of points on each face
                Nold = N

            nS, nE = 0, 0
            # loop over source-box faces
            for iFace, face in enumerate(facekeys):
                Nold = nE+2*(iFace > 0)
                N = NP[iFace]  # get row number according to face
                # create group
                facegrp = fh5.create_group("/".join((fid, face)))
                # loop over different profiles
                for iProf, prof in enumerate(profilekeys):
                    nS = 2*iProf+iProf*N+Nold+2
                    nE = 2*iProf+(1+iProf)*N+Nold+2
                    v = [float(s) for s in findlines[nS:nE]]

                    # FIXME: check that 2D ParseFrenOut plotting works
                    if flag2D is True:
                        # sort coordinate arrays in descending order
                        if prof == "x" or prof == "y" or prof == "z":
                            sortind = np.argsort(v)
                        # sort array (profile or other)
                        v = np.array(v)[sortind]

                    dset = facegrp.create_dataset(prof, data=v)
                    dset.attrs["Unit of measurement"] = unit_meas[iProf]

        fh5.close()
        print("DONE \n")
        print("Elapsed time %f s" % (t.time()-tstart))

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
