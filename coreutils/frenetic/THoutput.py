import os
import re
from copy import deepcopy as cp
from warnings import catch_warnings
import h5py as h5
import numpy as np
import itertools
from pathlib import Path
from numbers import Real
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon
from matplotlib.collections import PatchCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
from coreutils.tools.plot import RadialMap
from coreutils.core import Core
from matplotlib import rcParams


class THoutput:
    """
    Class to read TH profiles computed by FRENETIC.
    """

    # default keys for integral parameters (namelist)
    inout = {'DensOut', 'DensIn', 'EnthOut', 'EnthIn', 'PIn',
             'POut', 'TOut', 'TIn', 'VIn', 'VOut', 'mDotOut',
             'mDotIn'}

    maximum = ['Tcoolant', 'Tpin_average', 'Tpin_center', 
               'Tpin_surface', 'pressure', 'zMax_pressure',
               'zMax_Tcoolant', 'zMax_Tpin_average', 
               'zMax_Tpin_center', 'zMax_Tpin_surface']

    distrout = ['timeDistr', 'T_coolant', 'T_pin_avg', 'T_pin_ctr', 
                'T_pin_sur', 'density', 'htc', 'pressure',
                 'q_pin', 'velocity']

    aliases = {'DensOut': ['Densout', 'densout'], 'DensIn': ['Densin', 'densin'],
               'EnthOut': ['Enthout', 'enthout'], 'EnthIn': ['Enthin', 'enthin'],
               'PIn': ['Pin', 'pin'], 'POut': ['Pout', 'pout'],
               'TOut': ['Tout', 'tout'], 'TIn': ['Tin', 'tin'],
               'VIn': ['Vin', 'vin'], 'VOut': ['Vout', 'vout'],
               'mDotOut': ['mDotout', 'mdotout', 'mDotout'],
               'mDotIn': ['mDotin', 'mdotin', 'mDotin']
              }

    distrout_attr = {'timeDistr': 'time instant [s]', 
                     'T_coolant': 'coolant temperature [K]', 
                     'T_pin_avg': 'Average pin temperature [K]',
                     'T_pin_ctr': 'Center pin temperature [K]', 
                     'T_pin_sur': 'Surface pin temperature [K]', 
                     'density': 'Coolant density [kg/m^3]', 
                     'htc': 'Heat Transfer Coefficient [W/(m^2 K)]', 
                     'pressure': 'Coolant pressure [Pa]',
                     'q_pin': 'Pin heat flux [W/m^2]',
                     'velocity': 'Coolant velocity [m/s]'}

    # default profiles unit of measures
    inout_uom = {'DensOut': '[kg/m^3]', 'DensIn': '[kg/m^3]', 'EnthOut': 'J/(kg K)',
                 'EnthIn': '[J/(kg K)]', 'PIn': '[Pa]',
                 'POut': '[Pa]', 'TOut': '[K]', 'TIn': '[K]', 'VIn': '[m/s]', 
                 'VOut': '[m/s]', 'mDotOut': '[kg/s]',
                 'mDotIn': '[kg/s]'}

    distrout_uom = {'timeDistr': '[s]', 'T_coolant': '[K]', 
                    'T_pin_avg': '[K]', 'T_pin_ctr': '[K]', 
                    'T_pin_sur': '[K]', 'density': '[kg/m^3]', 
                    'htc': '[W/(m^2 K)]', 'pressure': '[Pa]',
                    'q_pin': '[W/m^2]', 'velocity': '[m/s]'}

    maximum_uom = {'Tcoolant': '[K]', 'Tpin_average': '[K]', 
                   'T_pin_center': '[K]', 
                   'T_pin_surface': '[K]', 
                   'pressure': '[Pa]',
                   'zMax_pressure': '[m]',
                   'zMax_Tcoolant': '[m]', 'zMax_Tpin_average': '[m]',
                   'zMax_Tpin_center': '[m]', 'zMax_Tpin_surface': '[m]',
                }

    def __init__(self, path):
        """Initialise the class.

        Parameters
        ----------
        path : string
            Path to the FRENETIC case.
        """
        self.casepath = path
        self.THpath = os.path.join(path, 'TH')
        # looking for core file
        self.core = Core(os.path.join(path, 'core.h5'))
        self.mapHAType = {}
        # map HA type to the number of assemblies
        for nchan, chan in self.core.TH.THassemblytypes.items():
            # loop over time
            whichHex = self.core.getassemblylist(nchan, self.core.TH.THconfig[0], isfren=True)
            self.mapHAType[nchan] = whichHex

        self.inout = THoutput.inout
        self.distributions = THoutput.distrout
        self.maximum = THoutput.maximum
        self.inout_measure = THoutput.inout_uom
        self.maximum_meaure = THoutput.maximum_uom
        self.distributions_descr = THoutput.distrout_attr
        self.distributions_measure = THoutput.distrout_uom

    def get(self, which, hex=None, t=None, z=None):
        """
        Get profile from output.

        Parameters
        ----------
        which: string
            Name of the variable to be parsed
        hex: integer or iterable, optional
            Number of assembly, by default ``None``.
        t: float or iterable, optional
            Time instant(s), by default ``None``.
        z: float or iterable, optional
            Axial coordinate(s), by default ``None``.

        Returns
        -------
        profile: array
            Output profile requested.
        """
        # check if which is an alias
        for key, alias_list in self.aliases.items():
            if which in alias_list:
                which = key

        try:
            datapath = os.path.join(self.THpath, "output.h5")
            fh5 = h5.File(datapath, "r")
        except OSError as err:
            if 'Unable to open file' in str(err):
                if not os.path.exists(datapath):
                    raise THoutputError(f"No output in directory {self.NEpath}")

        if which in self.distributions:
            if which == "timeDistr":
                times = cp(np.asarray(fh5["distributions"]["timeDistr"])[()])
                # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                times[0] = 0
                # --- close H5 file
                fh5.close()
                return times
            isdistr = True
            dictkey = "distributions"
            fname = 'output.h5'
            idx = self.distributions.index(which)
            # check core h5 is present
            if self.core is None:
                raise THoutputError(f'Cannot provide distributions. \
                                    No `core.h5` file in {self.casepath}')

            # --- PARAMETERS
            # select HAType to be parsed
            whichHexType = {k: [] for k in self.mapHAType.keys()}
            if hex is not None:
                hex.sort()
                for h in hex:
                    for nchan, ass in self.mapHAType.items():
                        if h in ass:
                            whichHexType[nchan].append(h)
            else:
                whichHexType = self.mapHAType
                if self.core.dim == 1:
                    hex = [1]
                else:
                    hex = np.arange(1, self.core.NAss+1).tolist()

            # "t" refers to slicing
            if t is None:
                if len(self.core.TH.CZtime) == 1:
                    t = [0]  # time instant, not python index!
            # "times" refers to all time instants
            nTimeConfig = len(self.core.TH.CZtime)
            if nTimeConfig == 1:
                times = None
            else:  # parse time from h5 file
                times = cp(np.asarray(fh5[dictkey]["timeDistr"])[()])
                # FIXME path for issue https://github.com/h5py/h5py/issues/2069
                times[0] = 0
            # --- TIME AND AXIAL COORDINATE PARAMETERS
            idt, idz = self._shift_index(t, z, times=times)

            if t is not None:
                timesSnap = self.core.TimeSnap # TODO distinguish existence of snapshots in simulations

        else:  # InOut or Maximum data
            isdistr = False
            notfound = True
            for k in self.maximum:
                if which == k:
                    dictkey = k
                    notfound = False
                    group = "maximum"
                    break

            for k in self.inout:
                if which == k:
                    dictkey = k
                    notfound = False
                    group = "inout"
                    break

            if notfound:
                raise THoutputError(f'{which} not found in data!')

            # --- PARAMETERS
            if hex is not None:
                hex = [h-1 for h in hex]
            else:
                if self.core.dim == 1:
                    hex = [1]
                else:
                    hex = np.arange(1, self.core.NAss+1).tolist()

            # "t" refers to slicing
            if t is None:
                if not self.core.trans:
                    idt = [0]  # time instant, not python index!
                else:
                    # FIXME (here and in FRENETIC) current output misses "timeDistr"
                    t = cp(np.asarray(fh5[dictkey]["timeDistr"])[()])
                    idt = np.arange(0, len(t)).tolist()
            else:
                if isinstance(t, (list, np.ndarray)):
                    idt = [np.argmin(abs(ti-times)) for ti in t]
                else:
                    idt = np.argmin(abs(t-times))

        # --- PARSE PROFILE FROM H5 FILE
        if isdistr:
            # allocate output profile
            profile = np.zeros((len(idt), len(idz), len(hex)), dtype=float)
            dimlst = [None]*3
            dimlst[0] = idt
            dimlst[1] = idz
            prof = {}
            ichan = 0
            whichhex = []
            # look for various assemblies in Type_nH groups
            for nchan in whichHexType:
                # define 3rd dimension (index of matching hexagons)
                dimlst[2] = [self.mapHAType[nchan].index(h) for h in whichHexType[nchan]]
                if len(dimlst[2]) > 0:
                    # track all hexagons
                    whichhex = whichhex + whichHexType[nchan]
                    # parse output
                    outprof = np.asarray(fh5[dictkey][f"Type_{nchan:02d}"][which])
                    outprof = outprof[np.ix_(*dimlst)]
                    # add each column
                    for icol in range(outprof.shape[2]):
                        profile[:, :, ichan] = outprof[:, :, icol]
                        ichan += 1
            # reshuffle last index order to match hex numeration
            idx = np.argsort(whichhex)
            profile = profile[:, :, idx]
        else:
            profile = fh5[group][dictkey][idt, hex][()]

        # --- close H5 file
        fh5.close()

        return profile[:]

    def plot1D(self, which, t=None, ax=None, abscissas=None, z=None, 
               hex=None, leglabels=None, figname=None, xlabel=None,
               xlims=None, ylims=None, ylabel=None,
               style='sty1D.mplstyle', legend=True, **kwargs):
        """Plot time/axial profile of integral parame. or distribution in hex.

        Parameters
        ----------
        which: string
            Name of the variable to be parsed
        t: float or iterable, optional
            Time instant(s), by default ``None``.
        ax : `matplotlib.axes.Axes`, optional
            Ax on which to plot the data, by default `None`. If not provided,
            a new figure is created.
        abscissas : list, optional
            User-defined coordinates for the x-axis, by default ``None``
        z: float or iterable, optional
            Axial coordinate(s), by default ``None``.
        hex: integer or iterable, optional
            Number of assembly, by default ``None``.
        leglabels : list, optional
            List of strings for the legend entries, by default ``None``
        figname : string, optional
            Name of the figure to be saved, including its format, by default ``None``
        xlabel : string, optional
            Label for the x-axis, by default ``None``
        xlims : list, optional
            Limits on the x-axis, by default ``None``
        ylims : list, optional
            Limits on the y-axis, by default ``None``
        ylabel : string, optional
           Label for the y-axis, by default ``None``
        style : str, optional
            Path of the `matplotlib` style, by default ``sty1D.mplstyle``
        legend : bool, optional
            Option to print the legend, by default ``True``

        Raises
        ------
        THoutputError
            If the ``tools`` path in the ``coreutils`` directory is not found.
        THoutputError
            _description_
        """
        if style == 'sty1D.mplstyle':
            pwd = Path(__file__).parent.parent
            toolspath = Path.joinpath(pwd, "tools")
            if toolspath.exists():
                sty1D = str(Path.joinpath(pwd, "tools", style))
            else:
                raise THoutputError(f"{toolspath} not found!")
        else:
            if not Path(style).exists():
                print(f'Warning: {style} style sheet not found! \
                    Switching to default...')
            else:
                sty1D = style

        label = which
        # check if which is an alias
        for key, alias_list in self.aliases.items():
            if which in alias_list:
                which = key

        # select unit of measure corresponding to profile
        plotvstime = True if t else False
        if t:
            t = None

        if which in self.distributions:
            isdistr = True
            uom = self.distrout_uom[which]
        else:  # integral data
            isdistr = False
            notfound = True
            for k in self.maximum:
                if which == k:
                    dictkey = k
                    notfound = False
                    group = "maximum"
                    uom = self.maximum_uom[which]
                    break

            for k in self.inout:
                if which == k:
                    dictkey = k
                    notfound = False
                    group = "inout"
                    uom = self.inout_uom[which]
                    break

        # --- parse profile
        prof = self.get(which, t=t, z=z, hex=hex)

        # --- select independent variable
        # it can be time or axial coordinate
        if not self.core.trans:
            times = None # np.array([0])
        else:  # parse time from h5 file
            datapath = os.path.join(self.NEpath, "output.h5")
            times = cp(self.get('timeDistr')[()])
            if plotvstime:
                t = times

        if t is None:
            t = [0]  # initial condition

        ax = plt.gca() if ax is None else ax
        if not isdistr:
            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                handles = []
                handlesapp = handles.append
                if abscissas is not None:
                    x = abscissas
                else:
                    x = times
                lin1, = ax.plot(x, y, **kwargs)
                ax.set_xlabel(xlabel)
                if ylabel is None:
                    # select unit of measure corresponding to profile
                    ax.set_ylabel(fr"{which} {uom}")
                else:
                    ax.set_ylabel(ylabel)
        else:   # plot distribution
            if hex is None:
                hex = [0] # 1st hexagon (this is python index, not hex. number)

            # get python-wise index for slicing
            idt, idz = self._shift_index(t, z, times=times)
            # map indexes from full- to sliced-array
            idt, idz = self._to_index(idt, idz)

            if nTime > 1 and plotvstime:  # plot against time
                x = times
                dim2plot = 'ntim'
                if xlabel is None:
                    xlabel = 'time [s]'
            else:  # plot time snapshots, if any, against axial coordinate
                x = self.core.TH.zcoord
                dim2plot = 'nelz'
                if xlabel is None:
                    xlabel = 'z-coordinate [cm]'

            # --- DEFINE SLICES
            dimdict = {'ntim': idt, 'nelz': idz, 'nhex': hex}
            usrdict = {'ntim': t, 'nelz': z, 'nhex': hex}
            dimlst = [None]*len(dimdict.keys())
            for k in dimdict.keys():
                i = dimdict.keys().index(k)
                dimlst[i] = dimdict[k]
            # define multi-index
            tmp = dimlst.pop(idx)
            indexes = list(itertools.product(*dimlst))
            indexes = [list(tup) for tup in indexes]
            for i in range(len(indexes)):
                indexes[i].insert(idx, tmp)

            # --- PLOT
            # plot against time or axial coordinate
            with plt.style.context(sty1D):
                ax = plt.gca() if ax is None else ax
                handles = []
                handlesapp = handles.append
                ymin, ymax = np.inf, -np.inf
                # loop over dimensions to slice
                for i, s in enumerate(indexes):
                    y = prof[s[i]]
                    label = self._build_label(s, dims, dim2plot, usrdict)
                    if abscissas is not None:
                        x = abscissas
                    lin1, = ax.plot(x, y, label=label, **kwargs)
                    handlesapp(lin1)
                    # track minimum and maximum
                    if ylims is None:
                        ymin = y.min() if y.min() < ymin else ymin
                        ymax = y.max() if y.max() > ymax else ymax

                if ylims is not None:
                    ymin = min(ylims)
                    ymax = max(ylims)

                plt.xlabel(xlabel)
                if rcParams['text.usetex']:
                    plt.ylabel(rf"{which} ${uom}$")
                else:
                    plt.ylabel(f"{which} {uom}")

                # ax.set_ylim(ymin, ymax)
                ax.set_xlim(x.min(), x.max())

                legend_x = 0.50
                legend_y = 1.01
                ncol = 2 if len(indexes) < 4 else 4
                if leglabels is not None:
                    plt.legend(handles, leglabels, bbox_to_anchor=(legend_x, legend_y),
                            loc='lower center', ncol=ncol)
                else:
                    if legend:
                        plt.legend(bbox_to_anchor=(legend_x, legend_y),
                                loc='lower center', ncol=ncol)

                plt.tight_layout()
                # plt.show()
                if figname is not None:
                    ax.savefig(figname)

    def RadialMap(self, what, z=0, t=0,
                  label=False, figname=None, hex=None,
                  usetex=False, fill=True, axes=None, cmap='Spectral_r',
                  thresh=None, cbarLabel=True, xlabel=None, ylabel=None,
                  log=None, title=True, scale=1, fmt="%.2f", **kwargs):
        """Plot FRENETIC output on the x-y plane.

        Parameters
        ----------
        what : string
            Field to be plotted.
        z : float, optional
            Axial coordinate, by default 0
        t : float, optional
            Time instant, by default 0
        label : bool, optional
            plot label, by default ``False``
        figname : string, optional
            Name of the figure to be saved, with its extension, by default ``None``
        hex : list, optional
            List of assemblies to be plotted, by default ``None``
        usetex : bool, optional
            Boolean for LaTeX string formatting, by default ``False``
        fill : bool, optional
            Bool to fill the patch with colours, by default ``True``
        axes : `matplotlib.axes.Axes`, optional
            Ax on which to plot the data, by default `None`. If not provided,
            a new figure is created.
        cmap : str, optional
            Name of the color map, by default 'Spectral_r'
        thresh : float, optional
            Avoid plot data below this threshold, by default ``None``
        cbarLabel : bool, optional
            Boolean for the label of the colorbar, by default ``True``
        xlabel : string, optional
            Label of the x-axis, by default ``None``
        ylabel : string, optional
            Label of the y-axis, by default ``None``
        log : bool, optional
            Boolean for a log scale, by default ``None``
        title : bool, optional
            Boolean for the plot title, by default ``True``
        scale : int, optional
            Scaling parameter for the plot, by default 1
        fmt : str, optional
            String format, by default "%.2f"

        Raises
        ------
        ``None``
        """
        # check data type
        if isinstance(what, dict):  # comparison with FRENETIC and other vals.
            tallies = np.zeros((self.core.NAss, len(what.keys())))
            for i, k in enumerate(what.keys()):
                v2 = what[k]
                v1 = self.get(k, hex=hex, t=t, z=z)
                v1 = np.squeeze(v1)
                tmp = np.true_divide(norm(v1-v2), norm(v1))
                tmp[tmp == np.inf] = 0
                tmp = np.nan_to_num(tmp)
                tallies[:, i] = tmp*100

        elif isinstance(what, list):  # list of output
            tallies = np.zeros((self.core.NAss, len(what)))
            for i, w in enumerate(what):
                _tmp = self.get(w, hex=hex, t=t, z=z)
                tallies[:, i] = np.squeeze(_tmp)

        elif isinstance(what, str):  # single output
            tallies = self.get(what, hex=hex, t=t, z=z)
            tallies = np.squeeze(tallies)
        else:
            raise TypeError('Input must be str, dict or list!')

        if title:
            timeSnap = self.core.TimeSnap
            idt = np.argmin(abs(t-timeSnap))

            if core.dim != 2:
                nodes = self.core.TH.zcoord
                idz = np.argmin(abs(z-nodes))
                title = 'z=%.2f [cm], t=%.2f [s]' % (nodes[idz], timeSnap[idt])
            else:
                nodes = np.array([0])
                idz = 0
                title = 't=%.2f [s]' % (timeSnap[idt])

        if cbarLabel:
            dist = self.distributions_descr[what]
            uom = self.distributions[what]
            uom = uom.replace('**', '^')
            changes = ['-1', '-2', '-3']
            for c in changes:
                uom = uom.replace(c, '{%s}' % c)
            uom = uom.replace('*', '~')
            # uom = '$%s$' % uom if usetex is True else uom
            cbarLabel = r'%s $%s$' % (dist, uom)

        RadialMap(core, tallies=tallies, z=z, time=t, label=label,
                  figname=figname,
                  which=None,
                  fren=True,
                  whichconf='TH',
                  asstype=False,
                  dictname=None,
                  legend=False,
                  txtcol='k',
                  fill=False,
                  axes=axes,
                  cmap=cmap,
                  thresh=thresh,
                  cbarLabel=cbarLabel,
                  xlabel=xlabel,
                  ylabel=ylabel,
                  loglog=log,
                  logx=False, 
                  logy=False,
                  title=title,
                  scale=scale, 
                  fmt=fmt,
                  **kwargs)

    def _shift_index(self, t, z, times=None):
        """Convert input parameters to lists of indexes for slicing.

        Parameters
        ----------
        t : int or list
            Time instant(s).
        z : int or list
            Axial coordinate(s).

        Returns
        -------
        list
            t and z converted in listed indexes
        """
        nodes = self.core.TH.zcoord if self.core.dim != 2 else np.array([0])
        if z is not None:
            if isinstance(z, (list, np.ndarray)):
                idz = [np.argmin(abs(zi-nodes)) for zi in z]
            else:
                idz = [np.argmin(abs(z-nodes))]
        else:
            idz = np.arange(0, len(nodes)).tolist()

        if times is not None:
            if t is not None:
                if isinstance(t, (list, np.ndarray)):
                    idt = [np.argmin(abs(ti-times)) for ti in t]
                else:
                    idt = np.argmin(abs(t-times))
            else:
                idt = np.arange(0, len(times)).tolist()
        else:
            idt = [0]

        return idt, idz

    def _to_index(self, t, z):
        """Map full-array indexes to sliced array indexes.

        Parameters
        ----------
        t : int or list
            Time instant(s).
        z : int or list
            Axial coordinate(s).

        Returns
        -------
        list
            idt and iz converted in listed indexes
        """
        if t is not None:
            idt = np.arange(0, len(t))
        else:
            idt = None

        if z is not None:
            idz = np.arange(0, len(z))
        else:
            idz = None

        return idt, idz

    def _build_label(self, s, dims, dim2plot, usrdict):
        """Build legend label.

        Parameters
        ----------
        s : list
            Slice for the np.array.
        dims : list
            List of dimensions.
        dim2plot : string
            Dimension to be plotted.
        usrdict : dict
            Dict mapping dimension name and lists.

        Returns
        -------
        str
            Label for the plot.
        """
        label_dict = {'nhex': 'n='}
        dim2plot_dict = {'ntim': 't', 'nelz': 'z'}
        uom = {'ntim': 's', 'nelz': 'm'}

        if plt.rcParams['text.usetex']:
            equal = "$=$"
        else:
            equal = "="

        label = []
        for i, k in enumerate(dims):
            if self.core.dim == 1 and k == 'nhex':
                continue

            if k != dim2plot:
                txt = usrdict[k][s[i]]
                txt = rf"{dim2plot_dict[k]}{equal}{txt} {uom[k]}"
                label.append(txt)

        return str(", ".join(label))

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
                raise FileNotFoundError("File extension is wrong. Only HDF5 can be parsed")

        return fname

class THoutputError(Exception):
    pass