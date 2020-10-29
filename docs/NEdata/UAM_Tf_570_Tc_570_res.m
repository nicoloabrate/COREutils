
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
INPUT_FILE_NAME           (idx, [1:  8])  = 'UAM_HZP1' ;
WORKING_DIRECTORY         (idx, [1: 33])  = '/home/abrate/ricerca/esrel2020/XS' ;
HOSTNAME                  (idx, [1:  7])  = 'vpcen13' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz' ;
CPU_MHZ                   (idx, 1)        = 4294967295.0 ;
START_DATE                (idx, [1: 24])  = 'Sat Aug 29 19:41:15 2020' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Sun Aug 30 03:33:18 2020' ;

% Run parameters:

POP                       (idx, 1)        = 1000000 ;
CYCLES                    (idx, 1)        = 100 ;
SKIP                      (idx, 1)        = 1000 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1598722875174 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 1 0 15 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 1 ;
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
OMP_HISTORY_PROFILE       (idx, [1:  30]) = [  1.02009E+00  9.94705E-01  1.00387E+00  1.00056E+00  9.88198E-01  1.00722E+00  1.00401E+00  9.96277E-01  1.00226E+00  1.00432E+00  9.94099E-01  9.95657E-01  9.95880E-01  9.96650E-01  1.00162E+00  1.00152E+00  9.97196E-01  1.00175E+00  9.98859E-01  9.94033E-01  1.00599E+00  1.00773E+00  1.00269E+00  9.96632E-01  9.96583E-01  1.00070E+00  9.98139E-01  9.97152E-01  9.98903E-01  9.96708E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 46])  = '/opt/serpent/xsdata/jeff311/sss_jeff311.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  3.02816E-01 0.00011  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  6.97184E-01 4.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  5.09482E-01 4.4E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  5.62564E-01 3.2E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.81431E+00 8.9E-05  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  2.36050E+01 0.00010  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  1.50578E+01 0.00018  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 100 ;
SIMULATED_HISTORIES       (idx, 1)        = 100003951 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.14426E+04 ;
RUNNING_TIME              (idx, 1)        =  4.72050E+02 ;
INIT_TIME                 (idx, [1:  2])  = [  2.40100E-01  2.40100E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.48333E-03  5.48333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  4.71803E+02  4.71803E+02  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
LEAKAGE_CORR_SOL_TIME     (idx, 1)        =  1.93334E-03 ;
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  4.72036E+02  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 24.24027 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.41670E+01 0.00036 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  8.01323E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 100712.49 ;
ALLOC_MEMSIZE             (idx, 1)        = 8618.97;
MEMSIZE                   (idx, 1)        = 8405.65;
XS_MEMSIZE                (idx, 1)        = 1458.21;
MAT_MEMSIZE               (idx, 1)        = 161.71;
RES_MEMSIZE               (idx, 1)        = 40.61;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 6745.12;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 213.32;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 2 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 377473 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.50000E-04 ;
URES_EMAX                 (idx, 1)        =  1.00000E+00 ;
URES_AVAIL                (idx, 1)        = 22 ;
URES_USED                 (idx, 1)        = 22 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 51 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 51 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 1255 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 1 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
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

NORM_COEF                 (idx, [1:   4]) = [  3.37127E+09 0.00011  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  5.77603E-01 0.00025 ];
U235_FISS                 (idx, [1:   4]) = [  9.90572E+14 0.00019  7.34684E-01 0.00017 ];
U238_FISS                 (idx, [1:   4]) = [  9.21228E+13 0.00056  6.83252E-02 0.00052 ];
PU239_FISS                (idx, [1:   4]) = [  2.18024E+14 0.00063  1.61704E-01 0.00061 ];
PU240_FISS                (idx, [1:   4]) = [  2.57850E+12 0.00379  1.91239E-03 0.00376 ];
PU241_FISS                (idx, [1:   4]) = [  4.33275E+13 0.00115  3.21349E-02 0.00112 ];
U235_CAPT                 (idx, [1:   4]) = [  2.18104E+14 0.00038  1.07557E-01 0.00036 ];
U238_CAPT                 (idx, [1:   4]) = [  8.16001E+14 0.00026  4.02407E-01 0.00016 ];
PU239_CAPT                (idx, [1:   4]) = [  1.19322E+14 0.00062  5.88430E-02 0.00060 ];
PU240_CAPT                (idx, [1:   4]) = [  1.06800E+14 0.00077  5.26678E-02 0.00076 ];
PU241_CAPT                (idx, [1:   4]) = [  1.46475E+13 0.00157  7.22336E-03 0.00156 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 100003951 1.00000E+08 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.42950E+05 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 60063923 6.01492E+07 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 39940028 3.99937E+07 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 1.58504E-04 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  4.40000E+04 0.0E+00 ];
TOT_POWDENS               (idx, [1:   2]) = [  6.08444E-03 6.9E-09 ];
TOT_GENRATE               (idx, [1:   2]) = [  3.43997E+15 1.7E-05 ];
TOT_FISSRATE              (idx, [1:   2]) = [  1.34797E+15 3.4E-06 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  2.02801E+15 0.00012 ];
TOT_ABSRATE               (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_SRCRATE               (idx, [1:   2]) = [  3.37127E+15 0.00011 ];
TOT_FLUX                  (idx, [1:   2]) = [  1.54978E+17 0.00012 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  1.02483E+17 0.00011 ];
INI_FMASS                 (idx, 1)        =  7.23156E+00 ;
TOT_FMASS                 (idx, 1)        =  7.23156E+00 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.59347E+00 0.00010 ];
SIX_FF_F                  (idx, [1:   2]) = [  7.86859E-01 6.5E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.09029E-01 9.5E-05 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.33656E+00 9.5E-05 ];
SIX_FF_LF                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_LT                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.55197E+00 2.0E-05 ];
FISSE                     (idx, [1:   2]) = [  2.03733E+02 3.4E-06 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.02065E+00 0.00013  1.01426E+00 0.00013  6.36553E-03 0.00198 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
COL_KEFF                  (idx, [1:   2]) = [  1.02038E+00 0.00011 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.69604E+01 4.8E-05 ];
IMP_ALF                   (idx, [1:   2]) = [  1.69598E+01 2.6E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  8.61468E-07 0.00081 ];
IMP_EALF                  (idx, [1:   2]) = [  8.61929E-07 0.00044 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.43848E-01 0.00060 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.43913E-01 0.00024 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  6.41574E-03 0.00138  1.77755E-04 0.00760  9.59151E-04 0.00319  5.22748E-04 0.00428  1.16888E-03 0.00304  2.04914E-03 0.00239  7.14018E-04 0.00388  5.89915E-04 0.00359  2.34134E-04 0.00687 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.79898E-01 0.00196  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.4E-09  2.92467E-01 0.0E+00  6.66488E-01 3.7E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  6.39411E-03 0.00193  1.79105E-04 0.01071  9.51549E-04 0.00465  5.21851E-04 0.00621  1.16414E-03 0.00445  2.04733E-03 0.00383  7.08080E-04 0.00538  5.89788E-04 0.00580  2.32266E-04 0.00948 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.79629E-01 0.00287  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.2E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 2.6E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  2.08580E-05 0.00030  2.08373E-05 0.00031  2.41314E-05 0.00231 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  2.12887E-05 0.00026  2.12676E-05 0.00027  2.46299E-05 0.00233 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  6.22890E-03 0.00210  1.71842E-04 0.01246  9.28634E-04 0.00501  5.07929E-04 0.00666  1.13399E-03 0.00417  1.99048E-03 0.00350  6.93602E-04 0.00640  5.76057E-04 0.00647  2.26363E-04 0.01118 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.80252E-01 0.00314  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.0E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  2.07746E-05 0.00068  2.07537E-05 0.00069  2.41287E-05 0.00720 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  2.12036E-05 0.00066  2.11823E-05 0.00066  2.46267E-05 0.00719 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  6.18290E-03 0.00684  1.75511E-04 0.03639  9.52548E-04 0.01641  4.82324E-04 0.02302  1.09572E-03 0.01605  1.97731E-03 0.01143  6.86947E-04 0.02032  5.90552E-04 0.02301  2.21991E-04 0.03841 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.82637E-01 0.01112  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 3.2E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  6.16570E-03 0.00656  1.74535E-04 0.03564  9.47350E-04 0.01608  4.84709E-04 0.02241  1.08905E-03 0.01531  1.97312E-03 0.01103  6.84544E-04 0.01978  5.89190E-04 0.02159  2.23206E-04 0.03829 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.83650E-01 0.01097  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.5E-09  1.33042E-01 3.2E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -2.97940E+02 0.00692 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  2.08903E-05 0.00022 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  2.13217E-05 0.00017 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  6.27285E-03 0.00156 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -3.00278E+02 0.00161 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  3.79968E-07 0.00016 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  2.82212E-06 0.00011  2.82200E-06 0.00011  2.83937E-06 0.00111 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.51693E-05 0.00015  2.51641E-05 0.00015  2.59132E-05 0.00158 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.09615E-01 9.5E-05  6.09284E-01 9.8E-05  6.60988E-01 0.00196 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.21135E+01 0.00292 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.03573E+01 6.5E-05  3.13774E+01 9.9E-05 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  2])  = 'U2' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  3.04929E+06 0.00112  1.24187E+07 0.00074  2.58494E+07 0.00074  2.82755E+07 0.00076  2.63381E+07 0.00079  2.88255E+07 0.00075  1.96536E+07 0.00059  1.74830E+07 0.00058  1.33161E+07 0.00053  1.08678E+07 0.00080  9.35854E+06 0.00075  8.45849E+06 0.00060  7.80653E+06 0.00086  7.41686E+06 0.00064  7.22703E+06 0.00091  6.24171E+06 0.00081  6.18271E+06 0.00071  6.12946E+06 0.00079  6.00895E+06 0.00066  1.17421E+07 0.00089  1.13489E+07 0.00053  8.19933E+06 0.00046  5.32005E+06 0.00090  6.13677E+06 0.00068  5.79003E+06 0.00053  5.27701E+06 0.00121  8.64640E+06 0.00063  1.97659E+06 0.00103  2.47453E+06 0.00064  2.24290E+06 0.00044  1.30253E+06 0.00092  2.26189E+06 0.00081  1.53531E+06 0.00053  1.31062E+06 0.00075  2.50031E+05 0.00101  2.48577E+05 0.00118  2.54167E+05 0.00092  2.62077E+05 0.00149  2.58927E+05 0.00153  2.54817E+05 0.00172  2.64180E+05 0.00135  2.47753E+05 0.00104  4.68630E+05 0.00098  7.47126E+05 0.00085  9.50945E+05 0.00072  2.50625E+06 0.00060  2.63596E+06 0.00082  2.85435E+06 0.00040  1.91252E+06 0.00045  1.39708E+06 0.00033  1.07439E+06 0.00097  1.25047E+06 0.00054  2.31986E+06 0.00068  3.03021E+06 0.00093  5.68454E+06 0.00075  8.40771E+06 0.00069  1.20552E+07 0.00065  7.55867E+06 0.00057  5.30903E+06 0.00063  3.76326E+06 0.00058  3.35666E+06 0.00058  3.27843E+06 0.00054  2.72944E+06 0.00071  1.81682E+06 0.00066  1.67494E+06 0.00047  1.47704E+06 0.00081  1.24106E+06 0.00024  9.64280E+05 0.00052  6.37689E+05 0.00054  2.20013E+05 0.00043 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  1.04508E+00 0.00021 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  5.61630E+16 0.00064  1.29203E+16 0.00050 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  5.48545E-01 4.9E-05  1.34820E+00 3.9E-05 ];
INF_CAPT                  (idx, [1:   4]) = [  6.71089E-03 0.00024  3.52710E-02 6.2E-05 ];
INF_ABS                   (idx, [1:   4]) = [  8.75579E-03 0.00019  7.37314E-02 0.00011 ];
INF_FISS                  (idx, [1:   4]) = [  2.04490E-03 6.3E-05  3.84604E-02 0.00016 ];
INF_NSF                   (idx, [1:   4]) = [  5.28323E-03 6.5E-05  9.36972E-02 0.00016 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.58361E+00 2.0E-05  2.43620E+00 0.0E+00 ];
INF_KAPPA                 (idx, [1:   4]) = [  2.03669E+02 7.8E-07  2.02270E+02 0.0E+00 ];
INF_INVV                  (idx, [1:   4]) = [  5.96917E-08 0.00012  2.45489E-06 3.3E-05 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  5.39791E-01 4.7E-05  1.27446E+00 4.9E-05 ];
INF_SCATT1                (idx, [1:   4]) = [  2.46453E-01 9.1E-05  3.34345E-01 8.9E-05 ];
INF_SCATT2                (idx, [1:   4]) = [  9.73697E-02 0.00018  8.18629E-02 0.00024 ];
INF_SCATT3                (idx, [1:   4]) = [  7.31369E-03 0.00170  2.46816E-02 0.00086 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.03129E-02 0.00087 -6.57291E-03 0.00230 ];
INF_SCATT5                (idx, [1:   4]) = [  2.56171E-04 0.03018  5.01494E-03 0.00261 ];
INF_SCATT6                (idx, [1:   4]) = [  5.16730E-03 0.00046 -1.34973E-02 0.00081 ];
INF_SCATT7                (idx, [1:   4]) = [  7.65837E-04 0.00595 -1.87168E-04 0.09151 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  5.39830E-01 4.7E-05  1.27446E+00 4.9E-05 ];
INF_SCATTP1               (idx, [1:   4]) = [  2.46453E-01 9.1E-05  3.34345E-01 8.9E-05 ];
INF_SCATTP2               (idx, [1:   4]) = [  9.73700E-02 0.00018  8.18629E-02 0.00024 ];
INF_SCATTP3               (idx, [1:   4]) = [  7.31369E-03 0.00170  2.46816E-02 0.00086 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.03129E-02 0.00086 -6.57291E-03 0.00230 ];
INF_SCATTP5               (idx, [1:   4]) = [  2.56199E-04 0.03011  5.01494E-03 0.00261 ];
INF_SCATTP6               (idx, [1:   4]) = [  5.16732E-03 0.00046 -1.34973E-02 0.00081 ];
INF_SCATTP7               (idx, [1:   4]) = [  7.65829E-04 0.00594 -1.87168E-04 0.09151 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  2.22859E-01 0.00011  8.94369E-01 5.9E-05 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.49572E+00 0.00011  3.72702E-01 5.9E-05 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  8.71704E-03 0.00019  7.37314E-02 0.00011 ];
INF_REMXS                 (idx, [1:   4]) = [  2.69644E-02 0.00017  7.50358E-02 0.00018 ];

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

INF_CHIT                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHIP                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHID                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

