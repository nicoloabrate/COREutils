import re
import numpy as np


def RetrieveDetectorPowerMatrix(core, filename = "transient.out"):
    """
    Creates a matrix of detector power values over time.

    Parameters
    ----------
    filename : str
        Path to the data file.

    Returns
    -------
    numpy.ndarray
        A 2D numpy array where each row represents the power values for a detector over time.
        Returns None if there is an error reading the file or no data is found.
    """

    num_detectors = len(core.Map.fren2eranos)
    detector_data = [[] for _ in range(num_detectors)]
    time_vector = np.array([])
    detector_locations = {}

    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith("DETECTOR  1 TIME,RATE:"):
                    # Extract time from the line
                    parts = line.split()
                    try:
                        time_value = float(parts[3])
                        time_vector = np.append(time_vector, time_value)
                    except ValueError:
                        print(f"Warning: Invalid time format in line: {line}. Skipping.")
                if "DETECTOR" in line and "X/Y LOCATION" in line:
                    # Use regex to extract detector number and x, y locations
                    match = re.search(r'DETECTOR\s*(\d+).*?PLANE/AXIAL LOCATION:\s*(\d+)\s*(\d+)', line)
                    if match:
                        detector_number = int(match.group(1))
                        xx = int(match.group(2))
                        yy = int(match.group(3))
                        detector_locations[detector_number] = (xx, yy)
                    else:
                        print(f"Warning: Could not parse detector location from line: {line}")
                if "TIME,RATE" in line:
                    parts = line.split()
                    try:
                        match = re.search(r'DETECTOR\s*(\d+)', line)
                        if match:
                            detector_number = int(match.group(1))
                            power_value = float(parts[-1])
                        # Adjust detector number to be 0-indexed
                        detector_index = detector_number - 1
                        if 0 <= detector_index < num_detectors:
                            detector_data[detector_index].append(power_value)
                        else:
                            print(f"Warning: Detector number {detector_number} is out of range (1-{num_detectors}). Skipping line: {line}")
                    except ValueError:
                        print(f"Warning: Invalid data format in line: {line}. Skipping.")
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return None

    # Convert the list of lists to a NumPy array.
    max_time_points = max(len(data) for data in detector_data)
    # Create an empty numpy array of the appropriate size, filled with NaN values.
    power_matrix = np.full((num_detectors, max_time_points), np.nan)
    # Copy the data into the numpy array.  Rows with less data will be padded with NaN.
    for i, detector_values in enumerate(detector_data):
        power_matrix[i, :len(detector_values)] = detector_values

    return time_vector, power_matrix, detector_locations


def RetrieveDetectorPowerMatrix2(core, filename = "transient.out"):
    """
    Creates a matrix of detector power values over time.

    Parameters
    ----------
    filename : str
        Path to the data file.

    Returns
    -------
    numpy.ndarray
        A 2D numpy array where each row represents the power values for a detector over time.
        Returns None if there is an error reading the file or no data is found.
    """

    num_detectors = len(core.Map.fren2eranos)
    detector_data = [[] for _ in range(num_detectors)]
    time_vector = np.array([])
    detector_locations = {}
    normalization_factors = np.array([])

    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if "RATE IS DIVIDED BY" in line:
                    m = re.search(r'DETECTOR\s*(\d+)\s*RATE IS DIVIDED BY\s*([0-9.Ee+-]+)', line)
                    if m:
                        factor = float(m.group(2))
                        normalization_factors = np.append(normalization_factors,factor)
                

                if line.startswith("DETECTOR  1 TIME,RATE:"):
                    # Extract time from the line
                    parts = line.split()
                    try:
                        time_value = float(parts[3])
                        time_vector = np.append(time_vector, time_value)
                    except ValueError:
                        print(f"Warning: Invalid time format in line: {line}. Skipping.")
                if "DETECTOR" in line and "X/Y LOCATION" in line:
                    # Use regex to extract detector number and x, y locations
                    match = re.search(r'DETECTOR\s*(\d+).*?PLANE/AXIAL LOCATION:\s*(\d+)\s*(\d+)', line)
                    if match:
                        detector_number = int(match.group(1))
                        xx = int(match.group(2))
                        yy = int(match.group(3))
                        detector_locations[detector_number] = (xx, yy)
                    else:
                        print(f"Warning: Could not parse detector location from line: {line}")
                if "TIME,RATE" in line:
                    parts = line.split()
                    try:
                        match = re.search(r'DETECTOR\s*(\d+)', line)
                        if match:
                            detector_number = int(match.group(1))
                            power_value = float(parts[-1])
                        # Adjust detector number to be 0-indexed
                        detector_index = detector_number - 1
                        if 0 <= detector_index < num_detectors:
                            detector_data[detector_index].append(power_value)
                        else:
                            print(f"Warning: Detector number {detector_number} is out of range (1-{num_detectors}). Skipping line: {line}")
                    except ValueError:
                        print(f"Warning: Invalid data format in line: {line}. Skipping.")
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return None

    norm_factors = normalization_factors/sum(normalization_factors)
    # Convert the list of lists to a NumPy array.
    max_time_points = max(len(data) for data in detector_data)
    # Create an empty numpy array of the appropriate size, filled with NaN values.
    power_matrix = np.full((num_detectors, max_time_points), np.nan)
    # Copy the data into the numpy array.  Rows with less data will be padded with NaN.
    for i, detector_values in enumerate(detector_data):
        power_matrix[i, :len(detector_values)] = detector_values

    for i in range(len(power_matrix)):
        power_matrix[i] = power_matrix[i] * norm_factors[i]

    return time_vector, power_matrix, detector_locations


