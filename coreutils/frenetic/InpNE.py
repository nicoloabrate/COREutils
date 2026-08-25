import io
import os
import json
import logging
from shutil import rmtree
import numpy as np
import pandas as pd
import h5py as h5
from coreutils.tools.utils import fortranformatter as ff
from coreutils.frenetic.frenetic_namelists import FreneticNamelist, FreneticNamelistError

# TODO: implementare gestione proprieta' fotoni
# TODO: quale coppia di temperature considero per i param. cinetici?
logger = logging.getLogger(__name__)


def writemacro(core, path, nmix, vel, lambda0, beta0,
               unimap, H5fmt):
    """
    Write the input file "macro.nml" for the NE module of FRENETIC.

    Parameters
    ----------
    core : obj
        Core object created with Core class
    path : pathlib object
        Path to file
    nmix : int
        Number of different regions after homogenisation in the core
    vel : ndarray
        Multi-group velocity [cm/s]
    lambda0 : ndarray
        Precursors' families decay constants
    beta0 : ndarray
        Precursors' families physical neutron delayed fraction
    temperatures : list
        List of tuples with T fuel and T coolant used to evaluate NE data
    unimap : dict
        Dictionary mapping in which list each universe is located in
        core.NE.MMGClibrary.data.data dict

    Returns
    -------
    ``None``
    """
    # BUG FIXME TODO
    nGrp = 0
    nDhp = 0
    nPrp = 0

    macronames = ["DIFFCOEF", "XS_TOT", "XS_SCATT", "XS_FISS", "NUSF", "ESIGF", "KERMA"]
    # FIXME kerma should be separated from photon data and set to zero if not present in the input data
    macronamesp = ["MUSIGP", "DIFFP", "XS_TOT_P", "XS_SCATT_P", "KERMAP"]
    inpnames = ["filediff", "filesigt", "filesigs", "filesigf", "filenusigf",
                "fileesigf", "filekerma"]
    inpnamesp = ["filemusigp", "filediffp", "filesigtp", "filesigsp", "filekermap"]

    nFrenCuts = len(core.NE.AxialConfig.zcuts)-1 if core.dim != 2 else 1
    
    # PATCH FIXME TODO
    iPar = 0
    temp = core.NE.MGClibrary.parameters.values
    (Tf, Tc) = temp[iPar]

    if core.NE.MGClibrary.n_prec is None:
        nPre = core.NE.nPre
    else:
        nPre = core.NE.MGClibrary.n_prec
    # -- write macro.nml file
    asstypeN = 0
    inpname = "macro.nml"
    filepath = path.joinpath(inpname)
    if filepath.exists():
        rmtree(filepath)
        logger.warning(f'Overwriting file {inpname}')

    f = io.open(filepath, 'w', newline='\n')
    f.write('&MACROXS0\n')
    f.write(f'nMat = {nmix} \n')
    f.write(f'nGro = {core.NE.MGClibrary.n_groups} \n')
    f.write(f'nPre = {nPre} \n')
    f.write(f'nDhp = {nDhp} \n')
    f.write(f'nGrp = {nGrp} \n')
    f.write(f'nPrp = {nPrp } \n')
    f.write('/\n\n')
    f.write('&MACROXS\n')
    f.write('iRHO = 0,\n')
    f.write(f'veloc0(1:{core.NE.MGClibrary.n_groups}) = ')

    for igro in range(core.NE.MGClibrary.n_groups):
        f.write('%s,' % ff(vel[igro]))

    if nGrp> 0:
        f.write(f'\nvelocP0(1:{core.NE.nGrp}) = 1.0E7')
        # FIXME FIXME FIXME at the moment the photon velocity is not computed
        # therefore hardcode value
        #for igrp in range(core.NE.nGrp):
        #    f.write('%s,' % ff(velp[igrp]))
    f.write(f'\nlambda0(1:{nPre}) = ')

    for iprec in range(nPre):
        if iprec == nPre-1:
            f.write(f'{ff(lambda0[iprec])} \n')
        else:
            f.write(f'{ff(lambda0[iprec])},')

    if nDhp > 0:
        f.write(' \n lambdaDHP0(1:1) = 1.000000d+99,\n') # FIXME FIXME FIXME large value for steady state
        f.write('betaDHP0(1:1) = 0.000000d+00,\n')
    f.write(f'iDiff(1:{nmix}) = {nmix}*2,\n')
    f.write(f'iSigT(1:{nmix}) = {nmix}*2,\n')
    f.write(f'iSigF(1:{nmix}) = {nmix}*2,\n')
    f.write(f'iSigS(1:{nmix}) = {nmix}*2,\n')

    if nGrp> 0:
        # FIXME KERMA should be placed in another if.. statement
        f.write(f'iKERMA(1:{nmix}) = {nmix}*2,\n')
        f.write(f'iSigP(1:{nmix}) = {nmix}*2,\n')
        f.write(f'iDiffP(1:{nmix}) = {nmix}*2,\n')
        f.write(f'iKERMAP(1:{nmix}) = {nmix}*2,\n')
        f.write(f'iSigtP(1:{nmix}) = {nmix}*2,\n')
        f.write(f'iSigsP(1:{nmix}) = {nmix}*2,\n')

    f.write(f'TempFuel0 = {ff(Tf)},\n')
    f.write(f'TempCool0 = {ff(Tc)},\n')

    for imix in range(nmix):

        # perform operations only when the assembly is changed
    
        whichmix = core.NE.regions[imix+1]
        chit = core.NE.MGClibrary.data[iPar][whichmix].get_MGC('chi_tot')[np.newaxis, :]
        chid = core.NE.MGClibrary.data[iPar][whichmix].get_MGC('chi_del')[np.newaxis, :]
        chip = core.NE.MGClibrary.data[iPar][whichmix].get_MGC('chi_pro')[np.newaxis, :]
        beta = core.NE.MGClibrary.data[iPar][whichmix].get_MGC('beta')

        chit = chip*(1-beta.sum())
        for ig in range(chip.shape[1]):
             chit[0, ig] += np.dot(beta, chid[0, :, ig])

        imixF = 0
        # look for root universe
        if core.dim == 2:
            u = whichmix
        else:
            for atype in core.NE.AxialConfig.config_str.keys():
                if whichmix in core.NE.AxialConfig.config_str[atype]:
                    u = atype
                    break

        # write universe number and name
        if core.dim == 1:
            f.write(f'\n!Mix n.{imix+1} is {whichmix}\n')
        elif core.dim == 2:
            f.write(f'\n!Mix n.{imix+1} is {whichmix}\n')
        else:
            f.write(f'\n!Mix n.{imix+1} is {whichmix} and belongs to {u}\n')

        # write kinetic and spectrum parameters
        f.write(f'chiT0({imix+1},1:{core.NE.MGClibrary.n_groups}) = ')
        if np.isnan(chit).any():
            raise FreneticNamelistError(f"NaN found in chiT data for mix {whichmix}!")

        for igro in range(core.NE.MGClibrary.n_groups):
            f.write(f'{ff(chit[imixF, igro])},')

        # single photon group --> all emitted in this group
        if nGrp> 0:
            f.write(f'\nzetaT0({imix+1:d},1:{core.NE.nGrp:d}) = 1.0E+0,')
            
        for igro in range(core.NE.MGClibrary.n_groups):
            if len(chid.shape) > 2:
                v = chid[imixF, 0, igro]
            else:
                v = chid[imixF, igro]
            f.write(f'\nchiD0({imix+1:d},{igro+1:d},1:{nPre:d}) = {nPre:d}*{ff(v)},')
        f.write('\n')
        imixF = imixF+1
        f.write(f'beta0({imix+1},1:{nPre}) = ')
        for iprec in range(nPre):
            f.write(f'{ff(beta0[iprec])},')

        f.write('\n')
        f.write('\n')
        # write macroscopic NE multi-group data
        for inp, macro in zip(inpnames, macronames):

            if macro == "XS_SCATT":

                if H5fmt == 0:
                    for igrostart in range(core.NE.MGClibrary.n_groups):
                        f.write(f'{inp}({imix+1},{igrostart+1},1:{core.NE.MGClibrary.n_groups}) =')
                        for igroend in range(core.NE.MGClibrary.n_groups):
                            f.write(f" 'NEinputdata/{macro}_{imix+1}_{igrostart+1}_{igroend+1}.txt', ")
                        f.write('\n')
                elif H5fmt == 1:
                    for igrostart in range(core.NE.MGClibrary.n_groups):
                        f.write(f'{inp}({imix+1},{igrostart+1},1:{core.NE.MGClibrary.n_groups}) =')
                        for igroend in range(core.NE.MGClibrary.n_groups):
                            f.write(f" '{macro}_{imix+1}_{igrostart+1}_{igroend+1}', ")
                        f.write('\n')
                elif H5fmt == 2:
                    for igrostart in range(core.NE.MGClibrary.n_groups):
                        f.write(f'{inp}({imix+1},{igrostart+1},1:{core.NE.MGClibrary.n_groups}) =')
                        for igroend in range(core.NE.MGClibrary.n_groups):
                            f.write(f" '{imix+1}/{macro}', ")
                        f.write('\n')

            else:
                if H5fmt == 0:
                    f.write(f'{inp}({imix+1},1:{core.NE.MGClibrary.n_groups}) =')
                    for igro in range(core.NE.MGClibrary.n_groups):
                        f.write(f" 'NEinputdata/{macro}_{imix+1:d}_{igro+1:d}.txt', ")
                    f.write('\n')
                elif H5fmt == 1:
                    f.write(f'{inp}({imix+1},1:{core.NE.MGClibrary.n_groups}) =')
                    for igro in range(core.NE.MGClibrary.n_groups):
                        f.write(f" '{macro}_{imix+1:d}_{igro+1:d}', ")
                    f.write('\n')
                elif H5fmt == 2:
                    f.write(f'{inp}({imix+1},1:{core.NE.MGClibrary.n_groups}) =')
                    for igro in range(core.NE.MGClibrary.n_groups):
                        f.write(f" '{imix+1}/{macro}', ")
                    f.write('\n')

        if nGrp > 0:
            for inp, macro in zip(inpnamesp, macronamesp):

                if macro == "XS_SCATT_P":
                    for igrostart in range(core.NE.nGrp):
                        f.write(f'{inp}({imix+1},{igrostart+1},1:{core.NE.nGrp}) =')
                        for igroend in range(core.NE.nGrp):
                            f.write(f" 'input/{macro}_{imix+1}_{igrostart+1}_{igroend+1}.txt', ")
                        f.write('\n')
                elif macro == "KERMA" or macro == "MUSIGP":
                    f.write(f'{inp}({imix+1},1:{core.NE.MGClibrary.n_groups}) =')
                    for igro in range(core.NE.MGClibrary.n_groups):
                        f.write(f" 'input/{macro}_{imix+1:d}_{igro+1:d}.txt', ")
                    f.write('\n')
                else:
                    f.write(f'{inp}({imix+1},1:{core.NE.nGrp}) =')
                    for igrp in range(core.NE.nGrp):
                        f.write(f" 'input/{macro}_{imix+1:d}_{igrp+1}.txt', ")
                    f.write('\n')

    # write namelist end
    f.write('/\n')


