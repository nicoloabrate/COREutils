import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict


def genDictAxialCutsTrans(core):
    """
    Generates a dictionary that contains what the axial regions of the translated CRs see during the transient.
    Parameters
    ----------
    core : Core
        The core object containing the axial cuts information.
    Returns
    -------
    dict : 
        A dictionary where the keys are tuples representing the z-coordinates of the axial cuts,
        and the values are dictionaries with the time instants as keys and the region names as values.
    """

    dict_ass_cuts = core.NE.AxialConfig.cuts
    ass = dict_ass_cuts.keys()
    trans_ass = [assembly for assembly in ass if 'CR' in assembly]
    
    my_dict = {}
    
    for ass in trans_ass:
        ax_cuts = dict_ass_cuts[ass]
        reg = ax_cuts.reg
        loz = ax_cuts.loz
        upz = ax_cuts.upz
        my_dict[ass] = {'reg':reg,'loz':loz,'upz':upz}
    
    all_z = set()
    for config in my_dict.values():
        all_z.update(config['loz'])
        all_z.update(config['upz'])
    
    sorted_z = sorted(all_z)
    intervals = [(sorted_z[i], sorted_z[i+1]) for i in range(len(sorted_z) - 1)]
    inverted_dict = {}
    
    name_to_time = {}
    times = list(core.NE.config.keys())
    for i in range(len(times)):
        name_to_time[trans_ass[i]] = times[i]
    
    for z1, z2 in intervals:
        region_per_time = {}
        for config_name, config_data in my_dict.items():
            time = name_to_time[config_name]
            found = None
            for reg, lo, up in zip(config_data['reg'], config_data['loz'], config_data['upz']):
                if lo <= z1 and z2 <= up:
                    found = reg
                    break
            region_per_time[time] = found
        inverted_dict[(z1, z2)] = region_per_time
    # sanity check
    for interval, regions in inverted_dict.items():
        for time, region in regions.items():
            if region is None:
                print(f"No region in {interval} at time {time}")
    return inverted_dict

def newRegionLabels(core):
    """
    Change the region labels in order to distinguish them from the 
    rest of the regions in the core
    """
    axialCutsDict = genDictAxialCutsTrans(core)
    df = pd.DataFrame.from_dict(axialCutsDict, orient='index').sort_index()
    df.index.name = "z_interval"
    df_modified = df.copy()
    ii = 0
    for (start, end), row in df.iterrows():
        times = list(df.columns)
        regions = list(row.values)
        ii += 1
        for i in range(len(times) - 1):
            r1, r2 = regions[i], regions[i + 1]
            if r1 != r2: # there is a change of composition
                r1_label = f"{r1}_{ii:03}"
                r2_label = f"{r2}_{ii:03}"
                for tt in range(len(times)):
                    if regions[tt] == r1:
                        df_modified.at[(start, end), times[tt]] = r1_label
                    elif regions[tt] == r2:
                        df_modified.at[(start, end), times[tt]] = r2_label
    return  df_modified


def plotTableComps(core):
    """
    Generates a table with the compositions as a function of time
    """
    axialCutsDict = genDictAxialCutsTrans(core)
    df = pd.DataFrame.from_dict(axialCutsDict, orient='index').sort_index()
    df.index.name = "z_interval"
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)
    
    row_labels = [f"{start:.1f}–{end:.1f}" for start, end in df.index]
    col_labels = [f"{int(col)} s" if isinstance(col, float) else str(col) for col in df.columns]
    
    table = plt.table(cellText=df.values,
                    colLabels=col_labels,
                    rowLabels=row_labels,
                    cellLoc='center',
                    rowLoc='center',
                    loc='center')
    
    table.scale(0.8, 1)
    
    for key, cell in table.get_celld().items():
        row, col = key
        if row == 0 or col == -1:
            cell.set_fontsize(10)
            cell.set_text_props(weight='bold')
    
    #plt.title("Axial regions as a function of time", fontsize=14)
    plt.show()


def plotTableCompsWithLabels(core):
    """
    Generates a table with the compositions as a function of time
    """
    axialCutsDf = newRegionLabels(core)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)
    
    row_labels = [f"{start:.1f}–{end:.1f}" for start, end in axialCutsDf.index]
    col_labels = [f"{int(col)} s" if isinstance(col, float) else str(col) for col in axialCutsDf.columns]
    
    table = plt.table(cellText=axialCutsDf.values,
                    colLabels=col_labels,
                    rowLabels=row_labels,
                    cellLoc='center',
                    rowLoc='center',
                    loc='center')
    
    table.scale(0.8, 1)
    
    for key, cell in table.get_celld().items():
        row, col = key
        if row == 0 or col == -1:
            cell.set_fontsize(10)
            cell.set_text_props(weight='bold')
    
    #plt.title("Axial regions as a function of time", fontsize=14)
    plt.show()


def genKIN3DcompChanges(core):
    """
    Generate the COMPOSITION_CHANGE rows of KIN3D with axial-zone-specific region names.
    """
    axialCutsDict = genDictAxialCutsTrans(core)
    df = pd.DataFrame.from_dict(axialCutsDict, orient='index').sort_index()
    df.index.name = "z_interval"
    output_lines = []
    ii = 0
    for (start, end), row in df.iterrows():
        output_lines.append(f"!     axial interval ({start}, {end})")
        times = list(df.columns)
        regions = list(row.values)
        ii += 1
        for i in range(len(times) - 1):
            t1, t2 = times[i], times[i + 1]
            r1, r2 = regions[i], regions[i + 1]

            if r1 != r2:
                r1_label = f"{r1}_{ii:03}"
                r2_label = f"{r2}_{ii:03}"
                output_lines.append(f"COMPOSITION_CHANGE '{r1_label}' '{r2}' {t1} {t2}")

    return "\n".join(output_lines)


def genKIN3DhexagonalDetector(detector_position=(30,30), filename="detector_specs.txt"):
    """
    Generates the detector specifications for KIN3D, given the position of the hexagonal detectors
    """
    with open(filename, "a") as f:
        f.write("      DETECTOR_LOCATION_AND_CROSS_SECTIONS\n")
        f.write(f"        'VIDE_VOID' {detector_position[0]} {detector_position[1]}\n")
        f.write("          1  1  1  1  1  1  1  1  1  1  1\n")
        f.write("          1  1  1  1  1  1  1  1  1  1  1\n")
        f.write("          1  1  1  1  1  1  1  1  1  1  1\n")
    return


def genKIN3DfullDetectors(core, filename="detector_specs.txt"):
    """
    Generates the detector specifications for KIN3D, one for each subassembly
    """
    ass_positions = core.Map._Map__eranosCoords()
    with open(filename, "w") as f:
        pass
    for pos in ass_positions:
        genKIN3DhexagonalDetector(pos, filename)
    return

