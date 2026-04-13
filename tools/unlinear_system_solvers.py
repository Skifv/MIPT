import numpy as np
import sys
from typing import Callable, List, Union, Optional, Callable
from dataclasses import dataclass
import warnings

# import torch
# import torch.optim as optim

sys.path.append("./")

import linear_system_solvers as lss
import derrivates as derr


@dataclass
class NonlinearRootResult:
    root: np.ndarray
    iterations: int
    converged: bool
    x_diff_norm_history: List[float]
    f_norm_history: List[float]


def solve_bisection(
    f: Callable[[float], float],
    a: float,
    b: float,
    xtol: float = 2e-12,
    rtol: float = np.finfo(np.float64).eps * 4,  # ~8.88e-16
    maxiter: int = 100,
    full_output: bool = False,
) -> Union[float, "NonlinearRootResult"]:
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
        - `x_diff_norm_history` (List[float]): История абсолютной погрешности
          по x: половина длины отрезка (b-a)/2 на каждой итерации.
        - `f_norm_history` (List[float]): История нормы невязки |f(c)|.

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
            root=None,
            iterations=0,
            converged=False,
            x_diff_norm_history=[],
            f_norm_history=[],
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

        # Половина длины отрезка - это текущая абсолютная погрешность по x
        section_len = (b - a) / 2

        f_c = f(c)

        if full_output:
            result.x_diff_norm_history.append(section_len)
            result.f_norm_history.append(np.abs(f_c))

        # Смешанный (абсолютный + относительный) критерий остановки
        if section_len <= xtol + rtol * np.abs(c):
            if full_output:
                result.root = c
                result.converged = True
                result.iterations = iter_counter
                return result
            else:
                return c

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
    warnings.warn(
        f"solve_bisection: Сходимость не достигнута за {maxiter} итераций.",
        RuntimeWarning,
    )

    if full_output:
        result.root = c
        result.iterations = maxiter
        result.converged = False
        return result

    return c


