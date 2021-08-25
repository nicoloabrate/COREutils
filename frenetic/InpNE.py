"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import json
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
               unimap, NE_1D=False, H5fmt=1):
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

    for igro in range(NG):
        f.write('%s,' % ff(vel[igro], 'double'))

    f.write('\nLAMBDA0(1:%d) = ' % NP)

    for iprec in range(NP):
        f.write('%s,' % ff(lambda0[iprec], 'double'))

    f.write(' \nlambdadhp0(1:1) = 1.000000d+00,\n')
    f.write('betadhp0(1:1) = 0.000000d+00,\n')
    f.write('IDIFF(1:%d) = %d*2,\n' % (nmix, nmix))
    f.write('ISIGT(1:%d) = %d*2,\n' % (nmix, nmix))
    f.write('ISIGF(1:%d) = %d*2,\n' % (nmix, nmix))
    f.write('TEMPFUEL0 =	 %s,\n' % ff(Tf, 'double'))
    f.write('TEMPCOOL0 =	 %s,\n' % ff(Tc, 'double'))
    f.write('ISIGS(1:%d) = %d*2,\n' % (nmix, nmix))

    for imix in range(nmix):

        # perform operations only when the assembly is changed
        if NE_1D:
            u = list(core.config[0].regions.keys())
            chit = core.config[0].regions[u[0]].getxs('Chit')[np.newaxis, :]
            chid = core.config[0].regions[u[0]].getxs('Chid')[np.newaxis, :]
            imixF = 0
            u = u[imix]
        else:
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
        for igro in range(NG):
            f.write('%s,' % ff(chit[imixF, igro], 'double'))

        for igro in range(NG):
            v = chid[imixF, igro]
            f.write('\nCHID0(%d,%d,1:%d) = %d*%s,' % (imix+1, igro+1, NP, NP, 
                                                      ff(v, 'double')))
        f.write('\n')
        imixF = imixF+1
        f.write('BETA0(%d,1:%d) = ' % (imix+1, NP))
        for iprec in range(NP):
            f.write('%s,' % ff(beta0[iprec], 'double'))

        f.write('\n')
        f.write('\n')
        # write macroscopic NE multi-group data
        for inp, macro in zip(inpnames, macronames):

            if macro == "XS_SCATT":

                if H5fmt == 1:
                    for igrostart in range(NG):
                        f.write('%s(%d,%d,1:%d) =' % (inp, imix+1, igrostart+1,
                                                      NG))
                        for igroend in range(NG):
                            f.write(" '%s_%d_%d_%d', "
                                    % (macro, imix+1, igrostart+1, igroend+1))
                        f.write('\n')
                elif H5fmt == 2:
                    for igrostart in range(NG):
                        f.write('%s(%d,%d,1:%d) =' % (inp, imix+1, igrostart+1,
                                                      NG))
                        for igroend in range(NG):
                            f.write(" '{:d}/{}', ".format(imix+1, macro))
                        f.write('\n')

            else:
                if H5fmt == 1:
                    f.write('%s(%d,1:%d) =' % (inp, imix+1, NG))
                    for igro in range(NG):
                        triple = (macro, imix+1, igro+1)
                        f.write(" '%s_%d_%d', " % triple)
                    f.write('\n')
                elif H5fmt == 2:
                    f.write('%s(%d,1:%d) =' % (inp, imix+1, NG))
                    for igro in range(NG):
                        f.write(" '{:d}/{}', ".format(imix+1, macro))
                    f.write('\n')
    # write namelist end
    f.write('/\n')