INF_S0                    (idx, [1:   8]) = [  5.21581E-01 4.7E-05  1.82104E-02 0.00011  1.28954E-03 0.00129  1.27317E+00 4.9E-05 ];
INF_S1                    (idx, [1:   8]) = [  2.41152E-01 9.4E-05  5.30126E-03 0.00013  6.23121E-04 0.00136  3.33722E-01 8.9E-05 ];
INF_S2                    (idx, [1:   8]) = [  9.89596E-02 0.00017 -1.58984E-03 0.00074  3.30922E-04 0.00198  8.15319E-02 0.00025 ];
INF_S3                    (idx, [1:   8]) = [  9.19078E-03 0.00131 -1.87708E-03 0.00031  1.15845E-04 0.00832  2.45658E-02 0.00085 ];
INF_S4                    (idx, [1:   8]) = [ -9.70299E-03 0.00081 -6.09909E-04 0.00190 -7.96372E-07 1.00000 -6.57211E-03 0.00219 ];
INF_S5                    (idx, [1:   8]) = [  2.26628E-04 0.03196  2.95437E-05 0.02916 -4.74214E-05 0.01960  5.06236E-03 0.00258 ];
INF_S6                    (idx, [1:   8]) = [  5.31427E-03 0.00034 -1.46971E-04 0.00825 -5.96015E-05 0.00623 -1.34377E-02 0.00080 ];
INF_S7                    (idx, [1:   8]) = [  9.44913E-04 0.00506 -1.79076E-04 0.00393 -5.39754E-05 0.01000 -1.33193E-04 0.12621 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  5.21619E-01 4.7E-05  1.82104E-02 0.00011  1.28954E-03 0.00129  1.27317E+00 4.9E-05 ];
INF_SP1                   (idx, [1:   8]) = [  2.41152E-01 9.4E-05  5.30126E-03 0.00013  6.23121E-04 0.00136  3.33722E-01 8.9E-05 ];
INF_SP2                   (idx, [1:   8]) = [  9.89598E-02 0.00017 -1.58984E-03 0.00074  3.30922E-04 0.00198  8.15319E-02 0.00025 ];
INF_SP3                   (idx, [1:   8]) = [  9.19077E-03 0.00131 -1.87708E-03 0.00031  1.15845E-04 0.00832  2.45658E-02 0.00085 ];
INF_SP4                   (idx, [1:   8]) = [ -9.70295E-03 0.00080 -6.09909E-04 0.00190 -7.96372E-07 1.00000 -6.57211E-03 0.00219 ];
INF_SP5                   (idx, [1:   8]) = [  2.26655E-04 0.03188  2.95437E-05 0.02916 -4.74214E-05 0.01960  5.06236E-03 0.00258 ];
INF_SP6                   (idx, [1:   8]) = [  5.31429E-03 0.00034 -1.46971E-04 0.00825 -5.96015E-05 0.00623 -1.34377E-02 0.00080 ];
INF_SP7                   (idx, [1:   8]) = [  9.44905E-04 0.00505 -1.79076E-04 0.00393 -5.39754E-05 0.01000 -1.33193E-04 0.12621 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  2.98140E+06 0.00165  1.23048E+07 0.00084  2.57100E+07 0.00084  2.82036E+07 0.00068  2.62792E+07 0.00067  2.86536E+07 0.00075  1.95280E+07 0.00054  1.73457E+07 0.00051  1.31945E+07 0.00045  1.07593E+07 0.00078  9.26046E+06 0.00067  8.36565E+06 0.00060  7.71648E+06 0.00085  7.32790E+06 0.00072  7.13706E+06 0.00096  6.16207E+06 0.00085  6.10212E+06 0.00072  6.04823E+06 0.00087  5.92744E+06 0.00067  1.15814E+07 0.00094  1.11904E+07 0.00061  8.08652E+06 0.00049  5.24848E+06 0.00102  6.05590E+06 0.00074  5.71565E+06 0.00054  5.21388E+06 0.00128  8.54674E+06 0.00066  1.95426E+06 0.00094  2.44904E+06 0.00072  2.21990E+06 0.00042  1.28929E+06 0.00092  2.23931E+06 0.00082  1.52094E+06 0.00071  1.30038E+06 0.00076  2.48295E+05 0.00125  2.47034E+05 0.00148  2.52559E+05 0.00095  2.60580E+05 0.00159  2.57501E+05 0.00176  2.53424E+05 0.00179  2.62770E+05 0.00139  2.46389E+05 0.00106  4.65807E+05 0.00118  7.42840E+05 0.00077  9.45227E+05 0.00054  2.49216E+06 0.00070  2.62546E+06 0.00082  2.85707E+06 0.00039  1.92762E+06 0.00049  1.41570E+06 0.00035  1.09263E+06 0.00084  1.27610E+06 0.00052  2.37988E+06 0.00061  3.12283E+06 0.00091  5.89056E+06 0.00071  8.75253E+06 0.00066  1.25910E+07 0.00066  7.90664E+06 0.00061  5.55679E+06 0.00068  3.93983E+06 0.00055  3.51428E+06 0.00056  3.43243E+06 0.00055  2.85717E+06 0.00076  1.90159E+06 0.00065  1.75255E+06 0.00049  1.54527E+06 0.00085  1.29826E+06 0.00029  1.00832E+06 0.00054  6.66604E+05 0.00058  2.29903E+05 0.00041 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  1.05333E+00 0.00021 ];
B1_KEFF                   (idx, [1:   2]) = [  1.00000E+00 8.3E-09 ];
B1_B2                     (idx, [1:   2]) = [  9.57332E-04 0.00400 ];
B1_ERR                    (idx, [1:   2]) = [  4.27314E-08 0.05193 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  5.56756E+16 0.00063  1.34077E+16 0.00053 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  5.47725E-01 5.7E-05  1.35122E+00 4.3E-05 ];
B1_CAPT                   (idx, [1:   4]) = [  6.68842E-03 0.00028  3.54073E-02 6.0E-05 ];
B1_ABS                    (idx, [1:   4]) = [  8.73216E-03 0.00022  7.40252E-02 0.00011 ];
B1_FISS                   (idx, [1:   4]) = [  2.04373E-03 9.6E-05  3.86179E-02 0.00016 ];
B1_NSF                    (idx, [1:   4]) = [  5.28020E-03 0.00010  9.40809E-02 0.00016 ];
B1_NUBAR                  (idx, [1:   4]) = [  2.58361E+00 2.9E-05  2.43620E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  2.03673E+02 1.5E-06  2.02270E+02 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  5.96240E-08 5.5E-05  2.46460E-06 3.8E-05 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  5.38995E-01 5.5E-05  1.27718E+00 5.3E-05 ];
B1_SCATT1                 (idx, [1:   4]) = [  2.46030E-01 9.2E-05  3.34268E-01 8.9E-05 ];
B1_SCATT2                 (idx, [1:   4]) = [  9.72304E-02 0.00017  8.16203E-02 0.00023 ];
B1_SCATT3                 (idx, [1:   4]) = [  7.32408E-03 0.00168  2.46002E-02 0.00086 ];
B1_SCATT4                 (idx, [1:   4]) = [ -1.02749E-02 0.00092 -6.64826E-03 0.00228 ];
B1_SCATT5                 (idx, [1:   4]) = [  2.61191E-04 0.03049  5.05155E-03 0.00263 ];
B1_SCATT6                 (idx, [1:   4]) = [  5.15633E-03 0.00046 -1.35618E-02 0.00080 ];
B1_SCATT7                 (idx, [1:   4]) = [  7.62585E-04 0.00600 -1.62569E-04 0.10586 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  5.39033E-01 5.5E-05  1.27718E+00 5.3E-05 ];
B1_SCATTP1                (idx, [1:   4]) = [  2.46030E-01 9.2E-05  3.34268E-01 8.9E-05 ];
B1_SCATTP2                (idx, [1:   4]) = [  9.72306E-02 0.00017  8.16203E-02 0.00023 ];
B1_SCATTP3                (idx, [1:   4]) = [  7.32408E-03 0.00168  2.46002E-02 0.00086 ];
B1_SCATTP4                (idx, [1:   4]) = [ -1.02749E-02 0.00092 -6.64826E-03 0.00228 ];
B1_SCATTP5                (idx, [1:   4]) = [  2.61218E-04 0.03042  5.05155E-03 0.00263 ];
B1_SCATTP6                (idx, [1:   4]) = [  5.15634E-03 0.00046 -1.35618E-02 0.00080 ];
B1_SCATTP7                (idx, [1:   4]) = [  7.62577E-04 0.00599 -1.62569E-04 0.10586 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  2.41181E-01 0.00010  8.42390E-01 5.5E-05 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  1.38209E+00 0.00010  3.95699E-01 5.5E-05 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  8.69393E-03 0.00022  7.40252E-02 0.00011 ];
B1_REMXS                  (idx, [1:   4]) = [  2.69500E-02 0.00011  7.52784E-02 0.00017 ];

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

B1_CHIT                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHIP                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHID                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

B1_S0                     (idx, [1:   8]) = [  5.20775E-01 5.7E-05  1.82197E-02 3.5E-05  1.23842E-03 0.00131  1.27595E+00 5.4E-05 ];
B1_S1                     (idx, [1:   8]) = [  2.40722E-01 9.6E-05  5.30753E-03 0.00011  5.98430E-04 0.00136  3.33670E-01 8.9E-05 ];
B1_S2                     (idx, [1:   8]) = [  9.88158E-02 0.00016 -1.58535E-03 0.00072  3.17702E-04 0.00196  8.13026E-02 0.00024 ];
B1_S3                     (idx, [1:   8]) = [  9.20091E-03 0.00128 -1.87683E-03 0.00037  1.11123E-04 0.00830  2.44891E-02 0.00085 ];
B1_S4                     (idx, [1:   8]) = [ -9.66259E-03 0.00085 -6.12313E-04 0.00204 -8.53150E-07 0.99673 -6.64741E-03 0.00219 ];
B1_S5                     (idx, [1:   8]) = [  2.33382E-04 0.03203  2.78092E-05 0.03128 -4.55791E-05 0.01964  5.09713E-03 0.00260 ];
B1_S6                     (idx, [1:   8]) = [  5.30373E-03 0.00034 -1.47404E-04 0.00815 -5.72332E-05 0.00629 -1.35046E-02 0.00079 ];
B1_S7                     (idx, [1:   8]) = [  9.41521E-04 0.00509 -1.78936E-04 0.00383 -5.18104E-05 0.01008 -1.10759E-04 0.15259 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  5.20813E-01 5.7E-05  1.82197E-02 3.5E-05  1.23842E-03 0.00131  1.27595E+00 5.4E-05 ];
B1_SP1                    (idx, [1:   8]) = [  2.40723E-01 9.6E-05  5.30753E-03 0.00011  5.98430E-04 0.00136  3.33670E-01 8.9E-05 ];
B1_SP2                    (idx, [1:   8]) = [  9.88160E-02 0.00016 -1.58535E-03 0.00072  3.17702E-04 0.00196  8.13026E-02 0.00024 ];
B1_SP3                    (idx, [1:   8]) = [  9.20090E-03 0.00128 -1.87683E-03 0.00037  1.11123E-04 0.00830  2.44891E-02 0.00085 ];
B1_SP4                    (idx, [1:   8]) = [ -9.66255E-03 0.00085 -6.12313E-04 0.00204 -8.53150E-07 0.99673 -6.64741E-03 0.00219 ];
B1_SP5                    (idx, [1:   8]) = [  2.33409E-04 0.03194  2.78092E-05 0.03128 -4.55791E-05 0.01964  5.09713E-03 0.00260 ];
B1_SP6                    (idx, [1:   8]) = [  5.30375E-03 0.00034 -1.47404E-04 0.00815 -5.72332E-05 0.00629 -1.35046E-02 0.00079 ];
B1_SP7                    (idx, [1:   8]) = [  9.41513E-04 0.00508 -1.78936E-04 0.00383 -5.18104E-05 0.01008 -1.10759E-04 0.15259 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  2.41331E-01 0.00023  8.57043E-01 0.00053 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  2.43328E-01 0.00033  8.80708E-01 0.00206 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  2.43347E-01 0.00015  8.78710E-01 0.00116 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  2.37416E-01 0.00029  8.15066E-01 0.00128 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.38123E+00 0.00023  3.88934E-01 0.00053 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  1.36989E+00 0.00033  3.78490E-01 0.00206 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.36979E+00 0.00015  3.79346E-01 0.00116 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.40401E+00 0.00029  4.08968E-01 0.00128 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  6.98895E-03 0.00249  2.00978E-04 0.01430  1.01733E-03 0.00637  5.84736E-04 0.00853  1.29163E-03 0.00640  2.24428E-03 0.00453  7.65450E-04 0.00848  6.37084E-04 0.00810  2.47470E-04 0.01295 ];
LAMBDA                    (idx, [1:  18]) = [  4.74455E-01 0.00421  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.0E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 3.7E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];


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
INPUT_FILE_NAME           (idx, [1:  8])  = 'UAM_HZP1' ;
WORKING_DIRECTORY         (idx, [1: 33])  = '/home/abrate/ricerca/esrel2020/XS' ;
HOSTNAME                  (idx, [1:  7])  = 'vpcen13' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz' ;
CPU_MHZ                   (idx, 1)        = 4294967295.0 ;
START_DATE                (idx, [1: 24])  = 'Sat Aug 29 19:41:15 2020' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Sun Aug 30 03:33:18 2020' ;

% Run parameters:

POP                       (idx, 1)        = 1000000 ;
CYCLES                    (idx, 1)        = 100 ;
SKIP                      (idx, 1)        = 1000 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1598722875174 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 1 0 15 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 1 ;
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
OMP_HISTORY_PROFILE       (idx, [1:  30]) = [  1.02009E+00  9.94705E-01  1.00387E+00  1.00056E+00  9.88198E-01  1.00722E+00  1.00401E+00  9.96277E-01  1.00226E+00  1.00432E+00  9.94099E-01  9.95657E-01  9.95880E-01  9.96650E-01  1.00162E+00  1.00152E+00  9.97196E-01  1.00175E+00  9.98859E-01  9.94033E-01  1.00599E+00  1.00773E+00  1.00269E+00  9.96632E-01  9.96583E-01  1.00070E+00  9.98139E-01  9.97152E-01  9.98903E-01  9.96708E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 46])  = '/opt/serpent/xsdata/jeff311/sss_jeff311.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  3.02816E-01 0.00011  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  6.97184E-01 4.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  5.09482E-01 4.4E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  5.62564E-01 3.2E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.81431E+00 8.9E-05  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  2.36050E+01 0.00010  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  1.50578E+01 0.00018  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 100 ;
SIMULATED_HISTORIES       (idx, 1)        = 100003951 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.14426E+04 ;
RUNNING_TIME              (idx, 1)        =  4.72050E+02 ;
INIT_TIME                 (idx, [1:  2])  = [  2.40100E-01  2.40100E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.48333E-03  5.48333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  4.71803E+02  4.71803E+02  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
LEAKAGE_CORR_SOL_TIME     (idx, 1)        =  1.93334E-03 ;
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  4.72036E+02  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 24.24027 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.41670E+01 0.00036 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  8.01323E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 100712.49 ;
ALLOC_MEMSIZE             (idx, 1)        = 8618.97;
MEMSIZE                   (idx, 1)        = 8405.65;
XS_MEMSIZE                (idx, 1)        = 1458.21;
MAT_MEMSIZE               (idx, 1)        = 161.71;
RES_MEMSIZE               (idx, 1)        = 40.61;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 6745.12;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 213.32;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 2 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 377473 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.50000E-04 ;
URES_EMAX                 (idx, 1)        =  1.00000E+00 ;
URES_AVAIL                (idx, 1)        = 22 ;
URES_USED                 (idx, 1)        = 22 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 51 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 51 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 1255 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 1 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
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

NORM_COEF                 (idx, [1:   4]) = [  3.37127E+09 0.00011  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  5.77603E-01 0.00025 ];
U235_FISS                 (idx, [1:   4]) = [  9.90572E+14 0.00019  7.34684E-01 0.00017 ];
U238_FISS                 (idx, [1:   4]) = [  9.21228E+13 0.00056  6.83252E-02 0.00052 ];
PU239_FISS                (idx, [1:   4]) = [  2.18024E+14 0.00063  1.61704E-01 0.00061 ];
PU240_FISS                (idx, [1:   4]) = [  2.57850E+12 0.00379  1.91239E-03 0.00376 ];
PU241_FISS                (idx, [1:   4]) = [  4.33275E+13 0.00115  3.21349E-02 0.00112 ];
U235_CAPT                 (idx, [1:   4]) = [  2.18104E+14 0.00038  1.07557E-01 0.00036 ];
U238_CAPT                 (idx, [1:   4]) = [  8.16001E+14 0.00026  4.02407E-01 0.00016 ];
PU239_CAPT                (idx, [1:   4]) = [  1.19322E+14 0.00062  5.88430E-02 0.00060 ];
PU240_CAPT                (idx, [1:   4]) = [  1.06800E+14 0.00077  5.26678E-02 0.00076 ];
PU241_CAPT                (idx, [1:   4]) = [  1.46475E+13 0.00157  7.22336E-03 0.00156 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 100003951 1.00000E+08 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.42950E+05 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 60063923 6.01492E+07 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 39940028 3.99937E+07 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 1.58504E-04 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  4.40000E+04 0.0E+00 ];
TOT_POWDENS               (idx, [1:   2]) = [  6.08444E-03 6.9E-09 ];
TOT_GENRATE               (idx, [1:   2]) = [  3.43997E+15 1.7E-05 ];
TOT_FISSRATE              (idx, [1:   2]) = [  1.34797E+15 3.4E-06 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  2.02801E+15 0.00012 ];
TOT_ABSRATE               (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_SRCRATE               (idx, [1:   2]) = [  3.37127E+15 0.00011 ];
TOT_FLUX                  (idx, [1:   2]) = [  1.54978E+17 0.00012 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  1.02483E+17 0.00011 ];
INI_FMASS                 (idx, 1)        =  7.23156E+00 ;
TOT_FMASS                 (idx, 1)        =  7.23156E+00 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.59347E+00 0.00010 ];
SIX_FF_F                  (idx, [1:   2]) = [  7.86859E-01 6.5E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.09029E-01 9.5E-05 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.33656E+00 9.5E-05 ];
SIX_FF_LF                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_LT                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.55197E+00 2.0E-05 ];
FISSE                     (idx, [1:   2]) = [  2.03733E+02 3.4E-06 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.02065E+00 0.00013  1.01426E+00 0.00013  6.36553E-03 0.00198 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
COL_KEFF                  (idx, [1:   2]) = [  1.02038E+00 0.00011 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.69604E+01 4.8E-05 ];
IMP_ALF                   (idx, [1:   2]) = [  1.69598E+01 2.6E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  8.61468E-07 0.00081 ];
IMP_EALF                  (idx, [1:   2]) = [  8.61929E-07 0.00044 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.43848E-01 0.00060 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.43913E-01 0.00024 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  6.41574E-03 0.00138  1.77755E-04 0.00760  9.59151E-04 0.00319  5.22748E-04 0.00428  1.16888E-03 0.00304  2.04914E-03 0.00239  7.14018E-04 0.00388  5.89915E-04 0.00359  2.34134E-04 0.00687 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.79898E-01 0.00196  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.4E-09  2.92467E-01 0.0E+00  6.66488E-01 3.7E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  6.39411E-03 0.00193  1.79105E-04 0.01071  9.51549E-04 0.00465  5.21851E-04 0.00621  1.16414E-03 0.00445  2.04733E-03 0.00383  7.08080E-04 0.00538  5.89788E-04 0.00580  2.32266E-04 0.00948 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.79629E-01 0.00287  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.2E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 2.6E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  2.08580E-05 0.00030  2.08373E-05 0.00031  2.41314E-05 0.00231 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  2.12887E-05 0.00026  2.12676E-05 0.00027  2.46299E-05 0.00233 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  6.22890E-03 0.00210  1.71842E-04 0.01246  9.28634E-04 0.00501  5.07929E-04 0.00666  1.13399E-03 0.00417  1.99048E-03 0.00350  6.93602E-04 0.00640  5.76057E-04 0.00647  2.26363E-04 0.01118 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.80252E-01 0.00314  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.0E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  2.07746E-05 0.00068  2.07537E-05 0.00069  2.41287E-05 0.00720 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  2.12036E-05 0.00066  2.11823E-05 0.00066  2.46267E-05 0.00719 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  6.18290E-03 0.00684  1.75511E-04 0.03639  9.52548E-04 0.01641  4.82324E-04 0.02302  1.09572E-03 0.01605  1.97731E-03 0.01143  6.86947E-04 0.02032  5.90552E-04 0.02301  2.21991E-04 0.03841 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.82637E-01 0.01112  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 3.2E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  6.16570E-03 0.00656  1.74535E-04 0.03564  9.47350E-04 0.01608  4.84709E-04 0.02241  1.08905E-03 0.01531  1.97312E-03 0.01103  6.84544E-04 0.01978  5.89190E-04 0.02159  2.23206E-04 0.03829 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.83650E-01 0.01097  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.5E-09  1.33042E-01 3.2E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -2.97940E+02 0.00692 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  2.08903E-05 0.00022 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  2.13217E-05 0.00017 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  6.27285E-03 0.00156 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -3.00278E+02 0.00161 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  3.79968E-07 0.00016 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  2.82212E-06 0.00011  2.82200E-06 0.00011  2.83937E-06 0.00111 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.51693E-05 0.00015  2.51641E-05 0.00015  2.59132E-05 0.00158 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.09615E-01 9.5E-05  6.09284E-01 9.8E-05  6.60988E-01 0.00196 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.21135E+01 0.00292 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.03573E+01 6.5E-05  3.13774E+01 9.9E-05 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  2])  = 'U3' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  2.16662E+06 0.00116  8.80512E+06 0.00075  1.83377E+07 0.00118  2.00472E+07 0.00065  1.86463E+07 0.00065  2.04371E+07 0.00072  1.39201E+07 0.00088  1.23961E+07 0.00085  9.45333E+06 0.00102  7.72119E+06 0.00076  6.65033E+06 0.00061  6.01213E+06 0.00088  5.55192E+06 0.00093  5.28018E+06 0.00113  5.14324E+06 0.00089  4.44267E+06 0.00073  4.40000E+06 0.00104  4.35951E+06 0.00101  4.27054E+06 0.00089  8.33898E+06 0.00068  8.02811E+06 0.00083  5.78336E+06 0.00055  3.73454E+06 0.00105  4.28305E+06 0.00084  4.02618E+06 0.00078  3.66633E+06 0.00085  6.01033E+06 0.00093  1.37624E+06 0.00057  1.70097E+06 0.00068  1.52862E+06 0.00099  8.89121E+05 0.00168  1.56407E+06 0.00087  1.06389E+06 0.00088  9.00956E+05 0.00170  1.70607E+05 0.00191  1.69432E+05 0.00109  1.73928E+05 0.00102  1.79590E+05 0.00228  1.77890E+05 0.00152  1.75485E+05 0.00094  1.81406E+05 0.00091  1.69989E+05 0.00099  3.21192E+05 0.00180  5.12661E+05 0.00103  6.51796E+05 0.00160  1.70854E+06 0.00090  1.77599E+06 0.00077  1.86859E+06 0.00082  1.19800E+06 0.00069  8.46650E+05 0.00064  6.35144E+05 0.00108  7.23683E+05 0.00091  1.29866E+06 0.00136  1.64233E+06 0.00085  2.95836E+06 0.00095  4.20896E+06 0.00111  5.82844E+06 0.00079  3.57713E+06 0.00083  2.48483E+06 0.00085  1.74882E+06 0.00091  1.55007E+06 0.00128  1.50900E+06 0.00094  1.25032E+06 0.00089  8.30173E+05 0.00068  7.62751E+05 0.00063  6.70186E+05 0.00103  5.62505E+05 0.00139  4.35768E+05 0.00146  2.87655E+05 0.00161  9.97490E+04 0.00140 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  9.80731E-01 0.00033 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  3.97015E+16 0.00071  6.53247E+15 0.00077 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  5.49264E-01 9.1E-05  1.38232E+00 6.4E-05 ];
INF_CAPT                  (idx, [1:   4]) = [  7.38222E-03 0.00048  5.83340E-02 0.00019 ];
INF_ABS                   (idx, [1:   4]) = [  9.98045E-03 0.00041  1.10663E-01 0.00013 ];
INF_FISS                  (idx, [1:   4]) = [  2.59823E-03 0.00026  5.23287E-02 0.00026 ];
INF_NSF                   (idx, [1:   4]) = [  6.63443E-03 0.00025  1.27483E-01 0.00026 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.55344E+00 2.3E-05  2.43620E+00 0.0E+00 ];
INF_KAPPA                 (idx, [1:   4]) = [  2.03359E+02 1.6E-06  2.02270E+02 5.9E-09 ];
INF_INVV                  (idx, [1:   4]) = [  5.84143E-08 0.00022  2.35642E-06 5.6E-05 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  5.39284E-01 9.1E-05  1.27164E+00 5.2E-05 ];
INF_SCATT1                (idx, [1:   4]) = [  2.46182E-01 0.00010  3.43119E-01 0.00013 ];
INF_SCATT2                (idx, [1:   4]) = [  9.72803E-02 0.00014  8.60510E-02 0.00047 ];
INF_SCATT3                (idx, [1:   4]) = [  7.26980E-03 0.00146  2.60154E-02 0.00143 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.03272E-02 0.00064 -6.08482E-03 0.00259 ];
INF_SCATT5                (idx, [1:   4]) = [  2.69451E-04 0.01242  4.84228E-03 0.00619 ];
INF_SCATT6                (idx, [1:   4]) = [  5.17851E-03 0.00084 -1.32313E-02 0.00068 ];
INF_SCATT7                (idx, [1:   4]) = [  7.58653E-04 0.00682 -4.38860E-04 0.01801 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  5.39322E-01 9.1E-05  1.27164E+00 5.2E-05 ];
INF_SCATTP1               (idx, [1:   4]) = [  2.46182E-01 0.00010  3.43119E-01 0.00013 ];
INF_SCATTP2               (idx, [1:   4]) = [  9.72806E-02 0.00014  8.60510E-02 0.00047 ];
INF_SCATTP3               (idx, [1:   4]) = [  7.26990E-03 0.00146  2.60154E-02 0.00143 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.03271E-02 0.00064 -6.08482E-03 0.00259 ];
INF_SCATTP5               (idx, [1:   4]) = [  2.69414E-04 0.01242  4.84228E-03 0.00619 ];
INF_SCATTP6               (idx, [1:   4]) = [  5.17856E-03 0.00085 -1.32313E-02 0.00068 ];
INF_SCATTP7               (idx, [1:   4]) = [  7.58612E-04 0.00683 -4.38860E-04 0.01801 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  2.23015E-01 0.00014  9.12795E-01 8.4E-05 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.49466E+00 0.00014  3.65179E-01 8.4E-05 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  9.94234E-03 0.00043  1.10663E-01 0.00013 ];
INF_REMXS                 (idx, [1:   4]) = [  2.77362E-02 0.00021  1.12398E-01 0.00020 ];

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

