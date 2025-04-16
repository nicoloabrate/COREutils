import numpy as np
import pandas as pd
from coreutils.eranos.InpKIN3D import *
from collections import defaultdict


def genMaterialList(core):
    """
    Generate the material list to be included in the ECCO_Interface 
    """
    axialCutsDf = changeRegionLabels(core)
    regLabels = set()
    for (start, end), row in axialCutsDf.iterrows():
        regions = list(row.values)
        for reg in regions:
            regLabels.add(reg)

    regLabels = sorted(list(regLabels))
    reg_dict = defaultdict(list)

    for label in regLabels:
        base = label.split("_")
        reg_dict[base[0]].append(label)

    return reg_dict


def printMaterials(core):
    """
    Print the all the material labels which will be present in the KIN3D composition change,
    in order to define them in the interface with ECCO
    """
    reg_dict = genMaterialList(core)
    for unit, materials in reg_dict.items():
        print(f"   UNIT '{unit}'          (PN)   MEDIUM  '{unit}'     STRUCTURE")
        for mat in materials:
            if mat != unit:
                print(f"                               MEDIUM  '{mat}'  STRUCTURE")


def defineSubAssemblies(core):
    """
    Define the sub-assemblies in the core, cosidering the initial axial configuration
    of the translated CRs.
    """
    axialCutsDf = changeRegionLabels(core)
    print("    SUB_ASSEMBLY 'CROD_EXTR'     ABSORBER    1  0.00")
    print("        MEDIUM")
    for (start, end), row in axialCutsDf.iterrows():
        times = list(axialCutsDf.columns)
        regions = list(row.values)
        for ii in range(len(times)):
            if times[ii] == 0:
                print(f"            {regions[ii]}        ({start}*(DILAX))             ({end}*(DILAX))")
