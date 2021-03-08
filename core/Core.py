"""
Author: N. Abrate.

File: core.py

Description: Class to define the nuclear reactor core geometry defined in an
external text file.
"""
import re
import sys
import numpy as np

from copy import deepcopy
from collections import OrderedDict

from coreutils.utils import parse
from coreutils.core.Map import Map
from coreutils.core.UnfoldCore import UnfoldCore
from coreutils.core.MaterialData import NEMaterialData, CZMaterialData
from coreutils.core.Assembly import AssemblyGeometry, AxialConfig, AxialCuts


class Core:
    """
    Define NE, TH and CZ core configurations.

    Attributes
    ----------
    AssemblyGeom : obj
        Object with assembly geometrical features.
    NEregionslegendplot : dict
        Dictionary with regions names and strings for plot labelling.
    NEassemblytypes : dict
        Ordered dictionary with names of assembly NE types.
    THassemblytypes : dict
        Ordered dictionary with names of assembly TH types.
    CZassemblytypes : dict
        Ordered dictionary with names of assembly CZ types.
    Map : obj
        Object mapping the core assemblies with the different numerations.
    NEAxialConfig : obj
        Axial regions defined for NE purposes.
    NEMaterialData : obj
        NE data (multi-group constants) for each region defined in input.
    CZMaterialData : obj
        NE data (multi-group constants) for each region defined in input.
    NEconfig : dict
        Neutronics configurations according to time.
    NEtime : list
        Neutronics time instants when configuration changes.
    CZconfig : dict
        Cooling zones configurations according to time.
    CZtime : list
        Cooling zones time instants when configuration changes.

    Methods
    -------
    getassemblytype :
        Get type of a certain assembly.
    replace :
        Replace assemblies with user-defined new or existing type.
    perturb :
        Replace assemblies with user-defined new or existing type.
    translate :
        Replace assemblies with user-defined new or existing type.
    perturbBC :
        Spatially perturb cooling zone boundary conditions.
    writecentermap :
        Write assembly number and x and y coordinates of centers to text file.
    getassemblylist :
        Return assemblies belonging to a certain type.
    writecorelattice :
        Write core lattice to txt file.
    """

    def __init__(self, inpjson):

        isNE, isTH = False, False
        # -- parse input file
        if ".json" in inpjson:

            CIargs, NEargs, THargs = parse(inpjson)

            tEnd, nProf, pitch, shape, power, trans = CIargs

            # check if NEargs is not empty
            if NEargs is not None:
                [NEinp, NErotation, NEassemblynames,
                 NEassemblylabel, NEreplace, cuts, splitz, config, NEfren,
                 NEregionslegendplot, NEdata] = NEargs
                isNE = True

            # check if THargs is not empty
            if THargs is not None:
                # pitch and shape may be overwritten but they are equal
                [CZinp, THrotation, CZassemblynames,
                 CZreplace, THfren, bcs, mflow, temperatures, pressures,
                 THdata] = THargs
                isTH = True

        else:
            raise OSError("Input file must be in .json format!")

        if isNE is False:
            print('NE input not available, writing TH input only!')
        if isTH is False:
            print('TH input not available, writing NE input only!')

        # initialise assembly radial geometry object
        self.AssemblyGeom = AssemblyGeometry(pitch, shape)  # module indep.

        # assign power, if any
        if power is not None:
            self.power = power
        # assign time information
        self.TimeEnd = tEnd
        self.trans = trans

        if isinstance(nProf, (float, int)):
            dt = tEnd/nProf
            self.TimeProf = np.arange(0, tEnd+dt, dt)
        elif isinstance(nProf, list) and len(nProf) > 1:
            self.TimeProf = nProf
        else:
            raise OSError('nProf in .json file must be list, float or int!')

        if isNE:
            # store legend plot
            self.NEregionslegendplot = NEregionslegendplot
            # sort list
            assnum = np.arange(1, len(NEassemblynames)+1)
            if cuts is not None:
                univ = []  # consider axial regions in "cuts"
            else:
                univ = deepcopy(NEassemblynames)  # regions are assembly names

            NEassemblynames = OrderedDict(dict(zip(NEassemblynames, assnum)))
            # define dict between strings and ints for assembly type
            self.NEassemblytypes = OrderedDict(dict(zip(assnum,
                                                        NEassemblynames)))

            if NEassemblylabel is not None:
                self.NEassemblylabel = OrderedDict(dict(zip(assnum,
                                                    NEassemblylabel)))
            else:
                self.NEassemblylabel = self.NEassemblytypes
            # define NE core with assembly types
            tmp = UnfoldCore(NEinp, NErotation, NEassemblynames)
            NEcore = tmp.coremap
            NEinp = tmp.inp
            # define input matrix for core mapping
            MAPcore = NEcore
            MAPinp = NEinp
            rotation = NErotation

        if isTH:

            # sort list
            assnum = np.arange(1, len(CZassemblynames)+1)

            CZassemblynames = OrderedDict(dict(zip(CZassemblynames, assnum)))
            # define dict between strings and ints for assembly type
            self.CZassemblytypes = OrderedDict(dict(zip(assnum,
                                                        CZassemblynames)))

            # define TH core with assembly types
            CZcore = UnfoldCore(CZinp, THrotation, CZassemblynames).coremap

            if THdata is not None:
                THassemblynames = THdata['assemblynames']
                assnum = np.arange(1, len(THassemblynames)+1)
                THassemblynames = OrderedDict(dict(zip(THassemblynames,
                                                       assnum)))
                # define dict between strings and ints for assembly type
                self.THassemblytypes = OrderedDict(dict(zip(assnum,
                                                        THassemblynames)))
                THinp = THdata['filename']
                tmp = UnfoldCore(THinp, THrotation, THassemblynames)
                THcore = tmp.coremap
                THinp = tmp.inp

                # define input matrix for core mapping
                # if already assigned, not an issue if shape is ok
                MAPcore = THcore
                MAPinp = THinp
                rotation = THrotation

            if THcore.shape != CZcore.shape:
                raise OSError("CZ and TH core dimensions mismatch!")

        # --- define core geometry and map
        if shape == 'H' and rotation != 60:
            raise OSError('Hexagonal core geometry requires one sextant, so' +
                          '"rotation" must be 60 degree!')

        if isNE and isTH:
            # dimensions consistency check
            if CZcore.shape != NEcore.shape:
                raise OSError("NE and TH core dimensions mismatch:" +
                              "%s vs. %s"
                              % (CZcore.shape, NEcore.shape))

            # non-zero elements location consistency check
            tmp1 = deepcopy(CZcore)
            tmp1[tmp1 != 0] = 1

            tmp2 = deepcopy(NEcore)
            tmp2[tmp2 != 0] = 1

            if THdata is not None:
                tmp3 = deepcopy(THcore)
                tmp3[tmp3 != 0] = 1

            if (tmp1 != tmp2).all():
                raise OSError("Assembly positions in CZ and NE mismatch. " +
                              "Check core input file!")

            if (tmp1 != tmp3).all():
                raise OSError("Assembly positions in CZ and TH mismatch. " +
                              "Check core input file!")

        # initialise core map object
        self.Map = Map(MAPcore, rotation, self.AssemblyGeom, inp=MAPinp)
        self.NAss = len((self.Map.serpcentermap))

        # --- define NE material and configurations
        if isNE:
            # --- Axial geometry
            if cuts is not None:
                # initial axial configuration
                self.NEAxialConfig = AxialConfig(cuts, splitz)
                for k in self.NEAxialConfig.cuts.keys():
                    univ.extend(self.NEAxialConfig.cuts[k].reg)
            # squeeze repetitions
            univ = list(set(univ))

            # -- Material data
            if NEdata is not None:

                try:
                    path = NEdata['path']
                except KeyError:
                    raise OSError('"path" missing in "NEdata"!')

                try:
                    files = NEdata['beginwith']
                except KeyError:
                    files = None

                self.NEMaterialData = NEMaterialData(path, univ, files=files)

            # user-defined assembly type insertion
            if isinstance(NEreplace, dict):
                # loop over assembly types
                for k, v in NEreplace.items():
                    NEcore = self.replace(NEassemblynames[k], v, NEfren,
                                          NEcore)

            else:
                if NEreplace is not None:
                    raise OSError("'replace' in NE must be of type dict!")

            # keep each core configuration in time
            self.NEconfig = {}
            self.NEconfig[0] = NEcore
            self.NEtime = [0]
            # check core configuration
            if config is not None:
                for time in config.keys():
                    if time != '0':
                        t = float(time)
                        # increment time list
                        self.NEtime.append(t)
                    else:
                        # set initial condition
                        t = 0

                    # check operation
                    if "translate" in config[time]:
                        self.translate(config[time]["translate"], time,
                                       isfren=NEfren)

                    if "perturb" in config[time]:
                        self.perturb(config[time]["perturb"], time,
                                     isfren=NEfren)

        # --- define TH core geometry and data
        if isTH:

            if THdata is not None and "replace" in THdata.keys():
                # loop over assembly types
                for k, v in THdata["replace"].items():
                    try:
                        THcore = self.replace(THassemblynames[k], v, THfren,
                                              THcore)
                    except KeyError:
                        raise OSError("%s not present in TH assembly types!"
                                      % k)
            # TH configuration
            self.THtime = [0]
            self.THconfig = {}
            self.THconfig[0] = THcore

            # CZ replace
            if isinstance(CZreplace, dict):
                # loop over assembly types
                for k, v in CZreplace.items():
                    try:
                        CZcore = self.replace(CZassemblynames[k], v, THfren,
                                              CZcore)
                    except KeyError:
                        raise OSError("%s not present in CZ assembly types!"
                                      % k)
            else:
                if CZreplace is not None:
                    raise OSError("'replace' in TH must be of type dict!")

            # assign material properties
            cz = CZMaterialData(mflow, pressures, temperatures,
                                self.CZassemblytypes.values())
            self.CZMaterialData = cz

            # keep each core configuration in time
            self.CZconfig = {}
            self.CZconfig[0] = CZcore
            self.CZtime = [0]
            # check if boundary conditions change in time
            if bcs is not None:
                for time in bcs.keys():
                    t = float(time)
                    # increment time list
                    self.CZtime.append(t)
                    self.perturbBC(bcs[time], time, isfren=THfren)

    def getassemblytype(self, assemblynumber, time=0, isfren=False,
                        whichconf="NEconfig"):
        """
        Get type of a certain assembly.

        Parameters
        ----------
        assemblynumber : int
            Number of the assembly of interest
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is False.

        Returns
        -------
        which : int
            Type of assembly.

        """
        if isfren is True:
            # translate FRENETIC numeration to Serpent
            index = self.Map.fren2serp[assemblynumber]-1  # -1 for py indexing
        else:
            index = assemblynumber-1  # -1 for py indexing
        # get coordinates associated to these assemblies
        rows, cols = np.unravel_index(index, self.Map.type.shape)

        if whichconf == "NEconfig":
            which = self.NEconfig[time][rows, cols]
        elif whichconf == "THconfig":
            which = self.THconfig[time][rows, cols]
        elif whichconf == "CZconfig":
            which = self.CZconfig[time][rows, cols]
        else:
            raise OSError("Unknown core config!")

        return which

    def replace(self, newtype, asslst, isfren=False, core=None):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        newtype : list
            List of new/existing types of assemblies.
        asslst : list
            List of assemblies to be replaced.
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        # check input type
        if isinstance(newtype, (int, np.int16, np.int32, np.int64)):
            # convert integer to list
            newtype = [newtype]

        if isinstance(asslst, int) is True:
            # convert list to list of lists
            asslst = [[asslst]]
        elif isinstance(asslst[0], list) is False:
            asslst = [asslst]

        # if user do not provide core, returns None
        if core is None:
            newcore = None
        else:
            newcore = core+0

        for ipos, ilst in enumerate(asslst):  # loop over lists
            # check map convention
            if isfren is True:
                # translate FRENETIC numeration to Serpent
                index = [self.Map.fren2serp[i]-1 for i in ilst]  # -1 for index
            else:
                index = [i-1 for i in ilst]  # -1 to match python indexing
            # get coordinates associated to these assemblies
            index = (list(set(index)))
            rows, cols = np.unravel_index(index, self.Map.type.shape)

            # load new assembly type
            if core is None:
                self.Map.type[rows, cols] = newtype[ipos]
            else:
                newcore[rows, cols] = newtype[ipos]

        return newcore

    def perturb(self, pertconfig, time, isfren=False):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        newtype : list
            List of new/existing types of assemblies.
        asslst : list
            List of assemblies to be replaced.
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        # check input type
        try:
            # check consistency between dz and which
            if len(pertconfig['which']) != len(pertconfig['what']):
                raise OSError('Groups of assemblies and number of ' +
                              'perturbations do not match in NE!')

            if len(pertconfig['with']) != len(pertconfig['what']):
                raise OSError('New regions and number of ' +
                              'perturbations do not match in NE!')

            pconf = zip(pertconfig['which'], pertconfig['with'],
                        pertconfig['what'])

            newcore = None
            if float(time) in self.NEconfig.keys():
                now = float(time)
            else:
                nt = self.NEtime.index(float(time))
                now = self.NEtime[nt-1]

            p = 0
            for which, withass, whatass in pconf:
                p = p + 1
                for assbly in which:
                    nt = self.NEtime.index(float(time))
                    atype = self.getassemblytype(assbly, now,
                                                 isfren=isfren,
                                                 whichconf="NEconfig")
                    what = self.NEassemblytypes[atype]
                    # take region name
                    basename = re.split(r"_t\d+.\d+_p\d+", what)[0]
                    newname = "%s_t%s_p%d" % (basename, time, p)
                    # define new cuts, if any
                    if newname not in self.NEAxialConfig.cuts.keys():
                        cuts = deepcopy(self.NEAxialConfig.cuts[what])
                        nass = len(self.NEassemblytypes.keys())
                        self.NEassemblytypes[nass + 1] = newname
                        if whatass in cuts.reg:
                            cuts.reg[cuts.reg == whatass] = withass
                            upz, loz, reg = cuts.upz, cuts.loz, cuts.reg
                            self.NEAxialConfig.cuts[newname] = AxialCuts(upz,
                                                                         loz,
                                                                         reg)

                        else:
                            raise OSError('%s not in assembly %d at time %ss'
                                          % (whatass, assbly, time))

                    # replace assembly
                    if newcore is None:
                        # take previous time-step configuration
                        newcore = self.replace(nass+1, assbly, isfren,
                                               self.NEconfig[now])
                    else:
                        # take "newcore"
                        newcore = self.replace(nass+1, assbly, isfren,
                                               newcore)

            self.NEconfig[float(time)] = newcore

        except KeyError:
            raise OSError('"which" and/or "dz" keys missing in "translate"!')

    def translate(self, transconfig, time, isfren=False):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        transconfig : dict
            Dictionary with details on translation transformation
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        # check input type
        try:
            # check consistency between dz and which
            if len(transconfig['which']) != len(transconfig['dz']):
                raise OSError('Groups of assemblies and number of ' +
                              'translations do not match!')

            newcore = None
            if float(time) in self.NEconfig.keys():
                now = float(time)
            else:
                nt = self.NEtime.index(float(time))
                now = self.NEtime[nt-1]

            for dz, which in zip(transconfig['dz'], transconfig['which']):
                # repeat configuration if dz = 0
                if dz != 0:
                    for assbly in which:
                        atype = self.getassemblytype(assbly, isfren=isfren,
                                                     time=now,
                                                     whichconf="NEconfig")
                        what = self.NEassemblytypes[atype]
                        newname = "%st%sz%d" % (what, time, dz)
                        # define new cuts, if any
                        if newname not in self.NEAxialConfig.cuts.keys():
                            cuts = deepcopy(self.NEAxialConfig.cuts[what])
                            cuts.upz[0:-1] = [z+dz for z in cuts.upz[0:-1]]
                            cuts.loz[1:] = [z+dz for z in cuts.loz[1:]]
                            nass = len(self.NEassemblytypes.keys())
                            self.NEassemblytypes[nass + 1] = newname
                            upz, loz, reg = cuts.upz, cuts.loz, cuts.reg
                            self.NEAxialConfig.cuts[newname] = AxialCuts(upz, loz,
                                                                         reg)

                        # replace assembly
                        if newcore is None:
                            # take previous time-step configuration
                            newcore = self.replace(nass+1, assbly,
                                                   isfren=isfren,
                                                   core=self.NEconfig[now])
                        else:
                            # take "newcore"
                            newcore = self.replace(nass+1, assbly, isfren,
                                                   newcore)

                else:
                    newcore = self.NEconfig[now]

            self.NEconfig[float(time)] = newcore

        except KeyError:
            raise OSError('"which" and/or "dz" keys missing in "translate"!')

    def perturbBC(self, pertconfig, time, isfren=False):
        """
        Spatially perturb cooling zone boundary conditions.

        Parameters
        ----------
        newtype : list
            List of new/existing types of assemblies.
        asslst : list
            List of assemblies to be replaced.
        isfren : bool, optional
            Flag for FRENETIC numeration. The default is ``False``.

        Returns
        -------
        ``None``

        """
        # check input type
        try:
            # check consistency between dz and which
            if len(pertconfig['which']) != len(pertconfig['what']):
                raise OSError('Groups of assemblies and perturbations do' +
                              'not match in TH "boundaryconditions"!')

            if len(pertconfig['with']) != len(pertconfig['what']):
                raise OSError('Each new value in TH "boundaryconditions"' +
                              ' must come with its identifying parameter!')

            pconf = zip(pertconfig['which'], pertconfig['with'],
                        pertconfig['what'])

            newcore = None
            if float(time) in self.CZconfig.keys():
                now = float(time)
            else:
                nt = self.CZtime.index(float(time))
                now = self.CZtime[nt-1]

            p = 0
            for which, withpar, whatpar in pconf:
                p = p + 1
                for assbly in which:
                    nt = self.CZtime.index(float(time))
                    atype = self.getassemblytype(assbly, now,
                                                 isfren=isfren,
                                                 whichconf="CZconfig")
                    what = self.CZassemblytypes[atype]
                    basename = re.split(r"_t\d+.\d+_p\d+", what)[0]
                    newname = "%s_t%s_p%d" % (basename, time, p)

                    # take region name
                    if newname not in self.CZassemblytypes.values():
                        nass = len(self.CZassemblytypes.keys())
                        self.CZassemblytypes[nass + 1] = newname
                        # update values inside parameters
                        self.CZMaterialData.__dict__[whatpar][newname] = withpar

                    # replace assembly
                    if newcore is None:
                        # take previous time-step configuration
                        newcore = self.replace(nass+1, assbly, isfren,
                                               self.CZconfig[now])
                    else:
                        # take "newcore"
                        newcore = self.replace(nass+1, assbly, isfren,
                                               newcore)
            # update cooling zones
            self.CZconfig[float(time)] = newcore

        except KeyError:
            raise OSError('"which" and/or "with" and/or "what" keys missing' +
                          ' in "boundaryconditions" in TH!')

    def writecentermap(self, numbers=True, fname="centermap.txt"):
        """
        Write centermap to text file.

        Parameters
        ----------
        numbers : bool, optional
            Write assembly numbers in the first columns. The default is
            ``True``. If ``False``, the assembly type are written instead.
        fname : str, optional
            Centermap file name. The default is "centermap.txt".

        Returns
        -------
        ``None``

        """
        # define regions
        typelabel = np.reshape(self.Map.type, (self.Map.Nx*self.Map.Ny, 1))
        regions = []
        for key, coord in (self.Map.serpcentermap).items():
            x, y = coord
            if numbers is False:
                key = typelabel[key-1, 0]
            regions.append((key, x, y))

        # write region to external file
        with open(fname, 'w') as f:  # open new file
            f.write("\n".join("{:03d} {:5f} {:5f}".format(elem[0], elem[1],
                                                          elem[2])
                              for elem in regions))
            f.write("\n")

    def getassemblylist(self, atype, time=0, match=True, isfren=False,
                        whichconf="NEconfig"):
        """
        Return assemblies belonging to a certain type.

        Parameters
        ----------
        atype : int
            Desired assembly type.
        match : bool, optional
            If ``True``, it takes the assemblies matching with atype. If
            ``False``, it takes the all others. The default is ``True``.

        Returns
        -------
        matchedass : list
            List of matching/non-matching assemblies.

        """
        if whichconf == "NEconfig":
            asstypes = self.NEconfig[time].flatten(order='C')
        elif whichconf == "THconfig":
            asstypes = self.THconfig[time].flatten(order='C')
        elif whichconf == "CZconfig":
            asstypes = self.CZconfig[time].flatten(order='C')
        else:
            raise OSError("Unknown core config!")

        if match is True:
            matchedass = np.where(asstypes == atype)[0]+1  # +1 for py indexing
        else:
            matchedass = np.where(asstypes != atype)[0]+1

        if isfren is True:
            matchedass = [self.Map.serp2fren[m] for m in matchedass]

        matchedass.sort()

        return matchedass
    # TODO: add writeregionmap method to plot region id, x and y for each assembly

    def writecorelattice(self, flatten=False, fname="corelattice.txt",
                         serpheader=False, string=True, whichconf="NEconfig",
                         numbers=False, fren=True):
        """
        Write core lattice to txt file.

        Parameters
        ----------
        flatten : bool, optional
            Flag to print matrix or flattened array. The default is ``False``.
        fname : str, optional
            File name. The default is "corelattice.txt".
        serpheader : bool, optional
            Serpent 2 code instructions for core lattice geometry
            header. The default is ``False``.
        numbers : bool, optional
            Print assembly numbers instead of assembly names in the core 
            lattice.

        Returns
        -------
        ``None``

        """
        Nx, Ny = self.Map.Nx, self.Map.Ny
        if whichconf == "NEconfig":
            asstypes = self.NEconfig[0]
            assemblynames = self.NEassemblytypes
        elif whichconf == "THconfig":
            asstypes = self.THconfig[0]
            assemblynames = self.THassemblytypes
        elif whichconf == "CZconfig":
            asstypes = self.CZconfig[0]
            assemblynames = self.CZassemblytypes
        else:
            raise OSError("Unknown core config!")

        if numbers is True:
            # flatten typelabel matrix
            typemap = np.reshape(asstypes, (Nx*Ny, 1))
            if fren is True:
                for s, f in self.Map.serp2fren.items():
                    typemap[s-1] = s
            else:
                for s in self.Map.serp2fren.keys():
                    typemap[s-1] = s
            asstypes = np.reshape(typemap, (Nx, Ny), order='F')

        # define regions
        if flatten is False:
            typelabel = asstypes
        else:
            typelabel = np.reshape(asstypes, (Nx*Ny, 1))

        # determine file format
        if string is False:
            # determine number of digits
            nd = str(len(str(self.Map.type.max())))
            fmt = "%0"+nd+"d"
        else:
            fmt = "%s"
            typelabel = typelabel.astype(str)
            for key, val in assemblynames.items():
                typelabel[typelabel == str(key)] = val

            typelabel[typelabel == '0'] = 'VV'

        # determine header
        if serpheader is False:
            header = ""
            comm = '#'
        else:  # Serpent-2 style header (define core lattice)
            # define assembly type according to Serpent
            if self.AssemblyGeom.type == 'S':
                asstype = '1'  # square
            elif self.AssemblyGeom.type == 'H':
                asstype = '3'  # hexagon
            # define central assembly coordinates
            x0, y0 = self.Map.serpcentermap[self.Map.fren2serp[1]]
            x0, y0 = str(x0), str(y0)
            # define number of assemblies along x and y directions
            Nx, Ny = str(Nx), str(Ny)
            # define assembly pitch
            P = str(2*self.AssemblyGeom.apothema)
            header = " ".join(("lat core ", asstype, x0, y0, Nx, Ny, P))
            comm = ''
        # save array to file
        np.savetxt(fname, typelabel, delimiter=" ", fmt=fmt, header=header,
                   comments=comm)


if __name__ == "__main__":

    # make input
    # FIXME: args in piu, rendi consistente con codice
    # TODO fare main a parte magari, in modo che venga costruito l'input FR/FF
    [geinp, rotation, pitch, assemblynames, replace, cuts, config,
     fren, fill] = parse(sys.argv)
    core = Core(geinp, rotation, pitch, assemblynames, replace=replace,
                cuts=cuts, config=config, fren=fren, fill=fill)
    # post-process
