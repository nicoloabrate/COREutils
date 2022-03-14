"""
Author: N. Abrate.

File: postprocess.py

Description: Class to plot data from Serpent calculations.
"""
import numpy as np
import math
from numbers import Real
from collections import OrderedDict
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.patches import RegularPolygon, Rectangle
from matplotlib.collections import PatchCollection
from serpentTools.utils import formatPlot, normalizerFactory, addColorbar
from matplotlib import rc, rcParams, colors


mycols1 = ["#1f271b", "#19647e", "#28afb0", "#f4d35e", "#ee964b", # generated with Coloor
           "#d62839", "#ba324f", "#175676", 
           "#004777", "#a30000", "#ff7700", "#efd28d", "#00afb5",
           "#4ba3c3", "#cce6f4",
           "#086788", "#07a0c3", "#f0c808", "#fff1d0", "#dd1c1a",
           "#003049", "#d62828", "#f77f00", "#fcbf49", "#eae2b7",
           "#6C5548", "#B45A38", "#603827", "#13466E", "#F5A964", 
           "#1980A7", "#491F15", "#006094", "#E8743F", "#2AA3C4",
           "#f66024", "#104b6d", "#3bbeaa", "#18441b", "#79ac3d", "#e27db1", "white",   # generated with Colorgorical (http://vrl.cs.brown.edu/color)
           "#e99863", "#5b0891", "#3986da", "#1f3e9e", "#8e80fb", "#e3488e", "#02b72e", 
           "#e26df8", "#52351d", "#852405", "#9ca08c", "#2524f9", "#e194be", "#fa1bfc",
           "#851657"]
xkcd = list(colors.XKCD_COLORS.keys())  
mycols1.extend(xkcd)


