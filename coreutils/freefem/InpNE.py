"""
Author: N. Abrate.

File: FreneticInpGen.py

Description: Set of methods for generating FRENETIC input files.

"""
import io
import os
import json
import logging
from shutil import rmtree
import numpy as np
import pandas as pd
import h5py as h5
from coreutils.tools.utils import fortranformatter as ff
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


def writeNEdata(core, verbose=False, fmt=1):
    """
    Generate FRENETIC NE module input (HDF5 file or many txt).

    Parameters
    ----------
    core : obj
        Core object created with Core class
    verbose : bool, optional
        Set to ``True`` in order to print also capture, nubar and scattering
        production data. Default is ``False``
    inf : bool, optional
        Set to ``False`` to get B1 Serpent calculation mode for the
        multi-group constants. Default is ``True``
    txtfmt : bool, optional
        Set to ``True`` to print data also in .txt format. Default is ``False``

    Returns
    -------
    ``None``
    """
    # --- define list of output filenames
    outnames = ["DIFFCOEF", "ESIGF", "NUSF", "XS_FISS", "XS_SCATT", "XS_TOT",
                "CHIT", "XS_REM"]
    matkeys = ['Diffcoef', 'Esigf', 'Nsf', 'Fiss', 'S0', 'Tot', 'Chit',
                'Remxs']

    outnames = tuple(outnames)
    matkeys = tuple(matkeys)
    datakeys = dict(zip(matkeys, outnames))

    # --- define temperature matrix to be filled with data
    temps = core.TfTc
    Tf, Tc = zip(*temps)
    n, m = len(set(Tf))+2, len(set(Tc))+1  # temp matrix dimensions
    frendata = np.zeros((n, m))
    frendata[0, 0], frendata[0, 1] = n-2, m-1  # write matrix size
    frendata[2:, 0] = core.Tf
    frendata[1, 1:] = core.Tc

    # create directory
    if os.path.isdir("NEinputdata"):
        print("'NEinputdata' directory exists. Overwriting...")
        ans = "yes" # input()
    else:
        ans = "no"

    if ans == "yes" or ans == "y":
        rmtree("NEinputdata")
        os.mkdir("NEinputdata")
    else:
        os.mkdir("NEinputdata")

    # define tuple of couples of temperatures
    temps.sort(key=lambda t: t[0])
    regmap = core.NE.regions.reverse()
    NEdata = core.NE.data
    if fmt == 0:
        for reg in core.NE.data[temps[0]].keys():
            ireg = regmap[reg]
            # update region (hexagon) type counter
            for data, dataname in datakeys.items():  # loop over data
                where = {}
                # temperature couples loop
                for itup, tup in enumerate(temps):
                    # store value in proper position in temp matrix
                    row = np.where(frendata[:, 0] == tup[0])
                    col = np.where(frendata[1, :] == tup[1])
                    where[tup] = (row, col)
                # -- split homogdata in regions and groups
                for g in range(core.NE.nGro):  # loop over energy groups
                    # check if matrix
                    if 'S' in data or 'Sp' in data:
                        for gdep in range(core.NE.nGro):  # loop over departure g
                            # edit name to include info on dep group
                            txtname = f"{dataname}_{ireg}_{gdep+1}_{g+1}"
                            gc = gdep+core.NE.nGro*g
                            for itup, tup in enumerate(temps):
                                # select matrix entry
                                r, c = where[tup]
                                S0 = NEdata[tup][reg].__dict__[data].flatten(order='F')
                                frendata[r, c] = S0[gc]
                                # write output if last tuple is reached
                                if itup == len(temps)-1:
                                    # write txt file
                                    mysavetxt(txtname, frendata)


                    else:
                        txtname = f"{dataname}_{ireg}_{g+1}"
                        for itup, tup in enumerate(temps):  # loop over temps
                            # select matrix entry
                            r, c = where[tup]
                            if 'Esigf' in data:
                                frendata[r, c] = NEdata[tup][reg].__dict__['Fiss'][g]*NEdata[tup][reg].__dict__['Kappa'][g]*1.60217653e-13                  
                            else:
                                frendata[r, c] = NEdata[tup][reg].__dict__[data][g]
                            # write data if all T tuples have been spanned
                            if itup == len(temps)-1:
                                # write txt file
                                mysavetxt(txtname, frendata)
    elif fmt == 1:
        # temperature couples loop
        for itup, tup in enumerate(temps):
            for data, dataname in datakeys.items():  # loop over data
                for regtype, reg in core.NE.data[tup].items():
                    ireg = regmap[regtype]
                    # create temperatures group
                    tmpgrp = f'Tf_{tup[0]:g}_Tc_{tup[1]:g}'
                    if data not in ['Nsf', 'Esigf']:
                        xsdata = reg.__dict__[data]
                    else:
                        if data == 'Nsf':
                            nubar = reg.Nubar
                            fiss = reg.Fiss
                            xsdata = nubar*fiss
                        elif data == 'Esigf':
                            kappa = reg.Kappa
                            fiss = reg.Fiss
                            xsdata = kappa*fiss*1.60217653e-13
                    # save in txt file
                    if 'S0' in data:
                        tmp = np.array(xsdata.reshape(core.NE.nGro, core.NE.nGro), dtype=np.float)
                    else:
                        tmp = np.array(xsdata, dtype=np.float)
                    txtname = f"{dataname}_{ireg}_{tmpgrp}"
                    mysavetxt_noTemp(txtname, tmp)


