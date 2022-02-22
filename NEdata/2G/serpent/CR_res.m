
% Increase counter:

if (exist('idx', 'var'));
  idx = idx + 1;
else;
  idx = 1;
end;

% Version, title and date:

VERSION                   (idx, [1: 14])  = 'Serpent 2.1.31' ;
COMPILE_DATE              (idx, [1: 20])  = 'Jul 14 2019 19:59:36' ;
DEBUG                     (idx, 1)        = 0 ;
TITLE                     (idx, [1:  8])  = 'Untitled' ;
CONFIDENTIAL_DATA         (idx, 1)        = 0 ;
INPUT_FILE_NAME           (idx, [1:  8])  = 'slab_B4C' ;
WORKING_DIRECTORY         (idx, [1: 32])  = '/home/abrate/Serpent2/phytra/D2O' ;
HOSTNAME                  (idx, [1:  7])  = 'vpcen13' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz' ;
CPU_MHZ                   (idx, 1)        = 4294967295.0 ;
START_DATE                (idx, [1: 24])  = 'Thu Dec 10 02:16:28 2020' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Thu Dec 10 02:22:45 2020' ;

% Run parameters:

POP                       (idx, 1)        = 100000 ;
CYCLES                    (idx, 1)        = 100 ;
SKIP                      (idx, 1)        = 500 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1607562988547 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 0 0 0 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 0 ;
IMPLICIT_REACTION_RATES   (idx, 1)        = 1 ;

% Optimization:

OPTIMIZATION_MODE         (idx, 1)        = 4 ;
RECONSTRUCT_MICROXS       (idx, 1)        = 1 ;
RECONSTRUCT_MACROXS       (idx, 1)        = 1 ;
DOUBLE_INDEXING           (idx, 1)        = 0 ;
MG_MAJORANT_MODE          (idx, 1)        = 0 ;

% Parallelization:

