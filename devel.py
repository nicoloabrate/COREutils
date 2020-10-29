"""
Created on Sat Oct 24 18:10:50 2020

author: N. Abrate.

file: .py

description:
"""
import os
import sys
sys.path.append(os.path.abspath('../'))
print(sys.path)
from coreutils.core.Core import Core
from coreutils.frenetic.InpGen import inpgen

alfred = Core("input.json")
inpgen(alfred)