import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Параметры эллиптической поляризации
A = 1.0    # Амплитуда по оси x
B = 0.6    # Амплитуда по оси y
phi = -np.pi / 2  # Сдвиг фаз (π/2 для λ/4)

# Временной интервал
t = np.linspace(0, 2*np.pi, 1000)

# Компоненты вектора E
x = A * np.cos(t)
y = B * np.sin(t + phi)

# Создание графиков
plt.figure(figsize=(12, 4))

# 1. Эллипс поляризации
plt.subplot(1, 2, 1)
plt.plot(x, y, color='blue')
plt.title('Эллипс поляризации\n(Сдвиг фаз = π/2)')
plt.xlabel('$E_x$')
plt.ylabel('$E_y$')
plt.grid(True)
plt.axis('equal')

# 2. Синусоиды компонент
plt.subplot(1, 2, 2)
plt.plot(t, x, label='$E_x(t) = A \cos(t)$', color='red')
plt.plot(t, y, label='$E_y(t) = B \sin(t + \pi/2)$', color='green')
plt.title('Компоненты вектора $E$')
plt.xlabel('Время')
plt.ylabel('Амплитуда')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# 3. Направление вращения (цветовая карта)
plt.figure()
colors = np.linspace(0, 1, len(t))
plt.scatter(x, y, c=colors, cmap='viridis', s=5)
plt.colorbar(label='Время')
plt.title('Направление вращения вектора $E$\n(По часовой стрелке)')
plt.xlabel('$E_x$')
plt.ylabel('$E_y$')
plt.grid(True)
plt.axis('equal')
plt.show()