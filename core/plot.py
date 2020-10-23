"""
Author: N. Abrate.

File: plot.py

Description: Class for plotting reactor data, physical quantities and geometry.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

from matplotlib import rc
from matplotlib.patches import RegularPolygon, Rectangle
from matplotlib.collections import PatchCollection

from serpentTools.utils import formatPlot, normalizerFactory, addColorbar


def RadialPlot(core, time=0, label=False, dictname=None, figname=None,
               fren=False, which=None, what=None, asstype=False, usetex=False,
               fill=True, axes=None, cmap='Spectral_r', thresh=None,
               cbarLabel=None, xlabel=None, ylabel=None, loglog=None,
               logx=None, logy=None, title=None, scale=1, fmt="%.2f",
               numbers=False, **kwargs):
    """
    Plot geometry or physics on the x-y plane.

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
    # TODO: add option for plotting core slices with colours matching the axial pl
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

    if what is None:

        physics = False
        # define default colorsets (if not enough, random colours are added)
        if core.AssemblyGeom.type == "S":
            def_colors = ['deepskyblue', 'white', 'limegreen', 'gold',
                          'lightgray', 'firebrick', 'orange', 'turquoise',
                          'royalblue', 'yellow']
            orientation = np.pi/4
            L = core.AssemblyGeom.edge
            L = L/2*np.sqrt(2)

        elif core.AssemblyGeom.type == "H":
            def_colors = ['turquoise', 'firebrick', 'chocolate', 'gold',
                          'lightgray', 'seagreen', 'darkgoldenrod', 'grey',
                          'royalblue', 'yellow', 'forestgreen', 'magenta',
                          'lime']
            orientation = 0
            L = core.AssemblyGeom.edge

        # check if more colors are needed and append in case
        css4 = list(mcolors.CSS4_COLORS.keys())
        if len(def_colors) < maxtype+1:
            N = (maxtype+1)-len(def_colors)
            if N < len(css4)-len(def_colors):
                icol = 0
                while icol <= N:
                    if css4[icol] not in def_colors:
                        def_colors.append(css4[icol])
                        icol = icol + 1
            else:
                # select all css4 colours
                icol = 0
                while icol <= N:
                    if css4(icol) not in def_colors:
                        def_colors.append(css4(icol))
                        icol = icol + 1
                # assign random colours
                for icol in range(0, N-len(css4)+len(def_colors)):
                    def_colors.append(np.random.randint(3,))

        # color dict
        asscol = dict(zip(coretype, def_colors))

    else:  # cont. <- if type(fill) is bool

        if core.AssemblyGeom.type == "S":
            orientation = np.pi/4
            L = L/2*np.sqrt(2)

        elif core.AssemblyGeom.type == "H":
            orientation = 0

        physics = True
        patches = []
        # values = []
        patchesapp = patches.append
        # valuesapp = values.append
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
        if physics is False:
            # select color
            col = asscol[typelabel[key-1, 0]]
            # define assembly patch
            asspatch = RegularPolygon(coord, core.AssemblyGeom.numedges, L*scale,
                                      orientation=orientation, color=col,
                                      fill=fill, **kwargs)
            ax.add_patch(asspatch)

        else:
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