MPI_TASKS                 (idx, 1)        = 1 ;
OMP_THREADS               (idx, 1)        = 30 ;
MPI_REPRODUCIBILITY       (idx, 1)        = 0 ;
OMP_REPRODUCIBILITY       (idx, 1)        = 1 ;
OMP_HISTORY_PROFILE       (idx, [1:  30]) = [  1.15717E+00  9.95691E-01  1.00131E+00  1.00359E+00  9.87875E-01  9.79589E-01  9.94917E-01  9.66374E-01  1.03259E+00  9.98716E-01  9.92712E-01  9.87793E-01  1.01488E+00  9.73599E-01  9.91897E-01  9.84583E-01  1.00722E+00  9.82941E-01  9.81340E-01  9.99780E-01  1.00859E+00  9.94636E-01  9.81551E-01  1.01219E+00  9.88220E-01  1.01591E+00  9.79084E-01  9.84118E-01  1.02179E+00  9.79343E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 44])  = '/opt/serpent/xsdata/endfb7/sss_endfb7.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  7.70660E-02 0.00041  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  9.22934E-01 3.4E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  3.72218E-01 0.00012  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  4.20512E-01 0.00011  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  3.18888E+00 0.00032  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  2.89614E+01 0.00019  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  2.89210E+01 0.00019  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  3.98547E+01 0.00027  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  4.71876E-02 0.00208  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 100 ;
SIMULATED_HISTORIES       (idx, 1)        = 9999673 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  9.99967E+04 0.00075 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  9.99967E+04 0.00075 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.31703E+02 ;
RUNNING_TIME              (idx, 1)        =  6.28030E+00 ;
INIT_TIME                 (idx, [1:  2])  = [  3.25667E-02  3.25667E-02 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.33334E-04  5.33334E-04 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  6.24715E+00  6.24715E+00  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  6.27913E+00  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 20.97080 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.16884E+01 0.00219 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  6.85326E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 100712.48 ;
ALLOC_MEMSIZE             (idx, 1)        = 1073.05;
MEMSIZE                   (idx, 1)        = 805.10;
XS_MEMSIZE                (idx, 1)        = 126.36;
MAT_MEMSIZE               (idx, 1)        = 8.53;
RES_MEMSIZE               (idx, 1)        = 2.02;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 668.19;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 267.95;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 7 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 101100 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.00000E+37 ;
URES_EMAX                 (idx, 1)        = -1.00000E+37 ;
URES_AVAIL                (idx, 1)        = 2 ;
URES_USED                 (idx, 1)        = 0 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 8 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 8 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 211 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 0 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 0 ;
TMS_MODE                  (idx, 1)        = 0 ;
SAMPLE_FISS               (idx, 1)        = 1 ;
SAMPLE_CAPT               (idx, 1)        = 1 ;
SAMPLE_SCATT              (idx, 1)        = 1 ;

% Radioactivity data:

TOT_ACTIVITY              (idx, 1)        =  0.00000E+00 ;
TOT_DECAY_HEAT            (idx, 1)        =  0.00000E+00 ;
TOT_SF_RATE               (idx, 1)        =  0.00000E+00 ;
ACTINIDE_ACTIVITY         (idx, 1)        =  0.00000E+00 ;
ACTINIDE_DECAY_HEAT       (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_ACTIVITY  (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_DECAY_HEAT(idx, 1)        =  0.00000E+00 ;
INHALATION_TOXICITY       (idx, 1)        =  0.00000E+00 ;
INGESTION_TOXICITY        (idx, 1)        =  0.00000E+00 ;
ACTINIDE_INH_TOX          (idx, 1)        =  0.00000E+00 ;
ACTINIDE_ING_TOX          (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_INH_TOX   (idx, 1)        =  0.00000E+00 ;
FISSION_PRODUCT_ING_TOX   (idx, 1)        =  0.00000E+00 ;
SR90_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
TE132_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
I131_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
I132_ACTIVITY             (idx, 1)        =  0.00000E+00 ;
CS134_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
CS137_ACTIVITY            (idx, 1)        =  0.00000E+00 ;
PHOTON_DECAY_SOURCE       (idx, 1)        =  0.00000E+00 ;
NEUTRON_DECAY_SOURCE      (idx, 1)        =  0.00000E+00 ;
ALPHA_DECAY_SOURCE        (idx, 1)        =  0.00000E+00 ;
ELECTRON_DECAY_SOURCE     (idx, 1)        =  0.00000E+00 ;

% Normalization coefficient:

NORM_COEF                 (idx, [1:   4]) = [  9.96313E-06 0.00029  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  1.50219E+00 0.00068 ];
U235_FISS                 (idx, [1:   4]) = [  2.55719E-01 0.00061  8.90107E-01 0.00019 ];
U238_FISS                 (idx, [1:   4]) = [  3.15710E-02 0.00162  1.09893E-01 0.00152 ];
U235_CAPT                 (idx, [1:   4]) = [  9.81345E-02 0.00096  1.45901E-01 0.00084 ];
U238_CAPT                 (idx, [1:   4]) = [  5.31598E-01 0.00044  7.90354E-01 0.00022 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 9999673 1.00000E+07 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 3.97076E+04 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 9999673 1.00397E+07 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 6723546 6.75097E+06 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 2872554 2.88353E+06 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 403573 4.05198E+05 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 9999673 1.00397E+07 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 2.28919E-06 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  9.33215E-12 0.00030 ];
TOT_POWDENS               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_GENRATE               (idx, [1:   2]) = [  7.11740E-01 0.00029 ];
TOT_FISSRATE              (idx, [1:   2]) = [  2.87224E-01 0.00030 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  6.72406E-01 0.00016 ];
TOT_ABSRATE               (idx, [1:   2]) = [  9.59629E-01 0.00010 ];
TOT_SRCRATE               (idx, [1:   2]) = [  9.96313E-01 0.00029 ];
TOT_FLUX                  (idx, [1:   2]) = [  7.54410E+01 0.00020 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  4.03705E-02 0.00246 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  2.89266E+01 0.00019 ];
INI_FMASS                 (idx, 1)        =  0.00000E+00 ;
TOT_FMASS                 (idx, 1)        =  0.00000E+00 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.79604E+00 0.00058 ];
SIX_FF_F                  (idx, [1:   2]) = [  9.93513E-01 8.5E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  1.18189E-01 0.00087 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  3.53166E+00 0.00096 ];
SIX_FF_LF                 (idx, [1:   2]) = [  9.60167E-01 0.00010 ];
SIX_FF_LT                 (idx, [1:   2]) = [  9.99285E-01 8.6E-06 ];
SIX_FF_KINF               (idx, [1:   2]) = [  7.44747E-01 0.00053 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  7.14570E-01 0.00054 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.47800E+00 1.3E-05 ];
FISSE                     (idx, [1:   2]) = [  2.02792E+02 1.6E-06 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  7.14506E-01 0.00052  7.09530E-01 0.00054  5.03945E-03 0.00691 ];
IMP_KEFF                  (idx, [1:   2]) = [  7.14555E-01 0.00029 ];
COL_KEFF                  (idx, [1:   2]) = [  7.14381E-01 0.00047 ];
ABS_KEFF                  (idx, [1:   2]) = [  7.14555E-01 0.00029 ];
ABS_KINF                  (idx, [1:   2]) = [  7.44739E-01 0.00028 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.27935E+01 0.00027 ];
IMP_ALF                   (idx, [1:   2]) = [  1.27964E+01 0.00019 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  5.56070E-05 0.00344 ];
IMP_EALF                  (idx, [1:   2]) = [  5.54329E-05 0.00244 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  3.77257E-01 0.00158 ];
IMP_AFGE                  (idx, [1:   2]) = [  3.76421E-01 0.00072 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  1.47902E-02 0.00111  3.03133E-04 0.00711  1.86524E-03 0.00281  9.75542E-04 0.00386  2.45780E-03 0.00258  4.52288E-03 0.00190  2.18201E-03 0.00265  1.59658E-03 0.00309  8.87013E-04 0.00420 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  6.06132E-01 0.00146  1.24667E-02 7.2E-09  2.82917E-02 0.0E+00  4.25244E-02 0.0E+00  1.33042E-01 0.0E+00  2.92467E-01 0.0E+00  6.66488E-01 2.7E-09  1.63478E+00 4.2E-09  3.55460E+00 2.9E-09 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  14]) = [  7.18806E-03 0.00667  1.78804E-04 0.04269  1.08758E-03 0.01666  1.10739E-03 0.01528  3.34415E-03 0.00915  1.11550E-03 0.01758  3.54633E-04 0.03414 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  14]) = [  8.25276E-01 0.01649  1.24909E-02 3.8E-06  3.15130E-02 0.00034  1.10735E-01 0.00046  3.22733E-01 0.00031  1.34094E+00 0.00021  9.04033E+00 0.00206 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  1.71656E-05 0.00124  1.71463E-05 0.00125  1.98967E-05 0.01332 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  1.22647E-05 0.00120  1.22509E-05 0.00119  1.42184E-05 0.01344 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  14]) = [  7.05642E-03 0.00713  1.91005E-04 0.04208  1.07307E-03 0.01792  1.08602E-03 0.01816  3.26645E-03 0.00970  1.09375E-03 0.01692  3.46128E-04 0.03382 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  14]) = [  8.22384E-01 0.01646  1.24909E-02 3.4E-06  3.15148E-02 0.00034  1.10706E-01 0.00047  3.22883E-01 0.00035  1.34111E+00 0.00020  9.05466E+00 0.00247 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  1.71472E-05 0.00368  1.71180E-05 0.00362  2.11998E-05 0.04026 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  1.22514E-05 0.00364  1.22306E-05 0.00358  1.51441E-05 0.04019 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  14]) = [  7.10223E-03 0.02510  2.56118E-04 0.13570  1.00375E-03 0.06094  1.02856E-03 0.05839  3.36088E-03 0.03586  1.00529E-03 0.06004  4.47645E-04 0.11221 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  14]) = [  9.32784E-01 0.06771  1.24910E-02 1.1E-05  3.14525E-02 0.00134  1.10784E-01 0.00155  3.22612E-01 0.00117  1.34098E+00 0.00077  9.04099E+00 0.00691 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  14]) = [  7.05817E-03 0.02470  2.57257E-04 0.13571  9.82873E-04 0.06007  1.02143E-03 0.05614  3.36350E-03 0.03443  9.98970E-04 0.06088  4.34147E-04 0.10504 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  14]) = [  9.19350E-01 0.06299  1.24909E-02 1.1E-05  3.14594E-02 0.00130  1.10873E-01 0.00160  3.22641E-01 0.00116  1.34136E+00 0.00075  9.04281E+00 0.00696 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -4.15091E+02 0.02506 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  1.71722E-05 0.00080 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  1.22693E-05 0.00062 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  7.09729E-03 0.00479 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -4.13331E+02 0.00488 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  7.60529E-08 0.00066 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  1.32468E-05 0.00052  1.32467E-05 0.00052  1.32443E-05 0.00562 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.38595E-05 0.00084  2.38579E-05 0.00086  2.40700E-05 0.01006 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  1.14290E-01 0.00088  1.14606E-01 0.00089  8.55746E-02 0.01107 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  9.93410E+00 0.00791 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  2.89210E+01 0.00019  3.25219E+01 0.00036 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  1])  = 'CR' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  4.88267E+03 0.02232  2.13774E+04 0.01178  3.99584E+04 0.00701  5.35511E+04 0.00896  4.93663E+04 0.00927  4.92038E+04 0.00464  3.59247E+04 0.00594  3.44379E+04 0.00815  3.14177E+04 0.01056  2.70205E+04 0.00686  2.19139E+04 0.00730  1.70337E+04 0.01038  1.27256E+04 0.00515  9.40738E+03 0.00488  6.98632E+03 0.00972  4.59991E+03 0.00651  3.48147E+03 0.01088  2.65491E+03 0.00568  1.96539E+03 0.00625  2.58162E+03 0.00455  1.37520E+03 0.00694  5.58877E+02 0.01325  2.39640E+02 0.01365  1.72501E+02 0.00727  1.03787E+02 0.00601  7.12599E+01 0.00881  5.57860E+01 0.01332  9.76190E+00 0.02472  1.06072E+01 0.03466  8.79260E+00 0.02990  4.57390E+00 0.03044  7.71892E+00 0.02228  4.53115E+00 0.02860  3.29996E+00 0.03427  5.61433E-01 0.08128  4.80161E-01 0.03123  4.34047E-01 0.06504  6.56930E-01 0.05582  5.52333E-01 0.08597  4.95302E-01 0.08191  5.08821E-01 0.04952  4.83002E-01 0.04111  9.03810E-01 0.05972  1.42891E+00 0.04767  1.76517E+00 0.03514  4.10565E+00 0.03911  3.60273E+00 0.03491  2.97935E+00 0.02028  1.44190E+00 0.03589  8.13029E-01 0.01121  5.51833E-01 0.07882  5.16126E-01 0.08842  8.18870E-01 0.02844  7.99081E-01 0.06515  1.04216E+00 0.04819  1.01991E+00 0.04072  8.92698E-01 0.03524  3.79346E-01 0.04762  1.81382E-01 0.09697  9.70821E-02 0.04147  9.11418E-02 0.08317  6.96783E-02 0.13733  5.16467E-02 0.19357  2.75878E-02 0.15425  2.17316E-02 0.08054  1.41693E-02 0.14174  1.02057E-02 0.13327  6.02406E-03 0.33198  3.51505E-03 0.16502  0.00000E+00 0.0E+00 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  2.15767E-01 0.00657  7.68714E-06 0.01051 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  5.28490E-01 0.00088  9.58550E+01 0.00472 ];
INF_CAPT                  (idx, [1:   4]) = [  1.78673E-01 0.00183  9.54655E+01 0.00474 ];
INF_ABS                   (idx, [1:   4]) = [  1.78673E-01 0.00183  9.54655E+01 0.00474 ];
INF_FISS                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_NSF                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_NUBAR                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_KAPPA                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_INVV                  (idx, [1:   4]) = [  2.69499E-09 0.00179  1.38266E-06 0.00475 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  3.49494E-01 0.00080  5.21526E-01 0.22541 ];
INF_SCATT1                (idx, [1:   4]) = [  3.82429E-02 0.00415 -4.34831E-02 1.00000 ];
INF_SCATT2                (idx, [1:   4]) = [  1.33381E-02 0.00552  2.27688E-02 1.00000 ];
INF_SCATT3                (idx, [1:   4]) = [  3.32415E-03 0.04463  3.42329E-02 0.43905 ];
INF_SCATT4                (idx, [1:   4]) = [  1.11377E-03 0.08726 -1.76689E-02 1.00000 ];
INF_SCATT5                (idx, [1:   4]) = [  2.64370E-04 0.40004  7.68290E-03 1.00000 ];
INF_SCATT6                (idx, [1:   4]) = [  6.96351E-05 1.00000 -2.99966E-02 0.45521 ];
INF_SCATT7                (idx, [1:   4]) = [  1.53614E-04 0.56239  2.23815E-02 0.99212 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  3.49494E-01 0.00080  5.21526E-01 0.22541 ];
INF_SCATTP1               (idx, [1:   4]) = [  3.82429E-02 0.00415 -4.34831E-02 1.00000 ];
INF_SCATTP2               (idx, [1:   4]) = [  1.33381E-02 0.00552  2.27688E-02 1.00000 ];
INF_SCATTP3               (idx, [1:   4]) = [  3.32415E-03 0.04463  3.42329E-02 0.43905 ];
INF_SCATTP4               (idx, [1:   4]) = [  1.11377E-03 0.08726 -1.76689E-02 1.00000 ];
INF_SCATTP5               (idx, [1:   4]) = [  2.64370E-04 0.40004  7.68290E-03 1.00000 ];
INF_SCATTP6               (idx, [1:   4]) = [  6.96351E-05 1.00000 -2.99966E-02 0.45521 ];
INF_SCATTP7               (idx, [1:   4]) = [  1.53614E-04 0.56239  2.23815E-02 0.99212 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.43035E-01 0.00159  1.53157E+02 0.11373 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  9.71729E-01 0.00159  2.27904E-03 0.10074 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  1.78673E-01 0.00183  9.54655E+01 0.00474 ];
INF_REMXS                 (idx, [1:   4]) = [  1.78998E-01 0.00263  9.53335E+01 0.00440 ];

