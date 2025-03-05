import numpy as np
import sys
from scipy.optimize import curve_fit

def func(x, a):
    return a * x

filename = sys.argv[1]
data = np.loadtxt(filename)
xdata = data[:, 0]
ydata = data[:, 1]
yerror = data[:, 2]

popt, pcov = curve_fit(func, xdata, ydata, sigma=yerror)

sigma_a = np.sqrt(np.diag(pcov))

print("Approximated constant a =", popt[0])
print("sigm a =", sigma_a[0])

