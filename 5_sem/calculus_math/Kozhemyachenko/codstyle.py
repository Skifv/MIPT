from typing import Callable, Tuple, List
import numpy as np
from dataclasses import dataclass
import warnings


@dataclass
class NonlinearRootResult:
    root: np.ndarray
    iterations: int
    converged: bool
    diff_norm_history: List[float]


def solve_bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    xtol: float = 2e-12,
    rtol: float = np.finfo(np.float64).eps * 4,  # ~8.88e-16
    maxiter: int = 100,
    full_output: bool = False
) -> Tuple[float, int]:
    """
    Находит корень уравнения f(x)=0 методом половинного деления (бисекции).

    Метод требует, чтобы на границах начального отрезка [a, b] значения
    функции f(a) и f(b) имели разные знаки.

    Parameters
    ----------
    f : Callable[[float], float]
        Функция одного переменного, корень которой ищется.
    a, b : float
        Граничные точки интервала [a, b]. Важно, чтобы f(a) и f(b)
        имели разные знаки.
    xtol : float, optional
        Абсолютная погрешность для критерия остановки.
    rtol : float, optional
        Относительная погрешность для критерия остановки.
        Значение по умолчанию - 4 * машинный эпсилон для float64.
    maxiter : int, optional
        Максимальное количество итераций.
    full_output : bool, optional
        Если False (по умолчанию), возвращается только корень.
        Если True, возвращается объект NonlinearRootResult с полной информацией.

    Returns
    -------
    root : float
        Возвращается, если `full_output=False`.
        - `float` : Найденное приближение к корню.

    result : NonlinearRootResult
        Возвращается, если `full_output=True`. Объект содержит поля:
        - `root` (float): Найденное приближение к корню.
        - `iterations` (int): Количество выполненных итераций.
        - `converged` (bool): True, если метод сошелся.
        - `diff_norm_history` (List[float]): История абсолютных значений
          функции в средней точке |f(c)| на каждой итерации.

    Notes
    -----
    Метод гарантированно сходится, если на концах отрезка [a, b] функция
    имеет разные знаки. На каждой итерации вычисляется середина c = (a + b) / 2,
    и выбирается та половина отрезка, на концах которой знаки функции
    по-прежнему различны.

    Процесс останавливается, когда половина длины текущего отрезка
    (b - a) / 2 становится меньше `xtol + rtol * abs(c)`.
    """
    # --- Этап 1: Инициализация и проверки ---
    if b <= a:
        raise ValueError("Верхняя граница 'b' должна быть больше нижней 'a'.")

    f_a = f(a)
    f_b = f(b)

    if full_output:
        result = NonlinearRootResult(
            root=None, iterations=0, converged=False, diff_norm_history=[]
        )

    # Главное условие применимости метода
    if f_a * f_b > 0:
        raise ValueError("Метод не применим: f(a) и f(b) должны иметь разные знаки.")
    # Проверка, не является ли одна из границ уже корнем
    elif np.isclose(f_a, 0):
        if full_output:
            result.root = a
            result.converged = True
            return result
        else:
            return a

    elif np.isclose(f_b, 0):
        if full_output:
            result.root = b
            result.converged = True
            return result
        else:
            return b

    # --- Этап 2: Основной итерационный цикл ---
    for iter_counter in range(1, maxiter + 1):

        c = (a + b) / 2

        # Половина длины отрезка - это текущая абсолютная погрешность
        section_len = (b - a) / 2

        # Смешанный (абсолютный + относительный) критерий остановки
        if section_len <= xtol + rtol * np.abs(c):
            if full_output:
                result.root = c
                result.converged = True
                result.iterations = iter_counter
                return result
            else:
                return c

        f_c = f(c)

        if full_output:
            result.diff_norm_history.append(np.abs(f(c)))

        # Выбираем новую половину отрезка
        if f_a * f_c < 0:
            b = c
            f_b = f_c
        elif f_c * f_b < 0:
            a = c
            f_a = f_c
        else:
            # Это происходит, если f(c) == 0, т.е. корень найден точно
            if full_output:
                result.root = c
                result.converged = True
                result.iterations = iter_counter
                return result
            else:
                return c

    # --- Этап 3: Обработка случая, если сходимость не достигнута ---
    warnings.warn(f"Сходимость не достигнута за {maxiter} итераций.", RuntimeWarning)

    if full_output:
        result.root = c
        result.iterations = maxiter
        result.converged = False
        return result

    return c