def solve_simple_iteration(
    g: Callable[[np.ndarray], np.ndarray],
    x0: np.ndarray,
    atol: float = 1e-8,
    maxiter: int = 100,
    full_output: bool = False,
) -> Union[np.ndarray, "NonlinearRootResult"]:
    """
    Решает систему нелинейных уравнений x = g(x) методом простой итерации.

    Parameters
    ----------
    g : Callable[[np.ndarray], np.ndarray]
        Функция, реализующая правую часть системы, приведенной к виду x = g(x).
        Она должна принимать на вход вектор NumPy и возвращать вектор той же размерности.
    x0 : np.ndarray
        Начальное приближение (вектор). Его размерность определяет размерность системы.
    atol : float, optional
        Абсолютная погрешность для критерия остановки.
        Итерации прекращаются, когда ||f(x_k)|| <= atol.
    maxiter : int, optional
        Максимальное количество итераций.
    full_output : bool, optional
        Если False (по умолчанию), возвращается только вектор-решение.
        Если True, возвращается объект NonlinearRootResult с полной информацией.

    Returns
    -------
    root : np.ndarray
        Возвращается, если `full_output=False`. Представляет собой найденное
        приближение к корню. **Внимание:** при `full_output=False` следует
        проверять сходимость по другим признакам, так как функция вернет
        последнее значение даже если не сошлась.

    result : NonlinearRootResult
        Возвращается, если `full_output=True`. Объект содержит поля:
        - `root` (np.ndarray): Найденное приближение к корню.
        - `iterations` (int): Количество выполненных итераций.
        - `converged` (bool): True, если метод сошелся.
        - `x_diff_norm_history` (List[float]): История евклидовой нормы шага
          ||x_k - x_{k-1}|| на каждой итерации. (Переименовано)
        - `f_norm_history` (List[float]): История нормы невязки ||g(x_k) - x_k||.

    Notes
    -----
    Метод последовательно вычисляет приближения по формуле:
        x^(k+1) = g(x^(k))

    Сходимость метода не гарантирована и сильно зависит от выбора функции g(x).
    Для сходимости необходимо, чтобы отображение g(x) было сжимающим в
    окрестности решения, т.е. норма матрицы Якоби функции g(x) должна
    быть меньше единицы.
    """
    # --- Этап 1: Инициализация ---
    x = np.asarray(x0, dtype=np.float64).copy()

    if full_output:
        result = NonlinearRootResult(
            root=x0,
            iterations=0,
            converged=False,
            x_diff_norm_history=[],
            f_norm_history=[],
        )

    # --- Этап 2: Основной итерационный цикл ---
    for iter_counter in range(1, maxiter + 1):
        x_old = x.copy()

        try:
            x = g(x_old)
        except (ValueError, ZeroDivisionError, OverflowError, RuntimeWarning) as e:
            msg = f"Вычисление g(x) прервалось на итерации {iter_counter}: {e}"
            warnings.warn(msg, RuntimeWarning)

            if full_output:
                result.root = x_old
                result.iterations = iter_counter
                result.converged = False
                return result

            # При full_output=False лучше выбросить ошибку
            raise RuntimeError(msg)

        # 1. Вычисляем норму шага ||x_k - x_{k-1}||
        diff_norm = np.linalg.norm(x - x_old)

        # 2. Вычисляем норму невязки ||f(x_k)|| = ||g(x_k) - x_k||
        f_norm = np.linalg.norm(g(x) - x)

        if full_output:
            # Запись нормы шага
            result.x_diff_norm_history.append(diff_norm)
            # Запись нормы невязки
            result.f_norm_history.append(f_norm)

        # Критерий остановки
        if f_norm <= atol:
            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = True
                return result
            return x

    # --- Этап 3: Обработка случая, если сходимость не достигнута ---
    warnings.warn(
        f"solve_simple_iteration: Сходимость не достигнута за {maxiter} итераций.",
        RuntimeWarning,
    )

    if full_output:
        result.root = x
        result.iterations = maxiter
        result.converged = False
        return result

    return x


