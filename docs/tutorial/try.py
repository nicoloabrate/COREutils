# import modules
import sys
import os
import numpy as np
import pandas as pd
import serpentTools
from matplotlib import rc
# from uncertainties import ufloat, unumpy

# add "coremap" directories to path
coremapath = 'C:\\Users\\39346\\Documents\\mycodes\\coreutils\\coremap'
sys.path.append(coremapath)
from CoreMap import CoreMap, uncformat
import matplotlib as mpl
mpl.rcParams['figure.dpi']= 200  # set dpi for increasing plot rendering quality
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# for Palatino and other serif fonts use:
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
rc('text', usetex=True)

# input file name and location
fname = 'alfred_1_6.txt'

# define geometrical parameters
L = 17.1  # pitch [cm]
rotangle = 60  # rotation angle [degree]

# instance initialisation
core = CoreMap(fname, rotangle, L)

# load ALFRED's safety rods
SR_fren_position = [92, 326, 237, 3]  # assemblies to be perturbed
SR_type = [5]  # new assembly type
core.loadassembly(SR_type, SR_fren_position, flagfren=True)

# plot new geometry without any label
core.plot(label=True, fren=True, scale=5)

cut1 = [2, 81, 94, 106, 117, 127, 136, 185, 1]
cut2 = [3, 15, 26, 36, 45, 53, 60, 66, 71, 75, 78]
cuts = [*cut1, *cut2]
# plot only selected assemblies
core.plot(label=True, which=[*cut1, *cut2], fren=True, fontsize=7)

# Serpent (v 2.1.31) output path
# read Serpent output file with serpentTools
H = 3  # axial bin width
datapath = 'C:\\Users\\39346\\Desktop\\ricerca\\sarotto\\traverse\\%gcm' % H
fname = os.path.join(datapath, "ALFRED_FC_HFP_det0.m")
alfred = serpentTools.read(fname)

# take useful detectors
POW = alfred.detectors['POW']
FLX = alfred.detectors['FLX']

# take geometry feature
Nz, Nx, Ny = POW.tallies.shape
zcoord = POW.grids['Z']

# workaround to fix Serpent-2 numeration bug
assnum = np.arange(2+Nx, Nx*Ny+2+Nx)

# select Serpent assemblies matching cuts
serpcuts = np.asarray([core.fren2serp[k]+Nx+1 for k in cuts])

# compute tally volume
zcoord = FLX.grids['Z']
H_FLX = 340/len(zcoord)
core.assembly.compute_volume(H_FLX)

# preallocations
dataset_mean = np.empty((Nz, len(cuts)))
dataset_std = np.empty((Nz, len(cuts)))
val = []
valappend = val.append
peak_factor = np.max(np.max(FLX.tallies))
print(np.where(FLX.tallies == peak_factor))
print(FLX.tallies[np.where(FLX.tallies == peak_factor)])

# reshape dataset
for iZ, z in enumerate(zcoord):
    # slice results
    tallies = FLX.tallies[iZ, :, :]
    errors = FLX.errors[iZ, :, :]
    # try to plot physics
    tallies = tallies/peak_factor # core.assembly.volume  # average flux over the bin volume
    if iZ == 10:
        print(np.max(tallies))
    # flattening sq. or hex. lattice by rows
    tallies = tallies.flatten('C')
    if iZ == 10:
        print(np.where(tallies==np.max(tallies)))
    # define standard deviation coming from Serpent
    errors = (errors.flatten('C'))
    # extract assemblies belonging to cut1 and cut2
    mean = list(tallies[serpcuts])
    if iZ == 10:
        print(mean)
    std = list(errors[serpcuts])
    # define uncertain array
    x = uncformat(mean, std, fmtn=".2E", fmts='%.2f') #unumpy.uarray(mean, std)
    valappend(x)
    # check consistency
    # define dict
    tallies = dict(zip(assnum, tallies))
    errors = dict(zip(assnum, errors))
    dataset_mean[iZ, :] = mean
    dataset_std[iZ, :] = std

# convert val to numpy array
val = np.asarray(val)
#pd.set_option('display.float_format', '{:.2eP}'.format)
pd.options.display.max_rows
pd.set_option('display.max_colwidth', None)

# define rows label
rows = map(lambda z: "z="+str(z)+" [cm]", zcoord[:,2]) #zip("z="*len(zcoord), zcoord[:,2])

print(FLX.tallies[10, 11, 14]/peak_factor)

# display results of 1st cut
df1 = pd.DataFrame(val[:, 0:len(cut1)], columns=cut1, index=list(rows))

# display results of 2nd cut
rows = map(lambda z: "z="+str(z)+" [cm]", zcoord[:,2])
df2 = pd.DataFrame(val[:, len(cut1):len(cuts)], columns=cut2, index=list(rows))

peak_factor = np.max(np.max(FLX.tallies))
print(np.where(FLX.tallies == peak_factor))
print(FLX.tallies[np.where(FLX.tallies == peak_factor)])
zplot = np.arange(0, 20) #[0, 4, 9, 10, 19]
for iZ, z in enumerate(zplot):
    tallies = FLX.tallies[iZ, :, :]
    errors = FLX.errors[iZ, :, :]
    # try to plot physics
    tallies = tallies/peak_factor
    # flattening sq. or hex. lattice by rows
    tallies_mod = tallies.flatten('C')
    errors = errors.flatten('C')
    tallies_mod = dict(zip(assnum, tallies_mod))
    errors = dict(zip(assnum, errors))
    core.plot(what={"tallies": tallies_mod},
          label=True, fren=True, fontsize=3,
          cbarLabel="1G total flux [-]", title="midplane z=%.1f cm" % zcoord[z,2]) # , "errors": errors
