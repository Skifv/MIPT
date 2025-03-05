import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Функция линейной аппроксимации
def func(x, a, b):
    return a * x + b

# Загружаем данные из файла
filename = "data.txt"  # Укажи свой файл
data = np.loadtxt(filename, skiprows=2)  # Пропускаем первые две строки (погрешности)

# Загружаем параметры погрешности
with open(filename, 'r') as file:
    error_type = file.readline().strip()  # Чтение типа погрешности (percent или absolute)
    error_values = file.readline().strip().split()  # Чтение двух значений погрешности (для X и Y)

# Если тип погрешности не указан, то ничего не делаем
if error_values[0] == '':
    error_type = None

# Преобразуем значения погрешности в числа, если они есть
if error_values:
    error_x = float(error_values[0])  # Погрешность по X
    error_y = float(error_values[1])  # Погрешность по Y

xdata = data[:, 0]
ydata = data[:, 1]

# Если погрешности в процентах
if error_type == 'percent' and error_values:
    xerr = error_x * xdata  # Погрешность по X в процентах
    yerr = error_y * ydata  # Погрешность по Y в процентах
# Если погрешности в абсолютных значениях
elif error_type == 'absolute' and error_values:
    xerr = np.full_like(xdata, error_x)  # Погрешность по X в абсолютных значениях
    yerr = np.full_like(ydata, error_y)  # Погрешность по Y в абсолютных значениях
else:
    xerr = yerr = None  # Если погрешности не заданы, то кресты не рисуем

# Находим коэффициенты прямой по МНК
popt, pcov = curve_fit(func, xdata, ydata)
a, b = popt
sigma_a, sigma_b = np.sqrt(np.diag(pcov))

# Выводим точные значения коэффициентов и их погрешностей
print("Approximated constant a =", a)
print("Approximated constant b =", b)
print("sigm a =", sigma_a)
print("sigm b =", sigma_b)

# Функция для округления с учетом погрешности
def round_with_uncertainty(value, uncertainty):
    order = -int(np.floor(np.log10(uncertainty)))  # Определяем порядок округления
    rounded_value = round(value, order)
    rounded_uncertainty = round(uncertainty, order)
    return rounded_value, rounded_uncertainty

# Округляем коэффициенты
a_rounded, sigma_a_rounded = round_with_uncertainty(a, sigma_a)
b_rounded, sigma_b_rounded = round_with_uncertainty(b, sigma_b)

# Выводим округленные значения в таком же формате
print("Approximated constant a =", a_rounded)
print("Approximated constant b =", b_rounded)
print("sigm a =", sigma_a_rounded)
print("sigm b =", sigma_b_rounded)

# Определяем границы построения
x_min = 0
x_max = max(xdata)

# Генерируем точки для линии тренда
x_fit = np.linspace(x_min, x_max, 100)
y_fit = func(x_fit, a, b)

# Строим график
plt.figure(figsize=(8, 6))

# Если кресты погрешности заданы, то рисуем их на графике
if xerr is not None and yerr is not None:
    plt.errorbar(xdata, ydata, xerr=xerr, yerr=yerr, fmt='o', color="blue", label="Исходные данные")
else:
    plt.scatter(xdata, ydata, color="blue", label="Исходные данные")

plt.plot(x_fit, y_fit, 'r-', label=f"МНК: y = ({a_rounded} ± {sigma_a_rounded})x + ({b_rounded} ± {sigma_b_rounded})")

# Оформление графика
plt.xlabel("X")
plt.ylabel("Y")
plt.legend()
plt.grid(True)

# Показываем график
plt.show()