def solve_newton(
    f: Callable[[float], float],
    x0: float,
    fprime: Callable[[float], float] = None,
    x0_extra: float = None,
    atol: float = 1e-8,
    maxiter: int = 100,
    full_output: bool = False,
) -> Union[float, "NonlinearRootResult"]:
    """
    Находит корень уравнения f(x)=0 методом Ньютона или методом секущих.

    Если предоставлена производная `fprime`, используется классический метод
    Ньютона. В противном случае используется метод секущих, для которого
    требуется дополнительная начальная точка `x0_extra`.

    Parameters
    ----------
    f : Callable[[float], float]
        Функция одного переменного, корень которой ищется.
    x0 : float
        Начальное приближение к корню.
    fprime : Callable[[float], float], optional
        Производная функции `f`. Если `None` (по умолчанию), для нахождения
        корня будет использован метод секущих.
    x0_extra : float, optional
        Вторая начальная точка, необходимая для метода секущих (когда `fprime`
        не предоставлена).
    atol : float, optional
        Абсолютная погрешность для критерия остановки.
        Итерации прекращаются, когда |f(x_k)| < atol.
    maxiter : int, optional
        Максимальное количество итераций.
    full_output : bool, optional
        Если False (по умолчанию), возвращается только корень.
        Если True, возвращается объект NonlinearRootResult с полной информацией.

    Returns
    -------
    root : float
        Возвращается, если `full_output=False`. Найденное приближение к корню.

    result : NonlinearRootResult
        Возвращается, если `full_output=True`. Объект содержит поля:
        - `root` (float): Найденное приближение к корню.
        - `iterations` (int): Количество выполненных итераций.
        - `converged` (bool): True, если метод сошелся.
        - `x_diff_norm_history` (List[float]): История абсолютных значений
          шага |x_k - x_{k-1}| на каждой итерации.
        - `f_norm_history` (List[float]): История нормы невязки |f(x_k)|.

    Notes
    -----
    Итерационная формула метода Ньютона:
        x_{k+1} = x_k - f(x_k) / f'(x_k)

    Итерационная формула метода секущих:
        x_{k+1} = x_k - f(x_k) * (x_k - x_{k-1}) / (f(x_k) - f(x_{k-1}))

    Сходимость метода не гарантирована и сильно зависит от выбора начального
    приближения `x0` и поведения функции.
    """

    if full_output:
        result = NonlinearRootResult(
            root=x0,
            iterations=0,
            converged=False,
            x_diff_norm_history=[],
            f_norm_history=[],
        )

    x = x0

    # Для метода секущих нужна предыдущая точка для первого шага
    if not callable(fprime):
        if x0_extra is None:
            raise ValueError(
                "Нужно две начальных точки (x0, x0_extra), так как производная fprime не предоставлена."
            )
        # На первой итерации x_old будет x0_extra, а x будет x0
        x_old = x0_extra

    for iter_counter in range(1, maxiter + 1):

        f_val = f(x)

        # 1. Запись нормы невязки |f(x_k)|
        if full_output:
            result.f_norm_history.append(np.abs(f_val))

        try:
            if callable(fprime):
                fp_val = fprime(x)
            else:
                fp_val = (f_val - f(x_old)) / (x - x_old)

            step = f_val / fp_val
        except (ValueError, ZeroDivisionError, OverflowError, RuntimeWarning) as e:
            msg = f"Вычисление шага прервалось на итерации {iter_counter}: {e}"
            warnings.warn(msg, RuntimeWarning)
            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = False
                return result
            raise RuntimeError(msg)

        x_old = x
        x = x_old - step

        step_abs = np.abs(step)

        # 2. Запись нормы шага |x_k - x_{k-1}|
        if full_output:
            result.x_diff_norm_history.append(step_abs)

        # Критерий остановки
        if np.abs(f_val) <= atol:
            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = True
                return result
            else:
                return x

    # --- Этап 3: Обработка случая, если сходимость не достигнута ---
    warnings.warn(
        f"solve_newton: Сходимость не достигнута за {maxiter} итераций.", RuntimeWarning
    )

    if full_output:
        result.root = x
        result.iterations = maxiter
        result.converged = False
        return result

    return x


