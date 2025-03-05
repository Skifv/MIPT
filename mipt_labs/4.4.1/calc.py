import xlsxwriter


# Исходные данные: углы в формате (градусы, минуты, секунды)
angles_dms = [
    (12, 41, 9),
    (14, 21, 24),
    (11, 44, 25),
    (15, 57, 55),
    (16, 56, 55),
    (16, 57, 35),
    (18, 19, 5)
]

# Погрешность прибора в угловых секундах
error_seconds = 5
error_radians = np.deg2rad(error_seconds / 3600)  # Переводим погрешность в радианы

# Функция для перевода градусов, минут, секунд в радианы
def dms_to_radians(d, m, s):
    degrees = d + m / 60 + s / 3600
    return np.deg2rad(degrees)

# Вычисление значений
angles_radians = [dms_to_radians(d, m, s) for d, m, s in angles_dms]
sin_values = [np.sin(angle) for angle in angles_radians]
sin_errors = [np.cos(angle) * error_radians for angle in angles_radians]

# Создание xlsx-файла
file_path = "/mnt/data/angles_calculations.xlsx"
workbook = xlsxwriter.Workbook(file_path)
worksheet = workbook.add_worksheet()

# Заголовки таблицы
headers = ["Угол (град, мин, сек)", "Угол (рад)", "Погрешность угла (рад)", "sin(α)", "Погрешность sin(α)"]
for col, header in enumerate(headers):
    worksheet.write(0, col, header)

# Заполнение таблицы
for row, ((d, m, s), rad, sin_val, sin_err) in enumerate(zip(angles_dms, angles_radians, sin_values, sin_errors), start=1):
    worksheet.write(row, 0, f"{d}°{m}'{s}\"")
    worksheet.write(row, 1, rad)
    worksheet.write(row, 2, error_radians)
    worksheet.write(row, 3, sin_val)
    worksheet.write(row, 4, sin_err)

# Сохранение файла
workbook.close()

# Вывод пути к файлу
file_path
