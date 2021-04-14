"""
Created on Thu Feb 25 14:53:51 2021

author: N. Abrate.

file: .py

description:
"""
# import external modules
import sys
import os
import numpy as np
import serpentTools
from matplotlib import rc
# add "coreutils" directories to path
sys.path.append(os.path.abspath('../../../../../'))
from coreutils.core.Core import Core
from coreutils.core.plot import RadialGeomPlot
import matplotlib as mpl
mpl.rcParams['figure.dpi']= 200  # set dpi for increasing plot rendering quality

rc('font', **{'family': 'sans-serif', 'sans-serif': ['Arial']})
rc('text', usetex=True)

# input file name and location
try:
    os.chdir("EBR-II")
except FileNotFoundError:
    pass

filepath = os.path.join("input.json")
ebrII = Core(filepath)
RadialGeomPlot(ebrII, label=True, fren=True, fontsize=3.5, legend=True,
               figname='EBR-II.png')