def solve_newton_multidim(
    f: Callable[[np.ndarray], np.ndarray],
    x0: np.ndarray,
    *,
    jac: Callable[[np.ndarray], np.ndarray] = None,
    atol: float = 1e-8,
    maxiter: int = 1000,
    full_output: bool = False,
) -> Union[np.ndarray, "NonlinearRootResult"]:
    """
    Решает систему нелинейных уравнений f(x) = 0 методом Ньютона.

    Parameters
    ----------
    f : callable
        Вектор-функция, корень которой ищется. Принимает вектор x,
        возвращает вектор f(x).
    x0 : array_like
        Начальное приближение (вектор).
    jac : callable
        Функция, вычисляющая матрицу Якоби (Якобиан) функции f.
        Принимает вектор x, возвращает матрицу J(x). Если `None` (по умолчанию),
        используется численный Якобиан `derr.jacobian(f, x)`.
    atol : float
        Абсолютная погрешность. Итерации прекращаются, если
        ||f(x)|| <= atol.
    maxiter : int
        Максимальное количество итераций.
    full_output : bool, optional
        Если True (по умолчанию False), возвращает объект `NonlinearRootResult`
        со всей информацией об итерациях.
        Если False, возвращает только найденный корень.

    Returns
    -------
    root : np.ndarray
        Найденный корень (если `full_output=False`).
    result : NonlinearRootResult
        Объект с результатами (если `full_output=True`).
        Атрибуты:
        - root (np.ndarray): Найденный корень.
        - iterations (int): Количество выполненных итераций.
        - converged (bool): True, если метод сошелся.
        - x_diff_norm_history (List[float]): История норм шага ||delta_x||.
        - f_norm_history (List[float]): История норм невязки ||f(x)||.

    Raises
    ------
    RuntimeError
        Если вычисление шага (решение СЛАУ) не удалось и
        `full_output=False`.
    """

    # --- Этап 1: Инициализация ---
    if jac is None:
        jac = lambda x: derr.jacobian(f, x)

    x = np.asarray(x0, dtype=np.float64).copy()

    if full_output:
        result = NonlinearRootResult(
            root=x,
            iterations=0,
            converged=False,
            x_diff_norm_history=[],
            f_norm_history=[],
        )

    for iter_counter in range(1, maxiter + 1):

        f_val = f(x)

        # ||f(x_k)||
        f_norm = np.linalg.norm(f_val)

        if not np.isfinite(f_norm):
            msg = f"Newton diverged (NaN/Inf) at iteration {iter_counter}"
            warnings.warn(msg, RuntimeWarning)
            if full_output:
                result.converged = False
                return result
            raise RuntimeError(msg)

        if full_output:
            result.f_norm_history.append(f_norm)

        # --- Этап 2: Проверка сходимости по шагу ---
        # ||f(x_k)|| <= atol
        if f_norm <= atol:
            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = True
                return result
            else:
                return x

        # --- Этап 3: Вычисление шага ---
        jac_val = jac(x)

        try:
            # Решаем СЛАУ: J(x) * delta_x = -f(x)
            delta_x = lss.solve(jac_val, -f_val)
        except (
            ValueError,
            ZeroDivisionError,
            OverflowError,
            RuntimeWarning,
            np.linalg.LinAlgError,
        ) as e:
            # Обработка вырожденной матрицы Якоби или других численных проблем
            msg = f"Вычисление шага прервалось на итерации {iter_counter}: {e}"
            warnings.warn(msg, RuntimeWarning)

            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = False
                return result

            raise RuntimeError(msg)

        # --- Этап 4: Обновление решения ---
        x = x + delta_x

        # 2. Запись нормы шага ||delta_x||
        if full_output:
            result.x_diff_norm_history.append(np.linalg.norm(delta_x))

    # --- Этап 5: Выход ---
    warnings.warn(
        f"solve_newton_multidim: Сходимость не достигнута за {maxiter} итераций.",
        RuntimeWarning,
    )

    if full_output:
        result.root = x
        result.iterations = maxiter
        result.converged = False
        return result
    else:
        return x