% Poison cross sections:

INF_I135_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM147_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148M_YIELD          (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM149_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_I135_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM147_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM148M_MICRO_ABS      (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_PM149_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_XE135_MACRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_SM149_MACRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Fission spectra:

INF_CHIT                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHIP                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHID                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

INF_S0                    (idx, [1:   8]) = [  3.49493E-01 0.00080  1.37838E-06 0.40830  0.00000E+00 0.0E+00  5.21526E-01 0.22541 ];
INF_S1                    (idx, [1:   8]) = [  3.82434E-02 0.00414 -5.20545E-07 0.89028  0.00000E+00 0.0E+00 -4.34831E-02 1.00000 ];
INF_S2                    (idx, [1:   8]) = [  1.33381E-02 0.00551  4.46749E-08 1.00000  0.00000E+00 0.0E+00  2.27688E-02 1.00000 ];
INF_S3                    (idx, [1:   8]) = [  3.32427E-03 0.04468 -1.18529E-07 1.00000  0.00000E+00 0.0E+00  3.42329E-02 0.43905 ];
INF_S4                    (idx, [1:   8]) = [  1.11376E-03 0.08726  8.53898E-09 1.00000  0.00000E+00 0.0E+00 -1.76689E-02 1.00000 ];
INF_S5                    (idx, [1:   8]) = [  2.64211E-04 0.40007  1.58809E-07 1.00000  0.00000E+00 0.0E+00  7.68290E-03 1.00000 ];
INF_S6                    (idx, [1:   8]) = [  6.96361E-05 1.00000 -9.41037E-10 1.00000  0.00000E+00 0.0E+00 -2.99966E-02 0.45521 ];
INF_S7                    (idx, [1:   8]) = [  1.53637E-04 0.56151 -2.27762E-08 1.00000  0.00000E+00 0.0E+00  2.23815E-02 0.99212 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  3.49493E-01 0.00080  1.37838E-06 0.40830  0.00000E+00 0.0E+00  5.21526E-01 0.22541 ];
INF_SP1                   (idx, [1:   8]) = [  3.82434E-02 0.00414 -5.20545E-07 0.89028  0.00000E+00 0.0E+00 -4.34831E-02 1.00000 ];
INF_SP2                   (idx, [1:   8]) = [  1.33381E-02 0.00551  4.46749E-08 1.00000  0.00000E+00 0.0E+00  2.27688E-02 1.00000 ];
INF_SP3                   (idx, [1:   8]) = [  3.32427E-03 0.04468 -1.18529E-07 1.00000  0.00000E+00 0.0E+00  3.42329E-02 0.43905 ];
INF_SP4                   (idx, [1:   8]) = [  1.11376E-03 0.08726  8.53898E-09 1.00000  0.00000E+00 0.0E+00 -1.76689E-02 1.00000 ];
INF_SP5                   (idx, [1:   8]) = [  2.64211E-04 0.40007  1.58809E-07 1.00000  0.00000E+00 0.0E+00  7.68290E-03 1.00000 ];
INF_SP6                   (idx, [1:   8]) = [  6.96361E-05 1.00000 -9.41037E-10 1.00000  0.00000E+00 0.0E+00 -2.99966E-02 0.45521 ];
INF_SP7                   (idx, [1:   8]) = [  1.53637E-04 0.56151 -2.27762E-08 1.00000  0.00000E+00 0.0E+00  2.23815E-02 0.99212 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_KEFF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_B2                     (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_ERR                    (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CAPT                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_ABS                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_FISS                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NSF                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NUBAR                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT1                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT2                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT3                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT4                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT5                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT6                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATT7                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP1                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP2                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP3                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP4                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP5                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP6                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SCATTP7                (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_REMXS                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Poison cross sections:

B1_I135_YIELD             (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM147_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148M_YIELD           (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM149_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_YIELD            (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_I135_MICRO_ABS         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM147_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM148M_MICRO_ABS       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_PM149_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_MICRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_XE135_MACRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SM149_MACRO_ABS        (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Fission spectra:

B1_CHIT                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHIP                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHID                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

B1_S0                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S1                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S2                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S3                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S4                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S5                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S6                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_S7                     (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP1                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP2                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP3                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP4                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP5                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP6                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_SP7                    (idx, [1:   8]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  1.84806E-02 0.00310  1.91474E-05 0.01133 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  1.16242E-02 0.00298  1.20566E-05 0.01356 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  2.62008E-02 0.00355  2.72274E-05 0.02276 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  2.62210E-02 0.00385  2.71105E-05 0.02257 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.80376E+01 0.00308  1.74179E+04 0.01153 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  2.86768E+01 0.00298  2.76673E+04 0.01332 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.27229E+01 0.00352  1.22668E+04 0.02173 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.27132E+01 0.00383  1.23196E+04 0.02188 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  14]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
LAMBDA                    (idx, [1:  14]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
