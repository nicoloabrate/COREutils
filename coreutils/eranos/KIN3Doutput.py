import re
import numpy as np



def RetrieveDetectorPowerMatrix(core, filename):
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

    num_detectors = len(core.Map._Map__draweranosmap())
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
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

    
    # Convert the list of lists to a NumPy array.
    max_time_points = max(len(data) for data in detector_data)
    
    # Create an empty numpy array of the appropriate size, filled with NaN values.
    power_matrix = np.full((num_detectors, max_time_points), np.nan)
    
    # Copy the data into the numpy array.  Rows with less data will be padded with NaN.
    for i, detector_values in enumerate(detector_data):
        power_matrix[i, :len(detector_values)] = detector_values

    return time_vector, power_matrix, detector_locations


def RetrieveTransientNodalPower(filename):
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
    #n_assembly = len(core.Map.fren2eranos.keys())
    n_assembly = 547
    
    with open(filename, 'r') as f:
        line1 = f.readline().split()
        if len(line1) == 6:
            n_cells = int(float(line1[3]))
            n_planes = int(n_cells/n_assembly)
        f.readline() # Skip the second line
        while True:
            line3 = f.readline().split()
            if len(line3) == 3:
                try:
                    time = float(line3[0])
                    power = float(line3[1])
                    time_power_list.append((time, power))
                except ValueError:
                    print(f"Warning: Unable to interpret the time, power, and constant data from the line: {line3}")
                    continue # Skip to the next data block
                power_densities = []
                num_read = 0
                while num_read < n_cells:
                    line = f.readline().split()
                    if not line:
                        print("Warning: Reached the end of the file before reading all expected power densities.")
                        break
                    try:
                        power_densities.extend([float(x) for x in line])
                        num_read += len(line)
                    except ValueError:
                        print("Warning: Found a non-numeric value in the power density lines.")
                        continue # Continue reading for the rest of the expected numbers
                if len(power_densities) == n_cells:
                    data.append(power_densities)
                elif num_read < n_cells:
                    print(f"Warning: Read only {num_read} power density values out of {n_cells} expected for time t={time}.")
            else:
                print(f"Warning: Unexpected line after the first data line: {f.readline().strip()}")

    power_density_matrix = np.array(data)
    time_power_constr = np.array(time_power_list)
    ntime = power_density_matrix.shape[0]
    power_density_by_plane = power_density_matrix.reshape((ntime, n_planes, n_assembly))

    return power_density_matrix, power_density_by_plane, time_power_constr


def TransientTracePlot(filename):
    """
    Plot transient data.

    Parameters
    ----------
    filename : str
        Path to the data file.

    Raises
    ------
    ValueError
        If the input file is not properly formatted.

    Returns
    -------
    None
    """
    time = []
    pow_values = [] 

    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith(" TIME, POWER:"):
                    values = line.split()
                    if len(values) >= 4:
                        try:
                            tt = float(values[2])
                            pp = float(values[3])
                            time.append(tt)
                            pow_values.append(pp)
                        except ValueError:
                            print(f"Skipping line due to invalid data: {line.strip()}")
                    else:
                         print(f"Skipping line due to insufficient data: {line.strip()}")
    except FileNotFoundError:
        print(f"Error: File not found at {filename}")
        return


    if not time or not pow_values:
        print("Error: No data found in the file.")
        return

    time = np.array(time)
    pow_values = np.array(pow_values)

    # Avoid division by zero or empty array
    if pow_values[0] != 0:
        normalized_power = pow_values / pow_values[0]
    else:
        print("Warning: Initial power is zero. Cannot normalize.")
        normalized_power = pow_values 

    plt.plot(time, normalized_power, label='Reactor Normalized Power')
    plt.xlabel('Time [s]')
    plt.ylabel('Power [W]')
    plt.title('Reactor Normalized Power during transient')
    plt.legend()
    plt.grid()
    plt.show()