INF_CHIT                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHIP                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHID                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

INF_S0                    (idx, [1:   8]) = [  5.21528E-01 8.9E-05  1.77560E-02 0.00018  1.72001E-03 0.00146  1.26992E+00 5.2E-05 ];
INF_S1                    (idx, [1:   8]) = [  2.41018E-01 0.00010  5.16341E-03 0.00018  8.38097E-04 0.00239  3.42281E-01 0.00013 ];
INF_S2                    (idx, [1:   8]) = [  9.88444E-02 0.00014 -1.56411E-03 0.00090  4.46856E-04 0.00333  8.56042E-02 0.00049 ];
INF_S3                    (idx, [1:   8]) = [  9.10290E-03 0.00118 -1.83310E-03 0.00020  1.59520E-04 0.01075  2.58559E-02 0.00147 ];
INF_S4                    (idx, [1:   8]) = [ -9.73830E-03 0.00064 -5.88923E-04 0.00114  6.68803E-07 1.00000 -6.08548E-03 0.00258 ];
INF_S5                    (idx, [1:   8]) = [  2.35778E-04 0.01540  3.36731E-05 0.02579 -6.41494E-05 0.02253  4.90643E-03 0.00615 ];
INF_S6                    (idx, [1:   8]) = [  5.32079E-03 0.00083 -1.42278E-04 0.00533 -8.28513E-05 0.00656 -1.31485E-02 0.00068 ];
INF_S7                    (idx, [1:   8]) = [  9.35369E-04 0.00586 -1.76716E-04 0.00595 -7.49114E-05 0.01033 -3.63949E-04 0.02131 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  5.21566E-01 8.9E-05  1.77560E-02 0.00018  1.72001E-03 0.00146  1.26992E+00 5.2E-05 ];
INF_SP1                   (idx, [1:   8]) = [  2.41019E-01 0.00010  5.16341E-03 0.00018  8.38097E-04 0.00239  3.42281E-01 0.00013 ];
INF_SP2                   (idx, [1:   8]) = [  9.88447E-02 0.00014 -1.56411E-03 0.00090  4.46856E-04 0.00333  8.56042E-02 0.00049 ];
INF_SP3                   (idx, [1:   8]) = [  9.10300E-03 0.00118 -1.83310E-03 0.00020  1.59520E-04 0.01075  2.58559E-02 0.00147 ];
INF_SP4                   (idx, [1:   8]) = [ -9.73819E-03 0.00064 -5.88923E-04 0.00114  6.68803E-07 1.00000 -6.08548E-03 0.00258 ];
INF_SP5                   (idx, [1:   8]) = [  2.35741E-04 0.01538  3.36731E-05 0.02579 -6.41494E-05 0.02253  4.90643E-03 0.00615 ];
INF_SP6                   (idx, [1:   8]) = [  5.32084E-03 0.00084 -1.42278E-04 0.00533 -8.28513E-05 0.00656 -1.31485E-02 0.00068 ];
INF_SP7                   (idx, [1:   8]) = [  9.35328E-04 0.00587 -1.76716E-04 0.00595 -7.49114E-05 0.01033 -3.63949E-04 0.02131 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  2.18370E+06 0.00134  8.87327E+06 0.00077  1.84846E+07 0.00082  2.02063E+07 0.00089  1.87911E+07 0.00076  2.05842E+07 0.00066  1.40213E+07 0.00084  1.24805E+07 0.00083  9.51571E+06 0.00109  7.77282E+06 0.00073  6.69300E+06 0.00069  6.04892E+06 0.00087  5.58628E+06 0.00094  5.31161E+06 0.00104  5.17333E+06 0.00088  4.46802E+06 0.00074  4.42426E+06 0.00093  4.38264E+06 0.00096  4.29259E+06 0.00093  8.37654E+06 0.00068  8.06126E+06 0.00071  5.80332E+06 0.00057  3.74553E+06 0.00098  4.29278E+06 0.00078  4.03335E+06 0.00081  3.67082E+06 0.00092  6.01230E+06 0.00105  1.37596E+06 0.00066  1.70009E+06 0.00061  1.52753E+06 0.00112  8.88020E+05 0.00173  1.56225E+06 0.00090  1.06271E+06 0.00089  8.99786E+05 0.00175  1.70531E+05 0.00216  1.69335E+05 0.00085  1.73952E+05 0.00086  1.79503E+05 0.00240  1.77782E+05 0.00122  1.75424E+05 0.00074  1.81274E+05 0.00072  1.69926E+05 0.00125  3.21062E+05 0.00176  5.12182E+05 0.00141  6.51156E+05 0.00178  1.70611E+06 0.00091  1.77193E+06 0.00083  1.85894E+06 0.00090  1.18698E+06 0.00082  8.35748E+05 0.00061  6.25140E+05 0.00130  7.10440E+05 0.00091  1.26851E+06 0.00137  1.59723E+06 0.00093  2.85924E+06 0.00102  4.04567E+06 0.00112  5.57846E+06 0.00080  3.41636E+06 0.00074  2.37096E+06 0.00071  1.66816E+06 0.00090  1.47843E+06 0.00126  1.43923E+06 0.00096  1.19276E+06 0.00083  7.92011E+05 0.00067  7.27994E+05 0.00062  6.39803E+05 0.00089  5.37036E+05 0.00135  4.16285E+05 0.00144  2.74909E+05 0.00153  9.53827E+04 0.00135 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  9.75914E-01 0.00031 ];
B1_KEFF                   (idx, [1:   2]) = [  1.00000E+00 2.8E-08 ];
B1_B2                     (idx, [1:   2]) = [ -4.51539E-04 0.01274 ];
B1_ERR                    (idx, [1:   2]) = [  5.78284E-08 0.25197 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  3.99318E+16 0.00070  6.30219E+15 0.00078 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  5.48748E-01 7.4E-05  1.37850E+00 6.3E-05 ];
B1_CAPT                   (idx, [1:   4]) = [  7.35920E-03 0.00041  5.80925E-02 0.00019 ];
B1_ABS                    (idx, [1:   4]) = [  9.95256E-03 0.00036  1.10169E-01 0.00012 ];
B1_FISS                   (idx, [1:   4]) = [  2.59336E-03 0.00024  5.20764E-02 0.00025 ];
B1_NSF                    (idx, [1:   4]) = [  6.62322E-03 0.00024  1.26868E-01 0.00025 ];
B1_NUBAR                  (idx, [1:   4]) = [  2.55391E+00 2.1E-05  2.43620E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  2.03363E+02 1.4E-06  2.02270E+02 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  5.80971E-08 0.00021  2.34517E-06 4.7E-05 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  5.38796E-01 7.6E-05  1.26832E+00 5.2E-05 ];
B1_SCATT1                 (idx, [1:   4]) = [  2.45931E-01 9.2E-05  3.43173E-01 0.00013 ];
B1_SCATT2                 (idx, [1:   4]) = [  9.71924E-02 0.00013  8.63280E-02 0.00047 ];
B1_SCATT3                 (idx, [1:   4]) = [  7.26264E-03 0.00145  2.61090E-02 0.00143 ];
B1_SCATT4                 (idx, [1:   4]) = [ -1.03104E-02 0.00072 -5.99534E-03 0.00259 ];
B1_SCATT5                 (idx, [1:   4]) = [  2.78531E-04 0.01204  4.79756E-03 0.00622 ];
B1_SCATT6                 (idx, [1:   4]) = [  5.17993E-03 0.00084 -1.31537E-02 0.00072 ];
B1_SCATT7                 (idx, [1:   4]) = [  7.58138E-04 0.00681 -4.68582E-04 0.01678 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  5.38834E-01 7.6E-05  1.26832E+00 5.2E-05 ];
B1_SCATTP1                (idx, [1:   4]) = [  2.45931E-01 9.2E-05  3.43173E-01 0.00013 ];
B1_SCATTP2                (idx, [1:   4]) = [  9.71927E-02 0.00013  8.63280E-02 0.00047 ];
B1_SCATTP3                (idx, [1:   4]) = [  7.26274E-03 0.00145  2.61090E-02 0.00143 ];
B1_SCATTP4                (idx, [1:   4]) = [ -1.03103E-02 0.00072 -5.99534E-03 0.00259 ];
B1_SCATTP5                (idx, [1:   4]) = [  2.78493E-04 0.01202  4.79756E-03 0.00622 ];
B1_SCATTP6                (idx, [1:   4]) = [  5.17997E-03 0.00085 -1.31537E-02 0.00072 ];
B1_SCATTP7                (idx, [1:   4]) = [  7.58097E-04 0.00682 -4.68582E-04 0.01678 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  2.39264E-01 9.6E-05  8.30928E-01 5.5E-05 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  1.39316E+00 9.6E-05  4.01158E-01 5.5E-05 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  9.91437E-03 0.00037  1.10169E-01 0.00012 ];
B1_REMXS                  (idx, [1:   4]) = [  2.75940E-02 0.00012  1.11963E-01 0.00019 ];

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

B1_CHIT                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHIP                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHID                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

B1_S0                     (idx, [1:   8]) = [  5.21154E-01 7.3E-05  1.76418E-02 0.00019  1.77821E-03 0.00146  1.26654E+00 5.2E-05 ];
B1_S1                     (idx, [1:   8]) = [  2.40802E-01 9.0E-05  5.12909E-03 0.00030  8.66452E-04 0.00241  3.42307E-01 0.00013 ];
B1_S2                     (idx, [1:   8]) = [  9.87480E-02 0.00012 -1.55560E-03 0.00078  4.62059E-04 0.00325  8.58659E-02 0.00048 ];
B1_S3                     (idx, [1:   8]) = [  9.08415E-03 0.00114 -1.82151E-03 0.00023  1.65021E-04 0.01071  2.59440E-02 0.00147 ];
B1_S4                     (idx, [1:   8]) = [ -9.72608E-03 0.00071 -5.84346E-04 0.00114  7.62905E-07 1.00000 -5.99610E-03 0.00258 ];
B1_S5                     (idx, [1:   8]) = [  2.44600E-04 0.01487  3.39304E-05 0.02560 -6.62893E-05 0.02251  4.86385E-03 0.00617 ];
B1_S6                     (idx, [1:   8]) = [  5.32131E-03 0.00084 -1.41375E-04 0.00534 -8.56592E-05 0.00662 -1.30681E-02 0.00072 ];
B1_S7                     (idx, [1:   8]) = [  9.33814E-04 0.00585 -1.75677E-04 0.00588 -7.74670E-05 0.01028 -3.91115E-04 0.01973 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  5.21193E-01 7.3E-05  1.76418E-02 0.00019  1.77821E-03 0.00146  1.26654E+00 5.2E-05 ];
B1_SP1                    (idx, [1:   8]) = [  2.40802E-01 9.0E-05  5.12909E-03 0.00030  8.66452E-04 0.00241  3.42307E-01 0.00013 ];
B1_SP2                    (idx, [1:   8]) = [  9.87483E-02 0.00012 -1.55560E-03 0.00078  4.62059E-04 0.00325  8.58659E-02 0.00048 ];
B1_SP3                    (idx, [1:   8]) = [  9.08425E-03 0.00114 -1.82151E-03 0.00023  1.65021E-04 0.01071  2.59440E-02 0.00147 ];
B1_SP4                    (idx, [1:   8]) = [ -9.72596E-03 0.00071 -5.84346E-04 0.00114  7.62905E-07 1.00000 -5.99610E-03 0.00258 ];
B1_SP5                    (idx, [1:   8]) = [  2.44563E-04 0.01483  3.39304E-05 0.02560 -6.62893E-05 0.02251  4.86385E-03 0.00617 ];
B1_SP6                    (idx, [1:   8]) = [  5.32135E-03 0.00084 -1.41375E-04 0.00534 -8.56592E-05 0.00662 -1.30681E-02 0.00072 ];
B1_SP7                    (idx, [1:   8]) = [  9.33774E-04 0.00586 -1.75677E-04 0.00588 -7.74670E-05 0.01028 -3.91115E-04 0.01973 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  9.83776E-02 0.00045  2.76661E-01 0.00064 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  9.87104E-02 0.00044  2.79148E-01 0.00146 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  9.87332E-02 0.00051  2.78989E-01 0.00093 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  9.76964E-02 0.00044  2.71971E-01 0.00075 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  3.38831E+00 0.00045  1.20485E+00 0.00064 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  3.37688E+00 0.00044  1.19412E+00 0.00146 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  3.37610E+00 0.00051  1.19480E+00 0.00093 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  3.41193E+00 0.00044  1.22562E+00 0.00075 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  6.94864E-03 0.00297  1.99646E-04 0.01912  1.00812E-03 0.00712  5.78303E-04 0.00979  1.27747E-03 0.00701  2.24722E-03 0.00583  7.57724E-04 0.00907  6.30280E-04 0.00900  2.49878E-04 0.01530 ];
LAMBDA                    (idx, [1:  18]) = [  4.75854E-01 0.00462  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.2E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 3.2E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];


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
INPUT_FILE_NAME           (idx, [1:  8])  = 'UAM_HZP1' ;
WORKING_DIRECTORY         (idx, [1: 33])  = '/home/abrate/ricerca/esrel2020/XS' ;
HOSTNAME                  (idx, [1:  7])  = 'vpcen13' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz' ;
CPU_MHZ                   (idx, 1)        = 4294967295.0 ;
START_DATE                (idx, [1: 24])  = 'Sat Aug 29 19:41:15 2020' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Sun Aug 30 03:33:18 2020' ;

% Run parameters:

POP                       (idx, 1)        = 1000000 ;
CYCLES                    (idx, 1)        = 100 ;
SKIP                      (idx, 1)        = 1000 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1598722875174 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 1 0 15 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 1 ;
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
OMP_HISTORY_PROFILE       (idx, [1:  30]) = [  1.02009E+00  9.94705E-01  1.00387E+00  1.00056E+00  9.88198E-01  1.00722E+00  1.00401E+00  9.96277E-01  1.00226E+00  1.00432E+00  9.94099E-01  9.95657E-01  9.95880E-01  9.96650E-01  1.00162E+00  1.00152E+00  9.97196E-01  1.00175E+00  9.98859E-01  9.94033E-01  1.00599E+00  1.00773E+00  1.00269E+00  9.96632E-01  9.96583E-01  1.00070E+00  9.98139E-01  9.97152E-01  9.98903E-01  9.96708E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 46])  = '/opt/serpent/xsdata/jeff311/sss_jeff311.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  3.02816E-01 0.00011  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  6.97184E-01 4.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  5.09482E-01 4.4E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  5.62564E-01 3.2E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.81431E+00 8.9E-05  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  2.36050E+01 0.00010  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  1.50578E+01 0.00018  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 100 ;
SIMULATED_HISTORIES       (idx, 1)        = 100003951 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.14426E+04 ;
RUNNING_TIME              (idx, 1)        =  4.72050E+02 ;
INIT_TIME                 (idx, [1:  2])  = [  2.40100E-01  2.40100E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.48333E-03  5.48333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  4.71803E+02  4.71803E+02  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
LEAKAGE_CORR_SOL_TIME     (idx, 1)        =  1.93334E-03 ;
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  4.72036E+02  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 24.24027 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.41670E+01 0.00036 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  8.01323E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 100712.49 ;
ALLOC_MEMSIZE             (idx, 1)        = 8618.97;
MEMSIZE                   (idx, 1)        = 8405.65;
XS_MEMSIZE                (idx, 1)        = 1458.21;
MAT_MEMSIZE               (idx, 1)        = 161.71;
RES_MEMSIZE               (idx, 1)        = 40.61;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 6745.12;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 213.32;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 2 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 377473 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.50000E-04 ;
URES_EMAX                 (idx, 1)        =  1.00000E+00 ;
URES_AVAIL                (idx, 1)        = 22 ;
URES_USED                 (idx, 1)        = 22 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 51 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 51 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 1255 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 1 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
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

NORM_COEF                 (idx, [1:   4]) = [  3.37127E+09 0.00011  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  5.77603E-01 0.00025 ];
U235_FISS                 (idx, [1:   4]) = [  9.90572E+14 0.00019  7.34684E-01 0.00017 ];
U238_FISS                 (idx, [1:   4]) = [  9.21228E+13 0.00056  6.83252E-02 0.00052 ];
PU239_FISS                (idx, [1:   4]) = [  2.18024E+14 0.00063  1.61704E-01 0.00061 ];
PU240_FISS                (idx, [1:   4]) = [  2.57850E+12 0.00379  1.91239E-03 0.00376 ];
PU241_FISS                (idx, [1:   4]) = [  4.33275E+13 0.00115  3.21349E-02 0.00112 ];
U235_CAPT                 (idx, [1:   4]) = [  2.18104E+14 0.00038  1.07557E-01 0.00036 ];
U238_CAPT                 (idx, [1:   4]) = [  8.16001E+14 0.00026  4.02407E-01 0.00016 ];
PU239_CAPT                (idx, [1:   4]) = [  1.19322E+14 0.00062  5.88430E-02 0.00060 ];
PU240_CAPT                (idx, [1:   4]) = [  1.06800E+14 0.00077  5.26678E-02 0.00076 ];
PU241_CAPT                (idx, [1:   4]) = [  1.46475E+13 0.00157  7.22336E-03 0.00156 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 100003951 1.00000E+08 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.42950E+05 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 60063923 6.01492E+07 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 39940028 3.99937E+07 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 1.58504E-04 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  4.40000E+04 0.0E+00 ];
TOT_POWDENS               (idx, [1:   2]) = [  6.08444E-03 6.9E-09 ];
TOT_GENRATE               (idx, [1:   2]) = [  3.43997E+15 1.7E-05 ];
TOT_FISSRATE              (idx, [1:   2]) = [  1.34797E+15 3.4E-06 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  2.02801E+15 0.00012 ];
TOT_ABSRATE               (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_SRCRATE               (idx, [1:   2]) = [  3.37127E+15 0.00011 ];
TOT_FLUX                  (idx, [1:   2]) = [  1.54978E+17 0.00012 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  1.02483E+17 0.00011 ];
INI_FMASS                 (idx, 1)        =  7.23156E+00 ;
TOT_FMASS                 (idx, 1)        =  7.23156E+00 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.59347E+00 0.00010 ];
SIX_FF_F                  (idx, [1:   2]) = [  7.86859E-01 6.5E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.09029E-01 9.5E-05 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.33656E+00 9.5E-05 ];
SIX_FF_LF                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_LT                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.55197E+00 2.0E-05 ];
FISSE                     (idx, [1:   2]) = [  2.03733E+02 3.4E-06 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.02065E+00 0.00013  1.01426E+00 0.00013  6.36553E-03 0.00198 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
COL_KEFF                  (idx, [1:   2]) = [  1.02038E+00 0.00011 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.69604E+01 4.8E-05 ];
IMP_ALF                   (idx, [1:   2]) = [  1.69598E+01 2.6E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  8.61468E-07 0.00081 ];
IMP_EALF                  (idx, [1:   2]) = [  8.61929E-07 0.00044 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.43848E-01 0.00060 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.43913E-01 0.00024 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  6.41574E-03 0.00138  1.77755E-04 0.00760  9.59151E-04 0.00319  5.22748E-04 0.00428  1.16888E-03 0.00304  2.04914E-03 0.00239  7.14018E-04 0.00388  5.89915E-04 0.00359  2.34134E-04 0.00687 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.79898E-01 0.00196  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.4E-09  2.92467E-01 0.0E+00  6.66488E-01 3.7E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  6.39411E-03 0.00193  1.79105E-04 0.01071  9.51549E-04 0.00465  5.21851E-04 0.00621  1.16414E-03 0.00445  2.04733E-03 0.00383  7.08080E-04 0.00538  5.89788E-04 0.00580  2.32266E-04 0.00948 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.79629E-01 0.00287  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.2E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 2.6E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  2.08580E-05 0.00030  2.08373E-05 0.00031  2.41314E-05 0.00231 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  2.12887E-05 0.00026  2.12676E-05 0.00027  2.46299E-05 0.00233 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  6.22890E-03 0.00210  1.71842E-04 0.01246  9.28634E-04 0.00501  5.07929E-04 0.00666  1.13399E-03 0.00417  1.99048E-03 0.00350  6.93602E-04 0.00640  5.76057E-04 0.00647  2.26363E-04 0.01118 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.80252E-01 0.00314  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.0E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  2.07746E-05 0.00068  2.07537E-05 0.00069  2.41287E-05 0.00720 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  2.12036E-05 0.00066  2.11823E-05 0.00066  2.46267E-05 0.00719 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  6.18290E-03 0.00684  1.75511E-04 0.03639  9.52548E-04 0.01641  4.82324E-04 0.02302  1.09572E-03 0.01605  1.97731E-03 0.01143  6.86947E-04 0.02032  5.90552E-04 0.02301  2.21991E-04 0.03841 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.82637E-01 0.01112  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 3.2E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  6.16570E-03 0.00656  1.74535E-04 0.03564  9.47350E-04 0.01608  4.84709E-04 0.02241  1.08905E-03 0.01531  1.97312E-03 0.01103  6.84544E-04 0.01978  5.89190E-04 0.02159  2.23206E-04 0.03829 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.83650E-01 0.01097  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.5E-09  1.33042E-01 3.2E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -2.97940E+02 0.00692 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  2.08903E-05 0.00022 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  2.13217E-05 0.00017 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  6.27285E-03 0.00156 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -3.00278E+02 0.00161 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  3.79968E-07 0.00016 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  2.82212E-06 0.00011  2.82200E-06 0.00011  2.83937E-06 0.00111 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.51693E-05 0.00015  2.51641E-05 0.00015  2.59132E-05 0.00158 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.09615E-01 9.5E-05  6.09284E-01 9.8E-05  6.60988E-01 0.00196 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.21135E+01 0.00292 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.03573E+01 6.5E-05  3.13774E+01 9.9E-05 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  2])  = 'MO' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  1.55175E+06 0.00142  5.95390E+06 0.00247  1.20290E+07 0.00223  1.31875E+07 0.00197  1.24250E+07 0.00194  1.36302E+07 0.00231  9.38060E+06 0.00216  8.34025E+06 0.00177  6.38826E+06 0.00208  5.17510E+06 0.00210  4.44559E+06 0.00176  3.99410E+06 0.00210  3.69021E+06 0.00201  3.49238E+06 0.00195  3.37799E+06 0.00223  2.91974E+06 0.00233  2.88210E+06 0.00177  2.86076E+06 0.00229  2.78436E+06 0.00220  5.39102E+06 0.00206  5.10817E+06 0.00186  3.59728E+06 0.00215  2.23897E+06 0.00184  2.60175E+06 0.00205  2.41920E+06 0.00202  2.00601E+06 0.00207  3.41124E+06 0.00190  7.87670E+05 0.00222  8.72512E+05 0.00150  8.20355E+05 0.00243  4.91072E+05 0.00240  8.37594E+05 0.00218  5.23266E+05 0.00225  3.47582E+05 0.00111  4.78019E+04 0.00131  4.24955E+04 0.00298  4.07019E+04 0.00338  4.11000E+04 0.00236  4.01751E+04 0.00264  4.03302E+04 0.00225  4.45782E+04 0.00319  4.54365E+04 0.00322  9.56337E+04 0.00453  1.72667E+05 0.00152  2.41134E+05 0.00332  6.72753E+05 0.00214  6.67461E+05 0.00223  6.03909E+05 0.00215  2.89735E+05 0.00230  1.65586E+05 0.00102  1.12314E+05 0.00319  1.21065E+05 0.00338  2.07749E+05 0.00225  2.61887E+05 0.00212  4.77579E+05 0.00214  6.84364E+05 0.00210  9.31426E+05 0.00183  5.65939E+05 0.00277  3.88518E+05 0.00228  2.71077E+05 0.00210  2.38892E+05 0.00259  2.30439E+05 0.00193  1.90661E+05 0.00267  1.26580E+05 0.00276  1.16757E+05 0.00190  1.01722E+05 0.00161  8.43595E+04 0.00311  6.64221E+04 0.00271  4.38549E+04 0.00144  1.54864E+04 0.00323 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  1.14174E+00 0.00015 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  2.55353E+16 0.00209  1.17384E+15 0.00211 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  5.49852E-01 4.3E-05  1.59695E+00 0.00015 ];
INF_CAPT                  (idx, [1:   4]) = [  1.12733E-02 0.00016  1.31809E-01 0.00031 ];
INF_ABS                   (idx, [1:   4]) = [  1.54222E-02 9.9E-05  2.89639E-01 0.00035 ];
INF_FISS                  (idx, [1:   4]) = [  4.14895E-03 0.00013  1.57830E-01 0.00040 ];
INF_NSF                   (idx, [1:   4]) = [  1.19917E-02 0.00014  4.51736E-01 0.00040 ];
INF_NUBAR                 (idx, [1:   4]) = [  2.89031E+00 8.1E-06  2.86217E+00 9.5E-07 ];
INF_KAPPA                 (idx, [1:   4]) = [  2.08019E+02 8.1E-07  2.08157E+02 1.9E-07 ];
INF_INVV                  (idx, [1:   4]) = [  4.53849E-08 0.00032  2.18142E-06 0.00011 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  5.34432E-01 5.3E-05  1.30730E+00 0.00013 ];
INF_SCATT1                (idx, [1:   4]) = [  2.42869E-01 7.5E-05  3.80798E-01 0.00025 ];
INF_SCATT2                (idx, [1:   4]) = [  9.62056E-02 0.00020  1.00877E-01 0.00061 ];
INF_SCATT3                (idx, [1:   4]) = [  6.97805E-03 0.00191  3.05993E-02 0.00183 ];
INF_SCATT4                (idx, [1:   4]) = [ -1.01637E-02 0.00082 -4.95931E-03 0.01620 ];
INF_SCATT5                (idx, [1:   4]) = [  5.17028E-04 0.01233  4.66304E-03 0.01511 ];
INF_SCATT6                (idx, [1:   4]) = [  5.36196E-03 0.00098 -1.32516E-02 0.00482 ];
INF_SCATT7                (idx, [1:   4]) = [  7.91634E-04 0.00870 -1.05661E-03 0.02020 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  5.34476E-01 5.3E-05  1.30730E+00 0.00013 ];
INF_SCATTP1               (idx, [1:   4]) = [  2.42869E-01 7.5E-05  3.80798E-01 0.00025 ];
INF_SCATTP2               (idx, [1:   4]) = [  9.62058E-02 0.00020  1.00877E-01 0.00061 ];
INF_SCATTP3               (idx, [1:   4]) = [  6.97802E-03 0.00190  3.05993E-02 0.00183 ];
INF_SCATTP4               (idx, [1:   4]) = [ -1.01637E-02 0.00082 -4.95931E-03 0.01620 ];
INF_SCATTP5               (idx, [1:   4]) = [  5.17074E-04 0.01250  4.66304E-03 0.01511 ];
INF_SCATTP6               (idx, [1:   4]) = [  5.36193E-03 0.00098 -1.32516E-02 0.00482 ];
INF_SCATTP7               (idx, [1:   4]) = [  7.91665E-04 0.00868 -1.05661E-03 0.02020 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  2.22914E-01 0.00014  1.09273E+00 0.00016 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.49535E+00 0.00014  3.05047E-01 0.00016 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  1.53786E-02 0.00011  2.89639E-01 0.00035 ];
INF_REMXS                 (idx, [1:   4]) = [  2.82193E-02 0.00011  2.93369E-01 0.00031 ];

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

