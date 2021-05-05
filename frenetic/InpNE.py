"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
from shutil import rmtree
import numpy as np
import h5py as h5
from . import templates
from coreutils.tools.utils import fortranformatter as ff
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

# TODO: implementare gestione proprieta' fotoni (con GFN e DV)
# TODO: quale coppia di temperature considero per i param. cinetici?
# TODO: evita ripetizione regioni quando omogenee (complica codice di molto)
# TODO: omogenizzazione velocita' su tutto il core?


def writemacro(core, nmix, NG, NP, vel, lambda0, beta0, nFrenCuts, temps,
               unimap):
    """
    Write the input file "macro.nml" for the NE module of FRENETIC.

    Parameters
    ----------
    core : obj
        Core object created with Core class
    nmix : int
        Number of different regions after homogenisation in the core
    NG : int
        Number of energy groups
    NP : int
        Number of precursors families
    vel : ndarray
        Multi-group velocity [cm/s]
    lambda0 : ndarray
        Precursors' families decay constants
    beta0 : ndarray
        Precursors' families physical neutron delayed fraction
    nFrenCuts : int
        Number of axial cuts in FRENETIC geometry
    temps : list
        List of tuples with T fuel and T coolant used to evaluate NE data
    unimap : dict
        Dictionary mapping in which list each universe is located in
        core.NEMaterialData.data dict

    Returns
    -------
    ``None``
    """
    macronames = ["DIFFCOEF", "XSTOT", "XS_SCATT", "XS_FISS", "NUSF", "EFISS"]
    inpnames = ["filediff", "filesigt", "filesigs", "filesigf", "filenusigf",
                "fileesigf"]
    (Tf, Tc) = temps
    # -- write macro.nml file
    asstypeN = 0
    f = io.open('macro.nml', 'w', newline='\n')
    f.write('&MACROXS0\n')
    f.write('NMAT = %d \n' % nmix)
    f.write('NGRO = %d \n' % NG)
    f.write('NPRE = %d \n' % NP)
    # FIXME: include photon data
    f.write('NDHP = %d \n' % 1)
    f.write('NGRP = %d \n' % 0)
    f.write('NPRP = %d \n' % 0)
    f.write('/\n\n')
    f.write('&MACROXS\n')
    f.write('IRHO = 0,\n')
    f.write('VELOC0(1:%d) = ' % NG)

    for igro in range(0, NG):
        f.write('%s,' % ff(vel[igro], 'double'))

    f.write('\nLAMBDA0(1:%d) = ' % NP)

    for iprec in range(0, NP):
        f.write('%s,' % ff(lambda0[iprec], 'double'))

    f.write(' \nlambdadhp0(1:1) = 1.000000d+00,\n')
    f.write('betadhp0(1:1) = 0.000000d+00,\n')
    f.write('IDIFF(1:%d) = %d*2,\n' % (nmix, nmix))
    f.write('ISIGT(1:%d) = %d*2,\n' % (nmix, nmix))
    f.write('ISIGF(1:%d) = %d*2,\n' % (nmix, nmix))
    f.write('TEMPFUEL0 =	 %s,\n' % ff(Tf, 'double'))
    f.write('TEMPCOOL0 =	 %s,\n' % ff(Tc, 'double'))
    f.write('ISIGS(1:%d) = %d*2,\n' % (nmix, nmix))

    for imix in range(0, nmix):

        # perform operations only when the assembly is changed
        if imix % nFrenCuts == 0:
            asstypeN = asstypeN+1
            u = core.NEassemblytypes[asstypeN]
            # perform homogenisation for total and delayed spectra
            chit = AxHomogenise(core, 'infChit', u, NG, (Tf, Tc), unimap)
            chid = AxHomogenise(core, 'infChid', u, NG, (Tf, Tc), unimap)
            imixF = 0

        # write universe number and name
        f.write('\n!Universe %d belongs to %s\n' % (imix+1, u))

        # write kinetic and spectrum parameters
        f.write('CHIT0(%d,1:%d) = ' % (imix+1, NG))
        for igro in range(0, NG):
            f.write('%s,' % ff(chit[imixF, igro], 'double'))

        for igro in range(0, NG):
            v = chid[imixF, igro]
            f.write('\nCHID0(%d,%d,1:%d) = %d*%s,' % (imix+1, igro+1, NP, NP, 
                                                      ff(v, 'double')))
        f.write('\n')
        imixF = imixF+1
        f.write('BETA0(%d,1:%d) = ' % (imix+1, NP))
        for iprec in range(0, NP):
            f.write('%s,' % ff(beta0[iprec], 'double'))

        f.write('\n')
        f.write('\n')
        # write macroscopic NE multi-group data
        for inp, macro in zip(inpnames, macronames):

            if macro == "XS_SCATT":

                for igrostart in range(0, NG):
                    f.write('%s(%d,%d,1:%d) =' % (inp, imix+1, igrostart+1,
                                                  NG))
                    for igroend in range(0, NG):
                        f.write(" '%s_%d_%d_%d', "
                                % (macro, imix+1, igrostart+1, igroend+1))

                    f.write('\n')

            else:

                f.write('%s(%d,1:%d) =' % (inp, imix+1, NG))
                for igro in range(0, NG):
                    triple = (macro, imix+1, igro+1)
                    f.write(" '%s_%d_%d', " % triple)

                f.write('\n')

    # write namelist end
    f.write('/\n')