def writeNEdata(core, NG, unimap, verbose=False, inf=True, H5fmt=2, 
                NE_1D=False):
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
    slabkeys = ['Diffcoef', 'Kappa', 'NuFiss', 'Fiss', 'S0', 'Tot', 'Chit',
                'Remxs']
    if verbose is True:
        infverb = ['infCapt', 'infNubar', 'infSp0']
        b1verb = ['b1Capt', 'b1Nubar', 'b1Sp0']
        verb_out = ["XS_CAPT", "NU", "XS_PSCATT"]
        # append to default list of names
        outnames.extend(verb_out)
        infkeys.extend(infverb)
        b1keys.extend(b1verb)

    outnames = tuple(outnames)
    infkeys = tuple(infkeys)
    b1keys = tuple(b1keys)
    if NE_1D:
        datakeys = slabkeys
        datakeys = dict(zip(datakeys, outnames))        
    else:
        datakeys = infkeys if inf is True else b1keys
        datakeys = dict(zip(datakeys, outnames))

    # -- create or overwrite hdf5 file (repro script)
    h5name = "NE_data.h5"
    fh5 = __wopen(h5name)

    NZ = core.config[0].nLayers if NE_1D else len(core.NEAxialConfig.mycuts)-1
    temps = [(300, 300)] if NE_1D else core.NEMaterialData.temp
    Tf, Tc = zip(*temps)
    if H5fmt == 1:
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

    if H5fmt is False or H5fmt == 0:
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

    # initialised as big numbers to check minima
    if NE_1D:
        regs = dict(zip(unimap.values(), unimap.keys()))
        for data, dataname in datakeys.items():  # loop over data
            iz = 0
            row = np.where(frendata[:, 0] == Tf[0])
            col = np.where(frendata[1, :] == Tc[0])
            for z in range(len(core.config[0].regions)):  # loop over cuts
                iz += 1  # new axial region
                if data != 'NuFiss':
                    mydata = core.config[0].regions[regs[iz-1]].__dict__[data]
                else:
                    nubar = core.config[0].regions[regs[iz-1]].Nubar
                    fiss = core.config[0].regions[regs[iz-1]].Fiss
                    mydata = nubar*fiss
                for g in range(NG):  # loop over energy groups
                    txt = "%s_%d_%d" % (dataname, iz, g+1)
                    # check if matrix
                    if 'S0' in data:
                        for gdep in range(NG):  # loop over departure g
                            # edit name to include info on dep group
                            txtname = "_".join([txt, str(gdep+1)])
                            frendata[row, col] = mydata[gdep, g]
                            # write output if last tuple is reached
                            if H5fmt is False or H5fmt == 0:
                                # write txt file
                                mysavetxt(txtname, frendata)
                            # save in h5 file
                            tmp = np.array(frendata, dtype=np.float)
                            fh5.create_dataset(txtname, data=tmp)
                    else:
                        frendata[row, col] = mydata[g]
                        # write data if all T tuples have been spanned
                        if H5fmt is False or H5fmt == 0:
                            # write txt file
                            mysavetxt(txt, frendata)
                        # save in h5 file
                        tmp = np.array(frendata, dtype=np.float)
                        fh5.create_dataset(txt, data=tmp)
       
    else:
        DFLmin = np.ones((len(core.NEassemblytypes), NZ))*1E6
        MFPmin = np.ones((len(core.NEassemblytypes), NZ))*1E6
        DFL = np.zeros((len(core.NEassemblytypes), NZ, NG, len(temps)))

        if H5fmt == 1:
            # loop over kind of SAs
            iz, ih = 0, -1
            for hextype, hexname in core.NEassemblytypes.items():
                zold = iz+0
                # update hexagon tpye counter
                ih = ih+1
                for data, dataname in datakeys.items():  # loop over data
                    iz = zold
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
                    for z in range(NZ):  # loop over cuts
                        iz = iz + 1  # new axial region
                        for g in range(NG):  # loop over energy groups
                            txt = "%s_%d_%d" % (dataname, iz, g+1)
                            # check if matrix
                            if 'infS' in data or 'b1S' in data:
                                for gdep in range(NG):  # loop over departure g
                                    # edit name to include info on dep group
                                    txtname = "_".join([txt, str(gdep+1)])
                                    gc = gdep+NG*g
        
                                    for itup, tup in enumerate(temps):
                                        # select matrix entry
                                        r, c = where[tup]
                                        frendata[r, c] = homogdata[tup][z, gc]
                                        # write output if last tuple is reached
                                        if itup == len(temps)-1:
                                            if H5fmt is False or H5fmt == 0:
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
                                    if data in ['infDiffcoef', 'b1Diffcoef']:
                                        DFL[ih, z, g, itup] = np.sqrt(homogdata[tup][z, g])
                                    elif data in ['infRemxs', 'b1Remxs']:
                                        DFL[ih, z, g, itup] = DFL[ih, z, g, itup]/np.sqrt(homogdata[tup][z, g])
                                    # write data if all T tuples have been spanned
                                    if itup == len(temps)-1:
                                        if H5fmt is False or H5fmt == 0:
                                            # write txt file
                                            mysavetxt(txt, frendata)
                                        # save in h5 file
                                        tmp = np.array(frendata, dtype=np.float)
                                        fh5.create_dataset(txt, data=tmp)
                                        # check if L or MFP are minimum
                                        if data in ['infTot', 'b1Tot']:
                                            if MFPmin[ih, z] > 1/tmp[2:, 1:].min():
                                                MFPmin[ih, z] = 1/tmp[2:, 1:].min()

        elif H5fmt == 2:
            # temperature couples loop
            for itup, tup in enumerate(temps):
                for data, dataname in datakeys.items():  # loop over data
                    iz, ih = 0, -1
                    for hextype, hexname in core.NEassemblytypes.items():
                        # update hexagon tpye counter
                        ih = ih+1 
                        # spatially homogenise data
                        homogdata = AxHomogenise(core, data, hexname, NG, tup, unimap)
                        # create temperatures group
                        tmpgrp = 'Tf_{}_Tc_{}'.format(tup[0], tup[1])
                        if tmpgrp not in fh5.keys():
                            fh5.create_group(tmpgrp)
                        fh5_TfTc = fh5[tmpgrp]
                        # loop over kind of SAs
   
                        # -- split homogdata in regions and groups
                        for z in range(NZ):  # loop over cuts
                            iz = iz + 1  # new axial region
                            # --- create group
                            izgrp = '{}'.format(iz)
                            if izgrp not in fh5_TfTc.keys():
                                fh5_TfTc.create_group(izgrp)
                            fh5_iz = fh5_TfTc[izgrp]

                            # save in h5 file
                            if 'infS' in data or 'b1S' in data:
                                tmp = np.array(homogdata[z, :].reshape(NG, NG), dtype=np.float)
                            else:
                                tmp = np.array(homogdata[z, :], dtype=np.float)
   
                            fh5_iz.create_dataset(dataname, data=tmp)

                            # check if L or MFP are minimum
                            if data in ['infDiffcoef', 'b1Diffcoef']:
                                DFL[ih, z, :, itup] = np.sqrt(homogdata[z, :])
                            elif data in ['infRemxs', 'b1Remxs']:
                                DFL[ih, z, :, itup] = DFL[ih, z, :, itup]/np.sqrt(homogdata[z, :])
                            
                            if data in ['infTot', 'b1Tot']:
                                if MFPmin[ih, z] > 1/tmp.min():
                                    MFPmin[ih, z] = 1/tmp.min()      

        fh5.close()
        # loop over kind of SAs for minimum L
        datadic = {}
        datadic['MFP'] = {}
        datadic['DFL'] = {}
        z = np.array(core.NEAxialConfig.mycuts)
        datadic['midz'] = ((z[1:]+z[:-1])/2).tolist()
        dz = ((z[1:]-z[:-1]))/core.NEAxialConfig.splitz
        ih = -1
        for hexname in core.NEassemblytypes.values():
            ih = ih+1
            for iz in range(NZ):  # loop over cuts
                # check if L or MFP are minimum
                if DFLmin[ih, iz] > DFL.min():
                    DFLmin[ih, iz] = DFL.min()
    
            for iz in range(NZ):  # loop over cuts
                # check if L or MFP are minimum
                if dz[iz] > min(DFLmin[ih, iz], MFPmin[ih, iz]):
                    print('WARNING: axial zone at {} should be refined in {} SA'.format(datadic['midz'][iz], hexname))
            datadic['MFP'][hexname] = MFPmin[ih, :].tolist()
            datadic['DFL'][hexname] = DFLmin[ih, :].tolist()
    
        with open('diffdata.json', 'w') as outfile:
            json.dump(datadic, outfile, indent=8)



