from typing import Callable, Literal
import numpy as np

# Определяем типы методов для автодополнения в IDE
DiffMethod = Literal[
    "forward",
    "backward",
    "central_o2",
    "central_o4",
    "central_o6",
]


def _forward_diff(f: Callable[[float], float], x: float, h: float) -> float:
    """
    Формула прямого численного дифференцирования.
    Порядок точности: O(h).
    """
    return (f(x + h) - f(x)) / h


def _backward_diff(f: Callable[[float], float], x: float, h: float) -> float:
    """
    Формула обратного численного дифференцирования.
    Порядок точности: O(h).
    """
    return (f(x) - f(x - h)) / h


def _central_diff_o2(f: Callable[[float], float], x: float, h: float) -> float:
    """
    Центральная разностная формула 2-го порядка точности.
    Порядок точности: O(h^2).
    """
    return (f(x + h) - f(x - h)) / (2 * h)


def _central_diff_o4(f: Callable[[float], float], x: float, h: float) -> float:
    """
    Центральная разностная формула 4-го порядка точности.
    Порядок точности: O(h^4).
    """
    term1 = (4 / 3) * (f(x + h) - f(x - h)) / (2 * h)
    term2 = (1 / 3) * (f(x + 2 * h) - f(x - 2 * h)) / (4 * h)
    return term1 - term2


def _central_diff_o6(f: Callable[[float], float], x: float, h: float) -> float:
    """
    Центральная разностная формула 6-го порядка точности.
    Порядок точности: O(h^6).
    """
    term1 = (3 / 2) * (f(x + h) - f(x - h)) / (2 * h)
    term2 = (3 / 5) * (f(x + 2 * h) - f(x - 2 * h)) / (4 * h)
    term3 = (1 / 10) * (f(x + 3 * h) - f(x - 3 * h)) / (6 * h)
    return term1 - term2 + term3


# Словарь, который сопоставляет название метода с соответствующей функцией
_METHODS = {
    "forward": _forward_diff,
    "backward": _backward_diff,
    "central_o2": _central_diff_o2,  # O(h^2)
    "central_o4": _central_diff_o4,  # O(h^4)
    "central_o6": _central_diff_o6,  # O(h^6)
}


def derivative(
    f: Callable[[float], float],
    x: float,
    *,
    h: float = 1e-5,
    method: DiffMethod = "central_o4",
) -> float:
    """
    Вычисляет численную производную функции f в точке x.

    Args:
        f (Callable[[float], float]): Функция для дифференцирования, принимающая один float и возвращающая float.
        x (float): Точка, в которой вычисляется производная.
        h (float, optional): Шаг дифференцирования. По умолчанию 1e-5.
        method (str, optional): Метод численного дифференцирования.
            Доступные методы:
            - 'forward': Прямая разность (O(h))
            - 'backward': Обратная разность (O(h))
            - 'central_o2': Центральная разность (O(h^2))
            - 'central_o4': Центральная разность (O(h^4)) - по умолчанию
            - 'central_o6': Центральная разность (O(h^6))
            По умолчанию 'central_o4'.

    Returns:
        float: Значение производной функции f в точке x.

    Raises:
        ValueError: Если указан неизвестный метод.
    """
    if method not in _METHODS:
        raise ValueError(
            f"Неизвестный метод '{method}'. Доступные методы: {list(_METHODS.keys())}"
        )

    diff_func = _METHODS[method]
    return diff_func(f, x, h)


def jacobian(
    f: Callable[[np.ndarray], np.ndarray],
    x: np.ndarray,
    h: float = 5e-6,
) -> np.ndarray:
    """
    Вычисляет матрицу Якоби функции с помощью центральных конечных разностей.

    Каждый столбец Якобиана соответствует частным производным выходов функции
    по одной из входных переменных, аппроксимируемым по формуле:
        J[:, j] ≈ (f(x + h·e_j) - f(x - h·e_j)) / (2h)

    Parameters
    ----------
    f : Callable[[np.ndarray], np.ndarray]
        Векторная функция f(x): ℝⁿ → ℝᵐ, возвращающая массив формы (m,).
    x : np.ndarray
        Точка, в которой вычисляется Якобиан, форма (n,).
    h : float, optional
        Шаг конечной разности (по умолчанию 1e-6).

    Returns
    -------
    J : np.ndarray
        Якобиан функции f в точке x, форма (m, n).

    Notes
    -----
    Используется **центральная разностная аппроксимация**, обеспечивающая
    порядок точности O(h²). Подходит для гладких функций.
    """

    n = x.size  # Число входных переменных

    f_x_base = f(x)
    m = f_x_base.size  # Число выходных компонент функции

    E = np.eye(n, dtype=x.dtype)  # Единичная матрица для построения базисных векторов e_j

    J = np.empty((m, n), dtype=x.dtype)  # Результирующая матрица Якобиана

    for j in range(n):
        e_j = E[:, j]  # Единичный вектор вдоль оси j

        # Формирование точек для центральной разности
        x_plus = x + h * e_j
        x_minus = x - h * e_j

        # Вычисление значений функции в точках x_plus и x_minus
        F_plus = f(x_plus)
        F_minus = f(x_minus)

        # Численное приближение производной по j-й переменной
        J[:, j] = (F_plus - F_minus) / (2 * h)

    return J