def writeNEdata(core, NG, unimap, verbose=False, inf=True, txtfmt=False):
    """
    Generate FRENETIC NE module input (HDF5 file or many txt).

    Parameters
    ----------
    core : obj
        Core object created with Core class
    NG : int
        Number of energy groups
    unimap : dict
        Dictionary mapping in which list each universe is located in
        core.NEMaterialData.data dict
    verbose : bool, optional
        Set to ``True`` in order to print also capture, nubar and scattering
        production data. Default is ``False``
    inf : bool, optional
        Set to ``False`` to get B1 Serpent calculation mode for the
        multi-group constants. Default is ``True``
    txtfmt : bool, optional
        Set to ``True`` to print data also in .txt format. Default is ``False``

    Returns
    -------
    ``None``
    """
    # --- define list of output filenames
    outnames = ["DIFFCOEF", "EFISS", "NUSF", "XS_FISS", "XS_SCATT", "XSTOT",
                "CHIT", "XS_REM"]
    infkeys = ['infDiffcoef', 'infKappa', 'infNsf',
               'infFiss', 'infS0', 'infTot', 'infChit', 'infRemxs']
    b1keys = ['b1Diffcoef', 'b1Kappa', 'b1Nsf', 'b1Fiss', 'b1S0', 'b1Chit',
              'b1Remxs']

    if verbose is True:
        infverb = ['infCapt', 'infNubar', 'infSp0']
        b1verb = ['b1Capt', 'b1Nubar', 'b1Sp0']
        verb_out = ["XS_CAPT", "NU", "XS_PSCATT"]
        # append to default list of names
        outnames.extend(verb_out)
        infkeys.extend(infverb)
        b1keys.extend(b1verb)

    datakeys = infkeys if inf is True else b1keys
    datakeys = dict(zip(datakeys, outnames))

    # -- create or overwrite hdf5 file (repro script)
    h5name = "NE_data.h5"
    fh5 = __wopen(h5name)

    NZ = len(core.NEAxialConfig.mycuts)-1
    temps = core.NEMaterialData.temp
    Tf, Tc = zip(*temps)
    # --- define temperature matrix to be filled with data
    n, m = len(set(Tf))+2, len(set(Tc))+1  # temp matrix dimensions
    frendata = np.zeros((n, m))
    frendata[0, 0], frendata[0, 1] = n-2, m-1  # write matrix size
    lstTf = list(set(Tf))
    lstTf.sort()
    frendata[2:, 0] = lstTf
    lstTc = list(set(Tc))
    lstTc.sort()
    frendata[1, 1:] = lstTc

    if txtfmt is True:
        # ---- write steady data to txt files
        # create directory
        if os.path.isdir("NEinputdata"):
            print("'NEinputdata' directory exists. Overwriting?")
            ans = input()
        else:
            ans = "no"

        if ans == "yes" or ans == "y":
            rmtree("NEinputdata")
            os.mkdir("NEinputdata")
        else:
            os.mkdir("NEinputdata")

    # define tuple of couples of temperatures
    temps.sort(key=lambda t: t[0])

    # loop over kind of rod
    zcount = 0
    for hextype, hexname in core.NEassemblytypes.items():
        zold = zcount+0
        for data, dataname in datakeys.items():  # loop over data
            zcount = zold
            homogdata = {}
            where = {}
            # temperature couples loop
            for itup, tup in enumerate(temps):
                # spatially homogenise data
                homogdata[tup] = AxHomogenise(core, data, hexname, NG, tup,
                                              unimap)
                # store value in proper position in temp matrix
                row = np.where(frendata[:, 0] == tup[0])
                col = np.where(frendata[1, :] == tup[1])
                where[tup] = (row, col)
            # -- split homogdata in regions and groups
            for z in range(0, NZ):  # loop over cuts
                zcount = zcount + 1  # new axial region
                for g in range(0, NG):  # loop over energy groups
                    txt = "%s_%d_%d" % (dataname, zcount, g+1)
                    # check if matrix
                    if 'infS' in data or 'b1S' in data:
                        for gdep in range(0, NG):  # loop over departure g
                            # edit name to include info on dep group
                            txtname = "_".join([txt, str(gdep+1)])
                            gc = gdep+NG*g

                            for itup, tup in enumerate(temps):
                                # select matrix entry
                                r, c = where[tup]
                                frendata[r, c] = homogdata[tup][z, gc]
                                # write output if last tuple is reached
                                if itup == len(temps)-1:
                                    if txtfmt is True:
                                        # write txt file
                                        mysavetxt(txtname, frendata)
                                    # save in h5 file
                                    tmp = np.array(frendata, dtype=np.float)
                                    fh5.create_dataset(txtname, data=tmp)

                    else:
                        for itup, tup in enumerate(temps):  # loop over temps
                            # select matrix entry
                            r, c = where[tup]
                            frendata[r, c] = homogdata[tup][z, g]
                            # write data if all T tuples have been spanned
                            if itup == len(temps)-1:
                                if txtfmt is True:
                                    # write txt file
                                    mysavetxt(txt, frendata)
                                # save in h5 file
                                tmp = np.array(frendata, dtype=np.float)
                                fh5.create_dataset(txt, data=tmp)


