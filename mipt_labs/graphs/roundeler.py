import numpy as np
import sys

def round_with_uncertainty(value, uncertainty):
    """Округляет число и его погрешность с учетом значащих цифр"""
    order = -int(np.floor(np.log10(abs(uncertainty))))  # Определяем порядок округления по погрешности
    rounded_uncertainty = round(uncertainty, order)  # Округляем погрешность
    rounded_value = round(value, order)  # Округляем число с тем же порядком
    return rounded_value, rounded_uncertainty, order

# Проверяем, передан ли файл с данными
if len(sys.argv) != 2:
    print("Использование: python script.py <файл с данными>")
    sys.exit(1)

filename = sys.argv[1]  # Получаем имя файла

try:
    # Загружаем данные (обработка случая одной строки)
    data = np.loadtxt(filename)

    # Если одна строка — преобразуем в 2D массив
    if data.ndim == 1:
        data = data.reshape(1, -1)

    # Проверяем, что у нас две колонки
    if data.shape[1] != 2:
        raise ValueError("Файл должен содержать две колонки (значение, погрешность)")

    # Обрабатываем и округляем каждую строку
    for value, uncertainty in data:
        rounded_value, rounded_uncertainty, order = round_with_uncertainty(value, uncertainty)

        # Вычисляем порядок числа
        scale_order = -int(np.floor(np.log10(abs(rounded_value))))  # Определяем порядок числа

        # Масштабируем значениe и погрешность в научную форму
        if scale_order != 0:
            latex_value = rounded_value * 10**scale_order
            latex_uncertainty = rounded_uncertainty * 10**scale_order
            print(f"{rounded_value} {rounded_uncertainty}")
            # Форматируем вывод в LaTeX
            print(f"= $\\left( {latex_value:.3f} \\pm {latex_uncertainty:.3f} \\right) \\cdot 10^{{-{scale_order}}}$, \\ $ (\\varepsilon = {rounded_uncertainty / rounded_value * 100:.2f} $\\%)")
        else:
            # Выводим без экспоненты для порядка 0
            print(f"{rounded_value} {rounded_uncertainty}")
            print(f"= $\\left( {rounded_value:.4f} \\pm {rounded_uncertainty:.4f} \\right)$, \\ $(\\varepsilon = {rounded_uncertainty / rounded_value * 100:.2f}$ \\%)")
        print()

except Exception as e:
    print(f"Ошибка при обработке файла: {e}")
    sys.exit(1)