def writeNEdata(core, path, H5fmt, txt, verbose=False, ):
    """
    Generate FRENETIC NE module input (HDF5 file or many txt).

    Parameters
    ----------
    core : obj
        Core object created with Core class
    path : pathlib object
        Path to file
    verbose : bool, optional
        Set to ``True`` in order to print also capture, nu_fiss and scattering
        production data, by default ``False``
    inf : bool, optional
        Set to ``False`` to get B1 Serpent calculation mode for the
        multi-group constants, by default ``True``
    txtfmt : bool, optional
        Set to ``True`` to print data also in .txt format, by default ``False``

    Returns
    -------
    ``None``
    """
    # --- define list of output filenames
    if core.NE.MGClibrary.use_nxn:
        scat_key = 'Sp0'
    else:
        scat_key = 'S0'

    outnames = ["DIFFCOEF", "ESIGF", "NUSF", "XS_FISS", "XS_SCATT", "XS_TOT",
                "CHIT", "KERMA"]
    matkeys = ['Diffcoef', 'fiss_energy', 'nuSigma_fiss', 'Sigma_fiss', scat_key, 'Sigma_tot', 'chi_tot',
               'kerma']
    if verbose:
        xsverb = ['Sigma_rabs']
        verb_out = ["XS_ABS"]
        # append to default list of names
        outnames.extend(verb_out)
        matkeys.extend(xsverb)

    outnames = tuple(outnames)
    matkeys = tuple(matkeys)
    datakeys = dict(zip(matkeys, outnames))

    # -- create or overwrite hdf5 file (repro script)
    inpname = "NE_data.h5"
    h5filepath = path.joinpath(inpname)
    # --- open hdf5 file
    if h5filepath.exists():
        rmtree(h5filepath)
        logger.warning(f'Overwriting file {inpname}')

    fh5 = h5.File(h5filepath, "a")

    # --- write general info (Tf, Tc, energy grid)
    param_names = core.NE.MGClibrary.parameters.names
    param_value = core.NE.MGClibrary.parameters.values
    if len(param_names) != 2:
        raise ValueError(f"Cannot write FRENETIC input handling parameters {param_names}! Only 2 parameters (Tf, Tc) can be handled.")
    else:
        if 'Tf' in param_names and 'Tc' in param_names:
            idTf = param_names.index('Tf')
            idTc = param_names.index('Tc')
            temperatures = np.zeros((len(param_value), 2))
            for i, v in enumerate(param_value.values()):
                temperatures[i, 0] = v[idTf]
                temperatures[i, 1] = v[idTc]
        else:
            raise ValueError(f"Cannot write FRENETIC input handling parameters {param_names}! Only Tf and Tc can be parsed.")

    TfTc = [(float(Ttup[0]), float(Ttup[1])) for Ttup in temperatures]
    Tf = sorted( list( set(temperatures[:, 0]) ) )
    Tc = sorted( list( set(temperatures[:, 1]) ) )

    fh5.create_dataset('TfTc', data=temperatures)
    fh5.create_dataset('Tf', data=Tf)
    fh5.create_dataset('Tc', data=Tc)
    fh5.create_dataset('energy_grid', data=core.NE.MGClibrary.energy_grid)
    fh5.create_dataset('energy_grid_name', data=core.NE.MGClibrary.energy_grid_name)

    # --- define temperature matrix to be filled with data
    n = len(Tf) + 2
    m = len(Tc) + 1
    frendata = np.zeros((n, m))
    frendata[0, 0], frendata[0, 1] = n - 2, m - 1  # write matrix size
    frendata[2:, 0] = Tf
    frendata[1, 1:] = Tc

    if txt:
        # create directory
        
        if os.path.isdir(path.joinpath("NEinputdata")):
            logger.info("'NEinputdata' directory exists. Overwriting...")
            ans = "yes" # input()
        else:
            ans = "no"

        if ans == "yes" or ans == "y":
            rmtree(path.joinpath("NEinputdata"))
            os.mkdir(path.joinpath("NEinputdata"))
        else:
            os.mkdir(path.joinpath("NEinputdata"))

    # define tuple of couples of temperatures
    temperatures = sorted(temperatures, key=lambda t: t[0])
    regmap = core.NE.regions.reverse()
    NEdata = core.NE.MGClibrary.data
    if H5fmt != 2:
        # FIXME TODO remove [0] and make it more robust
        for reg in core.NE.MGClibrary.data[0].keys():
            ireg = regmap[reg]
            # update region (hexagon) type counter
            for data, dataname in datakeys.items():  # loop over data
                where = {}
                # temperature couples loop
                # FIXME TODO make it consistent with core.NE.MGClibrary.parameters
                for itup, tup in enumerate(temperatures):
                    # store value in proper position in temp matrix
                    row = np.where(frendata[:, 0] == tup[0])
                    col = np.where(frendata[1, :] == tup[1])
                    where[tuple(tup)] = (row, col)
                # -- split homogdata in regions and groups
                for g in range(core.NE.MGClibrary.n_groups):  # loop over energy groups
                    # check if matrix
                    if 'S0' in data or 'Sp0' in data:
                        for gdep in range(core.NE.MGClibrary.n_groups):  # loop over departure g
                            # edit name to include info on dep group
                            txtname = f"{dataname}_{ireg}_{gdep+1}_{g+1}"
                            gc = gdep + core.NE.MGClibrary.n_groups * g
                            for itup, tup in enumerate(temperatures):
                                # select matrix entry
                                r, c = where[tuple(tup)]
                                S0 = NEdata[itup][reg].__dict__[data].flatten(order='F')
                                frendata[r, c] = S0[gc]
                                # write output if last tuple is reached
                                if itup == len(temperatures) - 1:
                                    if txt or H5fmt == 0:
                                        # write txt file
                                        mysavetxt(txtname, frendata, path)
                                    # save in h5 file
                                    tmp = np.array(frendata, dtype=float)
                                    fh5.create_dataset(txtname, data=tmp)

                    else:
                        txtname = f"{dataname}_{ireg}_{g+1}"
                        for itup, tup in enumerate(temperatures):  # loop over temperatures
                            # select matrix entry
                            r, c = where[tuple(tup)]
                            if 'fiss_energy' in data:
                                frendata[r, c] = NEdata[itup][reg].__dict__['Sigma_fiss'][g]*NEdata[itup][reg].__dict__['fiss_energy'][g]*1.60217653e-13                  
                            else:
                                frendata[r, c] = NEdata[itup][reg].__dict__[data][g]
                            # write data if all T tuples have been spanned
                            if itup == len(temperatures) - 1:
                                if txt or H5fmt == 0:
                                    # write txt file
                                    mysavetxt(txtname, frendata, path)
                                # save in h5 file
                                tmp = np.array(frendata, dtype=float)
                                fh5.create_dataset(txtname, data=tmp)

    else:
        # TODO FIXME check order scattering matrix, which should be: 1_1, 1_2, 1_3 with arr<--dep. The
        # numbers indicates row and col, not groups..it should be lower triangular
        # temperature couples loop
        for itup, tup in enumerate(temperatures):
            for data, dataname in datakeys.items():  # loop over data
                for regtype, reg in core.NE.MGClibrary.data[itup].items():
                    ireg = regmap[regtype]
                    # create temperatures group
                    # temporary patch
                    tmpgrp = f'Tf_{tup[0]:g}_Tc_{tup[1]:g}'
                    if tmpgrp not in fh5.keys():
                        fh5.create_group(tmpgrp)
                    fh5_TfTc = fh5[tmpgrp]

                    if data not in ['nuSigma_fiss', 'fiss_energy']:
                        xsdata = reg.__dict__[data]
                    else:
                        if data == 'nuSigma_fiss':
                            nu_fiss = reg.nu_fiss
                            Sigma_fiss = reg.Sigma_fiss
                            xsdata = nu_fiss*Sigma_fiss
                        elif data == 'fiss_energy':
                            fiss_energy = reg.fiss_energy
                            Sigma_fiss = reg.Sigma_fiss
                            xsdata = fiss_energy*Sigma_fiss*1.60217653e-13
                    # save in h5 file
                    if 'S0' in data or 'Sp0' in data:
                        tmp = np.array(xsdata.reshape(core.NE.MGClibrary.n_groups, core.NE.MGClibrary.n_groups), dtype=float)
                    else:
                        tmp = np.array(xsdata, dtype=float)

                    irgrp = f'{ireg}'
                    if irgrp not in fh5_TfTc.keys():
                        fh5_TfTc.create_group(irgrp)
                    fh5_ih = fh5_TfTc[irgrp]
                    fh5_ih.attrs['region'] = str(regtype)
                    fh5_ih.attrs['label'] = str(core.NE.labels[regtype])

                    fh5_ih.create_dataset(dataname, data=tmp)


    fh5.close()
    # FIXME TODO 
    # # get MFP and diff. length for sanity check wrt splitz
    # DFLmin = {}
    # MFPmin = {}
    # DFLmax = {}
    # MFPmax = {}
    # for itup, tup in enumerate(temperatures):
    #     for regtype, reg in core.NE.MGClibrary.data[itup].items():
    #         if not hasattr(reg, 'DiffLength'):
    #             if not hasattr(reg, 'Sigma_rem'):
    #                 DiffLength = np.sqrt(reg.Diffcoef / reg.Sigma_abs)
    #             else:
    #                 DiffLength = np.sqrt(reg.Diffcoef / reg.Sigma_rem)
    #         else:
    #             DiffLength = reg.DiffLength

    #         if itup == 0:
    #             DFLmin[regtype] = DiffLength.min()
    #             DFLmax[regtype] = DiffLength.max()
    #             MFPmin[regtype] = reg.MeanFreePath
    #         else:
    #             if DFLmin[regtype] > DiffLength.min():
    #                 DFLmin[regtype] = DiffLength.min()
    #             if DFLmax[regtype] < DiffLength.max():
    #                 DFLmax[regtype] = DiffLength.max()
    #             if MFPmin[regtype] > reg.MeanFreePath:
    #                 MFPmin[regtype] = reg.MeanFreePath

    # if core.dim != 2:
    #     zNodes = core.NE.AxialConfig.AxNodes
    #     nNodes = len(zNodes)

    #     # preallocation
    #     DFLtoZ = {}
    #     for asstype in core.NE.AxialConfig.config_str.keys():
    #         DFLtoZ[asstype] = [] # np.zeros((nNodes, 3))

    #     nS = 0
    #     iNode = 0
    #     for iCut, z1z2 in core.NE.zcoord.items(): # span het. cuts
    #         z1, z2 = z1z2
    #         nE = nS+core.NE.AxialConfig.splitz[iCut]
    #         for node in core.NE.AxialConfig.AxNodes[nS:nE]: # 
    #             if node < z1 or node > z2:
    #                 raise OSError("Something is wrong with the nodes!")
    #             zn1 = z1 if iNode == 0 else zn2
    #             zn2 = zn1+core.NE.AxialConfig.dz[iNode]
    #             for asstype in core.NE.AxialConfig.config_str.keys():
    #                 reg = core.NE.AxialConfig.config_str[asstype][iCut]
    #                 DFLtoZ[asstype].append([zn1, zn2, DFLmax[reg]/core.NE.AxialConfig.dz[iNode]])
    #             iNode += 1
    #         nS = nE
    # else:
    #     # preallocation
    #     DFLtoZ = {}
    #     for asstype in core.NE.regions.values():
    #         DFLtoZ[asstype] = DFLmax[asstype]/np.sqrt(core.Geometry.AssemblyGeometry.area)

    # L_to_dz_file = path.parent.joinpath('auxiliary', 'NE', 'DiffLength_to_NodeSize.json')
    # with open(L_to_dz_file, 'w') as outfile:
    #     json.dump({"DFLtoZ": DFLtoZ}, outfile, indent=2)