def writeConfig(core, NZ, Ntypes):
    """
    Write config.inp file.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    NZ : int
        Number of axial cuts
    Ntypes : int
        Number of assembly types

    Returns
    -------
    ``None``

    """
    types = np.zeros((core.NAss, ), dtype=int)
    NAssTypes = len(core.NEassemblytypes)
    compositions = np.reshape(np.arange(1, NZ*NAssTypes+1), (NAssTypes, NZ))
    f = io.open('config.inp', 'w', newline='\n')
    for t in core.NEtime:  # loop over time
        # loop over cut
        for iz, z in enumerate(range(0, NZ)):
            f.write('%s ' % ff(t, 'double'))  # write time instant for each cut
            # write the type of assembly according to FRENETIC numeration
            for n in range(1, core.NAss+1):  # loop over all assemblies
                whichtype = core.getassemblytype(n, time=t, isfren=True,
                                                 whichconf="NEconfig")
                types[n-1] = compositions[whichtype-1, iz]
            # define region number for each assembly
            typestr = types.astype(str)
            f.write('%s' % ' '.join(typestr))
            f.write('\n')


def makeNEinput(core, whereMACINP=None, whereNH5INP=None, template=None):
    """
    Make input.dat file.

    Parameters
    ----------
    core : obj
        Core object created with Core class
    whereMACINP : str, optional
        File path where the 'macro.nml' should be located
    whereNH5INP : str, optional
        File path where the 'NE_data.h5' should be located
    template : str, optional
        File path where the template file is located. Default is ``None``.
        In this case, the default template is used

    Returns
    -------
    ``None``
    """
    if whereMACINP is None:
        whereMACINP = "'macro.nml'"

    if whereNH5INP is None:
        whereNH5INP = "'NE_data.h5'"

    tmp = core.NEAxialConfig.splitz
    NZ = len(core.NEAxialConfig.mycuts)-1
    if isinstance(tmp, (int)):
        splitz = [tmp]*NZ 
    elif isinstance(tmp, (list)):
        splitz = tmp if len(tmp) > 1 else tmp[0]*NZ 
            
    nConfig = len(core.NEtime)
    nRun = 2 if core.trans is True else 1

    geomdata = {'$NH5INP': whereNH5INP, '$MACINP': whereMACINP, '$NELEZ0': NZ,
                '$MESHZ0': core.NEAxialConfig.mycuts, 
                '$SPLITZ': splitz,
                '$NCONFIG': nConfig, '$NRUN': nRun, '$POW': core.power,
                '$NPROF': len(core.TimeProf), '$TPROF': core.TimeProf}

    if template is None:
        tmp = pkg_resources.read_text(templates, 'template_NEinput.dat')
        tmp = tmp.splitlines()
    else:
        with open(template, 'r') as f:
            temp_contents = f.read()
            tmp = temp_contents. splitlines()

    f = io.open("input.dat", 'w', newline='\n')
    for line in tmp:  # loop over lines in reference file
        for key, val in geomdata.items():  # loop over dict keys
            if key in line:
                if key in ['$MESHZ0', '$SPLITZ']:
                    val = [str(v) for v in val]
                    val = "%s" % ",".join(val)
                elif key == '$TPROF':
                    tProf = [ff(t, 'double') for t in val]
                    val = ','.join(tProf)
                elif key == '$POW':
                    val = ff(val, 'double')
                else:
                    val = str(val)

                # write to file
                line = line.replace(key, val)

        # write to file
        f.write(line)
        f.write('\n')