def solve_gd(
    f: Callable[[np.ndarray], np.ndarray],
    x0: np.ndarray,
    *,
    jac: Optional[Callable[[np.ndarray], np.ndarray]] = None,
    lr: float = 0.001,
    atol: float = 1e-8,
    maxiter: int = 1000,
    full_output: bool = False,
) -> Union[np.ndarray, "NonlinearRootResult"]:
    """
    Решает нелинейную систему уравнений f(x) = 0 методом градиентного спуска.

    Задача f(x) = 0 преобразуется в задачу минимизации L(x) = ||f(x)||^2.

    Parameters
    ----------
    f : Callable[[np.ndarray], np.ndarray]
        Векторная функция f(x): ℝⁿ → ℝᵐ, возвращающая массив формы (m,).
    x0 : np.ndarray
        Начальное приближение, форма (n,).
    jac : Callable[[np.ndarray], np.ndarray], optional
        Функция, вычисляющая матрицу Якоби (Якобиан) функции f.
        Принимает вектор x, возвращает матрицу J(x). Если `None` (по умолчанию),
        используется численный Якобиан `derr.jacobian(f, x)`.
    lr : float, optional
        Скорость обучения (длина шага) для градиентного спуска (по умолчанию 0.01).
    atol : float, optional
        Абсолютная погрешность для критерия остановки.
        Итерации прекращаются, когда ||f|| <= atol.
    maxiter : int, optional
        Максимальное количество итераций.
    full_output : bool, optional
        Если False (по умолчанию), возвращается только корень.
        Если True, возвращается объект NonlinearRootResult с полной информацией.

    Returns
    -------
    root : np.ndarray
        Возвращается, если `full_output=False`. Найденное приближение к корню.

    result : NonlinearRootResult
        Возвращается, если `full_output=True`. Объект содержит поля:
        - `root` (np.ndarray): Найденное приближение к корню.
        - `iterations` (int): Количество выполненных итераций.
        - `converged` (bool): True, если метод сошелся.
        - `x_diff_norm_history` (List[float]): История норм шага ||delta_x||.
        - `f_norm_history` (List[float]): История норм невязки ||f(x)||.

    Notes
    -----
    Критерий остановки: ||f(x_k)|| <= atol.
    Градиент вычисляется по формуле: ∇L(x) = 2 * J(x)ᵀ @ f(x).
    """

    # --- Инициализация Якобиана ---
    if jac is None:
        jac = lambda x: derr.jacobian(f, x)

    x = np.asarray(x0, dtype=np.float64).copy()

    # --- Инициализация результатов ---
    if full_output:
        result = NonlinearRootResult(
            root=x,
            iterations=0,
            converged=False,
            x_diff_norm_history=[],
            f_norm_history=[],
        )

    # --- Основной итерационный цикл ---
    for iter_counter in range(1, maxiter + 1):

        # 1. Вычисляем f(x_k) и J(x_k)
        try:
            f_x = f(x)
            J = jac(x)
        except Exception as e:
            msg = f"Ошибка при вычислении f(x) или Якобиана на итерации {iter_counter}: {e}"
            warnings.warn(msg, RuntimeWarning)

            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = False
                return result
            return x

        # 2. Норма невязки ||f(x_k)||
        f_norm = np.linalg.norm(f_x)

        if full_output:
            result.f_norm_history.append(f_norm)

        # 3. Вычисляем градиент L(x_k): ∇L(x) = 2 * J(x)ᵀ @ f(x)
        grad_L = 2 * J.T @ f_x

        # 4. Вычисляем шаг: step = lr * ∇L(x_k)
        step_vec = lr * grad_L

        x_old = x.copy()

        # 5. Обновляем решение: x_{k+1} = x_k - step
        x = x_old - step_vec

        # 6. Вычисляем норму шага ||x_{k+1} - x_k||
        step_norm = np.linalg.norm(step_vec)

        if full_output:
            result.x_diff_norm_history.append(step_norm)

        # 7. Проверка критерия остановки
        # ||f(x_k)|| <= atol
        if f_norm <= atol:
            # Успешный выход: сходимость достигнута

            if full_output:
                result.root = x
                result.iterations = iter_counter
                result.converged = True
                return result
            return x

    # --- Завершение (сходимость не достигнута) ---
    warnings.warn(
        f"solve_gd: Сходимость не достигнута за {maxiter} итераций.", RuntimeWarning
    )

    if full_output:
        result.root = x
        result.iterations = maxiter
        result.converged = False
        return result

    return x


# def solve_gd_torch_adam(
#     f: Callable[[torch.Tensor], torch.Tensor],
#     x0: np.ndarray,
#     *,
#     lr: float = 0.001,
#     atol: float = 1e-8,
#     maxiter: int = 1000,
#     full_output: bool = False,
# ) -> Union[np.ndarray, 'NonlinearRootResult']:
#     """
#     Решает нелинейную систему уравнений f(x) = 0 методом градиентного спуска
#     с использованием адаптивного оптимизатора Adam (PyTorch).

#     Задача f(x) = 0 преобразуется в задачу минимизации L(x) = ||f(x)||².

