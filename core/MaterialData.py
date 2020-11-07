"""
Author: N. Abrate.

File: MaterialData.py

Description: Class that define core material (NE/TH/PH) data.
"""
import os
import warnings
import coreutils
import serpentTools as st

from os.path import join


class NEMaterialData:
    """
    Assign material data NE to reactor core.

    Attributes
    ----------
    data : dict
        Dictionary storing objects with macro-group constants parsed by
        serpentTools.
    temp : list
        List with tuples (Tf, Tc).

    Methods
    -------
    ``None``
    """

    def __init__(self, datapath, univ, files=None):
        """
        Initialise object.

        Parameters
        ----------
        datapath: str
            path where files are stored.
        univ : list
            List with universes used in calculations. The universes names must
            match the universes defined in Serpent 2 calculations.
        files: list, optional.
            List with file beginning (e.g. "ALFRED-FC" for file
            "ALFRED-FC_Tf_1400_Tc_673_res.m"). Default is ``None``.

        Returns
        -------
        ``None``
        """
        data, tempcouples = NEMaterialData.__parseNEdata(datapath, univ,
                                                         files=files)
        self.data = data
        self.temp = tempcouples

    def __parsetemp(path, files=None):
        """
        Generate lists with fuel, coolant temperatures and file names.

        Parameters
        ----------
        path: str
            path of the directory with the files
        files: list, optional.
            List with file beginning (e.g. "ALFRED-FC" for file
            "ALFRED-FC_Tf_1400_Tc_673_res.m"). Default is ``None``.

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
        deletefiles = []
        for f in resfiles:
            basename = (f.split("_res.m")[0]).split("_")  # consider only name
            fnameapp(basename[0])  # store filename in a list

            # find pos to handle both Tc_Tf and Tf_Tc
            try:
                posTc, posTf = basename.index("Tc"), basename.index("Tf")
                # temperatures sanity check
                T1, T2 = int(basename[posTc+1]), int(basename[posTf+1])
                if T1 > T2:
                    raise OSError("The fuel is cooler than coolant! Check %s"
                                  % f)
                # append temperatures
                Tcapp(T1)
                Tfapp(T2)

            except ValueError:
                deletefiles.append(basename[0])
                warnings.warn("Ignoring %s file since no T is specified!"
                              % f)
                pass

        if deletefiles != []:
            for f in deletefiles:
                fname.remove(f)

        # return lists
        return fname, Tc, Tf

    def __parseNEdata(datapath, univ, files=None):
        """
        Generate FRENETIC NE module input HDF5 file.

        Parameters
        ----------
        datapath: string
            path of the directory with the files
        Returns
        -------
        """
        # manipulate datapath for examples
        if "/" in datapath and os.name == 'nt':
            datapath = datapath.split("/")
            if "." in datapath:
                idx = datapath.index(".")
                modulepath = os.path.abspath(coreutils.__file__)
                datapath[idx] = modulepath.split("__init__.py")[0]
            datapath = join(*datapath)

        fname, Tc, Tf = NEMaterialData.__parsetemp(datapath, files)

        # -- serpentTools settings
        st.settings.rc['microxs.getFlx'] = False
        st.settings.rc['microxs.getXS'] = False

        # --- store _res files in temperature-wise dict
        resdict = {}  # dict to store output
        unidict = {}  # dict to check universes
        templst = []  # list of temperature couples
        for idx, f in enumerate(fname):  # loop over Serpent files
            # define current filename
            suffT = "_".join(["Tf", str(Tf[idx]), "Tc", str(Tc[idx])])
            # concatenate name,temp and suff
            name = "_".join([f, suffT, "res.m"])
            # concatenate filename and path
            fnameT = os.path.join(datapath, name)

            # try to parse Serpent output with serpentTools
            try:
                res = st.read(fnameT)  # read results from Serpent

                # maybe Tf and Tc swapped

            except OSError():
                suffT2 = "_".join(["Tc", str(Tc[idx]), "Tf", str(Tf[idx])])
                # join name,temp and suff
                name = "_".join([f, suffT2, "res.m"])
                # join filename and path
                fnameT = os.path.join(datapath, name)

                try:
                    res = st.read(fnameT)

                except OSError():
                    print("File does not exist!")

            # sanity check on number of groups
            if idx == 0:
                for k in res.universes.keys():
                    ngro = res.universes[k]._numGroups
                    break  # check only on 1st universe
            else:
                for k in res.universes.keys():
                    if ngro != res.universes[k]._numGroups:
                        raise OSError("Number of energy groups mismatch in %s!"
                                      % f)
                    break  # check only on 1st universe

            # store in temp dict lists of ResObject
            if (Tf[idx], Tc[idx]) in resdict:
                resdict[(Tf[idx], Tc[idx])].append(res)  # append in list
                for k in res.universes:
                    unidict[(Tf[idx], Tc[idx])].append(k[0])

            else:
                templst.append((Tf[idx], Tc[idx]))
                resdict[(Tf[idx], Tc[idx])] = []  # initialise as list
                resdict[(Tf[idx], Tc[idx])].append(res)  # append in list
                unidict[(Tf[idx], Tc[idx])] = []
                for k in res.universes:
                    unidict[(Tf[idx], Tc[idx])].append(k[0])

        # check all T couples contain the same number of universes
        for idx, tmpcouple in enumerate(unidict.keys()):
            if idx == 0:
                NP = len(unidict[tmpcouple])

            if len(unidict[tmpcouple]) != NP:
                raise OSError("Universe numbers mismatch. " +
                              "Check files with Tf,Tc = (%d,%d)!" % tmpcouple)

        # check if all user-defined universes are in Serpent files for each T
        for u in univ:
            # loop over temperature couples
            for tmpcouple in unidict.keys():
                if u not in unidict[tmpcouple]:
                    raise OSError('%s not in Serpent universes. ' % u +
                                  'Check "assemblynames" and "cuts" entries' +
                                  ' in .json input file!')

        return resdict, templst


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
