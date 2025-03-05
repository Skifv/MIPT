import numpy as np
import sys 
from scipy.optimize import curve_fit
import math

def random_error(arr):

    n = len(arr)
    mean_value = sum(arr) / n
    
    sum_of_squared_deviations = sum((x - mean_value) ** 2 for x in arr)
    variance = sum_of_squared_deviations / (n * (n-1))
    random_error = math.sqrt(variance)
    
    return random_error, mean_value

filename = sys.argv[1]
data = np.loadtxt(filename)
xdata = data
sigma, avarage = random_error(xdata)

print("avarage =", avarage)
print("sigma =", sigma)
