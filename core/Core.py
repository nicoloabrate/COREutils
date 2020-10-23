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
from coreutils.core.MaterialData import MaterialData
from coreutils.core.Assembly import AssemblyGeometry, AxialConfig, AxialCuts


class Core:
    """


    Attributes
    ----------

    Methods
    -------

    """

    def __init__(self, geinp, rotation=None, pitch=None, assemblynames=None,
                 replace=None, cuts=None, config=None, fren=False, fill=None):

        if ".json" in geinp:
            [geinp, rotation, pitch, assemblynames, replace, cuts, config,
             fren, fill, regionslegendplot] = parse(geinp)

        if None in [rotation, pitch, assemblynames]:
            raise OSError("Input args must be a .json path or " +
                          "(geinp, rotation=rotation, pitch=pitch, " +
                          "assemblynames=assemblynames)")

        if rotation == 60:
            shape = 'H'
        else:
            shape = 'S'

        # store legend plot
        self.regionslegendplot = regionslegendplot
        # sort list
        assnum = np.arange(1, len(assemblynames)+1)
        assemblynames = OrderedDict(dict(zip(assemblynames, assnum)))
        # define dict between strings and ints for assembly type
        self.assemblytypes = OrderedDict(dict(zip(assnum, assemblynames)))
        # initialise assembly radial geometry object
        self.AssemblyGeom = AssemblyGeometry(pitch, shape)
        # initialise core map object
        self.Map = Map(geinp, rotation, self.AssemblyGeom, assemblynames)

        # initialise assembly axial geometry object
        if cuts is not None:
            # initial axial configuration
            self.AxialConfig = AxialConfig(cuts)

        # initialise material data object
        if fill is not None:
            self.MaterialData = MaterialData()

        # user-defined assembly type insertion
        if isinstance(replace, dict):
            # loop over assembly types
            for k in replace.keys():
                self.replace(assemblynames[k], replace[k], fren)

        else:
            if replace is not None:
                raise OSError("'replace' must be of type dict!")

        # keep each core configuration in time
        self.Config = {}
        self.Config[0] = deepcopy(self.Map.type)
        self.time = [0]
        # check core configuration
        if config is not None:
            for time in config.keys():
                t = float(time)
                # increment time list
                self.time.append(t)

                # check operation
                if "translate" in config[time]:
                    self.translate(config[time]["translate"], time,
                                   flagfren=fren)

                if "perturb" in config[time]:
                    self.perturb(config[time]["perturb"], time,
                                 flagfren=fren)

    def getassemblytype(self, assemblynumber, time=0, flagfren=False):
        """
        Get type of a certain assembly.

        Parameters
        ----------
        assemblynumber : int
            Number of the assembly of interest
        flagfren : bool, optional
            Flag for FRENETIC numeration. The default is False.

        Returns
        -------
        which : int
            Type of assembly.

        """
        if flagfren is True:
            # translate FRENETIC numeration to Serpent
            index = self.Map.fren2serp[assemblynumber]-1  # -1 for py indexing
        else:
            index = assemblynumber-1  # -1 for py indexing
        # get coordinates associated to these assemblies
        rows, cols = np.unravel_index(index, self.Map.type.shape)
        which = self.Config[time][rows, cols]
        return which

    def replace(self, newtype, asslst, flagfren=False):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        newtype : list
            List of new/existing types of assemblies.
        asslst : list
            List of assemblies to be replaced.
        flagfren : bool, optional
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

        for ipos, ilst in enumerate(asslst):  # loop over lists
            # check map convention
            if flagfren is True:
                # translate FRENETIC numeration to Serpent
                index = [self.Map.fren2serp[i]-1 for i in ilst]  # -1 for index
            else:
                index = [i-1 for i in ilst]  # -1 to match python indexing
            # get coordinates associated to these assemblies
            index = (list(set(index)))
            rows, cols = np.unravel_index(index, self.Map.type.shape)
            # load new assembly type
            self.Map.type[rows, cols] = newtype[ipos]

    def perturb(self, pertconfig, time, flagfren=False):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        newtype : list
            List of new/existing types of assemblies.
        asslst : list
            List of assemblies to be replaced.
        flagfren : bool, optional
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
                              'perturbations do not match!')

            if len(pertconfig['with']) != len(pertconfig['what']):
                raise OSError('New regions and number of ' +
                              'perturbations do not match!')

            pconf = zip(pertconfig['which'], pertconfig['with'],
                        pertconfig['what'])

            p = 0
            for which, withass, whatass in pconf:
                p = p + 1
                for assbly in which:
                    nt = self.time.index(float(time))
                    atype = self.getassemblytype(assbly, flagfren=flagfren,
                                                 time=self.time[nt-1])
                    what = self.assemblytypes[atype]
                    # take region name
                    basename = re.split(r"_t\d+.\d+_p\d+", what)[0]
                    newname = "%s_t%s_p%d" % (basename, time, p)
                    # define new cuts, if any
                    if newname not in self.AxialConfig.cuts.keys():
                        cuts = deepcopy(self.AxialConfig.cuts[what])
                        nass = len(self.assemblytypes.keys())
                        self.assemblytypes[nass + 1] = newname
                        if whatass in cuts.reg:
                            cuts.reg[cuts.reg == whatass] = withass
                            upz, loz, reg = cuts.upz, cuts.loz, cuts.reg
                            self.AxialConfig.cuts[newname] = AxialCuts(upz, loz, reg)

                        else:
                            raise OSError('%s not in assembly %d at time %ss'
                                          % (whatass, assbly, time))

                    # replace assembly
                    self.replace(nass + 1, assbly, flagfren)
                    self.Config[float(time)] = deepcopy(self.Map.type)

        except KeyError:
            raise OSError('"which" and/or "dz" keys missing in "translate"!')

    def translate(self, transconfig, time, flagfren=False):
        """
        Replace assemblies with user-defined new or existing type.

        Parameters
        ----------
        transconfig : dict
            Dictionary with details on translation transformation
        flagfren : bool, optional
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

            for dz, which in zip(transconfig['dz'], transconfig['which']):
                for assbly in which:
                    nt = self.time.index(float(time))
                    atype = self.getassemblytype(assbly, flagfren=flagfren,
                                                 time=self.time[nt-1])
                    what = self.assemblytypes[atype]
                    newname = "%st%sz%d" % (what, time, dz)
                    # define new cuts, if any
                    if newname not in self.AxialConfig.cuts.keys():
                        cuts = deepcopy(self.AxialConfig.cuts[what])
                        cuts.upz[0:-1] = [z+dz for z in cuts.upz[0:-1]]
                        cuts.loz[1:] = [z+dz for z in cuts.loz[1:]]
                        nass = len(self.assemblytypes.keys())
                        self.assemblytypes[nass + 1] = newname
                        upz, loz, reg = cuts.upz, cuts.loz, cuts.reg
                        self.AxialConfig.cuts[newname] = AxialCuts(upz, loz, reg)

                    # replace assembly
                    self.replace(nass + 1, assbly, flagfren)
                    self.Config[float(time)] = deepcopy(self.Map.type)

        except KeyError:
            raise OSError('"which" and/or "dz" keys missing in "translate"!')

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
            f.write("\n".join("{:03d} {:5f} {:5f}".format(elem[0], elem[1], elem[2])
                              for elem in regions))
            f.write("\n")

    def getassemblylist(self, atype, time=0, match=True):
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
        asstypes = self.Config[time].flatten(order='F')

        if match is True:
            matchedass = np.where(asstypes == atype)[0]+1  # +1 for py indexing
        else:
            matchedass = np.where(asstypes != atype)[0]+1

        return matchedass
    # TODO: add writeregionmap method to plot region id, x and y for each assembly

    def writecorelattice(self, flatten=False, fname="corelattice.txt",
                         serpheader=False, string=True):
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

        Returns
        -------
        ``None``

        """
        # define regions
        if flatten is False:
            typelabel = self.Map.type
        else:
            typelabel = np.reshape(self.Map.type, (self.Map.Nx*self.Map.Ny, 1))

        # determine file format
        if string is False:
            nd = str(len(str(self.Map.type.max())))  # determine number of digits
            fmt = "%0"+nd+"d"
        else:
            fmt = "%s"
            typelabel = typelabel.astype(str)
            for key in self.assemblytypes.keys():
                typelabel[typelabel == str(key)] = self.assemblytypes[key]

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
            Nx, Ny = str(self.Map.Nx), str(self.Map.Ny)
            # define assembly pitch
            P = str(2*self.AssemblyGeom.apothema)
            header = " ".join(("lat core ", asstype, x0, y0, Nx, Ny, P))
            comm = ''
        # save array to file
        np.savetxt(fname, typelabel, delimiter=" ", fmt=fmt, header=header,
                   comments=comm)

if __name__ == "__main__":

    # make input
    [geinp, rotation, pitch, assemblynames, replace, cuts, config,
     fren, fill] = parse(sys.argv)
    core = Core(geinp, rotation, pitch, assemblynames, replace=replace,
                cuts=cuts, config=config, fren=fren, fill=fill)
    # post-process

