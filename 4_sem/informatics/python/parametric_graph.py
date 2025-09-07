import numpy as np
import matplotlib.pyplot as plt

# Определяем параметрические уравнения
def parametric_curve(t, C1, C2):
    x = (C1 + C2) * np.exp(t) + C2 * t * np.exp(t) 
    y = C1 * np.exp(t) + C2 * t * np.exp(t)
    return x, y

# Задаем диапазон параметра t
t = np.linspace(0, 0.01, 300)

# Определяем диапазоны изменения констант
C1_values = np.linspace(1, 3, 1)  # 5 значений от 1 до 3
C2_values = np.linspace(1, 3, 3)  # 5 значений от 1 до 3

# Создаем график
plt.figure(figsize=(8, 8))

# Перебираем комбинации констант
for C1 in C1_values:
    for C2 in C2_values:
        x, y = parametric_curve(t, C1, C2)
        plt.plot(x, y, label=f"C1={C1:.1f}, C2={C2:.1f}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Параметрические кривые при разных C1, C2")
plt.legend()
plt.axis("equal")
plt.grid()
plt.show()
