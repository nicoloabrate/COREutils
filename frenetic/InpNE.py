"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""

import os
from shutil import rmtree
from os.path import isfile, join
import numpy as np
import serpentTools as st
import h5py as h5

# TODO: definire una sequenza automatica che generi i file di input (e.g. InpGen)
# TODO: implementare gestione proprieta' fotoni (con GFN e DV)
# TODO: quale coppia di temperature considero per i param. cinetici?


def writemacro(nmix, ngro, nprec, fname, Tf, Tc, unifuel=None,
               datapath=None, unidictkeys=None):
    """
    Write the input file "macro.nml" for the NE module of FRENETIC.

    Parameters
    ----------
    datapath: string
        path of the directory with the files
    Returns
    -------
    """
    # --- define list of output filenames
    macronames = ["DIFFCOEF", "XSTOT", "XS_SCATT", "XS_FISS", "NUSF", "EFISS"]
    inpnames = ["filediff", "sigt", "sigs", "sigf", "nusigf", "esigf"]

    # read Serpent output
    res = st.read(fname)  # read results from Serpent

    # store all universe keys
    if unidictkeys is None:

        unidictkeys = set()
        for key in sorted(res.universes):
            unidictkeys.add(key[0])

            if unifuel is None:
                if 'fuel'.lower() in key.lower():  # check also FUEL
                    unifuel = key

    if nmix != len(unidictkeys):
        raise OSError("Input number of regions does not match with" +
                      "universes in Serpent file!")

    # -- write macro.nml file
    fname = "macro.nml"
    if datapath is not None:
        fname = os.path.join(datapath, fname)

    with open(fname, 'w') as f:
        f.write('&MACROXS0\n')
        f.write('NMAT = %d \n' % nmix)
        f.write('NGRO = %d \n' % ngro)
        f.write('NPRE = %d \n' % nprec)
        f.write('NDHP = %d \n' % 1)
        f.write('NGRP = %d \n' % 0)
        f.write('NPRP = %d \n' % 0)
        f.write('/ \n \n')
        f.write('&MACROXS0\n')
        f.write('IRHO = 0,\n')
        f.write('VELOC0(1:%d) = ' % ngro)

        if unifuel is not None:
            vel = 1/res.getUniv(unifuel, 0).infExp['infInvv']

        else:
            raise OSError("Fuel region missing in universe list!")

        for igro in range(0, ngro):
            f.write('%1.6e, ' % vel(igro+1))

        f.write('\n LAMBDA0(1:%d) = ' % nprec)
        lambda0 = res.resdata['fwdAnaLambda']

        for iprec in range(0, nprec):
            f.write('%1.6e, ' % lambda0(iprec+1))

        f.write(' \nlambdadhp0(1:1) = 1.000000e+00,\n')
        f.write('betadhp0(1:1) = 1.000000e+00,\n')
        f.write('IDIFF(1:%d) = %d*2,\n' % (nmix, nmix))
        f.write('ISIGT(1:%d) = %d*2,\n' % (nmix, nmix))
        f.write('ISIGF(1:%d) = %d*2,\n' % (nmix, nmix))
        f.write('TEMPFUEL0 =	 %1.6e,\n' % Tf)
        f.write('TEMPCOOL0 =	 %1.6e,\n' % Tc)
        f.write('ISIGS(1:%d) = %d*2,\n\n' % (nmix, nmix))

        for imix in range(0, nmix):

            # write universe number and name
            f.write('!Universe %d:(%s)\n' % (imix, unidictkeys[imix]))

            # write kinetic and spectrum parameters
            beta0 = res.resdata['fwdAnaBetaZero']
            chid0 = res.getUniv(unidictkeys[imix], 0).infExp['infChit']
            chit0 = res.getUniv(unidictkeys[imix], 0).infExp['infChit']

            f.write('CHIT0(%d, 1:%d) = ' % (imix, ngro))
            for igro in range(0, ngro):
                f.write('%1.6e, ' % chit0(igro))

            for igro in range(0, ngro):
                f.write('\n CHID0(%d, %d, 1:%d) = %d*%1.6e' % (imix, igro,
                                                               nprec, nprec,
                                                               chid0(igro)))

            f.write('BETA0(%d, 1:%d) = ' % (imix, nprec))
            for iprec in range(0, nprec):
                f.write('%1.6e' % (beta0(iprec)))

            # write macroscopic NE multi-group data
            for inp, macro in (inpnames, macronames):

                if macro == "XS_SCATT":

                    for igrostart in range(0, ngro):
                        f.write('%s(%d, %d, 1:%d) =' % (inp, imix,
                                                        igrostart, ngro))
                        for igroend in range(0, ngro):
                            f.write(' ''NEinputdata/%s_%d_%d_%d.txt'', '
                                    % (macro, imix, igrostart, igroend))

                        f.write('/n')

                else:

                    f.write('%s(%d, 1:%d) =' % (inp, imix, ngro))
                    for igro in range(0, ngro):
                        f.write(' ''NEinputdata/%s_%d_%d.txt'', ' % (macro, imix, igro))

                    f.write('/n')

        f.write('/n')