def AxialGeomPlot(core, which, time=0, label=False, dictname=None,
                  figname=None, fren=False, asstype=False,
                  style='axgeom.mplstyle',
                  zcuts=False, title=None, scale=1, floating=False,
                  legend=False, seed=None, showhomog=False, **kwargs):
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
        Cooling Zones). Defaulit is "NE.config".
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
    zcuts : bool, optional
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
    if style == 'axgeom.mplstyle':
        pwd = Path(__file__).parent
        axgesty = str(Path.joinpath(pwd, style))
    else:
        if not Path(style).exists():
            print(f'Warning: {style} style sheet not found! \
                  Switching to default...')
        else:
            axgesty = style

    L = core.AssemblyGeom.edge*2
    # array of assembly type
    NxNy = core.Map.type.size
    config = core.NE.config[time]
    typelabel = np.reshape(config, (NxNy, 1))
    # explore types of assembly to be plotted
    types = []
    for i in which:
        t = core.getassemblytype(i, config, isfren=fren)
        if t not in types:
            types.append(t)

    if showhomog:
        reg = list(set(core.NE.labels.values()))
    else:
        reg = []
        regapp = reg.append
        for NEty, assbly in core.NE.AxialConfig.cuts.items():
            for l in assbly.labels:
                if l not in reg:
                    regapp(l)
    nReg = len(reg)

    # --- pick more colors
    if len(mycols1) < nReg:
        if seed is None:
            np.random.seed(1)
        N = nReg-len(mycols1)
        # assign random colours
        for icol in range(N):
            mycols1.append(np.random.randint(3,))
    # color dict
    asscol = dict(zip(reg, mycols1))

    # open figure
    idx = 0
    labels = []
    xlo, xup = np.inf, 0
    ylo, yup = np.inf, 0
    # --- plot with default or user style
    with plt.style.context(axgesty):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        kxy = (core.Map.serpcentermap).items()
        if fren:
            which = [core.Map.fren2serp[k] for k in which]
        else:
            tmp = list((core.serpcentermap).keys())
            which = [tmp[k] for k in which]
        xx = []
        for key, coord in kxy:
            # check key is in which list
            if key not in which:
                continue

            if floating:
                idx = idx + 2*L
                x, y = idx, None
            else:
                x, y = coord

            xx.append(x)
            # parse axial coordinates
            asstype = core.NE.assemblytypes[core.getassemblytype(key, config)]

            loz = np.asarray(core.NE.AxialConfig.cuts[asstype].loz)
            upz = np.asarray(core.NE.AxialConfig.cuts[asstype].upz)
            reg = np.asarray(core.NE.AxialConfig.cuts[asstype].reg)
            lab = np.asarray(core.NE.AxialConfig.cuts[asstype].labels)
            zmin = min(loz)
            zmax = max(upz)
            deltaz = upz-loz
            for iz, dz in enumerate(deltaz):
                # scale coordinate
                coord = ((x-L/2)*scale, loz[iz]*scale)
                # update ax limits
                xlo = coord[0] if coord[0] < xlo else xlo
                ylo = coord[1] if coord[1] < ylo else ylo
                xup = coord[0] if coord[0] > xup else xup
                yup = coord[1] if coord[1] > yup else yup
                # define assembly patch
                asspatch = Rectangle(coord, L, dz, color=asscol[lab[iz]],
                                    label=lab[iz], ec='k', lw=0.5, **kwargs)
                ax.add_patch(asspatch)

                if dictname is None:

                    if label:  # plot assembly number
                        if fren:  # FRENETIC numeration
                            txt = str(core.Map.serp2fren[key])  # translate keys
                        else:
                            txt = str(key)
                        txtcol = 'w' if isDark(asscol[lab[iz]]) else 'k'
                        plt.text(x*scale, (loz[iz]+dz/2)*scale, txt, ha='center',
                                va='center', color=txtcol)
                else:
                    if asstype:
                        for assN, txt in dictname:
                            txt = dictname[typelabel[key-1, 0]]
                            txtcol = 'w' if isDark(asscol[lab[iz]]) else 'k'
                            x, y = core.Map.serpcentermap[core.Map.fren2serp[assN]]
                            plt.text(x*scale, (loz[iz]+dz/2)*scale, txt,
                                    ha='center', va='center',
                                    color=txtcol)

            # add my cuts on top of patch
            if zcuts and 'zcuts' in core.NE.AxialConfig.__dict__.keys():
                for myz in core.NE.AxialConfig.zcuts:
                    plt.hlines(myz*scale, (x-L/2)*scale, (x+L/2)*scale,
                               linestyles='-.', linewidth=0.5, edgecolor='k')

        plt.axis('off')
        ax.set_xlim([min(xx)-L/2, max(xx)+L/2])
        ax.set_ylim([zmin-L/2, zmax+L/2])
        plt.title(title)
        # add legend, if any
        if legend:
            handles, labels = plt.gca().get_legend_handles_labels()
            by_label = OrderedDict(zip(labels, handles))
            plt.legend(by_label.values(), by_label.keys(), ncol=4,
                       loc="upper center", bbox_transform=ax.transData,
                       bbox_to_anchor=(np.mean(xx), zmin-0.1))
        plt.tight_layout()
        # save figure
        if figname is not None:
            fig.savefig(figname)