def writeConfig(core, NZ, Ntypes, NE_1D=False):
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
    if NE_1D:
        f = io.open('config.inp', 'w', newline='\n')
        regions = dict(zip(core.config[0].regions.keys(), range(len(core.config[0].regions))))
        for t in core.time:  # loop over time
            # loop over cut
            for iz, z in enumerate(range(NZ)):
                slab_now = core.config[t]
                f.write('%s ' % ff(t, 'double'))  # write time instant for each cut
                # write region number
                idr = regions[slab_now.regionmap[iz]]+1
                f.write('%s' % ' '.join(str(idr)))
                f.write('\n')
    else:
        types = np.zeros((core.NAss, ), dtype=int)
        NAssTypes = len(core.NEassemblytypes)
        compositions = np.reshape(np.arange(1, NZ*NAssTypes+1), (NAssTypes, NZ))
        f = io.open('config.inp', 'w', newline='\n')
        for t in core.NEtime:  # loop over time
            # loop over cut
            for iz, z in enumerate(range(NZ)):
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


def makeNEinput(core, whereMACINP=None, whereNH5INP=None, template=None, H5fmt=2):
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

    NE_1D = True if 'config' in core.__dict__.keys() else False
    if H5fmt is False:
        H5fmt = 1

    tmp = core.config[0].N.tolist() if NE_1D else core.NEAxialConfig.splitz
    NZ = core.config[0].nLayers if NE_1D else len(core.NEAxialConfig.mycuts)-1
    if isinstance(tmp, (int)):
        splitz = [tmp]*NZ 
    elif isinstance(tmp, (list)):
        splitz = tmp if len(tmp) > 1 else tmp[0]*NZ 
            
    nConfig = len(core.time) if NE_1D else len(core.NEtime)
    meshz = core.config[0].layers if NE_1D else core.NEAxialConfig.mycuts
    power = 1 if NE_1D else core.power
    if NE_1D:
        nRun = 2 if nConfig > 1 else 1
        ndim = 1
    else:
        nRun = 2 if core.trans is True else 1
        ndim = 3

    geomdata = {'$NH5INP': whereNH5INP, '$MACINP': whereMACINP, '$NELEZ0': NZ,
                '$MESHZ0': meshz, '$NDIM': ndim, '$SPLITZ': splitz, '$H5fmt': H5fmt,
                '$NCONFIG': nConfig, '$NRUN': nRun, '$POW': power,
                '$NPROF': len(core.TimeSnap), '$TPROF': core.TimeSnap}

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
                    try:
                        val = [str(v) for v in val]
                    except TypeError as err:
                        if "'int' object is not iterable" in str(err):
                            val = str(val)
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
    f.close()


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
    scattmat = [*['infS%d' % d for d in range(8)],
                *['infSp%d' % d for d in range(8)]]

    # homogenise in each group
    N = NG*NG if what in scattmat else NG
    homdata = np.zeros((len(fineincoarse), N))

    for g in range(NG):  # loop over energy groups
        idx = 0
        for izf in range(len(fineincoarse)):  # loop over axial cuts
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
                elif 'Kappa' in what:
                    data[i] = file.getUniv(u, 0, 0, 0).infExp[what][g]*file.getUniv(u, 0, 0, 0).infExp['infFiss'][g]
                else:
                    data[i] = file.getUniv(u, 0, 0, 0).infExp[what][g]

            # axially homogenise required data
            if what in scattmat:
                tmp = np.zeros((NG, ))
                for gg in range(NG):
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
        ans = "y"
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