#     Parameters
#     ----------
#     f : Callable[[torch.Tensor], torch.Tensor]
#         Векторная функция f(x): ℝⁿ → ℝᵐ. Должна принимать и возвращать torch.Tensor.
#     x0 : np.ndarray
#         Начальное приближение, форма (n,).
#     lr : float, optional
#         Скорость обучения (Learning Rate) для оптимизатора Adam (по умолчанию 0.01).
#     atol : float, optional
#         Абсолютная и относительная погрешности для критерия остановки.
#         Итерации прекращаются, когда ||f|| <= atol.
#     maxiter : int, optional
#         Максимальное количество итераций.
#     full_output : bool, optional
#         Если False (по умолчанию), возвращается только корень.
#         Если True, возвращается объект NonlinearRootResult с полной информацией.

#     Returns
#     -------
#     root : np.ndarray
#         Возвращается, если `full_output=False`. Найденное приближение к корню.

#     result : NonlinearRootResult
#         Возвращается, если `full_output=True`. Объект содержит поля:
#         - `root` (np.ndarray): Найденное приближение к корню.
#         - `iterations` (int): Количество выполненных итераций.
#         - `converged` (bool): True, если метод сошелся.
#         - `x_diff_norm_history` (List[float]): История норм шага ||delta_x||.
#         - `f_norm_history` (List[float]): История норм невязки ||f(x)||.

#     Notes
#     -----
#     Критерий остановки: ||f(x_k)|| <= atol.
#     Оптимизатор Adam автоматически регулирует шаг обновления параметров,
#     используя экспоненциальное сглаживание моментов градиента.
#     """

#     # --- Инициализация параметра x и оптимизатора ---
#     x = torch.tensor(x0, dtype=torch.float64, requires_grad=True)
#     optimizer = optim.Adam([x], lr=lr)

#     # --- Инициализация истории норм шагов ---
#     if full_output:
#         result = NonlinearRootResult(
#             root=x0,
#             iterations=0,
#             converged=False,
#             x_diff_norm_history=[],
#             f_norm_history=[],
#         )

#     # --- Основной итерационный цикл ---
#     for iter_counter in range(1, maxiter + 1):
#         x_old = x.clone().detach()  # Сохраняем x_k для вычисления изменения

#         # 1. Вычисляем функцию и скалярную целевую функцию L(x) = ||f(x)||²
#         try:
#             f_x = f(x)
#             loss = torch.sum(f_x**2)
#         except Exception as e:
#             msg = f"Ошибка при вычислении f(x) на итерации {iter_counter}: {e}"
#             warnings.warn(msg, RuntimeWarning)

#             root_np = x.detach().cpu().numpy()
#             if full_output:
#                 result.root = root_np
#                 result.iterations = iter_counter
#                 result.converged = False
#                 return result
#             return root_np

#         # 2. Норма невязки ||f(x_k)||
#         f_norm = torch.linalg.norm(f_x).item()

#         if full_output:
#             result.f_norm_history.append(f_norm)

#         # 3. Вычисляем градиенты и выполняем шаг Adam
#         optimizer.zero_grad(set_to_none=True)
#         loss.backward()
#         optimizer.step()

#         # 4. Вычисляем норму изменения параметра (шаг)
#         step_vec = x.detach() - x_old
#         step_norm = torch.linalg.norm(step_vec).item()

#         if full_output:
#             result.x_diff_norm_history.append(step_norm)

#         # 5. Проверяем критерий остановки
#         if f_norm <= atol:
#             # Успешная сходимость
#             root_np = x.detach().cpu().numpy()

#             if full_output:
#                 result.root = root_np
#                 result.iterations = iter_counter
#                 result.converged = True
#                 return result
#             return root_np

#     # --- Завершение (сходимость не достигнута) ---
#     warnings.warn(f"solve_gd_torch_adam: Сходимость не достигнута за {maxiter} итераций.", RuntimeWarning)

#     root_np = x.detach().cpu().numpy()
#     if full_output:
#         result.root = root_np
#         result.iterations = maxiter
#         result.converged = False
#         return result

#     return root_np
