import numpy as np
import matplotlib.pyplot as plt

# Параметры RLC контура
R = 2000      # Сопротивление, Ом
L = 0.10011   # Индуктивность, Гн
C = 6e-9      # Емкость, Ф

# Диапазон частот
frequencies = np.linspace(10, 50000, 1000)  # от 10 Гц до 1 МГц
omega = 2 * np.pi * frequencies  # переводим частоты в угловые частоты

# Вычисление АЧХ
amplitude_response = 1 / (np.sqrt((1 / (omega * C))**2 + (omega * L - 1 / (omega * C))**2))

# Построение графика
plt.figure(figsize=(10, 6))
plt.plot(frequencies, amplitude_response, color='red', label='АЧХ')
plt.xlabel("Частота (Гц)")
plt.ylabel("Амплитуда")
plt.title("Амплитудно-частотная характеристика (АЧХ) последовательного RLC контура")
plt.grid()
plt.legend()
plt.show()