def RetrieveAmplitude(filename = "TRPOW"):
    """
    Reads amplitude data from the TRPOW file.

    Args:
        filename (str): The path to the TRPOW file.

    Returns:
        tuple: A tuple containing:
            - time_vector (np.ndarray): Array of time values.
            - amplitude_matrix (np.ndarray): Matrix of amplitude values.
    """
    time_vector = []
    amplitude_vector = []

    try:
        with open(filename, 'r') as f:
            for line in f:
                line.strip()
                line = line.split()
                if len(line) == 3:
                    if float(line[2]) == 1:
                        try:
                            time_vector.append(float(line[0]))
                            amplitude_vector.append(float(line[1]))
                        except ValueError:
                            print(f"Warning: Invalid data format in line: {line}. Skipping.")
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return None
    
    return np.array(time_vector), np.array(amplitude_vector)


def RetrieveTransientNodalPower(core, filename):
    """
    Reads power data from the TRPOW file and organizes it into matrices.

    Args:
        filename (str): The path to the TRPOW file.

    Returns:
        tuple: A tuple containing:
            - power_density_matrix (np.ndarray): Matrix (ntime x ncells) with power densities for each time step.
            - power_density_by_plane (np.ndarray): Matrix (ntime x nplanes x nassembly) with power densities divided by plane.
            - time_power_constr (np.ndarray): Matrix (ntime x 3) with time instant, total power, and the constant.
    """
    data = []
    time_power_list = []
    n_assembly = len(core.Map.fren2eranos.keys())
    
    try:
        with open(filename, 'r') as f:
            line1 = f.readline().split()
            if len(line1) == 6:
                n_cells = int(float(line1[3]))
                n_planes = int(n_cells/n_assembly)
            f.readline() # Skip the second line
            while True:
                line3 = f.readline().split()
                if not line3:
                    break
                if len(line3) == 3:
                    time = float(line3[0])
                    power = float(line3[1])
                    time_power_list.append((time, power))
                n_count = 0
                power_densities = []
                while n_count < n_cells:
                    line = f.readline().split()
                    power_densities.extend([float(x) for x in line])
                    n_count += len(line)
                data.append(power_densities)         
    
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return None
    

    power_density_matrix = np.array(data)
    time_power = np.array(time_power_list)
    ntime = power_density_matrix.shape[0]
    power_density_by_plane = power_density_matrix.reshape((ntime, n_planes, n_assembly))

    # FIXME: Create a function to compute the cell volumes using only the core object
    cell_volumes = ComputeCellVolumes("../ALFRED_ENEA/ALFRED_KIN3D/CR_extraction2/geometry.out")
    cell_vol = cell_volumes[np.newaxis,:,np.newaxis]
    tot_pow_vector = time_power[:,1]
    tot_power = tot_pow_vector[:,np.newaxis,np.newaxis]
    power_by_plane = power_density_by_plane * cell_vol * tot_power

    return power_density_matrix, power_density_by_plane, power_by_plane, time_power


def ComputeCellVolumes(filename="geometry.out"):
    """
    Reads hexagonal surface area and mesh heights from a file,
    calculates the volume of each plane's cells, and returns a vector of the volumes.
    """
    hexagonal_surface_area = None
    mesh_heights = []
    found_z_mesh_header = False

    try:
        with open(filename, 'r') as f:
            for line in f:
                if "HEXAGON_SURFACE" in line:
                    data = line.split()
                    hexagonal_surface_area = float(data[-1])
                    #print(f"Hexagonal surface area: {hexagonal_surface_area}")
                
                if "CORNER_POINT_Z_COOR" in line and "Z_MESH_HEIGHT" in line:
                    found_z_mesh_header = True
                    continue

                if found_z_mesh_header:
                    stripped = line.strip()
                    if stripped == "":
                        continue  # salta righe vuote

                    data = stripped.split()
                    if len(data) >= 3:
                        try:
                            mesh_height = float(data[2])
                            mesh_heights.append(mesh_height)
                        except ValueError:
                            print(f"Warning: Invalid mesh height format in line: {line.strip()}. Skipping.")
                    else:
                        # Stop if line doesn't match expected format and at least one height is collected
                        if len(mesh_heights) > 0:
                            break
                    
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return np.array([])

    if hexagonal_surface_area is None or not mesh_heights:
        print("Error: Required data not found in the file.")
        return np.array([])

    cell_volumes = np.array([hexagonal_surface_area * h for h in mesh_heights])
    return cell_volumes