def writeConfig(core, path):
    """
    Write config.inp file.

    Parameters
    ----------
    core : obj
        Core object created with Core class.
    path: pathlib object
        Path to file

    Returns
    -------
    ``None``

    """
    inpname = 'config.inp'
    filepath = path.joinpath(inpname)
    if filepath.exists():
        rmtree(filepath)
        logger.warning(f'Overwriting file {inpname}')

    f1 = io.open(filepath, 'w', newline='\n')
    NAssTypes = len(core.NE.assemblytypes)
    isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
    nAss = int(core.nAss/6*isSym+1) if isSym else core.nAss
    nZ = len(core.NE.AxialConfig.zcuts)-1 if core.dim != 2 else 1
    if core.NE.worksheet:
        writer = pd.ExcelWriter("configurationsNE.xlsx", engine='xlsxwriter')
        workbook=writer.book

    ax_config = {}
    rad_config = {}
    if core.dim != 1: # write map
        SAnumbers = core.writecorelattice(fname=None, numbers=True, string=False, fren=True)
        if core.NE.worksheet:
            df_geom1 = pd.DataFrame(data=SAnumbers, index=np.arange(1, core.Map.Nx+1),
                                    columns=np.arange(1, core.Map.Ny+1))
            df_geom1.name = 'HA numbering according to FRENETIC'

    if core.dim != 2:
        z_cuts = np.asarray(core.NE.AxialConfig.zcuts)
        z_centre = (z_cuts[:-1]+z_cuts[1:])/2
        ax_nodes = np.array([z_cuts[:-1], z_cuts[1:], core.NE.AxialConfig.splitz])
        if core.NE.worksheet:
            df_geom2 = pd.DataFrame(data=ax_nodes, index=["upper z", "lower z", "splitz"],
                                    columns=np.arange(1, len(z_cuts)))
            df_geom2.name = 'Axial subdivision'

    if core.NE.worksheet:
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

        if core.dim != 2:
            worksheet.write_string(offset, 0, df_geom2.name)
            df_geom2.to_excel(writer, sheet_name=sheetname, startrow=startrow, startcol=0)

    for t in core.NE.time:  # loop over time
        # configuration dicts
        if core.dim != 1:
            rad_config[t] = core.writecorelattice(fname=None, time=t)
        
        if core.dim != 2:
            ax_config[t] = np.zeros((nZ, nAss), dtype=object)

        # --- write config.inp file
        config_int = np.zeros((nZ, nAss), dtype=int)
        config_str = np.zeros((nZ, nAss), dtype=object)
        for n in range(1, nAss+1):  # loop over all assemblies (1 assembly in 1D)
            iType = core.getassemblytype(n, core.NE.config[t], isfren=True)
            aType = core.NE.assemblytypes[iType]
            if core.dim != 2:
                config_int[:, n-1] = core.NE.AxialConfig.config[iType]
                config_str[:, n-1] = core.NE.AxialConfig.config_str[aType]
            else:
                config_int[:, n-1] = iType
                config_str[:, n-1] = aType
        for iz in range(nZ):
            # f1.write('%s ' % ff(t, 'double'))  # write time instant for each cut
            # FIXME set fixed precision even for t=0
            f1.write(f"{ff(t)} ")  # write time instant for each cut
            # define region number
            typestr = np.array(['{:04d}'.format(x) for x in config_int[iz, :]])
            # write to file
            f1.write('%s' % ' '.join(typestr))
            f1.write('\n')

        # --- write dataframes for human-readable configuration file
        if core.NE.worksheet:
            # dataframes for human-readable configuration file
            if core.dim != 2:
                df_ax = pd.DataFrame.from_dict(config_str)
                df_ax.name = 'Axial configuration'
                df_ax.index = z_centre

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

            writer.close()
            writer.handles = None


