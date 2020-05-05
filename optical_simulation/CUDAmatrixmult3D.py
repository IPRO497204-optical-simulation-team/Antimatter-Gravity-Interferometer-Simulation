from __future__ import division

import math
import time

import matplotlib.pyplot as plt
import numpy as np
from numba import cuda

start = time.time()

# Define wavelength
wl = 0.56  # nm
k = 2 * np.pi / wl

# slitwidth, num of slits
sw = 0.2
nslits = 100
gratingsize = 2000

# Define positions of point sources on each grating.
# Write a function to do this given grating parameters in the future
# y0 = np.empty((1),dtype=np.float32)
y0 = np.array(np.linspace(-0.1, 0.1, 2000), dtype=np.float32)
y1 = np.array(np.append(np.linspace(-0.2, -0.1, 200), np.linspace(0.1, 0.2, 200)), dtype=np.float32)
y2 = np.array(np.append(np.linspace(-0.2, -0.1, 200), np.linspace(0.1, 0.2, 200)), dtype=np.float32)
y3 = np.array(np.append(np.linspace(-0.2, -0.1, 200), np.linspace(0.1, 0.2, 200)), dtype=np.float32)
y4 = np.linspace(-5, 5, 1000)
y = [y0, y1, y2, y3, y4]

# List of distances between each grating (dimension: dim(y)-1)
# 4.5cm

d = [3, 3, 3, 5]

# List of vectors that hold amplitude at each point source
U = [np.zeros((len(yi), 2)) for yi in y]

# U is size [5][1000][2]

for i in range(len(U)):
    for j in range(len(U[i])):
        U[i][j][0] = 1.0 / len(U[i])  # U is amplitude

# Define transfer matrices from each grating to the next
M = [np.ones((len(y[i + 1]), len(y[i]), 2)) for i in range(0, len(y) - 1)]


# For each transfer matrix
# for n in range(0,len(M)):
# For each row
#	for i in range(0,M[n].shape[0]):
# For each column
#		for j in range(0,M[n].shape[1]):
#			rij=np.sqrt((y[n+1][i]-y[n][j])**2 + d[n]**2)
#			M[n][i][j]=(np.exp(1j*k*rij))/(k*rij)

# CUDA kernel to fill matrices
@cuda.jit
def calcM(M, dn, yn, yn1):
    i, j = cuda.grid(2)
    if i < M.shape[0] and j < M.shape[1]:
        rij = math.sqrt((yn1[i] - yn[j]) * (yn1[i] - yn[j]) + dn * dn)
        M[i][j][0] = (math.cos(k * rij)) / (k * rij)
        M[i][j][1] = (math.sin(k * rij)) / (k * rij)


for n in range(0, len(M)):
    Mn_glob_mem = cuda.to_device(M[n])
    yn_glob_mem = cuda.to_device(y[n])
    yn1_glob_mem = cuda.to_device(y[n + 1])
    threadsperblock = (16, 16)
    blockspergrid_x = int(math.ceil(M[n].shape[0] / threadsperblock[0]))
    blockspergrid_y = int(math.ceil(M[n].shape[1] / threadsperblock[1]))
    blockspergrid = (blockspergrid_x, blockspergrid_y)
    calcM[blockspergrid, threadsperblock](Mn_glob_mem, d[n], yn_glob_mem, yn1_glob_mem)
    M[n] = Mn_glob_mem.copy_to_host()
print(len(M))


# CUDA kernel to matmul
@cuda.jit
def matmul(A, B, C):
    row = cuda.grid(1)
    if row < C.shape[0]:
        tmp0 = 0.
        tmp1 = 0.
        for k in range(A.shape[1]):
            tmp0 += (A[row, k][0] * B[k][0]) - (A[row, k][1] * B[k][1])
            tmp1 += A[row, k][0] * B[k][1] + A[row, k][1] * B[k][0]
        C[row][0] = tmp0
        C[row][1] = tmp1


for n in range(0, len(M)):
    Mn_global_mem = cuda.to_device(M[n])
    Un_global_mem = cuda.to_device(U[n])
    Un1_global_mem = cuda.device_array_like(U[n + 1])
    threadsperblock = (256)
    blockspergrid_x = int(math.ceil(M[n].shape[0] / threadsperblock))
    blockspergrid = (blockspergrid_x)
    matmul[blockspergrid, threadsperblock](Mn_global_mem, Un_global_mem, Un1_global_mem)
    U[n + 1] = Un1_global_mem.copy_to_host()
# U[n+1]=np.matmul(M[n],U[n])

I = []

for u in U[-1]:
    I.append(u[0] + u[1])

print(time.time() - start)
plt.title("Normalized Intensity")
plt.plot(y[-1], I, 0 + 1)
# plt.plot(I)
plt.show()
