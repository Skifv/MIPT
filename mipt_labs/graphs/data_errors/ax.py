import numpy as np
import sys
from scipy.optimize import curve_fit

def func(x, a):
    return a * x

filename = sys.argv[1]
data = np.loadtxt(filename)
xdata = data[:, 0]
ydata = data[:, 1]

# Находим коэффициенты прямой по МНК
popt, pcov = curve_fit(func, xdata, ydata)
a = popt[0]
sigma_a = np.sqrt(np.diag(pcov))[0]

# Выводим точные значения коэффициента a и его погрешности
print("Approximated constant a =", a)
print("sigm a =", sigma_a)