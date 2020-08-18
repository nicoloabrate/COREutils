# import modules
import sys
import os
import numpy as np
import serpentTools
from matplotlib import rc
# add "coremap" directories to path
coremapath = 'C:\\Users\\39346\\Documents\\mycodes\\coreutils\\coremap'
sys.path.append(coremapath)
from CoreMap import CoreMap as cm
import matplotlib as mpl
mpl.rcParams['figure.dpi']= 200  # set dpi for increasing plot rendering quality

# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# for Palatino and other serif fonts use:
rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
rc('text', usetex=True)

# input file name and location
fname = 'alfred_1_6.txt'

# define geometrical parameters
L = 1.386  # pitch [cm]
rotangle = 60  # rotation angle [degree]

# instance initialisation
core = cm(fname, rotangle, L)

# Do you want to load new assemblies?
# let's load ALFRED's safety rods
SR_fren_position = [92, 326, 237, 3]  # assemblies to be perturbed
SR_type = [5]  # new assembly type
core.loadassembly(SR_type, SR_fren_position, flagfren=1)

# Do you want custom labels? Just define them using a python dictionary
coretype = [1, 2, 3, 4, 5, 6, 7]  # list with assembly numbers
corelabel = ['IF', 'OF', 'DR', 'CR', 'SR', 'BA', 'EL']  # list with assembly names (string)
asslabel = dict(zip(coretype, corelabel))  # zip lists and make the zip a dictionary

# plot with customised assembly labels
core.plot(label=True, dictname=asslabel, figname='ALFRED_LEADER.png', asstype=True)  # specify figname to save the figure

ass = [*np.arange(1, 14), 1, *np.arange(80, 92)]  # list with assembly numbers
label = [*['X']*13, *['O']*14]  # list with assembly names (string)
asslabel = tuple(zip(ass, label))  # zip lists and make the zip a dictionary

# plot with customised assembly labels
core.plot(label=True, dictname=asslabel, figname='ALFRED_LEADER_cuts.png')  # specify figname to save the figure