def RadialMap(core, tallies=None, z=0, time=0, pre=0, gro=0, grp=0,
              label=False, figname=None, which=None, fren=False,
              whichconf='NE', asstype=False, dictname=None,
              legend=False, fill=True, style='radgeom.mplstyle',
              axes=None, cmap='Spectral_r', thresh=None,
              cbarLabel=True, xlabel=None, ylabel=None,
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
    if style == 'radgeom.mplstyle':
        pwd = Path(__file__).parent
        radgesty = str(Path.joinpath(pwd, style))
    else:
        if not Path(style).exists():
            print(f'Warning: {style} style sheet not found! \
                  Switching to default...')
        else:
           radgesty = style

    if core.AssemblyGeom.type == "S":
        orientation = np.pi/4
        L = core.AssemblyGeom.edge
        L = L/2*np.sqrt(2)
    elif core.AssemblyGeom.type == "H":
        orientation = 0
        L = core.AssemblyGeom.edge

    if tallies is None:

        NxNy = core.Map.type.size
        config = core.__dict__[whichconf].config[time]
        # array of assembly type
        typelabel = np.reshape(config, (NxNy, 1))
        maxtype = int(max(typelabel))
        coretype = range(0, maxtype+1)  # define

        # color dict
        asscol = dict(zip(coretype, mycols1))

    # check which variable
    amap = core.Map
    if which is None:  # consider all assemblies
        which = list(amap.serpcentermap.keys())
    else:
        if fren:  # FRENETIC numeration
            which = [amap.fren2serp[k] for k in which]

    if thresh is None:
        thresh = -np.inf
    elif not isinstance(thresh, (Real, int, np.float)):
        raise TypeError(
            "thresh should be real, not {}".format(type(thresh)))
    # open figure
    with plt.style.context(radgesty):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        usetex = True if rcParams['text.usetex'] else False
        if usetex:
            rcParams.update({'text.usetex' : False})
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
                atype = core.getassemblytype(k, config)
                asspatch = RegularPolygon(xy, core.AssemblyGeom.numedges, L*scale,
                                        orientation=orientation, color=col, ec='k', lw=0.5,
                                        fill=fill, label=core.NE.assemblylabel[atype], **kwargs)
                ax.add_patch(asspatch)

        if tallies is not None:  # plot physics
            coord = np.asarray(coord)
            values = np.asarray(values)
            patches = np.asarray(patches, dtype=object)
            normalizer = normalizerFactory(values, None, False,
                                           coord[:, 0]*scale,
                                           coord[:, 1]*scale)
            pc = PatchCollection(patches, cmap=cmap, ec='k', lw=0.5, **kwargs)

            if title:
                nodes = core.NE.AxialConfig.AxNodes
                idz = np.argmin(abs(z-nodes))
                times = core.TimeProf
                idt = np.argmin(abs(time-times))
                title = 'z={nodes[idz]:.2f} [cm], t={times[idt]:.2f} [s]'

            formatPlot(ax, loglog=loglog, logx=logx, logy=logy,
                       xlabel=xlabel or "X [cm]",
                       ylabel=ylabel or "Y [cm]", title=title)
            pc.set_array(values)
            pc.set_norm(normalizer)
            ax.add_collection(pc)
            addColorbar(ax, pc, cbarLabel=cbarLabel)

            # add labels on top of the polygons
            if label:
                if fmt is None:
                    fmt = "%.1e" if abs(np.max(np.max(tallies))) > 999 else "%.1f"
                else:
                    fmt = fmt
                for key, coord in (core.Map.serpcentermap).items():
                    # check key is in "which" list
                    k = core.Map.serp2fren[key] if fren else key
                    if k not in which or tallies[k-1] <= thresh:
                        continue
                    else:
                        x, y = coord
                        # plot text inside assemblies
                        txtcol = 'w' # if isDark(asscol[lab[iz]]) else 'k'
                        txt = fmt % tallies[amap.serp2fren[key]-1] if fren else fmt % tallies[key-1]
                        plt.text(x*scale, y*scale, txt, ha='center',
                                va='center', color=txtcol)
                    
        else:
            # add labels on top of the polygons
            for key, coord in (core.Map.serpcentermap).items():
                # check key is in "which" list
                if key not in which:
                    continue
        
                x, y = coord
                col = asscol[typelabel[key-1, 0]]
                # plot text inside assemblies
                if dictname is None:
                    if label:  # plot assembly number
                        if fren:  # FRENETIC numeration
                            txt = str(core.Map.serp2fren[key])  # translate keys
                        else:
                            txt = str(key)
                        txtcol = 'w' if isDark(col) else 'k'
                        plt.text(x*scale, y*scale, txt, ha='center',
                                va='center', color=txtcol) # 
                else:
                    if asstype:  # plot assembly type
                        txt = dictname[typelabel[key-1, 0]]
                        txt = txt.split("-")[0]
                        if len(txt) > 3:
                            txt = txt[0:3]
                        txtcol = 'w' if isDark(col) else 'k'
                        plt.text(x*scale, y*scale, txt, ha='center', va='center',
                                 color=txtcol)

                    # FIXME: must be a better way to do this avoiding asstype, maybe.
                    # change "dictname" because maybe we want tuples to have
                    # overlappings (phytra fig) write other labels
                    else:
                        atype = core.getassemblytype(key, time=time)
                        x, y = core.Map.serpcentermap[key]
                        try:
                            assk = str(core.Map.serp2fren[key]) if fren else key
                            txt = dictname[int(assk)]
                            txtcol = 'w' if isDark(col) else 'k'
                            plt.text(x*scale, y*scale, txt, ha='center',
                                    va='center', color=txtcol)
                        except KeyError:
                            continue

        ax.axis('equal')
        if xlabel is None and ylabel is None:
            plt.axis('off')

            if tallies is None:
                # add legend, if any
                if legend:
                    if usetex:
                        rcParams.update({'text.usetex' : True})
                    handles, labels = plt.gca().get_legend_handles_labels()
                    by_label = OrderedDict(zip(labels, handles))
                    plt.legend(by_label.values(), by_label.keys(), ncol=4,
                            loc='lower center', bbox_to_anchor=(0.5, -0.2))

        plt.tight_layout()
        # save figure
        if figname is not None:
            fig.savefig(figname)


def SlabPlot(core, time=0, ax=None, xlabel=None, figname=None, ncols=None, style='axgeom.mplstyle'):
    """Plot regions in config (NOT IN CUTS OBJECT)."""
    if style == 'axgeom.mplstyle':
        pwd = Path(__file__).parent
        axgesty = str(Path.joinpath(pwd, style))
    else:
        if not Path(style).exists():
            print(f'Warning: {style} style sheet not found! \
                  Switching to default...')
        else:
            axgesty = style
    # --- plot with default or user style
    with plt.style.context(axgesty):
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(111)
        else:
            ax = ax or plt.gca()

        reg = list(set(core.NE.labels.values()))
        nReg = len(reg)
        # color dict
        asscol = dict(zip(reg, mycols1))

        labels = []
        handles = []
        nConf = core.NE.config[time][0]
        which = core.NE.assemblytypes[nConf]
        cuts = core.NE.AxialConfig.config_str[which]
        for i, which in enumerate(cuts):
            col = asscol[core.NE.labels[which]]
            h1 = ax.axvspan(*core.NE.zcoord[i],
                            alpha=0.5, color=col, zorder=1)
            if i == 0: # add left boundary
                ax.axvline(core.NE.zcoord[i][0], color='k', lw=1, zorder=2)

            ax.axvline(core.NE.zcoord[i][1], color='k', lw=1, zorder=2)
            if core.NE.labels[which] not in labels:
                labels.append(core.NE.labels[which])
                handles.append(h1)

        if ncols is None:
            ncols = 4 if len(cuts) > 2 else 2
        # xlabel = xlabel if xlabel is not None else 'z coordinate [cm]'
        # ax.set_xlabel(xlabel)
        # ax.set_xticks(self.layers)
        plt.axis('off')

        ax.set_xlim((core.NE.AxialConfig.zcuts[0], core.NE.AxialConfig.zcuts[-1]))
        plt.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.3),
                ncol=ncols, framealpha=1, shadow=1) # mode="expand", 
        plt.tight_layout()
        # save figure
        if figname is not None:
            plt.savefig(figname)


def isDark(color):
    # taken from https://stackoverflow.com/questions/22603510/is-this-possible-to-detect-a-colour-is-a-light-or-dark-colour
    [r,g,b] = colors.to_rgb(color)
    r, g, b = r*255, g*255, b*255
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5): # 
        return False
    else:
        return True
