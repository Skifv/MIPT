import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import sys

# Функция линейной аппроксимации y = ax
def func(x, a):
    return a * x

# Загружаем данные из файла
filename = sys.argv[1]  # Получаем имя файла как аргумент
data = np.loadtxt(filename, skiprows=2)  # Пропускаем первые три строки (тип погрешности и значения)

# Загружаем параметры погрешности
with open(filename, 'r') as file:
    error_type = file.readline().strip()  # Чтение типа погрешности (percent или absolute)
    error_values = file.readline().strip().split()  # Чтение двух значений погрешности для X и Y

# Если в файле не указаны два значения погрешности, выбрасываем ошибку
if len(error_values) != 2:
    raise ValueError("File must contain exactly two error values: one for X and one for Y.")

# Преобразуем значения погрешности в числа
error_x = float(error_values[0])  # Погрешность по X
error_y = float(error_values[1])  # Погрешность по Y

xdata = data[:, 0]
ydata = data[:, 1]

# Если погрешности в процентах
if error_type == 'percent':
    xerr = error_x * xdata  # Погрешность по X в процентах
    yerr = error_y * ydata  # Погрешность по Y в процентах
# Если погрешности в абсолютных значениях
elif error_type == 'absolute':
    xerr = np.full_like(xdata, error_x)  # Погрешность по X в абсолютных значениях
    yerr = np.full_like(ydata, error_y)  # Погрешность по Y в абсолютных значениях
else:
    raise ValueError("Invalid error type specified in the file. It should be either 'percent' or 'absolute'.")

# Находим коэффициенты прямой по МНК
popt, pcov = curve_fit(func, xdata, ydata)
a = popt[0]
sigma_a = np.sqrt(np.diag(pcov))[0]

# Выводим точные значения коэффициента a и его погрешности
print("Approximated constant a =", a)
print("sigm a =", sigma_a)

# Функция для округления с учетом погрешности
def round_with_uncertainty(value, uncertainty):
    order = -int(np.floor(np.log10(uncertainty)))  # Определяем порядок округления
    rounded_value = round(value, order)
    rounded_uncertainty = round(uncertainty, order)
    return rounded_value, rounded_uncertainty

# Округляем коэффициенты
a_rounded, sigma_a_rounded = round_with_uncertainty(a, sigma_a)

# Выводим округленные значения в таком же формате
print("Approximated constant a =", a_rounded)
print("sigm a =", sigma_a_rounded)

# Определяем границы построения
x_min = 0
x_max = max(xdata)

# Генерируем точки для линии тренда
x_fit = np.linspace(x_min, x_max, 100)
y_fit = func(x_fit, a)

# Строим график с крестами погрешностей
plt.figure(figsize=(8, 6))
plt.errorbar(xdata, ydata, xerr=xerr, yerr=yerr, fmt='o', color="blue", label="Исходные данные")
plt.plot(x_fit, y_fit, 'r-', label=f"МНК: y = ({a_rounded} ± {sigma_a_rounded})x")

# Оформление графика
plt.xlabel("λ, нм")
plt.ylabel("sin(α)")
plt.legend()
plt.grid(True)

# Показываем график
plt.show()
