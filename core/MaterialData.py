"""
Author: N. Abrate.

File: core.py

Description: Class to define the nuclear reactor core geometry defined in an
external text file.
"""
import os
from os.path import isfile, join
import numpy as np
import serpentTools as st


class MaterialData:
    """


    Attributes
    ----------

    Methods
    -------

    """

    def __init__(self, geinp, rotangle, pitch, regionsdict,
                 insertassemblies=None, cuts=None, fren=False, fill=None):
        a=1

    def __parsetemp(path, files=None):
        """
        Generates three lists with temperatures and file names.

        Parameters
        ----------
        datapath: string
            path of the directory with the files

        Returns
        -------
        filename: list
            all the file names
        Tc: list
            coolant temperatures
        Tf: list
            fuel temperatures
        """
        # parse "_res.m" files
        ext = '_res.m'
        resfiles = [f for f in os.listdir(path) if join(path, f).endswith(ext)]
        # select files, if any
        if files is not None:
            if isinstance(files, str):
                files = [files]

            tmp = resfiles
            resfiles = []

            for f in files:
                for nf, f2 in enumerate(tmp):
                    if f in tmp[nf]:
                        resfiles.append(tmp[nf])

                if resfiles == []:
                    raise OSError('File starting with %s does not exist!' % f)

        # get temperatures
        Tc, Tf, fname = [], [], []
        Tcapp, Tfapp, fnameapp = Tc.append, Tf.append, fname.append
        for f in resfiles:
            basename = (f.split("_res.m")[0]).split("_")  # consider only name
            fnameapp(basename[0])  # store filename in a list
            # find pos to handle both Tc_Tf and Tf_Tc

            # FIXME: ignore .m files with no temperature
            posTc, posTf = basename.index("Tc"), basename.index("Tf")
            # append temperatures
            Tcapp(int(basename[posTc+1]))
            Tfapp(int(basename[posTf+1]))
        # return lists
        return fname, Tc, Tf


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