import numpy as np
import matplotlib.pyplot as plt

measurements = np.loadtxt('data.txt')

plt.plot(measurements)
plt.xlabel('Номер измерения')
plt.ylabel('Показания АЦП')
plt.show()