def AxHomogeniseData(flux, data, hz, htot):
    """
    Axially homogenise multi-group data over a set of axial nodes.

    Parameters
    ----------
    flux : ndarray
        Flux over the hz regions
    data : ndarray
        Data over the hz regions
    hz : ndarray
        Fine axial discretisation
    htot : ndarray
        Total height of the sub-interval

    Returns
    -------
    homogdata : float
        Axially homogenised data

    """
    flux = flux*hz/htot
    # homogenise over deltaz preserving reaction rate
    homogdata = np.dot(flux, data)/sum(flux)

    return homogdata


def AxHomogenise(core, what, which, NG, temp, unidict):
    """
    Axially homogenise multi-group parameters.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    what : str
        Data name to be homogenised
    which : int
        Type of NE assembly
    NG : int
        Number of energy groups
    temps : list
        List of tuples with T fuel and T coolant used to evaluate NE data
    unidict : dict
        Dictionary mapping in which list each universe is located in
        core.NEMaterialData.data dict

    Returns
    -------
    homdata : ndarray
        2D array with homogenised data. The dimension is (number of axial
        cuts, number of energy groups).

    """
    if isinstance(which, int):
        # parse key from dict
        which = core.NEassemblytype[which]

    # get cuts coordinates and fine regions
    coarsecuts = np.asarray(core.NEAxialConfig.mycuts)
    reg = np.asarray(core.NEAxialConfig.cuts[which].reg)
    uppz = np.asarray(core.NEAxialConfig.cuts[which].upz)
    lowz = np.asarray(core.NEAxialConfig.cuts[which].loz)
    # get deltaz
    dzCoarse = coarsecuts[1::]-coarsecuts[0:-1]
    dzFine = uppz-lowz

    changeuniv = np.zeros((len(dzCoarse), ), dtype=int)
    fineincoarse = np.zeros((len(dzCoarse), ), dtype=int)
    izf = 0
    for izc in range(1, len(coarsecuts)):
        fineincoarse[izc-1] = 1
        while uppz[izf] < coarsecuts[izc]:
            izf = izf+1
            # update, fine cut included in coarse
            fineincoarse[izc-1] = fineincoarse[izc-1]+1
        if uppz[izf] == coarsecuts[izc]:
            izf = izf+1
            changeuniv[izc-1] = 1

    # define scattering matrices keys (used later on)
    scattmat = [*['infS%d' % d for d in range(0, 8)],
                *['infSp%d' % d for d in range(0, 8)]]

    # homogenise in each group
    N = NG*NG if what in scattmat else NG
    homdata = np.zeros((len(fineincoarse), N))

    for g in range(0, NG):  # loop over energy groups
        idx = 0
        for izf in range(0, len(fineincoarse)):  # loop over axial cuts
            iduniv = reg[idx:idx+fineincoarse[izf]]
            # get fine dz for fine regions inside coarse
            dzTot = dzFine[idx:idx+fineincoarse[izf]]
            dz = dzFine[idx:idx+fineincoarse[izf]]+0
            # correct value with difference between coarse and last fine
            dz[-1] = coarsecuts[izf+1]-lowz[idx+fineincoarse[izf]-1]

            if changeuniv[izf] == 1:
                dz[0] = uppz[idx]-coarsecuts[izf]
                idx = idx+fineincoarse[izf]
            else:
                if izf > 0:
                    dz[0] = uppz[idx]-coarsecuts[izf]

                if changeuniv[izf] == 0 and fineincoarse[izf] == 1:
                    dz[0] = dzCoarse[izf]

                idx = idx+fineincoarse[izf]-1

            # --- get flux and data for homogenisation
            flx = np.zeros((len(iduniv), ))
            if what in scattmat:
                # matrix for scattering matrix
                data = np.zeros((NG, len(iduniv)))
            else:
                data = np.zeros((len(iduniv), ))

            for i, u in enumerate(iduniv):  # loop over universes in dz
                idf = unidict[u]  # get file position in list
                file = core.NEMaterialData.data[temp][idf]  # get serpent data
                flx[i] = file.getUniv(u, 0, 0, 0).infExp['infFlx'][g]

                if what in scattmat:
                    # reshape in matrix
                    smat = np.reshape(file.getUniv(u, 0, 0, 0).infExp[what],
                                      (NG, NG))
                    # keep data
                    data[:, i] = smat[:, g]
                else:
                    data[i] = file.getUniv(u, 0, 0, 0).infExp[what][g]

            # axially homogenise required data
            if what in scattmat:
                tmp = np.zeros((NG, ))
                for gg in range(0, NG):
                    # homogenise scattering matrix over each sub-group
                    tmp[gg] = AxHomogeniseData(flx, data[gg, :], dz, dzTot)
                homdata[izf, g*NG:g*NG+NG] = tmp
            else:
                homdata[izf, g] = AxHomogeniseData(flx, data, dz, dzTot)

    return homdata


def mysavetxt(fname, x, fmt="%.6e", delimiter=' '):
    """
    Write file in txt format.

    Parameters
    ----------
    fname : str
        File name.
    x : ndarray
        Data to be written in txt.
    fmt : str, optional
        Data output format. The default is "%.6e".
    delimiter : str, optional
        Delimiter between data. The default is ' '.

    Returns
    -------
    None.

    """
    fname = fname+".txt"  # add file extension
    fname = os.path.join("NEinputdata", fname)
    with open(fname, 'w') as f:
        for idx, row in enumerate(x):
            if idx == 0:
                line = delimiter.join("%.0g" % value for value in row)
            else:
                line = delimiter.join(fmt % value for value in row)
            f.write(line + '\n')


def __wopen(h5name):
    """
    Open "h5name.hdf5" in "append" mode. If exists, user is asked to overwrite.

    Parameters
    ----------
    h5name : string
        File name

    Returns
    -------
    fh5 : object
        Object of h5py module

    """
    if os.path.isfile(h5name):
        print("File exists. Overwriting?")
        ans = input()
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