def AxialPlot(core, which, time=0, label=False, dictname=None, figname=None,
              fren=False, asstype=False, usetex=False, fill=True, axes=None,
              mycuts=False, scale=1, numbers=False, **kwargs):
    """ Plot geometry on x-z plane. """
    # TODO: add legend
    # set default font and TeX interpreter
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
    rc('text', usetex=usetex)

    kwargs.setdefault("ec", "k")
    kwargs.setdefault("linewidth", 0.1)
    kwargs.setdefault("lw", 0.5)
    kwargs.setdefault("alpha", 1)
    fontsize = kwargs.get("fontsize", 4)

    L = core.AssemblyGeom.edge*2
    Nass = core.Map.type.size
    # array of assembly type
    typelabel = np.reshape(core.Config[time], (Nass, 1))
    # explore types of assembly to be plotted
    types = []
    for i in which:
        t = core.getassemblytype(i, flagfren=fren, time=time)
        if t not in types:
            types.append(t)

    # gather regions for each type of assembly for colour matching
    # reg = []
    # for t in types:
    #     asslabel = core.assemblytypes[t]
    #     reglist = core.AxialConfig.cuts[asslabel].reg
    #     reg.extend(reglist)
    reg = set(core.regionslegendplot.values())
    # make list unique
    reg = list(set(reg))
    NR = len(reg)

    # delete size from kwargs to use it in pathces
    if 'fontsize' in kwargs:
        del kwargs['fontsize']

    # define default colorsets (if not enough, random colours are added)
    def_colors = ['deepskyblue', 'white', 'limegreen', 'gold',
                  'lightgray', 'firebrick', 'orange', 'turquoise',
                  'royalblue', 'yellow', 'blue', 'darkgrey', 'burlywood',
                  'lightsalmon', 'deeppink']

    # check if more colors are needed and append in case
    css4 = list(mcolors.CSS4_COLORS.keys())
    if len(def_colors) < NR:
        N = NR-len(def_colors)
        if N < len(css4)-len(def_colors):
            icol = 0
            while icol <= N:
                if css4[icol] not in def_colors:
                    def_colors.append(css4[icol])
                    icol = icol + 1
        else:
            # select all css4 colours
            icol = 0
            while icol <= N:
                if css4(icol) not in def_colors:
                    def_colors.append(css4(icol))
                    icol = icol + 1
            # assign random colours
            for icol in range(0, N-len(css4)+len(def_colors)):
                def_colors.append(np.random.randint(3,))

    # color dict
    asscol = dict(zip(reg, def_colors))

    # open figure
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if fren is True:
        which = [core.Map.fren2serp[k] for k in which]
    else:
        tmp = list((core.serpcentermap).keys())
        which = [tmp[k] for k in which]

    for key, coord in (core.Map.serpcentermap).items():
        # check key is in which list
        if key not in which:
            continue
        x, y = coord
        # parse axial coordinates
        asstype = core.assemblytypes[core.getassemblytype(key, time=time)]
        loz = np.asarray(core.AxialConfig.cuts[asstype].loz)
        upz = np.asarray(core.AxialConfig.cuts[asstype].upz)
        reg = np.asarray(core.AxialConfig.cuts[asstype].reg)
        deltaz = upz-loz

        for iz, dz in enumerate(deltaz):
            # scale coordinate
            coord = ((x-L/2)*scale, loz[iz]*scale)
            # select color
            reglabel = core.regionslegendplot[reg[iz]]
            col = asscol[reglabel]
            # define assembly patch
            asspatch = Rectangle(coord, L, dz, color=col, fill=fill, **kwargs)
            ax.add_patch(asspatch)

            if dictname is None:
                if label is True:  # plot assembly number
                    if fren is True:  # FRENETIC numeration
                        txt = str(core.Map.serp2fren[key])  # translate keys
                    else:
                        txt = str(key)

                    plt.text(x*scale, (loz[iz]+dz/2)*scale, txt, ha='center',
                             va='center', size=fontsize)

            else:
                if asstype is True:  # plot assembly type
                    txt = dictname[typelabel[key-1, 0]]
                    plt.text(x*scale, (loz[iz]+dz/2)*scale, txt, ha='center',
                             va='center', size=fontsize)

                # FIXME: must be a better way to do this avoiding asstype, maybe.
                # change "dictname" because maybe we want tuples to have overlappings (phytra fig)
                # write other labels
                if asstype is False:
                    for assN, txt in dictname:
                        x, y = core.Map.serpcentermap[core.Map.fren2serp[assN]]
                        plt.text(x*scale, (loz[iz]+dz/2)*scale, txt,
                                 ha='center', va='center', size=fontsize)

        # add my cuts on top of patch
        if mycuts is True:
            for myz in core.AxialConfig.mycuts:
                plt.hlines(myz*scale, (x-L/2)*scale, (x+L/2)*scale,
                           linestyles='dashed', linewidth=1, ec='k')

    ax.axis('equal')
    plt.axis('off')

    # save figure
    if figname is not None:
        fig.savefig(figname, bbox_inches='tight', dpi=250)
