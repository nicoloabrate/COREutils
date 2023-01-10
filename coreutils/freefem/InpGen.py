"""
Author: N. Abrate.

File: InpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import logging
import pathlib
import numpy as np
from shutil import move, copyfile, SameFileError
from os.path import join
from coreutils.tools.utils import fortranformatter as ff
from coreutils.tools.plot import RadialMap
import matplotlib.pyplot as plt
from .InpNE import writeConfig, writeNEdata
import coreutils.tools.h5 as myh5
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

figfmt = ['png', 'pdf']

def inpgen(core, json, casename=None, plotNE=None, whichSA=None,
           fmt=1):
    """
    Make FreeFEM NE files if the required data are in core object.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    json : str
        Absolute path of the ``.json`` input file.
    casename : str, optional
        File path where the case directory is located, by default ``None``.
        In this case, the name of the FRENETIC case is 'case1'.
    templates : dict, optional
        File path where the template files are located, by default ``None``.
        In this case, the default template is used.
    H5fmt : bool, optional
        Set ``True`` to print NE data also in txt format, by default ``False``.

    Returns
    -------
    ``None``
    """
    # generate case directory-tree
    cwd = os.getcwd()
    iwd = os.path.dirname(json)
    if casename is None:
        casename = join(cwd, 'case1')

    if '.json' not in json:
        json = f"{json}.json"

    if not os.path.exists(iwd):
        raise OSError(f'{iwd} path does not exist!')

    casepath = mkdir(join(iwd, casename))
    AUXpath = mkdir("auxiliary", casepath)
    # --- save json to root directory
    jsonname = pathlib.Path(json).name
    try:
        copyfile(f'{json}', join(casepath, f'{jsonname}'))
    except SameFileError:
        os.remove(join(casepath, f'{jsonname}'))
        print(f'Overwriting file {jsonname}')
        copyfile(f'{json}', join(casepath, f'{jsonname}'))
    # --- save core object to root directory
    corefname = 'core.h5'
    grp_name = 'core'
    myh5.write(core, grp_name, corefname, chunks=True, compression=True,
               overwrite=True, skip=['NE.data'])
    try:
        copyfile(f'{corefname}', join(casepath, f'{corefname}'))
    except SameFileError:
        os.remove(join(casepath, f'{corefname}'))
        print(f'Overwriting file {corefname}')
        copyfile(f'{corefname}', join(casepath, f'{corefname}'))

    # make NE input (config.dat, macro.nml)    
    if hasattr(core, "NE"):
        NE = True
        isNE1D = True if core.dim == 1 else False
    else:
        NE = False

    if NE:
        NEpath = casepath
        # --- write config.inp
        writeConfig(core)

        # move NE files
        NEfiles = ['config.inp']
        for f in NEfiles:
            try:
                move(f, join(NEpath, f))
            except SameFileError:
                os.remove(join(NEpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(NEpath, f))
    else:
        logging.warn('No NE object, so input.dat and config.inp not written!')

    # write NE data
    if hasattr(core.NE, 'data') or isNE1D:
        NEpath = casepath
        # -- prepare data
        # get temperatures couples
        temp = core.TfTc
        # get NGRO
        unifuel = None

        # reference temperatures defined as minima
        mincouple = min(temp, key=lambda t: (t[1]+t[0]))
        Tf, Tc = mincouple
        NGRO = core.NE.nGro
        # -- write NE_data.h5
        writeNEdata(core, verbose=False, fmt=fmt)
        try:
            f = 'NEinputdata'
            move(f, join(casepath, f))
        except SameFileError:
            os.remove(join(casepath, f))
            print('Overwriting dir {}'.format(f))
            move(f, join(casepath, f))
    else:
        logging.warn('macro.nml and NE_data.h5 not written!')

    # plot configurations
    if NE:
        AUX_NE_plot = []
        asslabel = core.NE.assemblytypes
        if core.dim != 1:
            for fmt in figfmt:
                # --- radial map (assembly numbers)
                figname = f'NE-rad-map.{fmt}'
                AUX_NE_plot.append(figname)
                RadialMap(core, label=True, fren=False, whichconf="NE", 
                          legend=True, asstype=True, figname=figname)
                # --- radial configurations
                for itime, t in enumerate(core.NE.time):
                    figname = f'NE-rad-conf{itime}-t{1E3*t:g}_ms.{fmt}'
                    AUX_NE_plot.append(figname)
                    RadialMap(core, time=t, label=True, fren=False, 
                              whichconf="NE", dictname=asslabel,
                              legend=True, asstype=True, figname=figname)

        else:
            SAs = None

        f = 'configurations.xlsx'
        try:
            move(f, join(AUXpath, f))
        except SameFileError:
            os.remove(join(AUXpath, f))
            print('Overwriting file {}'.format(f))
            move(f, join(AUXpath, f))

        # move files in directory
        for f in AUX_NE_plot:
            try:
                move(f, join(AUXpath, f))
            except SameFileError:
                os.remove(join(AUXpath, f))
                print('Overwriting file {}'.format(f))
                move(f, join(AUXpath, f))


def mkdir(dirname, indirs=None):
    """
    Make a new directory named dirname inside path.

    Parameters
    ----------
    dirname : string
        directory name
    indirs : list, optional
        List of directories where the new directory is created, by default
        ``None``

    Returns
    -------
    path : str
        Path of created directory
    """
    if indirs is None:
        path = dirname
    else:
        if isinstance(indirs, list) is False:
            indirs = [indirs]
        for i, p in enumerate(indirs):
            if i == 0:
                path = p
            else:
                path = join(path, p)
        path = join(path, dirname)

    os.makedirs((path), exist_ok=True)

    return path