def writeNEdata(datapath, steady=False, verbose=False, inf=True, unidict=None,
                asciifmt=False, files=None):
    """
    Generate FRENETIC NE module input HDF5 file.

    Parameters
    ----------
    datapath: string
        path of the directory with the files
    Returns
    -------
    """
    fname, Tc, Tf = parsetemp(datapath, files)   # call method to read useful lists

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

    if steady is False:
        infkin_keys = ['infChit', 'infChip', 'infChid', 'infInvv']
        b1kin_keys = ['b1Chit', 'b1Chip', 'b1Chid', 'b1Invv']
        kin_out = ["CHIT", "CHIP", "CHID", "INVVEL"]

    # -- create or overwrite hdf5 file (repro script)
    h5name = "NE_inp.hdf5"
    fh5 = __wopen(h5name)
    # if unidict not provided, I/O with user required
    flagIO = 0
    if unidict is None:
        flagIO = 1
        unidictkeys = []

    # --- store _res files in temperature-wise dict
    resdict = {}  # define dict to store output
    NU = []  # define list of universe number in each file
    grid = []  # define list of group number in each file
    for idx, f in enumerate(fname):  # loop over Serpent files
        print(idx)
        # define current filename
        suffT = "_".join(["Tf", str(Tf[idx]), "Tc", str(Tc[idx])])
        name = "_".join([f, suffT, "res.m"])  # concatenate name,temp and suff
        fnameT = os.path.join(datapath, name)  # concatenate filename and path

        # try to parse Serpent output with serpentTools
        try:
            res = st.read(fnameT)  # read results from Serpent
            # maybe Tf and Tc swapped

        except OSError():
            suffT2 = "_".join(["Tc", str(Tc[idx]), "Tf", str(Tf[idx])])
            name = "_".join([f, suffT2, "res.m"])  # join name,temp and suff
            fnameT = os.path.join(datapath, name)  # join filename and path

            try:
                res = st.read(fnameT)

            except OSError():
                print("File does not exist!")

        # store in temp dict lists of ResObject
        if (Tf[idx], Tc[idx]) in resdict:
            resdict[(Tf[idx], Tc[idx])].append(res)  # append in list
        else:
            resdict[(Tf[idx], Tc[idx])] = []  # initialise as list
            resdict[(Tf[idx], Tc[idx])].append(res)  # append in list

        # store all universe keys for later print to the user
        unidictkeys = set()
        if flagIO == 1:
            for key in sorted(res.universes):
                unidictkeys.add(key[0])

        # store number of groups and universes
        uni = (sorted(res.universes)[0]).universe  # get first universe
        data = res.getUniv(uni, 0)
        grid.append(tuple(data.groups))  # list to remove duplicates later
        NU.append(len(res.universes))

    # --- check energy grid consistency
    grid = list(set(grid))
    if len(grid) > 1:
        raise OSError("Check MACRO_E in Serpent! Energy grid not the same")

    NG = len(grid[0])-1  # define number of groups

    # --- ask for user input to define unidict
    if flagIO == 1:
        print("Please enter the id numbers for the following Serpent" +
              " universes:", list(unidictkeys))
        unidictval = []
        for i in range(0, len(unidictkeys)):
            elem = int(input())
            unidictval.append(elem)  # adding the element
        unidict = dict(zip(unidictkeys, unidictval))
    # print dict to the user
    print(unidict)

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

    if asciifmt is True:
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
    TfTc = list(zip(Tf, Tc))
    TfTc.sort(key=lambda t: t[0])
    # delete repetitions from fname list
    fname = list(dict.fromkeys(fname))

    # file loop
    for ifile in range(0, len(fname)):
        # data loop
        for idx, out in enumerate(outnames):
            # universe loop
            for iUni in range(0, NU[ifile]):
                # group loop
                for iGro in range(0, NG):

                    # temperature loop (fill temperature matrix)
                    for itup, tup in enumerate(TfTc):
                        # select file
                        res = resdict[tup][ifile]
                        # take universe
                        uni = sorted(res.universes)[iUni]

                        if uni[0] not in unidict.keys():
                            continue

                        uniname, burnup, step, days = uni
                        unitup = (uniname, burnup, step, days)

                        if itup == len(TfTc)-1:
                            # define filename
                            imix = unidict[uni[0]]
                            # FIXME: save only selected universes
                            txtname = "_".join([out, str(imix), str(iGro+1)])

                        # store value in proper position in temp matrix
                        row = np.where(frendata[:, 0] == tup[0])
                        col = np.where(frendata[1, :] == tup[1])

                        # select inf or b1 results
                        if inf is True:
                            val = res.getUniv(*unitup).infExp[infkeys[idx]]
                            # scattering has double group index
                            if infkeys[idx].startswith('infS'):
                                # departure group
                                for iGroDep in range(0, NG):

                                    # edit name to include info on dep group
                                    txtname2 = "_".join([txtname,
                                                         str(iGroDep+1)])
                                    frendata[row, col] = val[iGroDep+(iGro+1)
                                                             * (iGro > 0)]

                                    # write data if all T tuples spanned
                                    if itup == len(TfTc)-1:
                                        # write output
                                        if asciifmt is True:
                                            # write txt file
                                            mysavetxt(txtname2, frendata)

                                        # save in h5 file
                                        fh5.create_dataset(txtname2,
                                                           data=np.array(
                                                               frendata,
                                                               dtype=np.float))

                            else:
                                frendata[row, col] = val[iGro]
                                # write data if all T tuples have been spanned
                                if itup == len(TfTc)-1:
                                    # write output
                                    if asciifmt is True:
                                        # write txt file
                                        mysavetxt(txtname, frendata)

                                    # save in h5 file
                                    fh5.create_dataset(txtname,
                                                       data=np.array(
                                                           frendata,
                                                           dtype=np.float))

                        else:  # if inf is False
                            val = res.getUniv(*unitup).b1Exp[b1keys[idx]]
                            if b1keys[idx].startswith('b1S'):
                                # departure group
                                for iGroDep in range(0, NG):
                                    # edit name to include info on dep group
                                    txtname2 = "_".join([txtname,
                                                         str(iGroDep+1)])
                                    frendata[row, col] = val[iGroDep+(iGro+1)
                                                             * (iGro > 0)]

                                    # write data if all T tuples spanned
                                    if itup == len(TfTc)-1:
                                        # write output
                                        if asciifmt is True:
                                            # write txt file
                                            mysavetxt(txtname2, frendata)

                                        # save in h5 file
                                        fh5.create_dataset(txtname2,
                                                           data=np.array(
                                                               frendata,
                                                               dtype=np.float))

                            else:  # no scattering data
                                frendata[row, col] = val[iGro]
                                # write data if all T tuples have been spanned
                                if itup == len(TfTc)-1:
                                    # write output
                                    if asciifmt is True:
                                        # write txt file
                                        mysavetxt(txtname, frendata)

                                    # save in h5 file
                                    fh5.create_dataset(txtname,
                                                       data=np.array(
                                                            frendata,
                                                            dtype=np.float))


def mysavetxt(fname, x, fmt="%.6e", delimiter=' '):
    """Write file in txt format."""
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
