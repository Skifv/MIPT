import numpy as np
import sys

def dms_to_radians(deg, min, sec):
    return (deg + min / 60 + sec / 3600) * np.pi / 180

def dms_to_degrees(deg, min, sec):
    return deg + min / 60 + sec / 3600

# Проверяем, передан ли файл с данными
if len(sys.argv) != 2:
    print("Использование: python script.py <файл с данными>")
    sys.exit(1)

filename = sys.argv[1]

try:
    data = np.loadtxt(filename)

    if data.ndim == 1:
        data = data.reshape(1, -1)

    if data.shape[1] != 6:
        raise ValueError("Файл должен содержать шесть колонок (градусы, минуты, секунды + их погрешности)")

    for row in data:
        deg, min, sec, err_deg, err_min, err_sec = row

        radians = dms_to_radians(deg, min, sec)
        degrees = dms_to_degrees(deg, min, sec)

        rad_error = dms_to_radians(err_deg, err_min, err_sec)
        deg_error = dms_to_degrees(err_deg, err_min, err_sec)

        print(f"{radians:.6f} рад")
        print(f"{degrees:.6f} °")
        print(f"{rad_error:.6f} рад (погрешность)")
        print(f"{deg_error:.6f} ° (погрешность)\n")

except Exception as e:
    print(f"Ошибка при обработке файла: {e}")
    sys.exit(1)
