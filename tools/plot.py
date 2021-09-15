"""
Author: N. Abrate.

File: postprocess.py

Description: Class to plot data from Serpent calculations.
"""
import numpy as np
from numbers import Real
from collections import OrderedDict
import matplotlib.pyplot as plt
from matplotlib.patches import RegularPolygon, Rectangle
from matplotlib.collections import PatchCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
from matplotlib import rc, colors


def AxialGeomPlot(core, which, time=0, label=False, dictname=None,
                  figname=None, fren=False, asstype=False, usetex=False,
                  fill=True, mycuts=False, title=None, scale=1, floating=False,
                  legend=False, seed=None, **kwargs):
    """
    Plot core geometry on the x-z or y-z plane for NEutronics configuration.

    Parameters
    ----------
    core : obj
        Reactor core object created with "Core" class.
    which : list
        List of int with assemblies to be plotted in the desired numeration
        convention (Serpent, FRENETIC, ...).
    time : float, optional
        Time instant when core configuration is plotted. Default is 0.
    whichconf : str, optional
        Configuration to be plotted (NEutronics, THermal-hydraulics or
        Cooling Zones). Defaulit is "NEconfig".
    label : bool, optional
        Assembly labels. The default is ``False``.
    dictname : dict, optional
        Dictionary with user defined labels. The default is ``None``.
    figname : str, optional
        Name to save the figure in .png format. The default is ``None``.
    fren : bool, optional
        Boolean for FRENETIC numeration. The default is ``False``.

    usetex : bool, optional
        Bool to choose TeX format for strings. The default is ``False``.
    fill : bool, optional
        Boolean to decide if assemblies are filled or not. The default is
        ``True``.
    mycuts : bool, optional
        Boolean for plotting user-defined cuts stored in ``Core`` object.
        Default is ``None``.
    title : str, optional
        Plot title. The default is ``None``.
    scale : float, optional
        Geometry scaling factor. The default is 1.
    floating : bool, optional
        Floating object flag. If ``True``, the assemblies are plotted without
        taking into account their position inside the core.
        The default is ``False``.
    legend : bool, optional
        Legend flag. If ``True``, the legend is plotted. The default is
        ``False``.
    **kwargs :
        KeyWord optional arguments for plotting.

    Raises
    ------
    ``None``

    Returns
    -------
    ``None``

    """
    # TODO: add legend
    # set default font and TeX interpreter
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
    rc('text', usetex=usetex)

    kwargs.setdefault("ec", "k")
    kwargs.setdefault("linewidth", 0.1)
    kwargs.setdefault("lw", 0.5)
    kwargs.setdefault("alpha", 1)
    fontsize = kwargs.get("fontsize", 4)

    if seed is not None:
        np.random.seed(1)

    L = core.AssemblyGeom.edge*2
    Nass = core.Map.type.size
    # array of assembly type
    typelabel = np.reshape(core.NEconfig[time], (Nass, 1))
    # explore types of assembly to be plotted
    types = []
    for i in which:
        t = core.getassemblytype(i, isfren=fren, time=time)
        if t not in types:
            types.append(t)

    reg = set(core.NEregionslegendplot.values())
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
    css4 = list(colors.CSS4_COLORS.keys())
    if len(def_colors) < NR:
        N = NR-len(def_colors)
        if N < len(css4)-len(def_colors):
            icol, newc = 0, 0
            while newc <= N:
                if css4[icol] not in def_colors:
                    def_colors.append(css4[icol])
                    newc += 1
                icol += 1
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

    idx = 0
    labels = []
    xlo, xup = np.inf, 0
    ylo, yup = np.inf, 0
    for key, coord in (core.Map.serpcentermap).items():
        # check key is in which list
        if key not in which:
            continue
        if floating is False:
            x, y = coord
        else:
            idx = idx + 2*L
            x, y = idx, None

        # parse axial coordinates
        asstype = core.NEassemblytypes[core.getassemblytype(key, time=time)]
        loz = np.asarray(core.NEAxialConfig.cuts[asstype].loz)
        upz = np.asarray(core.NEAxialConfig.cuts[asstype].upz)
        reg = np.asarray(core.NEAxialConfig.cuts[asstype].reg)
        deltaz = upz-loz
        for iz, dz in enumerate(deltaz):
            # scale coordinate
            coord = ((x-L/2)*scale, loz[iz]*scale)
            # update ax limits
            xlo = coord[0] if coord[0] < xlo else xlo
            ylo = coord[1] if coord[1] < ylo else ylo
            xup = coord[0] if coord[0] > xup else xup
            yup = coord[1] if coord[1] > yup else yup
            # select color
            reglabel = core.NEregionslegendplot[reg[iz]]
            col = asscol[reglabel]
            if reglabel not in labels:
                labels.append(reglabel)
            # define assembly patch
            asspatch = Rectangle(coord, L, dz, color=col, fill=fill,
                                 label=reglabel, **kwargs)
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

                if asstype is False:
                    for assN, txt in dictname:
                        x, y = core.Map.serpcentermap[core.Map.fren2serp[assN]]
                        plt.text(x*scale, (loz[iz]+dz/2)*scale, txt,
                                 ha='center', va='center', size=fontsize)

        # add my cuts on top of patch
        if mycuts is True and 'mycuts' in core.NEAxialConfig.__dict__.keys():
            for myz in core.NEAxialConfig.mycuts:
                plt.hlines(myz*scale, (x-L/2)*scale, (x+L/2)*scale,
                           linestyles='dashed', linewidth=1, edgecolor='k')

    ax.axis('equal')
    # recompute the ax.dataLim
    # plt.xlim(xlo, xup)
    # plt.ylim(ylo, yup)
    plt.axis('off')
    plt.title(title)
    plt.tight_layout()
    # add legend, if any
    if legend is True:
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = OrderedDict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(),
                   bbox_to_anchor=(0.8, 1), loc='upper left',
                   framealpha=1)

    plt.tight_layout()
    # save figure
    if figname is not None:
        fig.savefig(figname, bbox_inches='tight', dpi=250)