INF_CHIT                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHIP                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_CHID                  (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

INF_S0                    (idx, [1:   8]) = [  5.21633E-01 4.8E-05  1.27996E-02 0.00031  3.71713E-03 0.00257  1.30358E+00 0.00013 ];
INF_S1                    (idx, [1:   8]) = [  2.39307E-01 7.4E-05  3.56209E-03 0.00062  1.85161E-03 0.00444  3.78946E-01 0.00024 ];
INF_S2                    (idx, [1:   8]) = [  9.75744E-02 0.00019 -1.36876E-03 0.00095  1.00180E-03 0.00146  9.98750E-02 0.00062 ];
INF_S3                    (idx, [1:   8]) = [  8.34863E-03 0.00151 -1.37057E-03 0.00095  3.65598E-04 0.00505  3.02337E-02 0.00188 ];
INF_S4                    (idx, [1:   8]) = [ -9.84019E-03 0.00083 -3.23530E-04 0.00377  1.14583E-05 0.18175 -4.97077E-03 0.01639 ];
INF_S5                    (idx, [1:   8]) = [  4.11957E-04 0.01542  1.05072E-04 0.00318 -1.31084E-04 0.02340  4.79413E-03 0.01480 ];
INF_S6                    (idx, [1:   8]) = [  5.45142E-03 0.00104 -8.94598E-05 0.01323 -1.79057E-04 0.01726 -1.30725E-02 0.00474 ];
INF_S7                    (idx, [1:   8]) = [  9.33472E-04 0.00777 -1.41838E-04 0.00864 -1.63187E-04 0.01280 -8.93425E-04 0.02246 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  5.21676E-01 4.7E-05  1.27996E-02 0.00031  3.71713E-03 0.00257  1.30358E+00 0.00013 ];
INF_SP1                   (idx, [1:   8]) = [  2.39307E-01 7.5E-05  3.56209E-03 0.00062  1.85161E-03 0.00444  3.78946E-01 0.00024 ];
INF_SP2                   (idx, [1:   8]) = [  9.75746E-02 0.00019 -1.36876E-03 0.00095  1.00180E-03 0.00146  9.98750E-02 0.00062 ];
INF_SP3                   (idx, [1:   8]) = [  8.34859E-03 0.00150 -1.37057E-03 0.00095  3.65598E-04 0.00505  3.02337E-02 0.00188 ];
INF_SP4                   (idx, [1:   8]) = [ -9.84018E-03 0.00084 -3.23530E-04 0.00377  1.14583E-05 0.18175 -4.97077E-03 0.01639 ];
INF_SP5                   (idx, [1:   8]) = [  4.12002E-04 0.01562  1.05072E-04 0.00318 -1.31084E-04 0.02340  4.79413E-03 0.01480 ];
INF_SP6                   (idx, [1:   8]) = [  5.45139E-03 0.00104 -8.94598E-05 0.01323 -1.79057E-04 0.01726 -1.30725E-02 0.00474 ];
INF_SP7                   (idx, [1:   8]) = [  9.33503E-04 0.00776 -1.41838E-04 0.00864 -1.63187E-04 0.01280 -8.93425E-04 0.02246 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  1.67902E+06 0.00173  6.37036E+06 0.00234  1.27255E+07 0.00223  1.36573E+07 0.00198  1.26651E+07 0.00198  1.36542E+07 0.00228  9.27931E+06 0.00211  8.25227E+06 0.00176  6.24779E+06 0.00206  5.08536E+06 0.00210  4.37211E+06 0.00174  3.93025E+06 0.00206  3.63048E+06 0.00200  3.43741E+06 0.00203  3.33632E+06 0.00223  2.87747E+06 0.00231  2.84199E+06 0.00182  2.80794E+06 0.00231  2.73852E+06 0.00212  5.30610E+06 0.00206  5.02243E+06 0.00186  3.53280E+06 0.00220  2.19665E+06 0.00185  2.56697E+06 0.00205  2.38177E+06 0.00213  1.97103E+06 0.00210  3.35265E+06 0.00192  7.74890E+05 0.00223  8.55957E+05 0.00141  8.05925E+05 0.00254  4.82945E+05 0.00234  8.23428E+05 0.00219  5.13563E+05 0.00234  3.39455E+05 0.00127  4.64498E+04 0.00175  4.11961E+04 0.00300  3.94062E+04 0.00354  3.97794E+04 0.00257  3.88886E+04 0.00260  3.90122E+04 0.00235  4.31571E+04 0.00317  4.39975E+04 0.00329  9.27983E+04 0.00448  1.67831E+05 0.00185  2.34796E+05 0.00348  6.55216E+05 0.00227  6.48893E+05 0.00237  5.83742E+05 0.00230  2.77620E+05 0.00231  1.57425E+05 0.00130  1.06337E+05 0.00330  1.14100E+05 0.00357  1.94476E+05 0.00244  2.43597E+05 0.00219  4.40646E+05 0.00235  6.26378E+05 0.00227  8.46342E+05 0.00201  5.13039E+05 0.00298  3.51912E+05 0.00241  2.45408E+05 0.00214  2.16401E+05 0.00268  2.08757E+05 0.00206  1.72924E+05 0.00275  1.15003E+05 0.00274  1.06244E+05 0.00211  9.25411E+04 0.00159  7.67934E+04 0.00316  6.06015E+04 0.00280  4.00480E+04 0.00174  1.41585E+04 0.00296 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  1.13504E+00 0.00017 ];
B1_KEFF                   (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
B1_B2                     (idx, [1:   2]) = [  2.63091E-03 0.00144 ];
B1_ERR                    (idx, [1:   2]) = [  4.23416E-08 0.04332 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  2.56213E+16 0.00208  1.08781E+15 0.00227 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  5.43360E-01 5.9E-05  1.59015E+00 0.00016 ];
B1_CAPT                   (idx, [1:   4]) = [  1.10331E-02 8.6E-05  1.31681E-01 0.00031 ];
B1_ABS                    (idx, [1:   4]) = [  1.51724E-02 4.3E-05  2.89072E-01 0.00035 ];
B1_FISS                   (idx, [1:   4]) = [  4.13929E-03 0.00016  1.57391E-01 0.00039 ];
B1_NSF                    (idx, [1:   4]) = [  1.19711E-02 0.00016  4.50459E-01 0.00039 ];
B1_NUBAR                  (idx, [1:   4]) = [  2.89206E+00 7.8E-06  2.86204E+00 9.8E-07 ];
B1_KAPPA                  (idx, [1:   4]) = [  2.07999E+02 1.1E-06  2.08154E+02 1.9E-07 ];
B1_INVV                   (idx, [1:   4]) = [  4.43815E-08 0.00032  2.16115E-06 0.00011 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  5.28190E-01 6.7E-05  1.30107E+00 0.00013 ];
B1_SCATT1                 (idx, [1:   4]) = [  2.39929E-01 8.1E-05  3.80957E-01 0.00024 ];
B1_SCATT2                 (idx, [1:   4]) = [  9.52794E-02 0.00020  1.01459E-01 0.00058 ];
B1_SCATT3                 (idx, [1:   4]) = [  7.14440E-03 0.00181  3.07847E-02 0.00181 ];
B1_SCATT4                 (idx, [1:   4]) = [ -9.81653E-03 0.00081 -4.77601E-03 0.01661 ];
B1_SCATT5                 (idx, [1:   4]) = [  6.27830E-04 0.01033  4.57601E-03 0.01515 ];
B1_SCATT6                 (idx, [1:   4]) = [  5.34866E-03 0.00096 -1.31116E-02 0.00487 ];
B1_SCATT7                 (idx, [1:   4]) = [  8.03857E-04 0.00855 -1.10916E-03 0.01883 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  5.28237E-01 6.7E-05  1.30107E+00 0.00013 ];
B1_SCATTP1                (idx, [1:   4]) = [  2.39930E-01 8.2E-05  3.80957E-01 0.00024 ];
B1_SCATTP2                (idx, [1:   4]) = [  9.52797E-02 0.00020  1.01459E-01 0.00058 ];
B1_SCATTP3                (idx, [1:   4]) = [  7.14436E-03 0.00180  3.07847E-02 0.00181 ];
B1_SCATTP4                (idx, [1:   4]) = [ -9.81653E-03 0.00081 -4.77601E-03 0.01661 ];
B1_SCATTP5                (idx, [1:   4]) = [  6.27879E-04 0.01048  4.57601E-03 0.01515 ];
B1_SCATTP6                (idx, [1:   4]) = [  5.34863E-03 0.00096 -1.31116E-02 0.00487 ];
B1_SCATTP7                (idx, [1:   4]) = [  8.03891E-04 0.00852 -1.10916E-03 0.01883 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  2.39689E-01 0.00014  9.11852E-01 0.00016 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  1.39069E+00 0.00014  3.65556E-01 0.00016 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  1.51254E-02 4.8E-05  2.89072E-01 0.00035 ];
B1_REMXS                  (idx, [1:   4]) = [  2.76500E-02 0.00011  2.92981E-01 0.00030 ];

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

B1_CHIT                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHIP                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_CHID                   (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Scattering matrixes:

B1_S0                     (idx, [1:   8]) = [  5.15710E-01 6.2E-05  1.24799E-02 0.00028  3.89731E-03 0.00249  1.29717E+00 0.00014 ];
B1_S1                     (idx, [1:   8]) = [  2.36461E-01 8.0E-05  3.46860E-03 0.00054  1.94135E-03 0.00435  3.79016E-01 0.00023 ];
B1_S2                     (idx, [1:   8]) = [  9.66204E-02 0.00019 -1.34100E-03 0.00095  1.05070E-03 0.00147  1.00409E-01 0.00060 ];
B1_S3                     (idx, [1:   8]) = [  8.48221E-03 0.00143 -1.33781E-03 0.00094  3.83725E-04 0.00492  3.04010E-02 0.00186 ];
B1_S4                     (idx, [1:   8]) = [ -9.50360E-03 0.00080 -3.12929E-04 0.00384  1.22810E-05 0.17687 -4.78829E-03 0.01682 ];
B1_S5                     (idx, [1:   8]) = [  5.23208E-04 0.01241  1.04622E-04 0.00310 -1.37319E-04 0.02343  4.71333E-03 0.01483 ];
B1_S6                     (idx, [1:   8]) = [  5.43541E-03 0.00102 -8.67485E-05 0.01323 -1.87756E-04 0.01717 -1.29239E-02 0.00479 ];
B1_S7                     (idx, [1:   8]) = [  9.42462E-04 0.00766 -1.38604E-04 0.00857 -1.71175E-04 0.01275 -9.37987E-04 0.02082 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  5.15757E-01 6.2E-05  1.24799E-02 0.00028  3.89731E-03 0.00249  1.29717E+00 0.00014 ];
B1_SP1                    (idx, [1:   8]) = [  2.36461E-01 8.0E-05  3.46860E-03 0.00054  1.94135E-03 0.00435  3.79016E-01 0.00023 ];
B1_SP2                    (idx, [1:   8]) = [  9.66207E-02 0.00019 -1.34100E-03 0.00095  1.05070E-03 0.00147  1.00409E-01 0.00060 ];
B1_SP3                    (idx, [1:   8]) = [  8.48217E-03 0.00142 -1.33781E-03 0.00094  3.83725E-04 0.00492  3.04010E-02 0.00186 ];
B1_SP4                    (idx, [1:   8]) = [ -9.50360E-03 0.00080 -3.12929E-04 0.00384  1.22810E-05 0.17687 -4.78829E-03 0.01682 ];
B1_SP5                    (idx, [1:   8]) = [  5.23257E-04 0.01258  1.04622E-04 0.00310 -1.37319E-04 0.02343  4.71333E-03 0.01483 ];
B1_SP6                    (idx, [1:   8]) = [  5.43538E-03 0.00102 -8.67485E-05 0.01323 -1.87756E-04 0.01717 -1.29239E-02 0.00479 ];
B1_SP7                    (idx, [1:   8]) = [  9.42495E-04 0.00765 -1.38604E-04 0.00857 -1.71175E-04 0.01275 -9.37987E-04 0.02082 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  5.14858E-02 0.00212  4.70605E-02 0.00302 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  5.25370E-02 0.00213  4.74987E-02 0.00305 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  5.25131E-02 0.00223  4.74567E-02 0.00316 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  4.95260E-02 0.00203  4.62483E-02 0.00324 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  6.47439E+00 0.00212  7.08333E+00 0.00302 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  6.34485E+00 0.00213  7.01800E+00 0.00304 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  6.34775E+00 0.00222  7.02423E+00 0.00316 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  6.73058E+00 0.00203  7.20777E+00 0.00324 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  4.29705E-03 0.00430  1.01759E-04 0.02825  7.26963E-04 0.01186  3.03390E-04 0.01415  7.23136E-04 0.01022  1.32813E-03 0.00824  5.11755E-04 0.00949  4.28491E-04 0.01372  1.73429E-04 0.02254 ];
LAMBDA                    (idx, [1:  18]) = [  5.06528E-01 0.00732  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 3.5E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];


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
INPUT_FILE_NAME           (idx, [1:  8])  = 'UAM_HZP1' ;
WORKING_DIRECTORY         (idx, [1: 33])  = '/home/abrate/ricerca/esrel2020/XS' ;
HOSTNAME                  (idx, [1:  7])  = 'vpcen13' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz' ;
CPU_MHZ                   (idx, 1)        = 4294967295.0 ;
START_DATE                (idx, [1: 24])  = 'Sat Aug 29 19:41:15 2020' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Sun Aug 30 03:33:18 2020' ;

% Run parameters:

POP                       (idx, 1)        = 1000000 ;
CYCLES                    (idx, 1)        = 100 ;
SKIP                      (idx, 1)        = 1000 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1598722875174 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 1 0 15 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 1 ;
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
OMP_HISTORY_PROFILE       (idx, [1:  30]) = [  1.02009E+00  9.94705E-01  1.00387E+00  1.00056E+00  9.88198E-01  1.00722E+00  1.00401E+00  9.96277E-01  1.00226E+00  1.00432E+00  9.94099E-01  9.95657E-01  9.95880E-01  9.96650E-01  1.00162E+00  1.00152E+00  9.97196E-01  1.00175E+00  9.98859E-01  9.94033E-01  1.00599E+00  1.00773E+00  1.00269E+00  9.96632E-01  9.96583E-01  1.00070E+00  9.98139E-01  9.97152E-01  9.98903E-01  9.96708E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 46])  = '/opt/serpent/xsdata/jeff311/sss_jeff311.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  3.02816E-01 0.00011  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  6.97184E-01 4.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  5.09482E-01 4.4E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  5.62564E-01 3.2E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.81431E+00 8.9E-05  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  2.36050E+01 0.00010  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  1.50578E+01 0.00018  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 100 ;
SIMULATED_HISTORIES       (idx, 1)        = 100003951 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.14426E+04 ;
RUNNING_TIME              (idx, 1)        =  4.72050E+02 ;
INIT_TIME                 (idx, [1:  2])  = [  2.40100E-01  2.40100E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.48333E-03  5.48333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  4.71803E+02  4.71803E+02  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
LEAKAGE_CORR_SOL_TIME     (idx, 1)        =  1.93334E-03 ;
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  4.72036E+02  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 24.24027 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.41670E+01 0.00036 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  8.01323E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 100712.49 ;
ALLOC_MEMSIZE             (idx, 1)        = 8618.97;
MEMSIZE                   (idx, 1)        = 8405.65;
XS_MEMSIZE                (idx, 1)        = 1458.21;
MAT_MEMSIZE               (idx, 1)        = 161.71;
RES_MEMSIZE               (idx, 1)        = 40.61;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 6745.12;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 213.32;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 2 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 377473 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.50000E-04 ;
URES_EMAX                 (idx, 1)        =  1.00000E+00 ;
URES_AVAIL                (idx, 1)        = 22 ;
URES_USED                 (idx, 1)        = 22 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 51 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 51 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 1255 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 1 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
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

NORM_COEF                 (idx, [1:   4]) = [  3.37127E+09 0.00011  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  5.77603E-01 0.00025 ];
U235_FISS                 (idx, [1:   4]) = [  9.90572E+14 0.00019  7.34684E-01 0.00017 ];
U238_FISS                 (idx, [1:   4]) = [  9.21228E+13 0.00056  6.83252E-02 0.00052 ];
PU239_FISS                (idx, [1:   4]) = [  2.18024E+14 0.00063  1.61704E-01 0.00061 ];
PU240_FISS                (idx, [1:   4]) = [  2.57850E+12 0.00379  1.91239E-03 0.00376 ];
PU241_FISS                (idx, [1:   4]) = [  4.33275E+13 0.00115  3.21349E-02 0.00112 ];
U235_CAPT                 (idx, [1:   4]) = [  2.18104E+14 0.00038  1.07557E-01 0.00036 ];
U238_CAPT                 (idx, [1:   4]) = [  8.16001E+14 0.00026  4.02407E-01 0.00016 ];
PU239_CAPT                (idx, [1:   4]) = [  1.19322E+14 0.00062  5.88430E-02 0.00060 ];
PU240_CAPT                (idx, [1:   4]) = [  1.06800E+14 0.00077  5.26678E-02 0.00076 ];
PU241_CAPT                (idx, [1:   4]) = [  1.46475E+13 0.00157  7.22336E-03 0.00156 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 100003951 1.00000E+08 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.42950E+05 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 60063923 6.01492E+07 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 39940028 3.99937E+07 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 1.58504E-04 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  4.40000E+04 0.0E+00 ];
TOT_POWDENS               (idx, [1:   2]) = [  6.08444E-03 6.9E-09 ];
TOT_GENRATE               (idx, [1:   2]) = [  3.43997E+15 1.7E-05 ];
TOT_FISSRATE              (idx, [1:   2]) = [  1.34797E+15 3.4E-06 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  2.02801E+15 0.00012 ];
TOT_ABSRATE               (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_SRCRATE               (idx, [1:   2]) = [  3.37127E+15 0.00011 ];
TOT_FLUX                  (idx, [1:   2]) = [  1.54978E+17 0.00012 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  1.02483E+17 0.00011 ];
INI_FMASS                 (idx, 1)        =  7.23156E+00 ;
TOT_FMASS                 (idx, 1)        =  7.23156E+00 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.59347E+00 0.00010 ];
SIX_FF_F                  (idx, [1:   2]) = [  7.86859E-01 6.5E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.09029E-01 9.5E-05 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.33656E+00 9.5E-05 ];
SIX_FF_LF                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_LT                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.55197E+00 2.0E-05 ];
FISSE                     (idx, [1:   2]) = [  2.03733E+02 3.4E-06 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.02065E+00 0.00013  1.01426E+00 0.00013  6.36553E-03 0.00198 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
COL_KEFF                  (idx, [1:   2]) = [  1.02038E+00 0.00011 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.69604E+01 4.8E-05 ];
IMP_ALF                   (idx, [1:   2]) = [  1.69598E+01 2.6E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  8.61468E-07 0.00081 ];
IMP_EALF                  (idx, [1:   2]) = [  8.61929E-07 0.00044 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.43848E-01 0.00060 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.43913E-01 0.00024 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  6.41574E-03 0.00138  1.77755E-04 0.00760  9.59151E-04 0.00319  5.22748E-04 0.00428  1.16888E-03 0.00304  2.04914E-03 0.00239  7.14018E-04 0.00388  5.89915E-04 0.00359  2.34134E-04 0.00687 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.79898E-01 0.00196  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.4E-09  2.92467E-01 0.0E+00  6.66488E-01 3.7E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  6.39411E-03 0.00193  1.79105E-04 0.01071  9.51549E-04 0.00465  5.21851E-04 0.00621  1.16414E-03 0.00445  2.04733E-03 0.00383  7.08080E-04 0.00538  5.89788E-04 0.00580  2.32266E-04 0.00948 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.79629E-01 0.00287  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.2E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 2.6E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  2.08580E-05 0.00030  2.08373E-05 0.00031  2.41314E-05 0.00231 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  2.12887E-05 0.00026  2.12676E-05 0.00027  2.46299E-05 0.00233 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  6.22890E-03 0.00210  1.71842E-04 0.01246  9.28634E-04 0.00501  5.07929E-04 0.00666  1.13399E-03 0.00417  1.99048E-03 0.00350  6.93602E-04 0.00640  5.76057E-04 0.00647  2.26363E-04 0.01118 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.80252E-01 0.00314  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.0E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  2.07746E-05 0.00068  2.07537E-05 0.00069  2.41287E-05 0.00720 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  2.12036E-05 0.00066  2.11823E-05 0.00066  2.46267E-05 0.00719 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  6.18290E-03 0.00684  1.75511E-04 0.03639  9.52548E-04 0.01641  4.82324E-04 0.02302  1.09572E-03 0.01605  1.97731E-03 0.01143  6.86947E-04 0.02032  5.90552E-04 0.02301  2.21991E-04 0.03841 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.82637E-01 0.01112  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 3.2E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  6.16570E-03 0.00656  1.74535E-04 0.03564  9.47350E-04 0.01608  4.84709E-04 0.02241  1.08905E-03 0.01531  1.97312E-03 0.01103  6.84544E-04 0.01978  5.89190E-04 0.02159  2.23206E-04 0.03829 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.83650E-01 0.01097  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.5E-09  1.33042E-01 3.2E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -2.97940E+02 0.00692 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  2.08903E-05 0.00022 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  2.13217E-05 0.00017 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  6.27285E-03 0.00156 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -3.00278E+02 0.00161 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  3.79968E-07 0.00016 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  2.82212E-06 0.00011  2.82200E-06 0.00011  2.83937E-06 0.00111 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.51693E-05 0.00015  2.51641E-05 0.00015  2.59132E-05 0.00158 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.09615E-01 9.5E-05  6.09284E-01 9.8E-05  6.60988E-01 0.00196 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.21135E+01 0.00292 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.03573E+01 6.5E-05  3.13774E+01 9.9E-05 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  2])  = 'SS' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  1.68160E+05 0.00336  6.51525E+05 0.00234  1.68135E+06 0.00189  2.93863E+06 0.00118  4.89288E+06 0.00191  7.94158E+06 0.00142  7.54093E+06 0.00154  6.44489E+06 0.00224  6.09042E+06 0.00178  3.89752E+06 0.00186  3.16871E+06 0.00179  2.12880E+06 0.00282  2.53038E+06 0.00262  1.64822E+06 0.00232  1.04216E+06 0.00253  1.13883E+06 0.00244  1.20766E+06 0.00286  1.44860E+06 0.00276  1.36339E+06 0.00295  2.39231E+06 0.00318  1.92718E+06 0.00297  1.63187E+06 0.00281  1.02824E+06 0.00302  5.87469E+05 0.00153  6.41339E+05 0.00157  5.64596E+05 0.00224  9.66576E+05 0.00225  1.85956E+05 0.00341  2.18542E+05 0.00085  1.82086E+05 0.00235  1.01175E+05 0.00406  1.64351E+05 0.00226  1.03406E+05 0.00257  8.12542E+04 0.00246  1.46935E+04 0.00437  1.40777E+04 0.00504  1.41126E+04 0.00476  1.41577E+04 0.00344  1.35238E+04 0.00603  1.30990E+04 0.00598  1.31818E+04 0.00723  1.21746E+04 0.00448  2.25563E+04 0.00397  3.51141E+04 0.00536  4.30704E+04 0.00215  1.04713E+05 0.00382  9.55396E+04 0.00514  8.53005E+04 0.00225  4.49581E+04 0.00331  2.80279E+04 0.00217  1.95048E+04 0.00884  2.05331E+04 0.00337  3.36510E+04 0.00749  3.83035E+04 0.00335  6.23286E+04 0.00157  7.96225E+04 0.00247  9.79570E+04 0.00229  5.37617E+04 0.00232  3.48700E+04 0.00243  2.31893E+04 0.00264  1.93773E+04 0.00291  1.77458E+04 0.00144  1.37222E+04 0.00542  8.56577E+03 0.00624  7.43674E+03 0.00713  6.09268E+03 0.00599  4.69021E+03 0.00741  3.24596E+03 0.00375  1.75803E+03 0.01229  4.52220E+02 0.02927 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  1.16335E+16 0.00189  1.34958E+14 0.00145 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  4.81822E-01 0.00034  9.81777E-01 0.00011 ];
INF_CAPT                  (idx, [1:   4]) = [  3.48818E-03 0.00051  1.13237E-01 0.00093 ];
INF_ABS                   (idx, [1:   4]) = [  3.48818E-03 0.00051  1.13237E-01 0.00093 ];
INF_FISS                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_NSF                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_NUBAR                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_KAPPA                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_INVV                  (idx, [1:   4]) = [  2.73376E-08 0.00038  1.87966E-06 0.00093 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  4.78337E-01 0.00034  8.68607E-01 0.00026 ];
INF_SCATT1                (idx, [1:   4]) = [  3.05110E-02 0.00051  1.05013E-02 0.01956 ];
INF_SCATT2                (idx, [1:   4]) = [  2.17272E-02 0.00145 -1.28131E-04 1.00000 ];
INF_SCATT3                (idx, [1:   4]) = [  4.27892E-03 0.00316 -2.00856E-04 0.76331 ];
INF_SCATT4                (idx, [1:   4]) = [  2.45805E-03 0.00466  7.00244E-05 1.00000 ];
INF_SCATT5                (idx, [1:   4]) = [  3.60677E-04 0.03000  2.80058E-05 1.00000 ];
INF_SCATT6                (idx, [1:   4]) = [  8.21714E-05 0.11582  1.92787E-05 1.00000 ];
INF_SCATT7                (idx, [1:   4]) = [  2.03270E-05 0.29753 -1.60479E-05 1.00000 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  4.78338E-01 0.00034  8.68607E-01 0.00026 ];
INF_SCATTP1               (idx, [1:   4]) = [  3.05111E-02 0.00051  1.05013E-02 0.01956 ];
INF_SCATTP2               (idx, [1:   4]) = [  2.17272E-02 0.00145 -1.28131E-04 1.00000 ];
INF_SCATTP3               (idx, [1:   4]) = [  4.27888E-03 0.00316 -2.00856E-04 0.76331 ];
INF_SCATTP4               (idx, [1:   4]) = [  2.45805E-03 0.00466  7.00244E-05 1.00000 ];
INF_SCATTP5               (idx, [1:   4]) = [  3.60664E-04 0.03000  2.80058E-05 1.00000 ];
INF_SCATTP6               (idx, [1:   4]) = [  8.21931E-05 0.11588  1.92787E-05 1.00000 ];
INF_SCATTP7               (idx, [1:   4]) = [  2.03221E-05 0.29754 -1.60479E-05 1.00000 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.09635E-01 0.00031  9.67689E-01 0.00023 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.07654E+00 0.00031  3.44463E-01 0.00023 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  3.48682E-03 0.00052  1.13237E-01 0.00093 ];
INF_REMXS                 (idx, [1:   4]) = [  3.75308E-03 0.00051  1.20745E-01 0.00120 ];

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

INF_S0                    (idx, [1:   8]) = [  4.78069E-01 0.00034  2.67290E-04 0.00459  7.57579E-03 0.00678  8.61031E-01 0.00027 ];
INF_S1                    (idx, [1:   8]) = [  3.05787E-02 0.00050 -6.77110E-05 0.00808 -7.23307E-04 0.05490  1.12246E-02 0.01959 ];
INF_S2                    (idx, [1:   8]) = [  2.17322E-02 0.00145 -5.02379E-06 0.03762 -3.34310E-04 0.12444  2.06179E-04 1.00000 ];
INF_S3                    (idx, [1:   8]) = [  4.28004E-03 0.00318 -1.12029E-06 0.06323 -1.24369E-04 0.11397 -7.64868E-05 1.00000 ];
INF_S4                    (idx, [1:   8]) = [  2.45897E-03 0.00467 -9.12772E-07 0.15743 -7.28126E-05 0.18237  1.42837E-04 0.89989 ];
INF_S5                    (idx, [1:   8]) = [  3.61181E-04 0.02945 -5.03661E-07 0.83953 -2.16834E-05 0.72107  4.96892E-05 1.00000 ];
INF_S6                    (idx, [1:   8]) = [  8.23002E-05 0.11473 -1.28800E-07 1.00000 -2.42382E-05 0.48836  4.35169E-05 1.00000 ];
INF_S7                    (idx, [1:   8]) = [  2.04460E-05 0.29431 -1.18977E-07 1.00000 -2.84208E-05 0.29873  1.23729E-05 1.00000 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  4.78071E-01 0.00034  2.67290E-04 0.00459  7.57579E-03 0.00678  8.61031E-01 0.00027 ];
INF_SP1                   (idx, [1:   8]) = [  3.05788E-02 0.00050 -6.77110E-05 0.00808 -7.23307E-04 0.05490  1.12246E-02 0.01959 ];
INF_SP2                   (idx, [1:   8]) = [  2.17322E-02 0.00145 -5.02379E-06 0.03762 -3.34310E-04 0.12444  2.06179E-04 1.00000 ];
INF_SP3                   (idx, [1:   8]) = [  4.28000E-03 0.00318 -1.12029E-06 0.06323 -1.24369E-04 0.11397 -7.64868E-05 1.00000 ];
INF_SP4                   (idx, [1:   8]) = [  2.45897E-03 0.00467 -9.12772E-07 0.15743 -7.28126E-05 0.18237  1.42837E-04 0.89989 ];
INF_SP5                   (idx, [1:   8]) = [  3.61167E-04 0.02945 -5.03661E-07 0.83953 -2.16834E-05 0.72107  4.96892E-05 1.00000 ];
INF_SP6                   (idx, [1:   8]) = [  8.23219E-05 0.11479 -1.28800E-07 1.00000 -2.42382E-05 0.48836  4.35169E-05 1.00000 ];
INF_SP7                   (idx, [1:   8]) = [  2.04410E-05 0.29431 -1.18977E-07 1.00000 -2.84208E-05 0.29873  1.23729E-05 1.00000 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  1.68160E+05 0.00336  6.51525E+05 0.00234  1.68135E+06 0.00189  2.93863E+06 0.00118  4.89288E+06 0.00191  7.94158E+06 0.00142  7.54093E+06 0.00154  6.44489E+06 0.00224  6.09042E+06 0.00178  3.89752E+06 0.00186  3.16871E+06 0.00179  2.12880E+06 0.00282  2.53038E+06 0.00262  1.64822E+06 0.00232  1.04216E+06 0.00253  1.13883E+06 0.00244  1.20766E+06 0.00286  1.44860E+06 0.00276  1.36339E+06 0.00295  2.39231E+06 0.00318  1.92718E+06 0.00297  1.63187E+06 0.00281  1.02824E+06 0.00302  5.87469E+05 0.00153  6.41339E+05 0.00157  5.64596E+05 0.00224  9.66576E+05 0.00225  1.85956E+05 0.00341  2.18542E+05 0.00085  1.82086E+05 0.00235  1.01175E+05 0.00406  1.64351E+05 0.00226  1.03406E+05 0.00257  8.12542E+04 0.00246  1.46935E+04 0.00437  1.40777E+04 0.00504  1.41126E+04 0.00476  1.41577E+04 0.00344  1.35238E+04 0.00603  1.30990E+04 0.00598  1.31818E+04 0.00723  1.21746E+04 0.00448  2.25563E+04 0.00397  3.51141E+04 0.00536  4.30704E+04 0.00215  1.04713E+05 0.00382  9.55396E+04 0.00514  8.53005E+04 0.00225  4.49581E+04 0.00331  2.80279E+04 0.00217  1.95048E+04 0.00884  2.05331E+04 0.00337  3.36510E+04 0.00749  3.83035E+04 0.00335  6.23286E+04 0.00157  7.96225E+04 0.00247  9.79570E+04 0.00229  5.37617E+04 0.00232  3.48700E+04 0.00243  2.31893E+04 0.00264  1.93773E+04 0.00291  1.77458E+04 0.00144  1.37222E+04 0.00542  8.56577E+03 0.00624  7.43674E+03 0.00713  6.09268E+03 0.00599  4.69021E+03 0.00741  3.24596E+03 0.00375  1.75803E+03 0.01229  4.52220E+02 0.02927 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_KEFF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_B2                     (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_ERR                    (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  1.16335E+16 0.00189  1.34958E+14 0.00145 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  4.81822E-01 0.00034  9.81777E-01 0.00011 ];
B1_CAPT                   (idx, [1:   4]) = [  3.48818E-03 0.00051  1.13237E-01 0.00093 ];
B1_ABS                    (idx, [1:   4]) = [  3.48818E-03 0.00051  1.13237E-01 0.00093 ];
B1_FISS                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NSF                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NUBAR                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  2.73376E-08 0.00038  1.87966E-06 0.00093 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  4.78337E-01 0.00034  8.68607E-01 0.00026 ];
B1_SCATT1                 (idx, [1:   4]) = [  3.05110E-02 0.00051  1.05013E-02 0.01956 ];
B1_SCATT2                 (idx, [1:   4]) = [  2.17272E-02 0.00145 -1.28131E-04 1.00000 ];
B1_SCATT3                 (idx, [1:   4]) = [  4.27892E-03 0.00316 -2.00856E-04 0.76331 ];
B1_SCATT4                 (idx, [1:   4]) = [  2.45805E-03 0.00466  7.00244E-05 1.00000 ];
B1_SCATT5                 (idx, [1:   4]) = [  3.60677E-04 0.03000  2.80058E-05 1.00000 ];
B1_SCATT6                 (idx, [1:   4]) = [  8.21714E-05 0.11582  1.92787E-05 1.00000 ];
B1_SCATT7                 (idx, [1:   4]) = [  2.03270E-05 0.29753 -1.60479E-05 1.00000 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  4.78338E-01 0.00034  8.68607E-01 0.00026 ];
B1_SCATTP1                (idx, [1:   4]) = [  3.05111E-02 0.00051  1.05013E-02 0.01956 ];
B1_SCATTP2                (idx, [1:   4]) = [  2.17272E-02 0.00145 -1.28131E-04 1.00000 ];
B1_SCATTP3                (idx, [1:   4]) = [  4.27888E-03 0.00316 -2.00856E-04 0.76331 ];
B1_SCATTP4                (idx, [1:   4]) = [  2.45805E-03 0.00466  7.00244E-05 1.00000 ];
B1_SCATTP5                (idx, [1:   4]) = [  3.60664E-04 0.03000  2.80058E-05 1.00000 ];
B1_SCATTP6                (idx, [1:   4]) = [  8.21931E-05 0.11588  1.92787E-05 1.00000 ];
B1_SCATTP7                (idx, [1:   4]) = [  2.03221E-05 0.29754 -1.60479E-05 1.00000 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  3.09635E-01 0.00031  9.67689E-01 0.00023 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  1.07654E+00 0.00031  3.44463E-01 0.00023 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  3.48682E-03 0.00052  1.13237E-01 0.00093 ];
B1_REMXS                  (idx, [1:   4]) = [  3.75308E-03 0.00051  1.20745E-01 0.00120 ];

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

B1_S0                     (idx, [1:   8]) = [  4.78069E-01 0.00034  2.67290E-04 0.00459  7.57579E-03 0.00678  8.61031E-01 0.00027 ];
B1_S1                     (idx, [1:   8]) = [  3.05787E-02 0.00050 -6.77110E-05 0.00808 -7.23307E-04 0.05490  1.12246E-02 0.01959 ];
B1_S2                     (idx, [1:   8]) = [  2.17322E-02 0.00145 -5.02379E-06 0.03762 -3.34310E-04 0.12444  2.06179E-04 1.00000 ];
B1_S3                     (idx, [1:   8]) = [  4.28004E-03 0.00318 -1.12029E-06 0.06323 -1.24369E-04 0.11397 -7.64868E-05 1.00000 ];
B1_S4                     (idx, [1:   8]) = [  2.45897E-03 0.00467 -9.12772E-07 0.15743 -7.28126E-05 0.18237  1.42837E-04 0.89989 ];
B1_S5                     (idx, [1:   8]) = [  3.61181E-04 0.02945 -5.03661E-07 0.83953 -2.16834E-05 0.72107  4.96892E-05 1.00000 ];
B1_S6                     (idx, [1:   8]) = [  8.23002E-05 0.11473 -1.28800E-07 1.00000 -2.42382E-05 0.48836  4.35169E-05 1.00000 ];
B1_S7                     (idx, [1:   8]) = [  2.04460E-05 0.29431 -1.18977E-07 1.00000 -2.84208E-05 0.29873  1.23729E-05 1.00000 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  4.78071E-01 0.00034  2.67290E-04 0.00459  7.57579E-03 0.00678  8.61031E-01 0.00027 ];
B1_SP1                    (idx, [1:   8]) = [  3.05788E-02 0.00050 -6.77110E-05 0.00808 -7.23307E-04 0.05490  1.12246E-02 0.01959 ];
B1_SP2                    (idx, [1:   8]) = [  2.17322E-02 0.00145 -5.02379E-06 0.03762 -3.34310E-04 0.12444  2.06179E-04 1.00000 ];
B1_SP3                    (idx, [1:   8]) = [  4.28000E-03 0.00318 -1.12029E-06 0.06323 -1.24369E-04 0.11397 -7.64868E-05 1.00000 ];
B1_SP4                    (idx, [1:   8]) = [  2.45897E-03 0.00467 -9.12772E-07 0.15743 -7.28126E-05 0.18237  1.42837E-04 0.89989 ];
B1_SP5                    (idx, [1:   8]) = [  3.61167E-04 0.02945 -5.03661E-07 0.83953 -2.16834E-05 0.72107  4.96892E-05 1.00000 ];
B1_SP6                    (idx, [1:   8]) = [  8.23219E-05 0.11479 -1.28800E-07 1.00000 -2.42382E-05 0.48836  4.35169E-05 1.00000 ];
B1_SP7                    (idx, [1:   8]) = [  2.04410E-05 0.29431 -1.18977E-07 1.00000 -2.84208E-05 0.29873  1.23729E-05 1.00000 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  2.16620E-02 0.00170  5.45412E-03 0.00205 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  2.19588E-02 0.00182  5.54410E-03 0.00148 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  2.19504E-02 0.00172  5.54026E-03 0.00237 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  2.10995E-02 0.00161  5.28619E-03 0.00265 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  1.53881E+01 0.00171  6.11169E+01 0.00206 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  1.51801E+01 0.00183  6.01244E+01 0.00148 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  1.51859E+01 0.00172  6.01670E+01 0.00237 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  1.57984E+01 0.00161  6.30592E+01 0.00266 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
LAMBDA                    (idx, [1:  18]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];


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
INPUT_FILE_NAME           (idx, [1:  8])  = 'UAM_HZP1' ;
WORKING_DIRECTORY         (idx, [1: 33])  = '/home/abrate/ricerca/esrel2020/XS' ;
HOSTNAME                  (idx, [1:  7])  = 'vpcen13' ;
CPU_TYPE                  (idx, [1: 41])  = 'Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz' ;
CPU_MHZ                   (idx, 1)        = 4294967295.0 ;
START_DATE                (idx, [1: 24])  = 'Sat Aug 29 19:41:15 2020' ;
COMPLETE_DATE             (idx, [1: 24])  = 'Sun Aug 30 03:33:18 2020' ;

% Run parameters:

POP                       (idx, 1)        = 1000000 ;
CYCLES                    (idx, 1)        = 100 ;
SKIP                      (idx, 1)        = 1000 ;
BATCH_INTERVAL            (idx, 1)        = 1 ;
SRC_NORM_MODE             (idx, 1)        = 2 ;
SEED                      (idx, 1)        = 1598722875174 ;
UFS_MODE                  (idx, 1)        = 0 ;
UFS_ORDER                 (idx, 1)        = 1.00000;
NEUTRON_TRANSPORT_MODE    (idx, 1)        = 1 ;
PHOTON_TRANSPORT_MODE     (idx, 1)        = 0 ;
GROUP_CONSTANT_GENERATION (idx, 1)        = 1 ;
B1_CALCULATION            (idx, [1:  3])  = [ 1 0 15 ];
B1_BURNUP_CORRECTION      (idx, 1)        = 0 ;

CRIT_SPEC_MODE            (idx, 1)        = 1 ;
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
OMP_HISTORY_PROFILE       (idx, [1:  30]) = [  1.02009E+00  9.94705E-01  1.00387E+00  1.00056E+00  9.88198E-01  1.00722E+00  1.00401E+00  9.96277E-01  1.00226E+00  1.00432E+00  9.94099E-01  9.95657E-01  9.95880E-01  9.96650E-01  1.00162E+00  1.00152E+00  9.97196E-01  1.00175E+00  9.98859E-01  9.94033E-01  1.00599E+00  1.00773E+00  1.00269E+00  9.96632E-01  9.96583E-01  1.00070E+00  9.98139E-01  9.97152E-01  9.98903E-01  9.96708E-01  ];
SHARE_BUF_ARRAY           (idx, 1)        = 0 ;
SHARE_RES2_ARRAY          (idx, 1)        = 1 ;
OMP_SHARED_QUEUE_LIM      (idx, 1)        = 0 ;

% File paths:

XS_DATA_FILE_PATH         (idx, [1: 46])  = '/opt/serpent/xsdata/jeff311/sss_jeff311.xsdata' ;
DECAY_DATA_FILE_PATH      (idx, [1:  3])  = 'N/A' ;
SFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
NFY_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;
BRA_DATA_FILE_PATH        (idx, [1:  3])  = 'N/A' ;

% Collision and reaction sampling (neutrons/photons):

MIN_MACROXS               (idx, [1:   4]) = [  5.00000E-02 0.0E+00  0.00000E+00 0.0E+00 ];
DT_THRESH                 (idx, [1:  2])  = [  9.00000E-01  9.00000E-01 ];
ST_FRAC                   (idx, [1:   4]) = [  3.02816E-01 0.00011  0.00000E+00 0.0E+00 ];
DT_FRAC                   (idx, [1:   4]) = [  6.97184E-01 4.9E-05  0.00000E+00 0.0E+00 ];
DT_EFF                    (idx, [1:   4]) = [  5.09482E-01 4.4E-05  0.00000E+00 0.0E+00 ];
REA_SAMPLING_EFF          (idx, [1:   4]) = [  1.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
REA_SAMPLING_FAIL         (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_COL_EFF               (idx, [1:   4]) = [  5.62564E-01 3.2E-05  0.00000E+00 0.0E+00 ];
AVG_TRACKING_LOOPS        (idx, [1:   8]) = [  4.81431E+00 8.9E-05  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
AVG_TRACKS                (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_REAL_COL              (idx, [1:   4]) = [  3.03573E+01 6.5E-05  0.00000E+00 0.0E+00 ];
AVG_VIRT_COL              (idx, [1:   4]) = [  2.36050E+01 0.00010  0.00000E+00 0.0E+00 ];
AVG_SURF_CROSS            (idx, [1:   4]) = [  1.50578E+01 0.00018  0.00000E+00 0.0E+00 ];
LOST_PARTICLES            (idx, 1)        = 0 ;

% Run statistics:

CYCLE_IDX                 (idx, 1)        = 100 ;
SIMULATED_HISTORIES       (idx, 1)        = 100003951 ;
MEAN_POP_SIZE             (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
MEAN_POP_WGT              (idx, [1:  2])  = [  1.00004E+06 0.00018 ];
SIMULATION_COMPLETED      (idx, 1)        = 1 ;

% Running times:

TOT_CPU_TIME              (idx, 1)        =  1.14426E+04 ;
RUNNING_TIME              (idx, 1)        =  4.72050E+02 ;
INIT_TIME                 (idx, [1:  2])  = [  2.40100E-01  2.40100E-01 ];
PROCESS_TIME              (idx, [1:  2])  = [  5.48333E-03  5.48333E-03 ];
TRANSPORT_CYCLE_TIME      (idx, [1:  3])  = [  4.71803E+02  4.71803E+02  0.00000E+00 ];
MPI_OVERHEAD_TIME         (idx, [1:  2])  = [  0.00000E+00  0.00000E+00 ];
LEAKAGE_CORR_SOL_TIME     (idx, 1)        =  1.93334E-03 ;
ESTIMATED_RUNNING_TIME    (idx, [1:  2])  = [  4.72036E+02  0.00000E+00 ];
CPU_USAGE                 (idx, 1)        = 24.24027 ;
TRANSPORT_CPU_USAGE       (idx, [1:   2]) = [  2.41670E+01 0.00036 ];
OMP_PARALLEL_FRAC         (idx, 1)        =  8.01323E-01 ;

% Memory usage:

AVAIL_MEM                 (idx, 1)        = 100712.49 ;
ALLOC_MEMSIZE             (idx, 1)        = 8618.97;
MEMSIZE                   (idx, 1)        = 8405.65;
XS_MEMSIZE                (idx, 1)        = 1458.21;
MAT_MEMSIZE               (idx, 1)        = 161.71;
RES_MEMSIZE               (idx, 1)        = 40.61;
IFC_MEMSIZE               (idx, 1)        = 0.00;
MISC_MEMSIZE              (idx, 1)        = 6745.12;
UNKNOWN_MEMSIZE           (idx, 1)        = 0.00;
UNUSED_MEMSIZE            (idx, 1)        = 213.32;

% Geometry parameters:

TOT_CELLS                 (idx, 1)        = 2 ;
UNION_CELLS               (idx, 1)        = 0 ;

% Neutron energy grid:

NEUTRON_ERG_TOL           (idx, 1)        =  0.00000E+00 ;
NEUTRON_ERG_NE            (idx, 1)        = 377473 ;
NEUTRON_EMIN              (idx, 1)        =  1.00000E-11 ;
NEUTRON_EMAX              (idx, 1)        =  2.00000E+01 ;

% Unresolved resonance probability table sampling:

URES_DILU_CUT             (idx, 1)        =  1.00000E-09 ;
URES_EMIN                 (idx, 1)        =  1.50000E-04 ;
URES_EMAX                 (idx, 1)        =  1.00000E+00 ;
URES_AVAIL                (idx, 1)        = 22 ;
URES_USED                 (idx, 1)        = 22 ;

% Nuclides and reaction channels:

TOT_NUCLIDES              (idx, 1)        = 51 ;
TOT_TRANSPORT_NUCLIDES    (idx, 1)        = 51 ;
TOT_DOSIMETRY_NUCLIDES    (idx, 1)        = 0 ;
TOT_DECAY_NUCLIDES        (idx, 1)        = 0 ;
TOT_PHOTON_NUCLIDES       (idx, 1)        = 0 ;
TOT_REA_CHANNELS          (idx, 1)        = 1255 ;
TOT_TRANSMU_REA           (idx, 1)        = 0 ;

% Neutron physics options:

USE_DELNU                 (idx, 1)        = 1 ;
USE_URES                  (idx, 1)        = 1 ;
USE_DBRC                  (idx, 1)        = 0 ;
IMPL_CAPT                 (idx, 1)        = 0 ;
IMPL_NXN                  (idx, 1)        = 1 ;
IMPL_FISS                 (idx, 1)        = 0 ;
DOPPLER_PREPROCESSOR      (idx, 1)        = 1 ;
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

NORM_COEF                 (idx, [1:   4]) = [  3.37127E+09 0.00011  0.00000E+00 0.0E+00 ];

% Analog reaction rate estimators:

CONVERSION_RATIO          (idx, [1:   2]) = [  5.77603E-01 0.00025 ];
U235_FISS                 (idx, [1:   4]) = [  9.90572E+14 0.00019  7.34684E-01 0.00017 ];
U238_FISS                 (idx, [1:   4]) = [  9.21228E+13 0.00056  6.83252E-02 0.00052 ];
PU239_FISS                (idx, [1:   4]) = [  2.18024E+14 0.00063  1.61704E-01 0.00061 ];
PU240_FISS                (idx, [1:   4]) = [  2.57850E+12 0.00379  1.91239E-03 0.00376 ];
PU241_FISS                (idx, [1:   4]) = [  4.33275E+13 0.00115  3.21349E-02 0.00112 ];
U235_CAPT                 (idx, [1:   4]) = [  2.18104E+14 0.00038  1.07557E-01 0.00036 ];
U238_CAPT                 (idx, [1:   4]) = [  8.16001E+14 0.00026  4.02407E-01 0.00016 ];
PU239_CAPT                (idx, [1:   4]) = [  1.19322E+14 0.00062  5.88430E-02 0.00060 ];
PU240_CAPT                (idx, [1:   4]) = [  1.06800E+14 0.00077  5.26678E-02 0.00076 ];
PU241_CAPT                (idx, [1:   4]) = [  1.46475E+13 0.00157  7.22336E-03 0.00156 ];

% Neutron balance (particles/weight):

BALA_SRC_NEUTRON_SRC     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_FISS    (idx, [1:  2])  = [ 100003951 1.00000E+08 ];
BALA_SRC_NEUTRON_NXN     (idx, [1:  2])  = [ 0 1.42950E+05 ];
BALA_SRC_NEUTRON_VR      (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_SRC_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_LOSS_NEUTRON_CAPT    (idx, [1:  2])  = [ 60063923 6.01492E+07 ];
BALA_LOSS_NEUTRON_FISS    (idx, [1:  2])  = [ 39940028 3.99937E+07 ];
BALA_LOSS_NEUTRON_LEAK    (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_CUT     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_ERR     (idx, [1:  2])  = [ 0 0.00000E+00 ];
BALA_LOSS_NEUTRON_TOT     (idx, [1:  2])  = [ 100003951 1.00143E+08 ];

BALA_NEUTRON_DIFF         (idx, [1:  2])  = [ 0 1.58504E-04 ];

% Normalized total reaction rates (neutrons):

TOT_POWER                 (idx, [1:   2]) = [  4.40000E+04 0.0E+00 ];
TOT_POWDENS               (idx, [1:   2]) = [  6.08444E-03 6.9E-09 ];
TOT_GENRATE               (idx, [1:   2]) = [  3.43997E+15 1.7E-05 ];
TOT_FISSRATE              (idx, [1:   2]) = [  1.34797E+15 3.4E-06 ];
TOT_CAPTRATE              (idx, [1:   2]) = [  2.02801E+15 0.00012 ];
TOT_ABSRATE               (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_SRCRATE               (idx, [1:   2]) = [  3.37127E+15 0.00011 ];
TOT_FLUX                  (idx, [1:   2]) = [  1.54978E+17 0.00012 ];
TOT_PHOTON_PRODRATE       (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
TOT_LEAKRATE              (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
ALBEDO_LEAKRATE           (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_LOSSRATE              (idx, [1:   2]) = [  3.37598E+15 7.1E-05 ];
TOT_CUTRATE               (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
TOT_RR                    (idx, [1:   2]) = [  1.02483E+17 0.00011 ];
INI_FMASS                 (idx, 1)        =  7.23156E+00 ;
TOT_FMASS                 (idx, 1)        =  7.23156E+00 ;

% Six-factor formula:

SIX_FF_ETA                (idx, [1:   2]) = [  1.59347E+00 0.00010 ];
SIX_FF_F                  (idx, [1:   2]) = [  7.86859E-01 6.5E-05 ];
SIX_FF_P                  (idx, [1:   2]) = [  6.09029E-01 9.5E-05 ];
SIX_FF_EPSILON            (idx, [1:   2]) = [  1.33656E+00 9.5E-05 ];
SIX_FF_LF                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_LT                 (idx, [1:   2]) = [  1.00000E+00 0.0E+00 ];
SIX_FF_KINF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];
SIX_FF_KEFF               (idx, [1:   2]) = [  1.02063E+00 0.00013 ];

% Fission neutron and energy production:

NUBAR                     (idx, [1:   2]) = [  2.55197E+00 2.0E-05 ];
FISSE                     (idx, [1:   2]) = [  2.03733E+02 3.4E-06 ];

% Criticality eigenvalues:

ANA_KEFF                  (idx, [1:   6]) = [  1.02065E+00 0.00013  1.01426E+00 0.00013  6.36553E-03 0.00198 ];
IMP_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
COL_KEFF                  (idx, [1:   2]) = [  1.02038E+00 0.00011 ];
ABS_KEFF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
ABS_KINF                  (idx, [1:   2]) = [  1.02042E+00 6.8E-05 ];
GEOM_ALBEDO               (idx, [1:   6]) = [  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00  1.00000E+00 0.0E+00 ];

% ALF (Average lethargy of neutrons causing fission):
% Based on E0 = 2.000000E+01 MeV

ANA_ALF                   (idx, [1:   2]) = [  1.69604E+01 4.8E-05 ];
IMP_ALF                   (idx, [1:   2]) = [  1.69598E+01 2.6E-05 ];

% EALF (Energy corresponding to average lethargy of neutrons causing fission):

ANA_EALF                  (idx, [1:   2]) = [  8.61468E-07 0.00081 ];
IMP_EALF                  (idx, [1:   2]) = [  8.61929E-07 0.00044 ];

% AFGE (Average energy of neutrons causing fission):

ANA_AFGE                  (idx, [1:   2]) = [  2.43848E-01 0.00060 ];
IMP_AFGE                  (idx, [1:   2]) = [  2.43913E-01 0.00024 ];

% Forward-weighted delayed neutron parameters:

PRECURSOR_GROUPS          (idx, 1)        = 8 ;
FWD_ANA_BETA_ZERO         (idx, [1:  18]) = [  6.41574E-03 0.00138  1.77755E-04 0.00760  9.59151E-04 0.00319  5.22748E-04 0.00428  1.16888E-03 0.00304  2.04914E-03 0.00239  7.14018E-04 0.00388  5.89915E-04 0.00359  2.34134E-04 0.00687 ];
FWD_ANA_LAMBDA            (idx, [1:  18]) = [  4.79898E-01 0.00196  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.4E-09  2.92467E-01 0.0E+00  6.66488E-01 3.7E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Beta-eff using Meulekamp's method:

ADJ_MEULEKAMP_BETA_EFF    (idx, [1:  18]) = [  6.39411E-03 0.00193  1.79105E-04 0.01071  9.51549E-04 0.00465  5.21851E-04 0.00621  1.16414E-03 0.00445  2.04733E-03 0.00383  7.08080E-04 0.00538  5.89788E-04 0.00580  2.32266E-04 0.00948 ];
ADJ_MEULEKAMP_LAMBDA      (idx, [1:  18]) = [  4.79629E-01 0.00287  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.2E-09  1.33042E-01 3.5E-09  2.92467E-01 0.0E+00  6.66488E-01 2.6E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using Nauchi's method:

IFP_CHAIN_LENGTH          (idx, 1)        = 15 ;
ADJ_NAUCHI_GEN_TIME       (idx, [1:   6]) = [  2.08580E-05 0.00030  2.08373E-05 0.00031  2.41314E-05 0.00231 ];
ADJ_NAUCHI_LIFETIME       (idx, [1:   6]) = [  2.12887E-05 0.00026  2.12676E-05 0.00027  2.46299E-05 0.00233 ];
ADJ_NAUCHI_BETA_EFF       (idx, [1:  18]) = [  6.22890E-03 0.00210  1.71842E-04 0.01246  9.28634E-04 0.00501  5.07929E-04 0.00666  1.13399E-03 0.00417  1.99048E-03 0.00350  6.93602E-04 0.00640  5.76057E-04 0.00647  2.26363E-04 0.01118 ];
ADJ_NAUCHI_LAMBDA         (idx, [1:  18]) = [  4.80252E-01 0.00314  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 4.0E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];

% Adjoint weighted time constants using IFP:

ADJ_IFP_GEN_TIME          (idx, [1:   6]) = [  2.07746E-05 0.00068  2.07537E-05 0.00069  2.41287E-05 0.00720 ];
ADJ_IFP_LIFETIME          (idx, [1:   6]) = [  2.12036E-05 0.00066  2.11823E-05 0.00066  2.46267E-05 0.00719 ];
ADJ_IFP_IMP_BETA_EFF      (idx, [1:  18]) = [  6.18290E-03 0.00684  1.75511E-04 0.03639  9.52548E-04 0.01641  4.82324E-04 0.02302  1.09572E-03 0.01605  1.97731E-03 0.01143  6.86947E-04 0.02032  5.90552E-04 0.02301  2.21991E-04 0.03841 ];
ADJ_IFP_IMP_LAMBDA        (idx, [1:  18]) = [  4.82637E-01 0.01112  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.7E-09  1.33042E-01 4.0E-09  2.92467E-01 0.0E+00  6.66488E-01 3.2E-09  1.63478E+00 0.0E+00  3.55460E+00 5.3E-09 ];
ADJ_IFP_ANA_BETA_EFF      (idx, [1:  18]) = [  6.16570E-03 0.00656  1.74535E-04 0.03564  9.47350E-04 0.01608  4.84709E-04 0.02241  1.08905E-03 0.01531  1.97312E-03 0.01103  6.84544E-04 0.01978  5.89190E-04 0.02159  2.23206E-04 0.03829 ];
ADJ_IFP_ANA_LAMBDA        (idx, [1:  18]) = [  4.83650E-01 0.01097  1.24667E-02 0.0E+00  2.82917E-02 0.0E+00  4.25244E-02 3.5E-09  1.33042E-01 3.2E-09  2.92467E-01 0.0E+00  6.66488E-01 4.0E-09  1.63478E+00 0.0E+00  3.55460E+00 5.1E-09 ];
ADJ_IFP_ROSSI_ALPHA       (idx, [1:   2]) = [ -2.97940E+02 0.00692 ];

% Adjoint weighted time constants using perturbation technique:

ADJ_PERT_GEN_TIME         (idx, [1:   2]) = [  2.08903E-05 0.00022 ];
ADJ_PERT_LIFETIME         (idx, [1:   2]) = [  2.13217E-05 0.00017 ];
ADJ_PERT_BETA_EFF         (idx, [1:   2]) = [  6.27285E-03 0.00156 ];
ADJ_PERT_ROSSI_ALPHA      (idx, [1:   2]) = [ -3.00278E+02 0.00161 ];

% Inverse neutron speed :

ANA_INV_SPD               (idx, [1:   2]) = [  3.79968E-07 0.00016 ];

% Analog slowing-down and thermal neutron lifetime (total/prompt/delayed):

ANA_SLOW_TIME             (idx, [1:   6]) = [  2.82212E-06 0.00011  2.82200E-06 0.00011  2.83937E-06 0.00111 ];
ANA_THERM_TIME            (idx, [1:   6]) = [  2.51693E-05 0.00015  2.51641E-05 0.00015  2.59132E-05 0.00158 ];
ANA_THERM_FRAC            (idx, [1:   6]) = [  6.09615E-01 9.5E-05  6.09284E-01 9.8E-05  6.60988E-01 0.00196 ];
ANA_DELAYED_EMTIME        (idx, [1:   2]) = [  1.21135E+01 0.00292 ];
ANA_MEAN_NCOL             (idx, [1:   4]) = [  3.03573E+01 6.5E-05  3.13774E+01 9.9E-05 ];

% Group constant generation:

GC_UNIVERSE_NAME          (idx, [1:  2])  = 'BW' ;

% Micro- and macro-group structures:

MICRO_NG                  (idx, 1)        = 70 ;
MICRO_E                   (idx, [1:  71]) = [  1.00000E-11  5.00000E-09  1.00000E-08  1.50000E-08  2.00000E-08  2.50000E-08  3.00000E-08  3.50000E-08  4.20000E-08  5.00000E-08  5.80000E-08  6.70000E-08  8.00000E-08  1.00000E-07  1.40000E-07  1.80000E-07  2.20000E-07  2.50000E-07  2.80000E-07  3.00000E-07  3.20000E-07  3.50000E-07  4.00000E-07  5.00000E-07  6.25000E-07  7.80000E-07  8.50000E-07  9.10000E-07  9.50000E-07  9.72000E-07  9.96000E-07  1.02000E-06  1.04500E-06  1.07100E-06  1.09700E-06  1.12300E-06  1.15000E-06  1.30000E-06  1.50000E-06  1.85500E-06  2.10000E-06  2.60000E-06  3.30000E-06  4.00000E-06  9.87700E-06  1.59680E-05  2.77000E-05  4.80520E-05  7.55014E-05  1.48728E-04  3.67262E-04  9.06898E-04  1.42510E-03  2.23945E-03  3.51910E-03  5.50000E-03  9.11800E-03  1.50300E-02  2.47800E-02  4.08500E-02  6.74300E-02  1.11000E-01  1.83000E-01  3.02500E-01  5.00000E-01  8.21000E-01  1.35300E+00  2.23100E+00  3.67900E+00  6.06550E+00  2.00000E+01 ];

MACRO_NG                  (idx, 1)        = 2 ;
MACRO_E                   (idx, [1:   3]) = [  1.00000E+37  6.25000E-07  0.00000E+00 ];

% Micro-group spectrum:

INF_MICRO_FLX             (idx, [1: 140]) = [  3.30994E+03 0.01883  8.47537E+03 0.01457  2.18778E+04 0.01377  4.46710E+04 0.00726  9.45168E+04 0.00427  1.86336E+05 0.00392  1.77924E+05 0.00117  1.84367E+05 0.00150  1.64678E+05 0.00166  1.33485E+05 0.00272  1.18119E+05 0.00365  1.05061E+05 0.00231  1.05328E+05 0.00150  9.64576E+04 0.00194  9.30577E+04 0.00220  8.13717E+04 0.00267  8.22418E+04 0.00340  8.27100E+04 0.00274  8.24007E+04 0.00204  1.64299E+05 0.00252  1.63173E+05 0.00206  1.22673E+05 0.00091  8.18741E+04 0.00157  9.78676E+04 0.00055  9.75594E+04 0.00137  8.48068E+04 0.00254  1.59380E+05 0.00244  3.38717E+04 0.00191  4.25118E+04 0.00223  3.79993E+04 0.00301  2.23423E+04 0.00315  3.84199E+04 0.00287  2.62456E+04 0.00490  2.26571E+04 0.00440  4.36087E+03 0.00728  4.40458E+03 0.00373  4.43927E+03 0.00808  4.55918E+03 0.00900  4.52557E+03 0.00690  4.45284E+03 0.00748  4.60268E+03 0.00394  4.32491E+03 0.00510  8.17720E+03 0.00409  1.31272E+04 0.00719  1.64949E+04 0.00271  4.38711E+04 0.00187  4.73186E+04 0.00219  5.73260E+04 0.00230  4.64501E+04 0.00227  3.83304E+04 0.00297  3.17734E+04 0.00402  4.02905E+04 0.00363  8.39694E+04 0.00279  1.20920E+05 0.00272  2.52101E+05 0.00266  4.12218E+05 0.00298  6.43279E+05 0.00316  4.27576E+05 0.00301  3.09799E+05 0.00226  2.24144E+05 0.00331  2.03641E+05 0.00304  2.02146E+05 0.00299  1.71000E+05 0.00288  1.15448E+05 0.00306  1.07478E+05 0.00309  9.62870E+04 0.00287  8.22285E+04 0.00283  6.50132E+04 0.00339  4.42661E+04 0.00282  1.60061E+04 0.00242 ];

% Integral parameters:

INF_KINF                  (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Flux spectra in infinite geometry:

INF_FLX                   (idx, [1:   4]) = [  5.35933E+14 0.00167  6.47119E+14 0.00290 ];
INF_FISS_FLX              (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

INF_TOT                   (idx, [1:   4]) = [  8.82007E-01 0.00026  1.99832E+00 7.0E-05 ];
INF_CAPT                  (idx, [1:   4]) = [  1.33158E-03 0.00069  3.41226E-02 0.00011 ];
INF_ABS                   (idx, [1:   4]) = [  1.33158E-03 0.00069  3.41226E-02 0.00011 ];
INF_FISS                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_NSF                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_NUBAR                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_KAPPA                 (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
INF_INVV                  (idx, [1:   4]) = [  1.05287E-07 0.00064  2.71371E-06 0.00011 ];

% Total scattering cross sections:

INF_SCATT0                (idx, [1:   4]) = [  8.80674E-01 0.00025  1.96417E+00 8.9E-05 ];
INF_SCATT1                (idx, [1:   4]) = [  5.19616E-01 0.00032  5.38461E-01 0.00051 ];
INF_SCATT2                (idx, [1:   4]) = [  1.97798E-01 0.00060  1.24858E-01 0.00136 ];
INF_SCATT3                (idx, [1:   4]) = [  8.22771E-03 0.01074  3.73040E-02 0.00461 ];
INF_SCATT4                (idx, [1:   4]) = [ -2.96171E-02 0.00335 -1.33253E-02 0.01067 ];
INF_SCATT5                (idx, [1:   4]) = [ -3.69183E-03 0.01707  9.43102E-03 0.01590 ];
INF_SCATT6                (idx, [1:   4]) = [  9.16101E-03 0.00529 -2.46773E-02 0.00152 ];
INF_SCATT7                (idx, [1:   4]) = [  1.12022E-03 0.07388  8.26060E-04 0.05453 ];

% Total scattering production cross sections:

INF_SCATTP0               (idx, [1:   4]) = [  8.80674E-01 0.00025  1.96417E+00 8.9E-05 ];
INF_SCATTP1               (idx, [1:   4]) = [  5.19616E-01 0.00032  5.38461E-01 0.00051 ];
INF_SCATTP2               (idx, [1:   4]) = [  1.97798E-01 0.00060  1.24858E-01 0.00136 ];
INF_SCATTP3               (idx, [1:   4]) = [  8.22771E-03 0.01074  3.73040E-02 0.00461 ];
INF_SCATTP4               (idx, [1:   4]) = [ -2.96171E-02 0.00335 -1.33253E-02 0.01067 ];
INF_SCATTP5               (idx, [1:   4]) = [ -3.69183E-03 0.01707  9.43102E-03 0.01590 ];
INF_SCATTP6               (idx, [1:   4]) = [  9.16101E-03 0.00529 -2.46773E-02 0.00152 ];
INF_SCATTP7               (idx, [1:   4]) = [  1.12022E-03 0.07388  8.26060E-04 0.05453 ];

% Diffusion parameters:

INF_TRANSPXS              (idx, [1:   4]) = [  3.02130E-01 0.00101  1.26127E+00 0.00028 ];
INF_DIFFCOEF              (idx, [1:   4]) = [  1.10328E+00 0.00101  2.64283E-01 0.00028 ];

% Reduced absoption and removal:

INF_RABSXS                (idx, [1:   4]) = [  1.33158E-03 0.00069  3.41226E-02 0.00011 ];
INF_REMXS                 (idx, [1:   4]) = [  5.58661E-02 0.00031  3.47411E-02 0.00152 ];

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

INF_S0                    (idx, [1:   8]) = [  8.26141E-01 0.00026  5.45331E-02 0.00019  5.93511E-04 0.00650  1.96358E+00 9.0E-05 ];
INF_S1                    (idx, [1:   8]) = [  5.03185E-01 0.00031  1.64308E-02 0.00080  3.82634E-04 0.01165  5.38079E-01 0.00050 ];
INF_S2                    (idx, [1:   8]) = [  2.02521E-01 0.00056 -4.72325E-03 0.00615  2.03600E-04 0.01353  1.24655E-01 0.00136 ];
INF_S3                    (idx, [1:   8]) = [  1.39442E-02 0.00532 -5.71645E-03 0.00504  7.34452E-05 0.04827  3.72306E-02 0.00459 ];
INF_S4                    (idx, [1:   8]) = [ -2.77074E-02 0.00304 -1.90970E-03 0.00873  2.12787E-06 1.00000 -1.33274E-02 0.01057 ];
INF_S5                    (idx, [1:   8]) = [ -3.77194E-03 0.01466  8.01094E-05 0.19883 -2.51381E-05 0.07597  9.45616E-03 0.01578 ];
INF_S6                    (idx, [1:   8]) = [  9.58108E-03 0.00499 -4.20072E-04 0.03097 -3.18654E-05 0.05171 -2.46455E-02 0.00157 ];
INF_S7                    (idx, [1:   8]) = [  1.65494E-03 0.04284 -5.34711E-04 0.03581 -2.82471E-05 0.06129  8.54307E-04 0.05431 ];

% Scattering production matrixes:

INF_SP0                   (idx, [1:   8]) = [  8.26141E-01 0.00026  5.45331E-02 0.00019  5.93511E-04 0.00650  1.96358E+00 9.0E-05 ];
INF_SP1                   (idx, [1:   8]) = [  5.03185E-01 0.00031  1.64308E-02 0.00080  3.82634E-04 0.01165  5.38079E-01 0.00050 ];
INF_SP2                   (idx, [1:   8]) = [  2.02521E-01 0.00056 -4.72325E-03 0.00615  2.03600E-04 0.01353  1.24655E-01 0.00136 ];
INF_SP3                   (idx, [1:   8]) = [  1.39442E-02 0.00532 -5.71645E-03 0.00504  7.34452E-05 0.04827  3.72306E-02 0.00459 ];
INF_SP4                   (idx, [1:   8]) = [ -2.77074E-02 0.00304 -1.90970E-03 0.00873  2.12787E-06 1.00000 -1.33274E-02 0.01057 ];
INF_SP5                   (idx, [1:   8]) = [ -3.77194E-03 0.01466  8.01094E-05 0.19883 -2.51381E-05 0.07597  9.45616E-03 0.01578 ];
INF_SP6                   (idx, [1:   8]) = [  9.58108E-03 0.00499 -4.20072E-04 0.03097 -3.18654E-05 0.05171 -2.46455E-02 0.00157 ];
INF_SP7                   (idx, [1:   8]) = [  1.65494E-03 0.04284 -5.34711E-04 0.03581 -2.82471E-05 0.06129  8.54307E-04 0.05431 ];

% Micro-group spectrum:

B1_MICRO_FLX              (idx, [1: 140]) = [  3.30994E+03 0.01883  8.47537E+03 0.01457  2.18778E+04 0.01377  4.46710E+04 0.00726  9.45168E+04 0.00427  1.86336E+05 0.00392  1.77924E+05 0.00117  1.84367E+05 0.00150  1.64678E+05 0.00166  1.33485E+05 0.00272  1.18119E+05 0.00365  1.05061E+05 0.00231  1.05328E+05 0.00150  9.64576E+04 0.00194  9.30577E+04 0.00220  8.13717E+04 0.00267  8.22418E+04 0.00340  8.27100E+04 0.00274  8.24007E+04 0.00204  1.64299E+05 0.00252  1.63173E+05 0.00206  1.22673E+05 0.00091  8.18741E+04 0.00157  9.78676E+04 0.00055  9.75594E+04 0.00137  8.48068E+04 0.00254  1.59380E+05 0.00244  3.38717E+04 0.00191  4.25118E+04 0.00223  3.79993E+04 0.00301  2.23423E+04 0.00315  3.84199E+04 0.00287  2.62456E+04 0.00490  2.26571E+04 0.00440  4.36087E+03 0.00728  4.40458E+03 0.00373  4.43927E+03 0.00808  4.55918E+03 0.00900  4.52557E+03 0.00690  4.45284E+03 0.00748  4.60268E+03 0.00394  4.32491E+03 0.00510  8.17720E+03 0.00409  1.31272E+04 0.00719  1.64949E+04 0.00271  4.38711E+04 0.00187  4.73186E+04 0.00219  5.73260E+04 0.00230  4.64501E+04 0.00227  3.83304E+04 0.00297  3.17734E+04 0.00402  4.02905E+04 0.00363  8.39694E+04 0.00279  1.20920E+05 0.00272  2.52101E+05 0.00266  4.12218E+05 0.00298  6.43279E+05 0.00316  4.27576E+05 0.00301  3.09799E+05 0.00226  2.24144E+05 0.00331  2.03641E+05 0.00304  2.02146E+05 0.00299  1.71000E+05 0.00288  1.15448E+05 0.00306  1.07478E+05 0.00309  9.62870E+04 0.00287  8.22285E+04 0.00283  6.50132E+04 0.00339  4.42661E+04 0.00282  1.60061E+04 0.00242 ];

% Integral parameters:

B1_KINF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_KEFF                   (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_B2                     (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];
B1_ERR                    (idx, [1:   2]) = [  0.00000E+00 0.0E+00 ];

% Critical spectra in infinite geometry:

B1_FLX                    (idx, [1:   4]) = [  5.35933E+14 0.00167  6.47119E+14 0.00290 ];
B1_FISS_FLX               (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

% Reaction cross sections:

B1_TOT                    (idx, [1:   4]) = [  8.82007E-01 0.00026  1.99832E+00 7.0E-05 ];
B1_CAPT                   (idx, [1:   4]) = [  1.33158E-03 0.00069  3.41226E-02 0.00011 ];
B1_ABS                    (idx, [1:   4]) = [  1.33158E-03 0.00069  3.41226E-02 0.00011 ];
B1_FISS                   (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NSF                    (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_NUBAR                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_KAPPA                  (idx, [1:   4]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
B1_INVV                   (idx, [1:   4]) = [  1.05287E-07 0.00064  2.71371E-06 0.00011 ];

% Total scattering cross sections:

B1_SCATT0                 (idx, [1:   4]) = [  8.80674E-01 0.00025  1.96417E+00 8.9E-05 ];
B1_SCATT1                 (idx, [1:   4]) = [  5.19616E-01 0.00032  5.38461E-01 0.00051 ];
B1_SCATT2                 (idx, [1:   4]) = [  1.97798E-01 0.00060  1.24858E-01 0.00136 ];
B1_SCATT3                 (idx, [1:   4]) = [  8.22771E-03 0.01074  3.73040E-02 0.00461 ];
B1_SCATT4                 (idx, [1:   4]) = [ -2.96171E-02 0.00335 -1.33253E-02 0.01067 ];
B1_SCATT5                 (idx, [1:   4]) = [ -3.69183E-03 0.01707  9.43102E-03 0.01590 ];
B1_SCATT6                 (idx, [1:   4]) = [  9.16101E-03 0.00529 -2.46773E-02 0.00152 ];
B1_SCATT7                 (idx, [1:   4]) = [  1.12022E-03 0.07388  8.26060E-04 0.05453 ];

% Total scattering production cross sections:

B1_SCATTP0                (idx, [1:   4]) = [  8.80674E-01 0.00025  1.96417E+00 8.9E-05 ];
B1_SCATTP1                (idx, [1:   4]) = [  5.19616E-01 0.00032  5.38461E-01 0.00051 ];
B1_SCATTP2                (idx, [1:   4]) = [  1.97798E-01 0.00060  1.24858E-01 0.00136 ];
B1_SCATTP3                (idx, [1:   4]) = [  8.22771E-03 0.01074  3.73040E-02 0.00461 ];
B1_SCATTP4                (idx, [1:   4]) = [ -2.96171E-02 0.00335 -1.33253E-02 0.01067 ];
B1_SCATTP5                (idx, [1:   4]) = [ -3.69183E-03 0.01707  9.43102E-03 0.01590 ];
B1_SCATTP6                (idx, [1:   4]) = [  9.16101E-03 0.00529 -2.46773E-02 0.00152 ];
B1_SCATTP7                (idx, [1:   4]) = [  1.12022E-03 0.07388  8.26060E-04 0.05453 ];

% Diffusion parameters:

B1_TRANSPXS               (idx, [1:   4]) = [  3.02130E-01 0.00101  1.26127E+00 0.00028 ];
B1_DIFFCOEF               (idx, [1:   4]) = [  1.10328E+00 0.00101  2.64283E-01 0.00028 ];

% Reduced absoption and removal:

B1_RABSXS                 (idx, [1:   4]) = [  1.33158E-03 0.00069  3.41226E-02 0.00011 ];
B1_REMXS                  (idx, [1:   4]) = [  5.58661E-02 0.00031  3.47411E-02 0.00152 ];

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

B1_S0                     (idx, [1:   8]) = [  8.26141E-01 0.00026  5.45331E-02 0.00019  5.93511E-04 0.00650  1.96358E+00 9.0E-05 ];
B1_S1                     (idx, [1:   8]) = [  5.03185E-01 0.00031  1.64308E-02 0.00080  3.82634E-04 0.01165  5.38079E-01 0.00050 ];
B1_S2                     (idx, [1:   8]) = [  2.02521E-01 0.00056 -4.72325E-03 0.00615  2.03600E-04 0.01353  1.24655E-01 0.00136 ];
B1_S3                     (idx, [1:   8]) = [  1.39442E-02 0.00532 -5.71645E-03 0.00504  7.34452E-05 0.04827  3.72306E-02 0.00459 ];
B1_S4                     (idx, [1:   8]) = [ -2.77074E-02 0.00304 -1.90970E-03 0.00873  2.12787E-06 1.00000 -1.33274E-02 0.01057 ];
B1_S5                     (idx, [1:   8]) = [ -3.77194E-03 0.01466  8.01094E-05 0.19883 -2.51381E-05 0.07597  9.45616E-03 0.01578 ];
B1_S6                     (idx, [1:   8]) = [  9.58108E-03 0.00499 -4.20072E-04 0.03097 -3.18654E-05 0.05171 -2.46455E-02 0.00157 ];
B1_S7                     (idx, [1:   8]) = [  1.65494E-03 0.04284 -5.34711E-04 0.03581 -2.82471E-05 0.06129  8.54307E-04 0.05431 ];

% Scattering production matrixes:

B1_SP0                    (idx, [1:   8]) = [  8.26141E-01 0.00026  5.45331E-02 0.00019  5.93511E-04 0.00650  1.96358E+00 9.0E-05 ];
B1_SP1                    (idx, [1:   8]) = [  5.03185E-01 0.00031  1.64308E-02 0.00080  3.82634E-04 0.01165  5.38079E-01 0.00050 ];
B1_SP2                    (idx, [1:   8]) = [  2.02521E-01 0.00056 -4.72325E-03 0.00615  2.03600E-04 0.01353  1.24655E-01 0.00136 ];
B1_SP3                    (idx, [1:   8]) = [  1.39442E-02 0.00532 -5.71645E-03 0.00504  7.34452E-05 0.04827  3.72306E-02 0.00459 ];
B1_SP4                    (idx, [1:   8]) = [ -2.77074E-02 0.00304 -1.90970E-03 0.00873  2.12787E-06 1.00000 -1.33274E-02 0.01057 ];
B1_SP5                    (idx, [1:   8]) = [ -3.77194E-03 0.01466  8.01094E-05 0.19883 -2.51381E-05 0.07597  9.45616E-03 0.01578 ];
B1_SP6                    (idx, [1:   8]) = [  9.58108E-03 0.00499 -4.20072E-04 0.03097 -3.18654E-05 0.05171 -2.46455E-02 0.00157 ];
B1_SP7                    (idx, [1:   8]) = [  1.65494E-03 0.04284 -5.34711E-04 0.03581 -2.82471E-05 0.06129  8.54307E-04 0.05431 ];

% Additional diffusion parameters:

CMM_TRANSPXS              (idx, [1:   4]) = [  9.64518E-04 0.00149  2.51039E-02 0.00360 ];
CMM_TRANSPXS_X            (idx, [1:   4]) = [  9.66808E-04 0.00150  2.52557E-02 0.00314 ];
CMM_TRANSPXS_Y            (idx, [1:   4]) = [  9.66599E-04 0.00155  2.52180E-02 0.00396 ];
CMM_TRANSPXS_Z            (idx, [1:   4]) = [  9.60178E-04 0.00144  2.48424E-02 0.00400 ];
CMM_DIFFCOEF              (idx, [1:   4]) = [  3.45599E+02 0.00149  1.32788E+01 0.00361 ];
CMM_DIFFCOEF_X            (idx, [1:   4]) = [  3.44780E+02 0.00150  1.31989E+01 0.00315 ];
CMM_DIFFCOEF_Y            (idx, [1:   4]) = [  3.44855E+02 0.00155  1.32189E+01 0.00396 ];
CMM_DIFFCOEF_Z            (idx, [1:   4]) = [  3.47161E+02 0.00144  1.34188E+01 0.00401 ];

% Delayed neutron parameters (Meulekamp method):

BETA_EFF                  (idx, [1:  18]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];
LAMBDA                    (idx, [1:  18]) = [  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00  0.00000E+00 0.0E+00 ];

