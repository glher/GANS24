# Complex very-fast implementation

import numba as nb
import numpy as np
import warnings

warnings.filterwarnings("ignore", message="The TBB threading layer requires TBB version")

# Numerical results may diverge if the input contains big values with many small ones.
# Does not support inputs containing NaN values or +/- Inf ones.
@nb.njit('float64[:,::1](float64[:,::1], int_)', parallel=True, fastmath=True)
def horizontalRollingSum(sample, filterSize):
    n, m = sample.shape
    fs = filterSize

    # Make the wrapping part of the rolling sum much simpler
    assert fs >= 1
    assert n >= fs and m >= fs

    # Horizontal rolling sum.
    tmp = np.empty((n, m), dtype=np.float64)
    for i in nb.prange(n):
        s = 0.0
        lShift = fs//2
        rShift = (fs-1)//2
        for j in range(m-lShift, m):
            s += sample[i, j]
        for j in range(0, rShift+1):
            s += sample[i, j]
        tmp[i, 0] = s
        for j in range(1, m):
            jLeft, jRight = (j-1-lShift) % m, (j+rShift) % m
            s += sample[i, jRight] - sample[i, jLeft]
            tmp[i, j] = s

    return tmp


@nb.njit('float64[:,::1](float64[:,::1], int_)', fastmath=True)
def verticaltalRollingSum(sample, filterSize):
    n, m = sample.shape
    fs = filterSize

    # Make the wrapping part of the rolling sum much simpler
    assert fs >= 1
    assert n >= fs and m >= fs

    # Horizontal rolling sum.
    tmp = np.empty((n, m), dtype=np.float64)
    tShift = fs//2
    bShift = (fs-1)//2
    for j in range(m):
        tmp[0, j] = 0.0
    for i in range(n-tShift, n):
        for j in range(m):
            tmp[0, j] += sample[i, j]
    for i in range(0, bShift+1):
        for j in range(m):
            tmp[0, j] += sample[i, j]
    for i in range(1, n):
        iTop = (i-1-tShift) % n
        iBot = (i+bShift) % n
        for j in range(m):
            tmp[i, j] = tmp[i-1, j] + (sample[iBot, j] - sample[iTop, j])

    return tmp


@nb.njit('float64[:,::1](float64[:,::1], int_)', fastmath=True)
def compute_nomask(sample, filterSize):
    n, m = sample.shape
    tmp = horizontalRollingSum(sample, filterSize)
    neighbors_sum = verticaltalRollingSum(tmp, filterSize)

    return neighbors_sum


@nb.njit('float64[:,::1](float64[:,::1], int_[:,::1], int_)', parallel=True, fastmath=True)
def compute(sample, mask, filterSize):
    n, m = sample.shape
    tmp = horizontalRollingSum(sample, filterSize)
    neighbors_sum = verticaltalRollingSum(tmp, filterSize)
    res = np.empty((n, m), dtype=np.float64)

    for i in nb.prange(n):
        for j in range(n):
            res[i, j] = neighbors_sum[i, j] * mask[i, j]

    return res
