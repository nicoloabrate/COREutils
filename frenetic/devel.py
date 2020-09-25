import sys
sys.path.append("C:\\Users\\39346\\Documenti\\mycodes")

import numpy as np
import time as t
import numpy as np
import matplotlib as mpl
import rom.reduction.POD as pod
import rom.interpolation.RBF as rbf
import coreutils.frenetic.ParseFrenOut as fren
from numpy.linalg import norm, cond

mpl.rcParams['figure.dpi']= 100  # set dpi for plots

tbegend = [(2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9),
           (3, 11), (4, 11), (5, 11), (6, 11),
           (7, 11), (8, 11), (5, 10), (2, 11)]  # , (2, 11)

dz1 = 17  # [cm]
dz2 = 17  # [cm]

# -- PARSING SNAPSHOT
rho = []
powtot = []
time = []
for idt, (t1, t2) in enumerate(tbegend):
    path = "G:\\Il mio Drive\\ricerca\\conferenze\\m&c2021\\FRENETIC\\CR_eject\\ref_case_%ds_%ds\\neutronic" % (t1, t2)
    file = fren(path)
    rho.append(file.get(path, 'reactivityn'))
    powtot.append(file.get(path, 'power tot.'))
    # define unionized time grid
    time = np.concatenate((time, rho[idt][:, 0]))
    time = np.unique(time)

ntim = len(time)
nsnap = len(rho)
reactivity = np.empty((ntim, nsnap))
power = np.empty((ntim, nsnap))

# interpolate over unionized time grid
for idt in range(0, nsnap):
    reactivity[:, idt] = 1e5*np.interp(time, rho[idt][:, 0], rho[idt][:, 1])
    power[:, idt] = 1e-6*np.interp(time, powtot[idt][:, 0], powtot[idt][:, 1])

#file.plot1D(reactivity, 'reactivityn', xlabel='time [s]', zt=time)
#file.plot1D(power, 'power tot.', xlabel='time [s]', zt=time)

# --- REDUCTION
snapshots = np.concatenate((reactivity, power))

tbegend = np.array(tbegend).T
# param = np.empty((4,nsnap))
param = np.empty((2,nsnap))
param[0, :] = dz1/tbegend[0, :]
param[1, :] = dz2/(tbegend[1, :]-tbegend[0, :])
# param[2, :] = tbegend[0, :]
# param[3, :] = tbegend[1, :]

print(param)

trunc_err = 1e-12  # POD truncation error
PODB = pod(snapshots, trunc_err)
psi = PODB.basis

# compute coefficient matrix
A = PODB.coeffs
Yt = np.dot(psi, A)  # truncated snapshot matrix

# --- TRAINING
rbftype = "Gaussian"  # you can try "HardyInvMultiQuadr" as well
smoothFactor = 2
# build RBF class instance
RBFM = rbf(snapshots, PODB.basis, rbftype, smoothFactor, param)

print("RBF training matrix condition number=", '{:2.1e}'.format(RBFM.condB))
print("The fill distance is ", '{:2.1e}'.format(RBFM.fillingdist))

# test metamodel on centers
RBFM.testcenters(PODB.basis, snapshots, param)
errmax, maxindex = max(RBFM.err), np.argmax(RBFM.err)
errmin, minindex = min(RBFM.err), np.argmin(RBFM.err)
print("The maximum error on the centers is %2.1e for velocities %1.3f cm/s and %1.3f cm/s." %(errmax, param[0,maxindex], param[1,maxindex]))
print("The minimum error on the centers is %2.1e for velocities %1.3f cm/s and %1.3f cm/s." %(errmin, param[0,minindex], param[1,maxindex]))

# check interpolation over center
iP = maxindex  # training point where error is maximum
P1 = param[:,iP]

# print minimum distance from RBF net
d1 = rbf.EuclDistMatrix(param, P1)
print("The minimum distance for maximum error case is ", '{:2.1e}'.format(min(d1)))

# interpolate over point 1
start_time = t.time()
Y1 = RBFM.interpolate(psi, param, P1)
errY1 = norm(Y1-snapshots[:, iP])/norm(snapshots[:, iP])
print("Elapsed time %f s." % (t.time() - start_time))
print("The ROM relative error for case %d is %2.1e" % (iP, errY1))

# --- INTERPOLATION
t1, t2 = 3, 10
v1, v2 = dz1/t1, dz2/(t2-t1)
# P1 = np.array([v1, v2, t1, t2])
P1 = np.array([v1, v2])
path = "G:\\Il mio Drive\\ricerca\\conferenze\\m&c2021\\FRENETIC\\CR_eject\\ref_case_%ds_%ds\\neutronic" % (t1, t2)
file = fren(path)
rhoU = file.get(path, 'reactivityn')
powU = file.get(path, 'power tot.')
rhoU = 1e5*np.interp(time, rhoU[:, 0], rhoU[:, 1])
powU = 1e-6*np.interp(time, powU[:, 0], powU[:, 1])
Yref = np.concatenate((rhoU, powU))
# print minimum distance from RBF net
d1 = rbf.EuclDistMatrix(param, P1)
print("The minimum distance for maximum error case is ", '{:2.1e}'.format(min(d1)))

# interpolate over point 1
start_time = t.time()
Y1 = RBFM.interpolate(psi, param, P1)
errY1 = norm(Y1-Yref)/norm(Yref)
print("Elapsed time %f s." % (t.time() - start_time))
print("The ROM relative error for case (v1=%f, v2=%f) is %2.1e" % (v1, v2, errY1))

# -- VISUALIZATION
rhorom = np.empty((ntim, 2))
powrom = np.empty((ntim, 2))
rhorom[:,0] = Y1[0:ntim]
powrom[:,0] = Y1[ntim::]
rhorom[:,1] = rhoU
powrom[:,1] = powU

file.plot1D(rhorom, 'reactivityn', xlabel='time [s]', ylabel='reactivity [pcm]', zt=time, leglabels=['P-NIROM', 'FRENETIC'], figname="rho.png")
file.plot1D(powrom, 'power tot.', xlabel='time [s]', ylabel='Total power [MW]', zt=time, leglabels=['P-NIROM', 'FRENETIC'], figname="pow.png")