def makeNEinput(core, path, H5fmt=2):
    """
    Make input.inp file.

    Parameters
    ----------
    core : obj
        Core object created with Core class
    path: pathlib object
        Path to file
    template : str, optional
        File path where the template file is located, by default ``None``.
        In this case, the default template is used

    Returns
    -------
    ``None``
    """
    if H5fmt is False:
        H5fmt = 1

    if core.dim != 2:
        tmp = core.NE.AxialConfig.splitz
        nZ = len(core.NE.AxialConfig.zcuts)-1
        if isinstance(tmp, (int)):
            splitz = [tmp]*nZ
        elif isinstance(tmp, (list, np.ndarray)):
            splitz = tmp if len(tmp) > 1 else [tmp[0]]*nZ
        else:
            raise OSError(f'splitz in core.NEAxialsConfig.splitz cannot'
                          f'be of type {type(tmp)}')
        meshz = core.NE.AxialConfig.zcuts
    else:
        nZ = 1
        splitz = [1]
        meshz = [0, 0]

    nConfig = len(core.NE.time)
    # core.trans = False if max(core.NE.time) == 0 else True
    nRun = 2 if core.trans else 1

    frnnml = FreneticNamelist()
    inpname = "input.inp"
    filepath = path.joinpath(inpname)
    if filepath.exists():
        rmtree(filepath)
        logger.warning(f'Overwriting file {inpname}')

    f = io.open(filepath, 'w', newline='\n')

    for namelist in frnnml.files["NEinput.inp"]:
        f.write(f"&{namelist}\n")
        for key, val in core.FreneticNamelist[namelist].items():
            # format value with FortranFormatter utility
            val = ff(val)
            # "vectorise" in Fortran input if needed
            if key in frnnml.vector_inp:
                isSym = core.FreneticNamelist['PRELIMINARY']['isSym']
                N = int(core.nAss/6*isSym+1) if isSym else core.nAss
                val = f"{N}*{val}"
            f.write(f"{key} = {val}\n")
        # write to file
        f.write("/\n")


def mysavetxt(fname, x, path, fmt="%.6e", delimiter=' '):
    """
    Write file in txt format.

    Parameters
    ----------
    fname : str
        File name.
    x : ndarray
        Data to be written in txt.
    fmt : str, optional
        Data output format, by default "%.6e".
    delimiter : str, optional
        Delimiter between data, by default ' '.

    Returns
    -------
    None.

    """
    fname = fname+".txt"  # add file extension
    fname = path.joinpath("NEinputdata").joinpath(fname)
    with open(fname, 'w') as f:
        for idx, row in enumerate(x):
            if idx == 0:
                line = delimiter.join("%.0g" % value for value in row)
            else:
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
