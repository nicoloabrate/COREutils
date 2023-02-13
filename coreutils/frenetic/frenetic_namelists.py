import os
import json
from numpy import nan
from collections import OrderedDict, UserDict


class FreneticNamelist():
   """Define the content of Frenetic namelists and assign default values.

   Attributes
   ----------
   files: dict
      Dictonary mapping the namelists to the input files where they are written
   namelists: dict
      Dictionary mapping the keywords to their corresponding namelist
   kw_descr: dict
      Dictionary giving a description of each keyword
   mandatory: dict
      Dictionary defining the mandatory arguments for NE and TH objects.
   vector_inp: dict
      Dictionary of keywords to be defined as vector input for FRENETIC.
      The values are the lengths of the input vector.
   DefaultValue: dict
      Dictionary assigning default values to each keyword. Mandatory 
      keyword are assigned with the value ``np.nan`` for later
      assignement in ``coreutils.frenetic.InpGen.inpgen``

   """
   def __init__(self):

      self.files = {
                     "common_input.inp": ["PRELIMINARY", "COREGEO", "COMMNUM", "ADDTH"],
                     "NEinput.inp": ["CONTROL", "GEOMETRY", "NUMERICS1", "NUMERICS2", "NUMERICS3",
                                    "OUTPUT0", "OUTPUT", "OPENMP"],
                     "THinput.inp": ["NUMERICS", "IBCONDITIONS", "COUPLING", "SENSOR", "SENSOR_RAD"],
                     "THdatainput.inp": ["COMMONS", "THERMALHYDRAULIC"],
                   }

      self.namelists = {
                           # common input
                           "PRELIMINARY": ["isSym", "isNETH", "iResta", "SERVERPORT", "HOSTNAME"],
                           "COREGEO": ["nChan", "nDiff", "HexPitch", "LeXag", "nR", "nL", "iTyCool"],
                           "COMMNUM": ["nElems", "xLengt", "iTyMsh", "nRef", "nElRef", "xBRefi", "xERefi", "SizMin", "SizMax", "iAdapTime", "tEnd", "StpMin", "StpMax", 
                                       "StpMinSteady"
                                      ], # "TrefBeg", "TrefEnd" 
                           "ADDTH": ["MaxNRadNode", "nMaxBCchange"],
                           "NUMERICS": ["ISTISC", "DTTISC", "TollToSteady", "method", "iQFun", "xQbeg", "xQend", "dxQ0", "Q0", "tQbeg", "tQend", "URTFLU", "URTPIN", "tolTemp", 
                                       "tolPres", "underTemp", "underPress", "frozencoeff", "nMaxIter", "sthMax", "errRelTime", "qPinDotStepIncrement", "kLocX", "underFlux",
                                       "powtot0"
                                       ],
                           "IBCONDITIONS": ["inTial", "temInl", "temOut", "preInl", "preOut", "mdtInl", "temIni", "eneBound", "masBound", "momBound", "mdtInlBiB", "preInl"],
                           "COUPLING": ["iThimb", "qVolBiBX", "qVolX", "FluxExtX"],
                           "SENSOR": ["nTimeProf", "TimeProf", "iTimeProf", "iSens", "nLayer", "zLayer", "iHDF5OutTH"],
                           "SENSOR_RAD": ["iRadProf", "iAxNodr", "tRadProf"],
                           # NE input
                           "CONTROL": ["iRun", "nConf", "nConf", "power", "NH5Inp", "MacInp", "MatInp", "RhoInp", "GeoInp", "NumInp", "OutInp", "iHDF5Inp"],
                           "GEOMETRY": ["nDim", "AlbedoXY", "AlbedoZN", "AlbedoZP", "nElez0", "Meshz0", "SplitZ"],
                           "NUMERICS1": ["TollFlux", "iOutAcc", "nOutMax"],
                           "NUMERICS2": ["iMethod", "iAlgVar", "iAdapt", "iCtrlQty", "dtShpMax", "dtRMax", "TollNorm", "TollForm", "TollIntp", "FacSaf", "iAdjoint", "nNormMax", "Teta"],
                           "NUMERICS3": ["nEqMax", "TollPow", "TollTmp", "iEqTyp", "RlxTmp"],
                           "OUTPUT0": ["nProf"],
                           "OUTPUT": [
                                     "tProf", "ioFluxDP", "ioFluxAP", "ioPrecuP", "ioReactP", "ioCompD", "ioIntPar", "ioFluxD", "ioPrecu", "ioFluxA", "ioPower", "ioReact",
                                     "ioTherm", "iHDF5OutNE"
                                     ],
                           "OPENMP": ["nThreadTH", "nThreadNE"],
                           # TH input
                           "COMMONS": ["iHA"],
                           "THERMALHYDRAULIC": [
                                                "nFuelX", "nNonHeatedX", "iFuelX", "dFuelX", "dFuelInX", "dFuelNfX", "RCoX", "RCiX", "ThickGasX", "ThickBoxX", "ThickClearX", "InBoxInsideX",
                                                "InBoxOutsideX", "dWireX", "pWireX", "PtoPDistX", "FPeakX", "QBoxX",
                                                "BoxMatX", "iHpbPinX", "iTyFrictX", "iChCouplX", 
                                                "iMatX", "iPinSolidX", "iBiBX", "iCRadX", "cNfX", "iCladX", "iGapX", "MaterHX", "HeatGhX"
                                               ],
                        }

      self.kw_descr = {
                           # common input
                           "isSym": "Simmetry flag: 0 = no simmetry; 1 = 60 degrees simmetry", 
                           "isNETH": "NE-TH codes coupling flag: 0 = no coupling; 1 = coupling (TISC); 2 = coupling (file r/w)", 
                           "iResta": "! Restart option (to be implemented)",
                           "SERVERPORT": "!!! port number for the TISC coupling (deprecated)", 
                           "HOSTNAME": "!!! host name of the pc where TISC is running  (deprecated)",
                           "nChan": "number of exagonal channels", 
                           "nDiff": "Number of different channels from the TH point of view", 
                           "HexPitch": "lattice pitch of the HA in [m]", 
                           "LeXag": "side of the inner-most hexagon (inside the inner perimeter of the wrapper) in [m]", 
                           "nR": "number of rows in a sextant", 
                           "nL": "number of HA in each row of a sextant (including the central hexagon)", 
                           "iTyCool": "Coolant type, it may be one among 'Pb', 'LBE', 'Na', 'Na_relap'",
                           "nElems": "spatial elements number",
                           "xLengt": "height of the core",
                           "iTyMsh": "! -1 does not work! Mesh type (0=fixed and uniform; 1=fixed refined;)",
                           "nRef": "! dummy argument, it should always be 1! Flag for mesh refinement, if iTyMsh != 0. (0=non refined; 1=refined);",
                           "nElRef": "Number of spatial elements in the refined zone",
                           "xBRefi": "Beginning of the refined zone (if iTyMsh != 0)",
                           "xERefi": "End of the refined zone (if iTyMsh != 0)",
                           "SizMin": "!!!!!!! unused? Spatial mesh minimum size (if refined)",
                           "SizMax": "!!!!!!! unused? Spatial mesh maximum size (if refined)",
                           "iAdapTime": "Time adaptivity flag (0=no adaptivity (tstep=tstepmin); 1=adaptivity; 2=adaptivity only with respect to temperatures)",
                           "tEnd": "End simulation time in [s]",
                           "StpMin": "Minimum coupling timestep in [s].",
                           "StpMax": "Maximum coupling timestep in [s].",
                           "StpMinSteady": "This parameter regulates the convergence in the fixed point iterations used to couple NE and TH.",
                           # "TrefBeg": "Initial simulation time, could be useful in case of restart runs [s]", # useful for forthcoming restarting opt in FRENETIC
                           # "TrefEnd": "End simulation time, if zero it is used as flag to just perform the steady state case [s]",
                           "MaxNRadNode": "Third dimension for temperature matrix, max radial pins nodes +1",
                           "nMaxBCchange": "The number of maximum rows input  entries for input files reading: mdot.inp, pressout.inp, etc.",
                           "nThreadTH": "Number of CPUs allocated for TH module",
                           "nThreadNE": "Number of CPUs allocated for NE module",
                           "ISTISC": "?! Deprecated",
                           "DTTISC": "?! Deprecated",
                           "TollToSteady": "Relative error tolerance for steady state condition",
                           "method": "Method choice for steady state model. It could be 'PSEUDO' or 'RAMP'",
                           "iQFun": "Type of input power profile. (-1=external function for the Q(z,t) dependence; 0=square wave form; -2=external function for the Q(z,t) dependence)", 
                           "xQbeg": "Beginning of the heated zone [m]",
                           "xQend": "End of the heated zone [m]",
                           "dxQ0": "??? Width of the axial bins between xQbeg and xQend for constant heating[m]",
                           "Q0": "Rods heat deposition in case of constant heating for standalone TH [W/m]",
                           "tQbeg": "Beginning heating time for heating in standalone TH",
                           "tQend": "End heating time for heating in standalone TH",
                           "URTFLU": "?! Deprecated",
                           "URTPIN": "?! Deprecated",
                           "tolTemp": "Tolerance on the relative error for energy equations", 
                           "tolPres": "Tolerance on the relative error for momentum equations", 
                           "underTemp": "Under-relaxation parameter for energy equations",
                           "underPress": "Under-relaxation parameter for momentum equations",
                           "frozencoeff": "Frozen coefficient option for coolant properties during transient (0=No; 1=Yes)",
                           "nMaxIter": "Maximum number of iterations in TH module",
                           "sthMax": "Optional maximum time step for transient radial fuel calculation",
                           "errRelTime": "Absolute error threshold for second order derivative to find optimal time step",
                           "qPinDotStepIncrement": "Heating ramp step for ramp steady method",
                           "kLocX": "Flag to search file for kloc, i.e. localised axial pressure drop (0=Off; 1=on)",
                           "underFlux": "Under-relaxation parameter for inter-wrapper heat exchange linear power",
                           "powtot0": "!!! ",
                           "inTial": "??? name meaning? Flag for reading boundary conditions from files: <0 means reading, >0 means values from input file, the BC type is however chosen by means of enebond, mombond and masbound", 
                           "eneBound": "Energy equation boundary condition (e.g., 'TIN')",
                           "masBound": "Mass equation boundary condition (e.g., 'mdotIN', 'presIN', 'pdrop')",
                           "momBound": "Momentum equation boundary condition (e.g., 'pdrop', 'presOUT', 'presIN')",
                           "mdtInlBiB": "Box-in-the-Box thimble inlet mass flow rate",
                           "temInl": "Inlet coolant temperature [K]", 
                           "temOut": "Outlet coolant temperature [K]", 
                           "preInl": "Inlet coolant pressure [Pa]",
                           "preOut": "?! Outlet coolant pressure [Pa] (deprecated)", 
                           "mdtInl": "Inlet mass flow rate [kg/s]", 
                           "temIni": "Initialisation temperature in each HAs (initial guess) [K]",
                           "iThimb": "! The number of thimble channels used as possible flag inside the code. It could be used to allocate thimble data structure only if iThimb > 0 (to be implemented)",
                           "qVolBiBX": "! Flag to search for the file for an additional coolant power deposition, -1 search file (to be implemented)",
                           "qVolX": "! Flag to search for the file for an additional coolant power deposition, -1 search file (to be implemented)",
                           "FluxExtX": "Flag to search for the file needed in case of 'EXTERNAL' option (to be implemented)",
                           "nTimeProf": "Number of times at which spatial profiles are saved",
                           "TimeProf": "Time instants at which spatial profiles are saved, in [s]",
                           "iTimeProf": "! Flag to save data of specific HA (needed only in the old txt output format, to be implemented in hdf5)",
                           "iSens": "! Flag to turn on inlet/outlet saving for channel i (needed only in the old txt output format, to be implemented in hdf5)",
                           "nLayer": "! Number of axial bins where the output is requested (needed only in the old txt output format, to be implemented in hdf5)",
                           "zLayer": "! Axial coordinate of the bins where the output is requested (needed only in the old txt output format, to be implemented in hdf5)",
                           "iHDF5OutTH": "Flag to save TH output in HDF5 format",
                           "iRadProf": "! Channels for saving radial T profile (sensor_rad to be implemented in hdf5 fmt, deprecated?)",
                           "iAxNodr": "! Axial bins for saving radial T profile (sensor_rad to be implemented in hdf5 fmt, deprecated?)",
                           "tRadProf": "! Time instant for radial T profiles (sensor_rad to be implemented in hdf5 fmt, deprecated?)",
                           # NE input
                           "iRun": "Run type (0=initialisation; 1=static; 2=transient)",
                           "nConf": "Number of system configurations during transient",
                           "power": "Total thermal power in [W]",
                           "NH5Inp": "Name of the HDF5 input file containing the group constants",
                           "MacInp": "Name of the file containing the group constants namelist",
                           "MatInp": "Name of the file contatining the time dependent material configuration",
                           "RhoInp": "Name of the file contatining the time dependent reactivity profile",
                           "GeoInp": "Name of the file contatining the geometry specifics",
                           "NumInp": "Name of the file contatining the numerical settings",
                           "OutInp": "Name of the file contatining the output settings",
                           "iHDF5Inp": "! Type of input HDF5 (1=HDF5 with data in the old txt fashion, 2=data in datasets optimised for HDF5 format, 1 is deprecated)",
                           "nDim": "Number of hexagonal-z spatial dimensions (allowed values = {0;1;2;3})",
                           "AlbedoXY": "Albedo coefficient in the xy-direction",
                           "AlbedoZN": "Albedo coefficient in the lower z-plane",
                           "AlbedoZP": "Albedo coefficient in the upper z-plane",
                           "nElez0": "Number of axial nodes",
                           "Meshz0": "Position of axial node faces of the mesh in [cm]",
                           "SplitZ": "Number of uniform bins in each interval defined in MeshZ0",
                           "TollFlux": "Tolerance for the relative error of the flux",
                           "iOutAcc": "Convergence acceleration of outer iterations (0=No; 1=Yes)",
                           "nOutMax": "Number of maximum outer iterations",
                           "iMethod": "Method chosen for reactor kinetics (0=Point Kinetics; 1=full order model; 2=Improved Quasi-static; 3=Predictor-Corrector Quasi-static)",
                           "iAlgVar": "Variant algorithm for reactor kinetics method (0=No; 1=Yes)", 
                           "iAdapt": "Adaptive time step selection (0=No; 1=Yes)",
                           "iCtrlQty": "Quantity to be controlled during convergence (0=adjoint-weighted distortion of the shape; 1=local error of the shape;)",
                           "dtShpMax": "Maximum timestep to update the shape [s]",
                           "dtRMax": "Maximum timestep to update the reactivity [s]",
                           "TollNorm": "Tolerance for the relative error of the normalisation condition (used only if iMethod=2);",
                           "TollForm": "Maximum allowed relative variation of the quantity specified by iCtrlQty across a shape time step (used only if iAdapt=1)",
                           "TollIntp": "maximum allowed relative variation of the integral kinetics parameters across a reactivity time step (used only if iAdapt=1)",
                           "FacSaf": "Safety factor of adaptive time step algorithm (allowed value between (0;1])",
                           "iAdjoint": "??? Flag to solve the adjoint for the adiabatic method",
                           "nNormMax": "Maximum number of normalisation condition iterations (used only if iMethod=2);",
                           "Teta": "Theta method parameter of prompt neutron balance equation (allowed values in (0;1]);",
                           "nEqMax": "Maximum number of neutronic/thermal-hydraulic equilibrium iterations",
                           "TollPow": "Tolerance for the relative error of the power (the tolerance for the relative error of the eigenvalue is automatically set to TollPow/10);",
                           "TollTmp": "Tolerance for the relative error of the temperatures;",
                           "iEqTyp": "Equilibrium iteration type (0=Picard (with damping provided by RlxTmp););",
                           "RlxTmp": "Relaxation factor for received temperature distributions;",
                           "nProf": "Number of discrete times at which phase space dependent ouput is requested.",
                           "tProf": "Discrete times at which phase space dependent ouput is requested;", 
                           "ioFluxDP": "Output the direct flux of photons; (0=No; 1=Yes)",
                           "ioFluxAP": "Output the adjoint flux of photons; (0=No; 1=Yes)",
                           "ioPrecuP": "Output the photon precursors concentrations; (0=No; 1=Yes)",
                           "ioReactP": "Output the reaction rate densities of photons; (0=No; 1=Yes)",
                           "ioCompD": "Output computational convergence and performance information; (0=No; 1=Yes)", 
                           "ioIntPar": "Output the integral parameters (0=No; 1=Yes)", 
                           "ioFluxD": "Output the direct flux; (0=No; 1=Yes)",
                           "ioPrecu": "Output the neutron precursors concentrations; (0=No; 1=Yes)",
                           "ioFluxA": "Output the adjoint flux; (0=No; 1=Yes)",
                           "ioPower": "Output the power density (all contributions); (0=No; 1=Yes)",
                           "ioReact": "Output the reaction rate densities; (0=No; 1=Yes)",
                           "ioTherm": "Output the thermal hydraulics data; (0=No; 1=Yes)",
                           "iHDF5OutNE": "Flag to save output in HDF5 format (0=No, use old txt format; 1=Yes)",
                           # TH input
                           "iHA": "Number of each hexagonal assembly belonging to the TH type family",
                           "nFuelX": "Number of heated fuel rods in each hexagonal channel",
                           "nNonHeatedX": "Number of non heated rods in each hexagonal channel",
                           "iFuelX": "Material label (e.g., 'UO2', 'U5Fs', 'B4C', 'SS')",
                           "dFuelX": "!!! it should be 'dPinX' Diameter of the pin in [m]",
                           "dFuelInX": "Diameter of the inner fuel radius in [m] if the pellet is annular",
                           "ThickBoxX": "Thickness of a single assembly box side in [m] (should be the same as before, in the suggested inputs it was 0.008m but from ALFRED papers i saw that should be 0.004m, maybe was wrong)",
                           "ThickClearX": "Half thickness of clearance between boxes in [m] (should be the same as before, in the suggested inputs it was 0.005m but from ALFRED papers i saw that should be  0.0025m, )",
                           "FPeakX": "! Friction factor multiplier (to be implemented)",
                           "QBoxX": "Multiplier of the inter-assembly heat transfer coefficient",
                           "BoxMatX": "HA wrapper material type (e.g., 'SS', 'COMP', '1515T', 'T91')",
                           "iHpbPinX": "Heat transfer correlation choice (e.g., 'SMTUBE', 'SCHAD', 'USHAKOV', 'EXPERIMENT', 'MIKITYUK', 'KAZIMI')",
                           "iTyFrictX": "Friction factor correlation choice (e.g., 'CONST', 'SMTUBE', 'BUNDLE', 'BLASIUS', 'WIRED')",
                           "iChCouplX": "Interchannel coupling type (e.g., 'CONV', 'UNIFORM', 'ADIABATIC', 'EXTERNAL')",
                           "iMatX": "?! unused? Default is 1",
                           "iPinSolidX": "Flag for homogeneous (=1) or heterogeneous (=2) radial geometry",
                           "RCoX": "Outer cladding radius for fuel rods in [m]. Even if iPinSolidx=0, the value is used to perform preliminary calculations, so take it equal to half of fuel diameter",
                           "RCiX": "Inner cladding radius for fuel rods in [m]",
                           "ThickGasX": "! Gas gap thickness in [m] (having Rco and Rci could be internally computed as suggested in input.f90 ---> to be implemented)",
                           "dFuelNfX": "Diameter of the non-fuel rods in [m]",
                           "InBoxInsideX": "Box-in-the-Box internal side length in [m]",
                           "InBoxOutsideX": "Box-in-the-Box outer side length in [m]", 
                           "dWireX": "Wire diameter in [m]",
                           "pWireX": "Wire pitch in [m]",
                           "PtoPDistX": "Fuel pitch distance in [m]",
                           "iBiBX": "Flag Box-in-the-Box (BiB) assembly type (apparently unused, to be implemented?)",
                           "iCRadX": "Flag for the annular pin pellet type (0=cylindrical; 1=annular)",
                           "cNfX": "Non-fuel rods types (e.g., 'B4C', 'SS')",
                           "iCladX": "Fuel type (e.g., 'UO2', 'U5Fs', 'B4C', 'SS', 'Zircaloy', '1515T', 'T91')",
                           "iGapX": "Gap material type (e.g., 'SS', 'UO2', 'He')",
                           "MaterHX": "Index of material type in the radial mesh vector (1=fuel; 2=gap; 3=cladding)",
                           "HeatGhX": "Index for heating option in the radial mesh vector (1=on; 0=off)",
                        }
      # mandatory args (excluding the ones from the set of mandatory args in COREutils)
      self.mandatory = {
                        # mandatory if NE is used
                        "NE": ["SplitZ"],
                        # mandatory if TH is used
                        "TH": ["xLengt"]
                       }

      self.vector_inp = {
                           "LeXag": "nAss",
                           "nElems": "nAss",
                           "xLengt": "nAss",
                           "iTyMsh": "nAss",
                           "nRef": "nAss",
                           "nElRef": "nAss",
                           "xBRefi": "nAss",
                           "xERefi": "nAss",
                           "SizMin": "nAss", 
                           "SizMax": "nAss",
                           "iTimeProf": "nAss",
                           "iSens": "nAss",
                           "iRadProf": "nAss",
                           "Q0": "nAss",
                           "dxQ0": "nAss",
                           "xQend": "nAss",
                           "xQbeg": "nAss",
                           "temIni": "nAss",
                           "temInl": "nAss",
                           "temOut": "nAss",
                           "preInl": "nAss",
                           "preOut": "nAss",
                           "mdtInl": "nAss",
                           "mdtInlBiB": "nAss",
                           "QBoxX": "nSides",
                           "ThickClearX": "nSides",
                        }

      # TODO FIXME add list of arguments divided by type (float, string, integer)
      # to better control the input generation

      self.DefaultValue = {
                           # common input
                           "isSym": 0,
                           "isNETH": nan,
                           "iResta": 0,
                           "SERVERPORT": 2000, 
                           "HOSTNAME": "0.0.0.0",
                           "nChan": nan,
                           "nDiff": nan,
                           "HexPitch": nan,
                           "LeXag": nan,
                           "nR": nan,
                           "nL": nan,
                           "iTyCool": "Pb",
                           "nElems": 100,
                           "xLengt": nan,
                           "iTyMsh": 1,
                           "nRef": 1, # dummy argument, it should always be 1!
                           "nElRef": 0,
                           "xBRefi": 0,
                           "xERefi": 0,
                           "SizMin": -1,
                           "SizMax": -1,
                           "iAdapTime": 2,
                           "tEnd": nan,
                           "StpMin": 0.005,
                           "StpMax": 0.005,
                           "StpMinSteady": 1.,
                           # "TrefBeg": 0., # useful for forthcoming restarting opt in FRENETIC
                           # "TrefEnd": 0.,
                           "MaxNRadNode": 50,
                           "nMaxBCchange": 100,
                           "ISTISC": 0,
                           "DTTISC": 1,
                           "TollToSteady": 1E-09,
                           "method": "PSEUDO",
                           "nThreadTH": 1,
                           "nThreadNE": 1,
                           # TH input.inp
                           "URTFLU": 1.,
                           "URTPIN": 1.,
                           "iQFun": -2,
                           "xQbeg": 0.,
                           "xQend": 1., # >0 to avoid "ERROR. Incorrect XQEND distribution. Allowed values: .GT. 0.0 ."
                           "dxQ0": 0.,
                           "Q0": 0.,
                           "tQbeg": 0.,
                           "tQend": 0.,
                           "tolTemp": 2E-07, 
                           "tolPres": 1E-02, 
                           "underTemp": 0.5,
                           "underPress": 5E-05,
                           "frozencoeff": 0,
                           "nMaxIter": 40000,
                           "sthMax": 10.0,
                           "errRelTime": 1E-02,
                           "qPinDotStepIncrement": 1,
                           "kLocX": 0,
                           "underFlux": 0.05,
                           "powtot0": 0.,
                           "inTial": -1,
                           "eneBound": 'TIN',
                           "masBound": 'mdotIN',
                           "momBound": 'presOUT',
                           "temIni": nan,
                           "temInl": 670.,
                           "temOut": 670.,
                           "preInl": 1E5,
                           "preOut": 1E5,
                           "mdtInl": 200.,
                           "mdtInlBiB": 0.,
                           "iThimb": 0,
                           "qVolBiBX": 0.,
                           "qVolX": 0.,
                           "FluxExtX": 0,
                           "nTimeProf": nan,
                           "TimeProf": nan,
                           "iSens": 1,
                           "nLayer": nan,
                           "zLayer": nan,
                           "iHDF5OutTH": 1,
                           "iRadProf": 0,
                           "iAxNodr": 1,
                           "iTimeProf": 1,
                           "tRadProf": 0,
                           # NE input.inp
                           "iRun": nan,
                           "nConf": nan,
                           "power": nan,
                           "NH5Inp": "NE_data.h5",
                           "MacInp": "macro.nml",
                           "MatInp": "config.inp",
                           "RhoInp": "rho.inp",
                           "GeoInp": "input.inp",
                           "NumInp": "input.inp",
                           "OutInp": "input.inp",
                           "iHDF5Inp": 2,
                           "nDim": nan,
                           "AlbedoXY": 0.0,
                           "AlbedoZN": 0.0,
                           "AlbedoZP": 0.0,
                           "nElez0": nan,
                           "Meshz0": nan,
                           "SplitZ": nan,
                           "TollFlux": 1E-07,
                           "iOutAcc": 1,
                           "nOutMax": 10000,
                           "iMethod": 3,
                           "iAlgVar": 1, 
                           "iAdapt": 1,
                           "iCtrlQty": 0,
                           "dtShpMax": 5.0,
                           "dtRMax": 5E-05,
                           "TollNorm": 1E-03,
                           "TollForm": 1E-03,
                           "TollIntp": 1E-03,
                           "FacSaf": 1,
                           "iAdjoint": 1,
                           "nNormMax": 10,
                           "Teta": 1,
                           "nEqMax": 1000,
                           "TollPow": 1E-05,
                           "TollTmp": 1E-03,
                           "iEqTyp": 0,
                           "RlxTmp": 0.1,
                           "nProf": 1,
                           "tProf": 0.,
                           "ioFluxDP": 1,
                           "ioFluxAP": 1,
                           "ioPrecuP": 1,
                           "ioReactP": 1,
                           "ioCompD": 1,
                           "ioIntPar": 1,
                           "ioFluxD": 1,
                           "ioPrecu": 1,
                           "ioFluxA": 1,
                           "ioPower": 1,
                           "ioReact": 1,
                           "ioTherm": 1,
                           "iHDF5OutNE": 1,
                           # TH input
                           "iHA": nan,
                           "nFuelX": nan,
                           "nNonHeatedX": nan,
                           "iFuelX": nan,
                           "dFuelX": nan,
                           "dFuelInX": nan,
                           "ThickBoxX": nan,
                           "ThickClearX": nan,
                           "FPeakX": nan,
                           "QBoxX": nan,
                           "BoxMatX": nan,
                           "iHpbPinX": nan,
                           "iTyFrictX": nan,
                           "iChCouplX": nan,
                           "iMatX": 1.,  # FIXME hardcoded value which is not read by COREutils. What is the meaning of this kw in FRENETIC?
                           "iPinSolidX": nan,
                           "RCoX": nan,
                           "RCiX": nan,
                           "ThickGasX": nan, 
                           "dFuelNfX": nan,
                           "InBoxInsideX": 0.,
                           "InBoxOutsideX": 0.,
                           "dWireX": 0.,
                           "pWireX": 0.,
                           "PtoPDistX": nan,
                           "iBiBX": 0,
                           "iCRadX": nan,
                           "cNfX": nan,
                           "iCladX": nan,
                           "iGapX": nan,
                           "MaterHX": nan,
                           "HeatGhX": nan,
                        }


class FreneticNamelistError(Exception):
   pass