def RadialMap(core, tallies=None, z=0, time=0, pre=0, gro=0, grp=0,
              label=False, figname=None, which=None, fren=False,
              whichconf='NEconfig', asstype=False, dictname=None,
              legend=False, txtcol='k', usetex=False, fill=True,
              axes=None, cmap='Spectral_r', thresh=None,
              cbarLabel=True, xlabel=None, ylabel=None, myfontsize=4,
              loglog=None, logx=None, logy=None, title=None,
              scale=1, fmt=None, numbers=False, **kwargs):
    """
    Plot something (geometry, input/output data) on the x-y plane.

    Parameters
    ----------
    label : TYPE, optional
        DESCRIPTION. The default is False.
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
    # set default font and TeX interpreter
    rc('font', **{'family': 'DejaVu Sans'})
    rc('text', usetex=usetex)
    # set default parameters
    kwargs.setdefault("ec", "k")
    kwargs.setdefault("linewidth", 0.5)
    kwargs.setdefault("lw", 0.5)
    kwargs.setdefault("alpha", 1)
    fontsize = kwargs.get("fontsize", myfontsize)
    # delete size from kwargs to use it in patches
    if 'fontsize' in kwargs:
        del kwargs['fontsize']

    # define default colorsets (if not enough, random colours are added)
    if core.AssemblyGeom.type == "S":
        orientation = np.pi/4
        L = core.AssemblyGeom.edge
        L = L/2*np.sqrt(2)
    elif core.AssemblyGeom.type == "H":
        orientation = 0
        L = core.AssemblyGeom.edge

    if tallies is None:

        Nass = core.Map.type.size
        # array of assembly type
        if whichconf == "NEconfig":
            typelabel = np.reshape(core.NEconfig[time], (Nass, 1))
        elif whichconf == "THconfig":
            typelabel = np.reshape(core.THconfig[time], (Nass, 1))
        elif whichconf == "CZconfig":
            typelabel = np.reshape(core.CZconfig[time], (Nass, 1))
        else:
            raise OSError("Unknown core config!")

        maxtype = int(max(typelabel))
        coretype = range(0, maxtype+1)  # define

        if core.AssemblyGeom.type == 'H':
            def_colors = ['turquoise', 'firebrick', 'chocolate', 'gold',
                          'palegoldenrod', 'forestgreen', 'darkgoldenrod', 'grey',
                          'royalblue', 'silver', 'darkorange', 'magenta',
                          'lime', 'seagreen']
        else:
            def_colors = ['deepskyblue', 'white', 'limegreen', 'gold',
                          'lightgray', 'deepskyblue', 'firebrick', 'darkorange',
                          'turquoise', 'royalblue', 'silver']

        # check if more colors are needed and append in case
        css4 = list(colors.CSS4_COLORS.keys())
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

    # check which variable
    amap = core.Map
    if which is None:  # consider all assemblies
        which = list(amap.serpcentermap.keys())
    else:
        if fren is True:  # FRENETIC numeration
            which = [amap.fren2serp[k] for k in which]

    if thresh is None:
        thresh = -np.inf
    elif not isinstance(thresh, (Real, int, np.float)):
        raise TypeError(
            "thresh should be real, not {}".format(type(thresh)))
    # open figure
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patches, coord, values = [], [], []
    patchesapp = patches.append
    coordapp = coord.append
    valuesapp = values.append
    for k, xy in amap.serpcentermap.items():

        if k not in which:
            continue

        if tallies is not None:
            if tallies[k-1] <= thresh:
                continue
            else:
                valuesapp(tallies[k-1])
            # plot geometry filled with colour
            asspatch = RegularPolygon(xy, core.AssemblyGeom.numedges,
                                      L*scale, orientation=orientation,
                                      **kwargs)
            coordapp(xy)
            x, y = xy
            # scale coordinate
            xy = (x*scale, y*scale)
            # define assembly patch
            patchesapp(asspatch)
        else:
            # select color
            col = asscol[typelabel[k-1, 0]]
            # get type
            atype = core.getassemblytype(k, time=time)
            asspatch = RegularPolygon(xy, core.AssemblyGeom.numedges, L*scale,
                                      orientation=orientation, color=col,
                                      fill=fill, label=core.NEassemblylabel[atype], **kwargs)
            ax.add_patch(asspatch)


    if tallies is not None:  # plot physics
        coord = np.asarray(coord)
        values = np.asarray(values)
        patches = np.asarray(patches, dtype=object)
    
        normalizer = normalizerFactory(values, None, False,
                                       coord[:, 0]*scale,
                                       coord[:, 1]*scale)
        pc = PatchCollection(patches, cmap=cmap, **kwargs)
    
        if title is True:
            nodes = core.NEAxialConfig.AxNodes
            idz = np.argmin(abs(z-nodes))
    
            times = core.TimeProf
            idt = np.argmin(abs(time-times))
    
            title = 'z=%.2f [cm], t=%.2f [s]' % (nodes[idz], times[idt])
    
        formatPlot(ax, loglog=loglog, logx=logx, logy=logy,
                   xlabel=xlabel or "X [cm]",
                   ylabel=ylabel or "Y [cm]", title=title)
        pc.set_array(values)
        pc.set_norm(normalizer)
        ax.add_collection(pc)
        addColorbar(ax, pc, cbarLabel=cbarLabel)
    
        # add labels on top of the polygons
        if label is True:
            if fmt is None:
                fmt = "%.1e" if abs(np.max(np.max(tallies))) > 999 else "%.1f"
            else:
                fmt = fmt
            for key, coord in (core.Map.serpcentermap).items():
                # check key is in "which" list
                k = core.Map.serp2fren[key] if fren is True else key
                if k not in which or tallies[k-1] <= thresh:
                    continue
                else:
                    x, y = coord
                    # plot text inside assemblies
                    txt = fmt % tallies[amap.serp2fren[key]-1] if fren is True else fmt % tallies[key-1]
                    # rc('text', usetex=False)
                    plt.text(x*scale, y*scale, txt, ha='center',
                             va='center', size=fontsize)

    else:
        # add labels on top of the polygons
        for key, coord in (core.Map.serpcentermap).items():
            # check key is in "which" list
            if key not in which:
                continue
    
            x, y = coord
            # plot text inside assemblies
            if dictname is None:
                if label is True:  # plot assembly number
                    if fren is True:  # FRENETIC numeration
                        txt = str(core.Map.serp2fren[key])  # translate keys
                    else:
                        txt = str(key)
    
                    plt.text(x*scale, y*scale, txt, ha='center',
                             va='center', size=fontsize, color=txtcol)
    
            else:
                if asstype is True:  # plot assembly type
                    txt = dictname[typelabel[key-1, 0]]
                    plt.text(x*scale, y*scale, txt, ha='center', va='center',
                             size=fontsize, color=txtcol)
    
                # FIXME: must be a better way to do this avoiding asstype, maybe.
                # change "dictname" because maybe we want tuples to have
                # overlappings (phytra fig) write other labels
                else:
                    atype = core.getassemblytype(key, time=time)
                    x, y = core.Map.serpcentermap[key]
                    try:
                        assk = str(core.Map.serp2fren[key]) if fren is True else key
                        txt = dictname[int(assk)]
                        plt.text(x*scale, y*scale, txt, ha='center',
                                 va='center', size=fontsize, color=txtcol)
                    except KeyError:
                        continue

    if tallies is None:
        # add legend, if any
        if legend is True:
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = OrderedDict(zip(labels, handles))
            plt.legend(by_label.values(), by_label.keys(),
                       bbox_to_anchor=(0.85, 1), loc='best',
                       framealpha=1)


    ax.axis('equal')
    if xlabel is None and ylabel is None:
        plt.axis('off')

    # save figure
    if figname is not None:
        fig.savefig(figname, bbox_inches='tight', dpi=250)