def writeConfig(core):
    """
    Write config.inp file.

    Parameters
    ----------
    core : obj
        Core object created with Core class.

    Returns
    -------
    ``None``

    """
    f1 = io.open('config.inp', 'w', newline='\n')
    NAssTypes = len(core.NE.assemblytypes)

    writer = pd.ExcelWriter("configurations.xlsx", engine='xlsxwriter')
    workbook=writer.book

    rad_config = {}
    if core.dim != 1: # write map
        SAnumbers = core.writecorelattice(fname=None, numbers=True, string=False, fren=False)
        df_geom1 = pd.DataFrame(data=SAnumbers, index=np.arange(1, core.Map.Nx+1),
                                columns=np.arange(1, core.Map.Ny+1))
        df_geom1.name = 'SA numbering according to Serpent'

    sheetname = 'geometry'
    worksheet=workbook.add_worksheet(sheetname)
    writer.sheets[sheetname] = worksheet

    offset = 0
    startrow = 1
    if core.dim != 1:
        worksheet.write_string(0, 0, df_geom1.name)
        df_geom1.to_excel(writer, sheet_name=sheetname, startrow=1 , startcol=0)
        offset = df_geom1.shape[0] + 4
        startrow = df_geom1.shape[0] + 5

    for t in core.NE.time:  # loop over time
        # configuration dicts
        if core.dim != 1:
            rad_config[t] = core.writecorelattice(fname=None, time=t)

        # --- write config.inp file
        for n in range(1, core.NAss+1):  # loop over all assemblies (1 assembly in 1D)
            iType = core.getassemblytype(n, core.NE.config[t], isfren=False)
            aType = core.NE.assemblytypes[iType]
            x, y = core.Map.serpcentermap[n]
            # write to file region number and coordinates
            f1.write(f"{iType:04d} {x:.5f} {y:.5f}")  # write time instant for each cut
            f1.write('\n')

        # --- write dataframes for human-readable configuration file
        # dataframes for human-readable configuration file
        if core.dim != 1:
            df_rad = pd.DataFrame.from_dict(rad_config[t])
            df_rad.name = 'Radial configuration'
        
        sheetname = f't={t:.15e} (s)'
        worksheet=workbook.add_worksheet(sheetname)
        writer.sheets[sheetname] = worksheet

        offset = 0
        startrow = 1
        if core.dim != 2:
            worksheet.write_string(0, 0, df_ax.name)
            df_ax.to_excel(writer, sheet_name=sheetname, startrow=1 , startcol=1)
            offset = df_ax.shape[0] + 4
            startrow = df_ax.shape[0] + 5

        if core.dim != 1:
            worksheet.write_string(offset, 0, df_rad.name)
            df_rad.to_excel(writer, sheet_name=sheetname, startrow=startrow, startcol=0)

    writer.save()


def mysavetxt(fname, x, fmt="%.6e", delimiter=' '):
    """
    Write file in txt format.

    Parameters
    ----------
    fname : str
        File name.
    x : ndarray
        Data to be written in txt.
    fmt : str, optional
        Data output format. The default is "%.6e".
    delimiter : str, optional
        Delimiter between data. The default is ' '.

    Returns
    -------
    None.

    """
    fname = fname+".txt"  # add file extension
    fname = os.path.join("NEinputdata", fname)
    with open(fname, 'w') as f:
        if len(x.shape) == 1:
            x = x[:, np.newaxis]
        for idx, row in enumerate(x):
            if idx == 0:
                line = delimiter.join("%.0g" % value for value in row)
            else:
                line = delimiter.join(fmt % value for value in row)
            f.write(line + '\n')

def mysavetxt_noTemp(fname, x, fmt="%.6e", delimiter=' '):
    """
    Write file in txt format.

    Parameters
    ----------
    fname : str
        File name.
    x : ndarray
        Data to be written in txt.
    fmt : str, optional
        Data output format. The default is "%.6e".
    delimiter : str, optional
        Delimiter between data. The default is ' '.

    Returns
    -------
    None.

    """
    fname = fname+".txt"  # add file extension
    fname = os.path.join("NEinputdata", fname)
    with open(fname, 'w') as f:
        if len(x.shape) == 1:
            x = x[:, np.newaxis]
        for idx, row in enumerate(x):
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
        ans = "y"
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
