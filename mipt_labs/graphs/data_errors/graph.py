import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# Определите передаточную функцию
numerator = [1]   # Числитель H(s)
denominator = [1, 10, 100]  # Знаменатель H(s)
system = signal.TransferFunction(numerator, denominator)

# Создаем частоты от 0.1 до 100 (в логарифмической шкале)
frequencies = np.logspace(-2, 2, 500)

# Вычисляем амплитуду и фазу
w, mag, phase = signal.bode(system, frequencies)

# Построение графика АЧХ
plt.figure()
plt.semilogx(w, mag)  # Логарифмическая шкала по оси X
plt.title('Amplitude Bode Plot')
plt.xlabel('Frequency [rad/s]')
plt.ylabel('Magnitude [dB]')
plt.grid(True)

# Построение графика ФЧХ
plt.figure()
plt.semilogx(w, phase)  # Логарифмическая шкала по оси X
plt.title('Phase Bode Plot')
plt.xlabel('Frequency [rad/s]')
plt.ylabel('Phase [degrees]')
plt.grid(True)

plt.show()