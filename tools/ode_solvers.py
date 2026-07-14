# Импорты
from typing import Callable, Optional, Tuple, List, Type, Dict, Any
import numpy as np
import sys
import math
from dataclasses import dataclass
import warnings

sys.path.append(r"D:\git\MIPT\tools")

import linear_system_solvers as lss
import unlinear_system_solvers as uss
import derrivates as derr


# Базовый класс
class BaseOdeSolver:
    """
    Base abstract class for Ordinary Differential Equation (ODE) solvers.

    Manages the integration loop, step size adjustments, and history tracking
    for the Cauchy problem: y' = f(t, y), y(t₀) = y₀.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system. Takes time `t` and state `y`, returns dy/dt.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Jacobian matrix of the right-hand side, J = df/dy. Required for implicit methods.

    Notes
    -----
    • *Algorithm workflow*
    - The class handles the global while-loop in `integrate()`.
    - Specific numerical methods (Runge-Kutta, Adams, etc.) must inherit from this
      class and implement the `step()` method to update `self.t` and `self.y_vec`.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        self.fun = fun
        self.jac = jac

        self.t = t0
        # Convert initial state to double precision array
        self.y_vec = np.asarray(y0_vec, dtype=np.float64).copy()  # shape: (N,)
        self.h = h
        self.t_bound = t_bound

        # --- Step 1: Initialize history ---
        # Lists to accumulate integration trajectory
        self.t_arr: List[float] = [self.t]
        self.y_arr: List[np.ndarray] = [self.y_vec.copy()]

    def step(self) -> None:
        """
        Performs a single numerical integration step.

        Raises
        ------
        - NotImplementedError
            Must be implemented by child classes.

        Notes
        -----
        • *Working hypotheses*
        - This method is responsible for evaluating the new state and strictly
          updating `self.t` and `self.y_vec` attributes.
        """
        raise NotImplementedError("Subclasses must implement the 'step' method.")

    def integrate(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Executes the main integration loop until the time boundary is reached.

        Returns
        -------
        - t_arr : (K,) ndarray
            Array of computed time points, where K is the number of steps.
        - y_arr : (K, N) ndarray
            Array of computed state vectors corresponding to t_arr.
        """
        # --- Step 1: Main Integration Loop ---
        while self.t < self.t_bound - 1e-12:

            # --- Step 1a: Step Size Adjustment ---
            # Truncate step size to prevent overshooting the right boundary
            if self.t + self.h > self.t_bound + 1e-14:
                self.h = self.t_bound - self.t

            # --- Step 1b: Method Execution ---
            # Call specific solver implementation to advance time and state
            self.step()

            if not np.all(np.isfinite(self.y_vec)):
                warnings.warn(f"Integrate: NaN or Inf", RuntimeWarning)
                self.t_arr.append(self.t)
                self.y_arr.append(self.y_vec.copy())
                break

            # --- Step 1c: Record Trajectory ---
            self.t_arr.append(self.t)
            self.y_arr.append(self.y_vec.copy())  # shape: (N,)

        # --- Step 2: Finalize Output ---
        # Convert lists to numpy arrays for consistency
        return np.array(self.t_arr), np.array(self.y_arr)  # shapes: (K,), (K, N)


# Методы Рунге-Кутты
class ExplicitRungeKutta(BaseOdeSolver):
    """
    Explicit Runge-Kutta (ERK) method solver for Ordinary Differential Equations.

    Solves the Cauchy problem y' = f(t, y) using a prescribed Butcher tableau.
    Being an explicit method, it calculates stage derivatives sequentially
    without solving nonlinear algebraic equations.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - a_mat : (s, s) array_like
        Strictly lower triangular matrix A from the Butcher tableau.
    - b_vec : (s,) array_like
        Vector of weights b from the Butcher tableau.
    - c_vec : (s,) array_like
        Vector of nodes c from the Butcher tableau.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Jacobian matrix (not used in explicit methods, kept for compatibility).

    Notes
    -----
    • *Mathematical foundation*
    - Stage derivatives: kᵢ = f(tₙ + cᵢh, yₙ + h * ∑(j=0 to i-1) aᵢⱼ kⱼ), for i = 0..s-1.
    - Step update: yₙ₊₁ = yₙ + h * ∑(i=0 to s-1) bᵢ kᵢ.

    • *Algorithm workflow*
    1. Initialize the k_mat matrix to store derivatives for each stage.
    2. Sequentially evaluate each stage kᵢ using previously computed stages.
    3. Perform a weighted sum of kᵢ to find the new state yₙ₊₁.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        a_mat: np.ndarray,
        b_vec: np.ndarray,
        c_vec: np.ndarray,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, jac=jac)

        # --- Step 1: Initialize Butcher tableau components ---
        self.a_mat = np.asarray(a_mat, dtype=np.float64)  # shape: (s, s)
        self.b_vec = np.asarray(b_vec, dtype=np.float64)  # shape: (s,)
        self.c_vec = np.asarray(c_vec, dtype=np.float64)  # shape: (s,)

        self.num_stages: int = len(b_vec)  # shape: scalar

    def step(self) -> None:
        """
        Executes a single step of the explicit Runge-Kutta method.
        """
        n_dim: int = self.y_vec.size
        s: int = self.num_stages

        # Matrix to store evaluated stage vectors kᵢ
        k_mat = np.zeros((s, n_dim), dtype=np.float64)  # shape: (s, N)

        # --- Step 1: Sequential Stage Evaluation ---
        # Matrix A is strictly lower triangular (aᵢⱼ = 0 for j ≥ i)
        for i in range(s):
            # tᵢ = tₙ + cᵢ * h
            t_i = self.t + self.c_vec[i] * self.h  # shape: scalar

            if i == 0:
                # First stage derivative is always evaluated at the current state
                y_i_vec = self.y_vec  # shape: (N,)
            else:
                # yᵢ = yₙ + h * ∑ aᵢⱼ kⱼ (for j from 0 to i-1)
                # Vectorized dot product for accumulated stage contributions
                y_i_vec = self.y_vec + self.h * (
                    self.a_mat[i, :i] @ k_mat[:i]
                )  # shape: (N,)

            # Compute stage derivative kᵢ = f(tᵢ, yᵢ)
            k_mat[i] = self.fun(t_i, y_i_vec)  # shape: (N,)

        # --- Step 2: Final State Update ---
        # yₙ₊₁ = yₙ + h * ∑ bᵢ kᵢ
        # Weighted combination of all computed stage derivatives
        self.y_vec += self.h * (self.b_vec @ k_mat)  # shape: (N,)
        self.t += self.h  # shape: scalar


class ImplicitRungeKutta(BaseOdeSolver):
    """
    Fully Implicit Runge-Kutta (IRK) method solver for Ordinary Differential Equations.

    Solves the dense nonlinear system for all internal stages simultaneously.
    Can handle stiff systems if the Butcher tableau represents a stiffly-accurate
    or L-stable method.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - a_mat : (s, s) array_like
        Matrix A from the Butcher tableau (Runge-Kutta matrix).
    - b_vec : (s,) array_like
        Vector of weights b from the Butcher tableau.
    - c_vec : (s,) array_like
        Vector of nodes c from the Butcher tableau.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Jacobian matrix of the right-hand side, J = df/dy.

    Notes
    -----
    • *Mathematical foundation*
    - The stage vectors kᵢ are defined implicitly:
      kᵢ = f(tₙ + cᵢh, yₙ + h * ∑(j=1 to s) aᵢⱼ kⱼ), for i = 1..s.
    - This forms a coupled system of sN nonlinear algebraic equations.

    • *Algorithm workflow*
    1. Formulate the residual function R(K) = 0 for the concatenated vector K.
    2. Compute the exact block-Jacobian of the residual if the analytical ODE Jacobian is provided.
    3. Solve the sN dimensional system using Newton's method.
    4. Advance the solution: yₙ₊₁ = yₙ + h * ∑(i=1 to s) bᵢ kᵢ.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        a_mat: np.ndarray,
        b_vec: np.ndarray,
        c_vec: np.ndarray,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, jac=jac)

        # --- Step 1: Initialize Butcher tableau ---
        self.a_mat = np.asarray(a_mat, dtype=np.float64)  # shape: (s, s)
        self.b_vec = np.asarray(b_vec, dtype=np.float64)  # shape: (s,)
        self.c_vec = np.asarray(c_vec, dtype=np.float64)  # shape: (s,)
        self.num_stages: int = len(b_vec)  # shape: scalar

    def step(self) -> None:
        """
        Executes a single step of the fully implicit Runge-Kutta method.
        """
        n_dim: int = self.y_vec.size
        s: int = self.num_stages

        # --- Step 1: Define the Non-Linear Residual Function ---
        def residual_fun(k_flat: np.ndarray) -> np.ndarray:
            """
            Computes the residual Rᵢ = kᵢ - f(tᵢ, Yᵢ) for all stages.
            """
            k_mat = k_flat.reshape(s, n_dim)  # shape: (s, N)

            # Compute inner stage states: Yᵢ = yₙ + h * ∑ aᵢⱼ kⱼ
            # Vectorized computation for all stages simultaneously
            y_inner_mat = self.y_vec + self.h * (self.a_mat @ k_mat)  # shape: (s, N)

            res_mat = np.empty_like(k_mat)  # shape: (s, N)
            for i in range(s):
                t_i = self.t + self.c_vec[i] * self.h
                # Calculate stage residual
                res_mat[i] = k_mat[i] - self.fun(t_i, y_inner_mat[i])  # shape: (N,)

            return res_mat.ravel()  # shape: (sN,)

        # --- Step 2: Define Block-Jacobian of the Residual ---
        if self.jac is not None:

            def residual_jac(k_flat: np.ndarray) -> np.ndarray:
                """
                Constructs the (sN, sN) Jacobian matrix of the residual vector.
                """
                k_mat = k_flat.reshape(s, n_dim)  # shape: (s, N)
                y_inner_mat = self.y_vec + self.h * (
                    self.a_mat @ k_mat
                )  # shape: (s, N)

                # Initialize a 4D tensor to store block matrices
                jac_blocks = np.zeros(
                    (s, s, n_dim, n_dim), dtype=np.float64
                )  # shape: (s, s, N, N)
                identity_mat = np.eye(n_dim)  # shape: (N, N)

                jac_fn = self.jac
                for i in range(s):
                    t_i = self.t + self.c_vec[i] * self.h
                    # Local ODE Jacobian: Jᵢ = df/dy at the i-th internal stage
                    J_i = jac_fn(t_i, y_inner_mat[i])  # shape: (N, N)

                    for j in range(s):
                        # Block components: ∂Rᵢ / ∂kⱼ = δᵢⱼ I - h aᵢⱼ Jᵢ
                        if i == j:
                            jac_blocks[i, j] = (
                                identity_mat - self.h * self.a_mat[i, j] * J_i
                            )  # shape: (N, N)
                        else:
                            jac_blocks[i, j] = (
                                -self.h * self.a_mat[i, j] * J_i
                            )  # shape: (N, N)

                # Flatten the block tensor into a standard 2D matrix
                return jac_blocks.transpose(0, 2, 1, 3).reshape(
                    s * n_dim, s * n_dim
                )  # shape: (sN, sN)

        else:
            residual_jac = None

        # --- Step 3: Newton Method Initial Guess ---

        k0_flat = np.zeros(s * n_dim, dtype=np.float64)

        # --- Step 4: Solve the Nonlinear System ---
        # Find roots of the multidimensional system to get stage derivatives
        k_new_flat = uss.solve_newton_multidim(
            residual_fun, k0_flat, jac=residual_jac, maxiter=30
        )  # shape: (sN,)
        assert isinstance(k_new_flat, np.ndarray)

        k_new_mat = k_new_flat.reshape(s, n_dim)  # shape: (s, N)

        # --- Step 5: Advance Integration Step ---
        # Update state: yₙ₊₁ = yₙ + h * ∑ bᵢ kᵢ
        self.y_vec += self.h * (self.b_vec @ k_new_mat)  # shape: (N,)
        self.t += self.h


# Диагональный неявный метод Рунге Кутты (ДНРК)
class DiagonallyImplicitRungeKutta(BaseOdeSolver):
    """
    Diagonally Implicit Runge-Kutta (DIRK) method solver for Ordinary Differential Equations.

    Exploits the lower triangular structure of the Butcher matrix A to solve the
    internal stages sequentially, reducing computational cost compared to fully
    implicit methods.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - a_mat : (s, s) array_like
        Lower triangular matrix A from the Butcher tableau.
    - b_vec : (s,) array_like
        Vector of weights b from the Butcher tableau.
    - c_vec : (s,) array_like
        Vector of nodes c from the Butcher tableau.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Jacobian matrix of the right-hand side, J = df/dy.

    Notes
    -----
    • *Mathematical foundation*
    - Since A is lower triangular (aᵢⱼ = 0 for j > i), the stages can be decoupled.
    - Stage vector kᵢ: kᵢ = f(tₙ + cᵢh, yₙ + h ∑(j=0 to i-1) aᵢⱼ kⱼ + h aᵢᵢ kᵢ).
    - If aᵢᵢ = 0, the stage is explicit.
    - If aᵢᵢ ≠ 0, we solve a smaller system of size N (instead of sN) for each stage.

    • *Algorithm workflow*
    1. Loop through each stage i from 0 to s-1.
    2. Compute the explicit part of the argument gᵢ = yₙ + h ∑(j=0 to i-1) aᵢⱼ kⱼ.
    3. If aᵢᵢ = 0, evaluate kᵢ directly.
    4. Otherwise, solve the N-dimensional nonlinear equation R(kᵢ) = 0 using Newton's method.
    5. Update state: yₙ₊₁ = yₙ + h ∑(i=0 to s-1) bᵢ kᵢ.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        a_mat: np.ndarray,
        b_vec: np.ndarray,
        c_vec: np.ndarray,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, jac=jac)
        self.a_mat = np.asarray(a_mat, dtype=np.float64)  # shape: (s, s)
        self.b_vec = np.asarray(b_vec, dtype=np.float64)  # shape: (s,)
        self.c_vec = np.asarray(c_vec, dtype=np.float64)  # shape: (s,)
        self.num_stages: int = len(b_vec)  # shape: scalar

    def step(self) -> None:
        """
        Executes a single step of the DIRK method by sequentially solving for stage vectors.
        """
        n_dim: int = self.y_vec.size
        s: int = self.num_stages

        # Matrix to store evaluated stage vectors kᵢ
        k_mat = np.zeros((s, n_dim), dtype=np.float64)  # shape: (s, N)

        # --- Step 1: Sequential Stage Evaluation ---
        for i in range(s):
            t_i = self.t + self.c_vec[i] * self.h

            # --- Step 1a: Compute Explicit Argument Part ---
            # gᵢ = yₙ + h * ∑ aᵢⱼ kⱼ (for j < i)
            g_i = self.y_vec.copy()  # shape: (N,)
            if i > 0:
                # Vectorized dot product of the i-th row up to i with computed kⱼ
                g_i += self.h * (self.a_mat[i, :i] @ k_mat[:i])  # shape: (N,)

            a_ii = self.a_mat[i, i]

            # --- Step 1b: Explicit Stage Check ---
            # If the diagonal element is zero, no nonlinear solver is needed
            if a_ii == 0.0:
                k_mat[i] = self.fun(t_i, g_i)  # shape: (N,)
                continue

            # --- Step 1c: Implicit Stage Setup ---
            # Residual R(kᵢ) = kᵢ - f(tᵢ, gᵢ + h aᵢᵢ kᵢ) = 0
            def residual_fun_i(k_i_guess: np.ndarray) -> np.ndarray:
                Y_i = g_i + self.h * a_ii * k_i_guess  # shape: (N,)
                return k_i_guess - self.fun(t_i, Y_i)  # shape: (N,)

            # Jacobian of the residual (if analytical ODE Jacobian is provided)
            if self.jac is not None:
                jac_fn = self.jac
                def residual_jac_i(k_i_guess: np.ndarray) -> np.ndarray:
                    Y_i = g_i + self.h * a_ii * k_i_guess  # shape: (N,)
                    J_f = jac_fn(t_i, Y_i)  # shape: (N, N)
                    # ∂R/∂kᵢ = I - h aᵢᵢ J_f
                    return np.eye(n_dim) - self.h * a_ii * J_f  # shape: (N, N)

            else:
                residual_jac_i = None

            initial_guess = np.zeros(n_dim, dtype=np.float64)  # shape: (N,)

            # --- Step 1d: Solve Nonlinear System for kᵢ ---
            k_i_new_vec = uss.solve_newton_multidim(
                f=residual_fun_i, x0=initial_guess, jac=residual_jac_i, maxiter=30
            )  # shape: (N,)
            assert isinstance(k_i_new_vec, np.ndarray)

            # Store the computed stage vector
            k_mat[i] = k_i_new_vec

        # --- Step 2: Finalize Integration Step ---
        # yₙ₊₁ = yₙ + h * ∑ bᵢ kᵢ
        self.y_vec += self.h * (self.b_vec @ k_mat)  # shape: (N,)
        self.t += self.h


# Методы Розенброка
class Rosenbrock(BaseOdeSolver):
    """
    Solves a system of ordinary differential equations using the Rosenbrock method.

    See relevant numerical methods textbooks for stiff ODEs and Rosenbrock algorithms.

    Notes
    -----
    • *Mathematical foundation*
    - The Rosenbrock method is a linearly implicit Runge-Kutta method designed for stiff ODEs.
    - Stage equation: (I - γ * h * J) * kᵢ = h * f(t + cᵢ * h, yₙ + ∑(j=0 to i-1) aᵢⱼ * kⱼ) + h * J * ∑(j=0 to i-1) cᵢⱼ * kⱼ + γ * h² * ∂f/∂t
    - Update rule: yₙ₊₁ = yₙ + ∑(i=0 to s-1) bᵢ * kᵢ

    • *Algorithm workflow*
    1. Compute the Jacobian J = ∂f/∂y and the partial time derivative ∂f/∂t.
    2. Form the iteration matrix W = I - γ * h * J and perform LU factorization.
    3. Iteratively solve the linear system for each stage kᵢ.
    4. Update the state vector y_vec and advance time t.

    • *Working hypotheses & Implementation details*
    - The ODE system is of the form y' = f(t, y). For autonomous systems, ∂f/∂t = 0.
    - The Jacobian matrix is square and non-singular for the matrix (I - γ * h * J).
    - If an analytical time derivative (df_dt) is not provided, ∂f/∂t is approximated numerically
      using a central difference scheme of 2nd order (O(h²)).
    - LU factorization is strictly performed only once per time step, making the method
      computationally efficient compared to fully implicit schemes requiring Newton iterations.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        a_mat: np.ndarray,
        c_mat: np.ndarray,
        b_vec: np.ndarray,
        c_vec: np.ndarray,
        gamma: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        """
        Initializes the Rosenbrock ODE solver with specific Butcher tableau coefficients.

        Parameters
        ----------
        - fun : Callable[[float, ndarray], ndarray]
            Right-hand side of the ODE system: f(t, y).
        - t0 : float
            Initial time.
        - y0_vec : (N,) ndarray
            Initial state vector.
        - h : float
            Integration step size.
        - t_bound : float
            Boundary time for integration.
        - a_mat : (s, s) ndarray
            Lower triangular coefficient matrix A for stage linear combinations.
        - c_mat : (s, s) ndarray
            Lower triangular coefficient matrix C for Jacobian historical corrections.
        - b_vec : (s,) ndarray
            Weights vector b for the final step update.
        - c_vec : (s,) ndarray
            Nodes vector c for time increments.
        - gamma : float
            Diagonal coefficient γ (usually the same for all stages).
        - jac : Callable[[float, ndarray], ndarray], optional
            Analytical Jacobian function J(t, y) = ∂f/∂y. If None, finite differences are used.
        - df_dt : Callable[[float, ndarray], ndarray], optional
            Analytical partial time derivative function ∂f/∂t. If None, central differences are used.
        """
        super().__init__(fun, t0, y0_vec, h, t_bound, jac=jac)

        self.a_mat = np.asarray(a_mat, dtype=np.float64)  # shape: (s, s)
        self.c_mat = np.asarray(c_mat, dtype=np.float64)  # shape: (s, s)
        self.b_vec = np.asarray(b_vec, dtype=np.float64)  # shape: (s,)
        self.c_vec = np.asarray(c_vec, dtype=np.float64)  # shape: (s,)

        self.gamma = float(gamma)
        self.df_dt = df_dt
        self.num_stages = len(b_vec)

    def step(self) -> None:
        """
        Performs a single integration step of size h using the Rosenbrock method.

        Returns
        -------
        - None
            Updates `self.y_vec` and `self.t` in place.
        """
        n_dim = self.y_vec.size

        # --- Step 1: Compute Jacobian df/dy ---
        if self.jac is not None:
            jac_matrix = self.jac(self.t, self.y_vec)  # shape: (N, N)
        else:
            # Numerical Jacobian from derr module
            jac_matrix = derr.jacobian(
                lambda y: self.fun(self.t, y), self.y_vec
            )  # shape: (N, N)

        # --- Step 2: Compute Partial Time Derivative df/dt ---
        if self.df_dt is not None:
            f_t_vec = self.df_dt(self.t, self.y_vec)  # shape: (N,)
        else:
            # Fallback to derr.derivative with fixed y_vec
            # Uses central difference (O(h^2)) to match Jacobian precision
            f_t_vec = derr.derivative(
                f=lambda t: self.fun(t, self.y_vec),
                x=self.t,
                h=self.h * 1e-4,
                method="central_o2",
            )  # shape: (N,)

        # --- Step 3: Iteration Matrix W = I - gamma * h * J ---
        w_mat = np.eye(n_dim) - self.gamma * self.h * jac_matrix  # shape: (N, N)
        plu_tuple = lss.lu_factor(w_mat)

        # Buffer for stage vectors k_i
        k_mat = np.zeros((self.num_stages, n_dim), dtype=np.float64)  # shape: (s, N)

        # --- Step 4: Sequential Stage Loop ---
        for i in range(self.num_stages):

            # Formulate y_i = y_n + ∑(j < i) a_{ij} * k_j
            y_stage_vec = self.y_vec.copy()  # shape: (N,)
            if i > 0:
                y_stage_vec += self.a_mat[i, :i] @ k_mat[:i]  # shape: (N,)

            t_stage = self.t + self.c_vec[i] * self.h
            f_stage = self.fun(t_stage, y_stage_vec)  # shape: (N,)

            # Construct RHS: h * f + h * J * ∑(c_ij * k_j) + γ * h² * f_t
            rhs_vec = self.h * f_stage  # shape: (N,)

            if i > 0:
                # Add historical Jacobian correction: J @ ∑(c_ij * k_j)
                combined_k_vec = self.c_mat[i, :i] @ k_mat[:i]  # shape: (N,)
                rhs_vec += self.h * (jac_matrix @ combined_k_vec)  # shape: (N,)

            # Autonomous correction term: γ * h² * ∂f/∂t
            rhs_vec += self.gamma * (self.h**2) * f_t_vec  # shape: (N,)

            # Solve (I - γ * h * J) * k_i = rhs
            k_mat[i] = lss.solve_lu(plu_tuple, rhs_vec)  # shape: (N,)

        # --- Step 5: Final Solution Update ---
        # Update rule: yₙ₊₁ = yₙ + ∑(b_i * k_i)
        self.y_vec += self.b_vec @ k_mat  # shape: (N,)
        self.t += self.h


# Многошаговые методы
class MultistepSolver(BaseOdeSolver):
    """
    Abstract base class for multistep Ordinary Differential Equation (ODE) solvers.

    Multistep methods (such as Adams or Gear formulas) require information not
    only from the current point yₙ, but also from several previous nodes:
    yₙ₋₁, yₙ₋₂, ..., yₙ₋ₖ₊₁ to compute the next state yₙ₊₁. Since only the
    initial point y₀ is known at the start, these methods require a "bootstrapping"
    procedure using a single-step method of the same order of accuracy.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system f(t, y).
    - t0 : float
        Initial integration time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - order : int
        Order of the method (number of required history steps, k).
    - bootstrap_solver : Type[BaseOdeSolver]
        Single-step solver class (e.g., RK4) used for bootstrapping.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Analytical Jacobian J(t, y).

    Notes
    -----
    • *Mathematical foundation*
    - A k-step method requires storing a history matrix of shape (k, N).
    - Bootstrapping: Integrating with a single-step method over [t₀, t₀ + (k-1)h].

    • *Algorithm workflow*
    1. Initialize history matrices.
    2. Upon the first step call, `_bootstrap()` is automatically executed.
    3. Subsequent `step()` calls (implemented in child classes) utilize the
       assembled history matrix.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        order: int,
        bootstrap_solver: Type[BaseOdeSolver],
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, jac=jac)

        # --- Step 1: Automatic Step Size Adjustment ---

        interval_length = self.t_bound - self.t  # shape: scalar
        n_steps_float = interval_length / self.h

        # Find the nearest integer number of steps
        n_steps = int(np.round(n_steps_float))

        if n_steps < order:
            raise ValueError(
                f"Interval too short for method order {order}. Need at least {order} steps."
            )

        # Adjust integration step size to perfectly fit the interval
        self.h = interval_length / n_steps

        # --- Step 2: Initialize Method Properties ---

        self.order: int = int(order)
        self.bootstrap_solver: Type[BaseOdeSolver] = bootstrap_solver
        self.is_bootstrapped: bool = False

        # History matrix for state vectors: [yₙ, yₙ₋₁, ..., yₙ₋ₖ₊₁]
        # Index 0 always contains the most "recent" point
        self.history_y_mat: Optional[np.ndarray] = None  # expected shape: (order, N)

        # History matrix for right-hand sides: [fₙ, fₙ₋₁, ..., fₙ₋ₖ₊₁]
        self.history_f_mat: Optional[np.ndarray] = None  # expected shape: (order, N)

    def _bootstrap(self) -> None:
        """
        Executes the bootstrapping procedure for the multistep method.

        Generates the missing history points using the provided single-step
        solver (`bootstrap_solver`).

        Notes
        -----
        • *Algorithm workflow*
        1. If order ≤ 1, it degenerates to a single-step method (no bootstrapping).
        2. Otherwise, instantiate the single-step solver.
        3. Integrate for (k - 1) steps.
        4. Reverse the resulting arrays so index 0 corresponds to the latest point (yₙ).
        5. Synchronize the history with the main loop of `BaseOdeSolver`.
        """

        # --- Step 1: Check Bootstrap Requirement ---
        # If the method order is 1 (e.g., multistep formulation of Euler), no bootstrap is needed
        if self.order <= 1:
            self.history_y_mat = np.array([self.y_vec.copy()])  # shape: (1, N)
            self.history_f_mat = np.array(
                [self.fun(self.t, self.y_vec)]
            )  # shape: (1, N)
            self.is_bootstrapped = True
            return

        # --- Step 2: Single-Step Integration ---
        # Integration boundary for bootstrapping: exactly (k - 1) new steps are required
        t_bound_boot: float = self.t + (self.order - 1) * self.h

        # Instantiate the bootstrap solver
        bootstrapper = self.bootstrap_solver(
            fun=self.fun,
            t0=self.t,
            y0_vec=self.y_vec,
            h=self.h,
            t_bound=t_bound_boot,
            jac=self.jac,
        )

        # Integrate to obtain the history
        # Arrays t_boot and y_boot will contain exactly order points: t₀, t₁, ..., tₖ₋₁
        t_boot, y_boot = bootstrapper.integrate()  # shapes: (order,), (order, N)

        # --- Step 3: Formulate History Matrices ---
        # Reverse the history: index [0] now contains the most recent point yₖ₋₁
        self.history_y_mat = y_boot[::-1].copy()  # shape: (order, N)

        # Reverse the time grid
        t_reversed = t_boot[::-1]  # shape: (order,)

        # Evaluate the right-hand side f(t, y) for the entire assembled history
        self.history_f_mat = np.array(
            [self.fun(t, y) for t, y in zip(t_reversed, self.history_y_mat)]
        )  # shape: (order, N)

        # --- Step 4: Synchronize with Base Solver ---
        # The point t₀ is already recorded in self.t_arr and self.y_arr of the base class.
        # Intermediate points t₁ ... tₖ₋₂ must be appended manually.
        # The final point tₖ₋₁ will be appended by the integrate() method after returning from step().
        for i in range(1, self.order - 1):
            self.t_arr.append(t_boot[i])
            self.y_arr.append(y_boot[i].copy())  # shape: (N,)

        # Shift the current time and state vector to the end of the bootstrap interval
        self.t = float(t_boot[-1])
        self.y_vec = y_boot[-1].copy()  # shape: (N,)

        self.is_bootstrapped = True


# Методы Адамса
class AdamsBashforth(MultistepSolver):
    """
    Explicit Adams-Bashforth multistep solver for Ordinary Differential Equations.

    Predicts the next state yₙ₊₁ by extrapolating the derivative f(t, y) using
    a Lagrange polynomial built on the history of previous derivative values.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - order : int
        Order of the method (k).
    - bootstrap_solver : Type[BaseOdeSolver]
        Single-step solver class used for bootstrapping the history.
    - coeffs_vec : (order,) array_like
        Coefficients for the Adams-Bashforth formula. Index 0 corresponds to
        the current step fₙ, and index (order-1) to the oldest step fₙ₋ₖ₊₁.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Analytical Jacobian J(t, y).

    Notes
    -----
    • *Mathematical foundation*
    - Formula: yₙ₊₁ = yₙ + h ∑(j=0 to k-1) cⱼ fₙ₋ⱼ
    - Explicit methods have small stability regions and are typically used
      only for non-stiff problems.

    • *Algorithm workflow*
    1. Bootstrap to generate history if not already done.
    2. Compute yₙ₊₁ using the explicit linear combination of historical f values.
    3. Evaluate the new right-hand side fₙ₊₁.
    4. Shift the history arrays and insert the new values at index 0.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        order: int,
        bootstrap_solver: Type[BaseOdeSolver],
        coeffs_vec: np.ndarray,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, order, bootstrap_solver, jac=jac)

        # Expected shape: (order,)
        # coeffs_vec[0] maps to fₙ, coeffs_vec[-1] maps to fₙ₋ₖ₊₁
        self.coeffs_vec = np.asarray(coeffs_vec, dtype=np.float64)

    def step(self) -> None:
        """
        Executes a single step of the explicit Adams-Bashforth method.
        """
        # --- Step 1: Bootstrap History ---
        # Generate initial history points if they do not exist
        if not self.is_bootstrapped:
            self._bootstrap()
            return

        # --- Step 2: Adams-Bashforth Evaluation ---
        assert self.history_f_mat is not None
        assert self.history_y_mat is not None
        # Vectorized dot product: coeffs_vec @ history_f_mat
        # (order,) @ (order, N) -> (N,)
        y_new_vec = self.y_vec + self.h * (
            self.coeffs_vec @ self.history_f_mat
        )  # shape: (N,)
        t_new = self.t + self.h

        # --- Step 3: Evaluate New Derivative ---
        f_new = self.fun(t_new, y_new_vec)  # shape: (N,)

        # --- Step 4: Update History Arrays ---
        # np.roll cyclically shifts elements along axis 0.
        # Shift=1 moves the oldest element to index 0, which we then overwrite.
        self.history_y_mat = np.roll(
            self.history_y_mat, shift=1, axis=0
        )  # shape: (order, N)
        self.history_f_mat = np.roll(
            self.history_f_mat, shift=1, axis=0
        )  # shape: (order, N)

        # Insert the newest point at index 0 to maintain order
        self.history_y_mat[0] = y_new_vec
        self.history_f_mat[0] = f_new

        # --- Step 5: Update Solver State ---
        self.t = t_new
        self.y_vec = y_new_vec


class AdamsMoulton(MultistepSolver):
    """
    Implicit Adams-Moulton multistep solver for Ordinary Differential Equations.

    Computes the next state yₙ₊₁ implicitly by including the unknown point
    in the interpolating Lagrange polynomial, yielding better stability
    characteristics than explicit Adams methods.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - order : int
        Order of the method (k).
    - bootstrap_solver : Type[BaseOdeSolver]
        Single-step solver class used for bootstrapping the history.
    - coeffs_vec : (order,) array_like
        Coefficients for the historical part [fₙ, fₙ₋₁, ..., fₙ₋ₖ₊₁].
    - beta_0 : float
        Coefficient for the implicit term f(tₙ₊₁, yₙ₊₁).
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Analytical Jacobian J(t, y).

    Notes
    -----
    • *Mathematical foundation*
    - Formula: yₙ₊₁ = yₙ + h β₀ f(tₙ₊₁, yₙ₊₁) + h ∑(j=0 to k-1) cⱼ fₙ₋ⱼ
    - Requires solving a nonlinear system at each step.

    • *Algorithm workflow*
    1. Bootstrap to generate history if needed.
    2. Formulate the residual function for the implicit equation.
    3. Use an explicit predictor (Euler step) as an initial guess.
    4. Solve the system using Newton's method (Corrector).
    5. Update the history arrays and internal state.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        order: int,
        bootstrap_solver: Type[BaseOdeSolver],
        coeffs_vec: np.ndarray,
        beta_0: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, order, bootstrap_solver, jac=jac)

        # Coefficient for the unknown point f(tₙ₊₁, yₙ₊₁)
        self.beta_0 = float(beta_0)

        # Coefficients for history: [fₙ, fₙ₋₁, ..., fₙ₋ₖ₊₁]
        self.coeffs_vec = np.asarray(coeffs_vec, dtype=np.float64)  # shape: (order,)

    def step(self) -> None:
        """
        Executes a single step of the implicit Adams-Moulton method.
        """
        # --- Step 1: Bootstrap History ---
        if not self.is_bootstrapped:
            self._bootstrap()
            return

        n_dim: int = self.y_vec.size
        t_next = self.t + self.h

        # --- Step 2: Compute Known History Sum ---
        assert self.history_f_mat is not None
        assert self.history_y_mat is not None
        # Sum over j from 0 to order-1: h * cⱼ * fₙ₋ⱼ
        known_history_sum = self.h * (
            self.coeffs_vec @ self.history_f_mat
        )  # shape: (N,)

        # --- Step 3: Define Residual for Newton's Method ---
        # R(yₙ₊₁) = yₙ₊₁ - yₙ - h β₀ f(tₙ₊₁, yₙ₊₁) - known_history_sum = 0
        def residual_fun(y_next: np.ndarray) -> np.ndarray:
            f_next = self.fun(t_next, y_next)  # shape: (N,)
            return (
                y_next - self.y_vec - self.h * self.beta_0 * f_next - known_history_sum
            )  # shape: (N,)

        # --- Step 4: Define Jacobian of the Residual ---
        # J_R = I - h β₀ J_f
        if self.jac is not None:
            jac_fn = self.jac
            def residual_jac(y_next: np.ndarray) -> np.ndarray:
                J_f = jac_fn(t_next, y_next)  # shape: (N, N)
                return np.eye(n_dim) - self.h * self.beta_0 * J_f  # shape: (N, N)

        else:
            residual_jac = None

        # --- Step 5: Initial Guess (Predictor) ---

        y_guess = self.y_vec.copy()  # shape: (N,)

        # --- Step 6: Solve Nonlinear System (Corrector) ---
        y_next_vec = uss.solve_newton_multidim(
            f=residual_fun,
            x0=y_guess,
            jac=residual_jac,
            maxiter=30,
        )  # shape: (N,)
        assert isinstance(y_next_vec, np.ndarray)

        # --- Step 7: Evaluate Final Derivative & Update History ---
        f_next_vec = self.fun(t_next, y_next_vec)  # shape: (N,)

        # Shift history arrays cyclically
        self.history_y_mat = np.roll(
            self.history_y_mat, shift=1, axis=0
        )  # shape: (order, N)
        self.history_f_mat = np.roll(
            self.history_f_mat, shift=1, axis=0
        )  # shape: (order, N)

        # Record new states
        self.history_y_mat[0] = y_next_vec
        self.history_f_mat[0] = f_next_vec

        # Update solver state
        self.t = t_next
        self.y_vec = y_next_vec


# Метод Гира
class GearBDF(MultistepSolver):
    """
    Solves a stiff system of ordinary differential equations using the Gear method
    (Backward Differentiation Formulas, or BDF).

    Notes
    -----
    • *Mathematical foundation*
    - The method is based on differentiating an interpolating polynomial of the solution.
    - General BDF formula of order k: yₙ₊₁ = ∑(j=1 to k) αⱼ * yₙ₋ⱼ₊₁ + h * β * f(tₙ₊₁, yₙ₊₁)
    - Since f(tₙ₊₁, yₙ₊₁) depends on the unknown yₙ₊₁, it is an implicit method requiring a non-linear solver.

    • *Algorithm workflow*
    1. Bootstrap: Generate the first k points using a single-step explicit/implicit method.
    2. Prediction: Use the last known point as an initial guess.
    3. Correction: Solve the implicit non-linear residual equation for yₙ₊₁ using Newton's method.
    4. Update the history array by shifting older states.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        order: int,
        bootstrap_solver: Type[Any],
        alpha_vec: np.ndarray,
        beta: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        """
        Initializes the Gear (BDF) multi-step ODE solver.

        Parameters
        ----------
        - fun : Callable[[float, ndarray], ndarray]
            Right-hand side of the ODE system: f(t, y).
        - t0 : float
            Initial time.
        - y0_vec : (N,) ndarray
            Initial state vector.
        - h : float
            Integration step size.
        - t_bound : float
            Boundary time for integration.
        - order : int
            Order of the BDF method (k).
        - bootstrap_solver : Type[Any]
            Solver class used to generate the initial history (e.g., RK4).
        - alpha_vec : (k,) ndarray
            Coefficients for the history terms: [yₙ, yₙ₋₁, ..., yₙ₋ₖ₊₁].
        - beta : float
            Coefficient for the right-hand side evaluation at the new step.
        - jac : Callable[[float, ndarray], ndarray], optional
            Analytical Jacobian function J(t, y) = ∂f/∂y. If None, finite differences are used in Newton's solver.
        """
        super().__init__(fun, t0, y0_vec, h, t_bound, order, bootstrap_solver, jac=jac)

        self.alpha_vec = np.asarray(alpha_vec, dtype=np.float64)  # shape: (k,)
        self.beta = float(beta)
        self.jac = jac

    def step(self) -> None:
        """
        Performs a single integration step of size h using the BDF method.

        Returns
        -------
        - None
            Updates `self.y_vec`, `self.t`, and the history matrices in place.
        """
        # --- Step 1: Bootstrap History ---
        if not self.is_bootstrapped:
            self._bootstrap()
            return

        n_dim = self.y_vec.size
        t_next = self.t + self.h

        # --- Step 2: Compute Historical Sum ---
        assert self.history_f_mat is not None
        assert self.history_y_mat is not None
        # Evaluate ∑(j=1 to k) αⱼ * yₙ₋ⱼ₊₁
        history_sum_vec = self.alpha_vec @ self.history_y_mat  # shape: (N,)

        # --- Step 3: Define Residual Function for Newton's Method ---
        # Formulate R(yₙ₊₁) = yₙ₊₁ - history_sum - h * β * f(tₙ₊₁, yₙ₊₁) = 0
        def residual_fun(y_next_vec: np.ndarray) -> np.ndarray:
            f_next = self.fun(t_next, y_next_vec)  # shape: (N,)
            return (
                y_next_vec - history_sum_vec - self.h * self.beta * f_next
            )  # shape: (N,)

        # --- Step 4: Define Jacobian of the Residual ---
        # Formulate J_R = I - h * β * J_f
        if self.jac is not None:
            jac_fn = self.jac
            def residual_jac(y_next_vec: np.ndarray) -> np.ndarray:
                jac_f = jac_fn(t_next, y_next_vec)  # shape: (N, N)
                return np.eye(n_dim) - self.h * self.beta * jac_f  # shape: (N, N)

        else:
            residual_jac = None

        # --- Step 5: Initial Guess (Predictor) ---
        # Use the current state yₙ as the starting point for Newton iterations
        y_guess = self.history_y_mat[0].copy()  # shape: (N,)

        # --- Step 6: Solve Nonlinear System (Corrector) ---
        y_next_vec = uss.solve_newton_multidim(
            f=residual_fun, x0=y_guess, jac=residual_jac, maxiter=30
        )  # shape: (N,)
        assert isinstance(y_next_vec, np.ndarray)

        # --- Step 7: Update History Matrix ---
        # Shift history arrays cyclically to accommodate the new point
        self.history_y_mat = np.roll(
            self.history_y_mat, shift=1, axis=0
        )  # shape: (k, N)
        self.history_f_mat = np.roll(
            self.history_f_mat, shift=1, axis=0
        )  # shape: (k, N)

        # Insert the newly computed state and its derivative at the head (index 0)
        self.history_y_mat[0] = y_next_vec
        self.history_f_mat[0] = self.fun(t_next, y_next_vec)

        # --- Step 8: Update Global Solver State ---
        self.t = t_next
        self.y_vec = y_next_vec


# Метод Гира в представлении Нордсика
class GearNordsieck(BaseOdeSolver):
    """
    Gear's method (BDF) implemented using the Nordsieck representation.

    Instead of storing historical state values [yₙ, yₙ₋₁, ..., yₙ₋ₖ], the Nordsieck
    formulation stores the current state and its scaled Taylor derivatives in a
    single matrix. This approach makes adaptive step-size changing mathematically
    trivial compared to the classical multistep formulation.

    Parameters
    ----------
    - fun : Callable[[float, np.ndarray], np.ndarray]
        Right-hand side of the ODE system.
    - t0 : float
        Initial time t₀.
    - y0_vec : (N,) array_like
        Initial state vector y₀.
    - h : float
        Integration step size.
    - t_bound : float
        Right boundary of the integration interval.
    - order : int
        Order of the method (k).
    - l_vec : (order + 1,) array_like
        Nordsieck equivalence vector l. (e.g., [2/3, 1, 1/3] for BDF2).
    - bootstrap_solver : Type[BaseOdeSolver]
        Single-step solver class used for bootstrapping the initial derivatives.
    - jac : Callable[[float, np.ndarray], np.ndarray], optional
        Jacobian matrix of the right-hand side, J = df/dy.

    Notes
    -----
    • *Mathematical foundation*
    - Nordsieck vector: zₙ = [yₙ, h y'ₙ, (h²/2!) y''ₙ, ..., (hᵏ/k!) y⁽ᵏ⁾ₙ]^T
    - Predictor step: z⁽⁰⁾ = P zₙ, where P is the Pascal matrix.
    - Corrector step: zₙ₊₁ = z⁽⁰⁾ + l ⊗ Δ, where Δ is the prediction error vector.

    • *Algorithm workflow*
    1. Bootstrap to approximate higher-order derivatives using backward differences.
    2. Predict the next Nordsieck vector using the Pascal matrix.
    3. Formulate the residual based on the first derivative (hy'ₙ₊₁).
    4. Solve for the new state yₙ₊₁ using Newton's method.
    5. Evaluate the error Δ and update the entire Nordsieck matrix zₙ₊₁.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        order: int,
        l_vec: np.ndarray,
        bootstrap_solver: Type[BaseOdeSolver],
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        super().__init__(fun, t0, y0_vec, h, t_bound, jac=jac)

        # --- Step 1: Automatic Step Size Adjustment ---
        interval_length = self.t_bound - self.t
        n_steps_float = interval_length / self.h

        n_steps = int(np.round(n_steps_float))

        if n_steps < order:
            raise ValueError(
                f"Interval too short for method order {order}. Need at least {order} steps."
            )

        # Adjust integration step size to perfectly fit the interval
        self.h = interval_length / n_steps

        # --- Step 2: Initialize Method Properties ---

        self.order: int = int(order)

        # l_vec: Nordsieck equivalence vector of length (order + 1)
        # e.g., for BDF2 it is [2/3, 1, 1/3], for BDF1 (Euler) it is [1, 1]
        self.l_vec = np.asarray(l_vec, dtype=np.float64)  # shape: (order + 1,)
        self.bootstrap_solver: Type[BaseOdeSolver] = bootstrap_solver

        # Nordsieck matrix storing [y, h y', (h²/2) y'', ..., (hᵏ/k!) y⁽ᵏ⁾]
        self.z_mat: Optional[np.ndarray] = None  # expected shape: (order + 1, N)

        # Upper triangular Pascal matrix for the predictor step
        self.pascal_mat: np.ndarray = self._get_pascal_matrix(
            self.order
        )  # shape: (order + 1, order + 1)
        self.is_initialized: bool = False

    def _get_pascal_matrix(self, k: int) -> np.ndarray:
        """
        Generates the upper triangular Pascal matrix for Taylor expansion prediction.

        Parameters
        ----------
        - k : int
            Order of the method.

        Returns
        -------
        - p_mat : (k+1, k+1) ndarray
            Matrix where P_ij = combination(j, i) for j >= i, else 0.
        """
        p_mat = np.zeros((k + 1, k + 1), dtype=np.float64)  # shape: (k + 1, k + 1)
        for j in range(k + 1):
            for i in range(j + 1):
                p_mat[i, j] = math.comb(j, i)
        return p_mat

    def _init_nordsieck_matrix(self) -> None:
        """
        Initializes the Nordsieck history matrix by integrating with a single-step
        solver and approximating derivatives using backward finite differences.
        """
        # --- Step 1: Execute Bootstrap Integration ---
        # Require 'order' steps to approximate up to the k-th derivative
        t_bound_boot = self.t + self.order * self.h

        bootstrapper = self.bootstrap_solver(
            fun=self.fun,
            t0=self.t,
            y0_vec=self.y_vec,
            h=self.h,
            t_bound=t_bound_boot,
            jac=self.jac,
        )

        # Retrieve the bootstrap trajectory
        t_boot, y_boot = (
            bootstrapper.integrate()
        )  # shapes: (order + 1,), (order + 1, N)
        n_dim = self.y_vec.size
        k_order = self.order

        self.z_mat = np.zeros(
            (self.order + 1, n_dim), dtype=np.float64
        )  # shape: (order + 1, N)

        # --- Step 2: Approximate Scaled Derivatives ---
        # Estimate y, y', y'', ... at the point t_order
        # Using built-in numpy difference function for backward differences
        current_diffs = (
            y_boot.copy()
        )  # shape: varies per iteration, starts at (order + 1, N)
        factorial = 1.0

        for k in range(self.order + 1):
            if k > 0:
                # Differentiate over time (along axis 0)
                current_diffs = np.diff(current_diffs, axis=0)
                factorial *= k
            # Assign the k-th scaled derivative at the final point of the bootstrap interval
            self.z_mat[k] = current_diffs[-1] / factorial  # shape: (N,)

        # --- Step 3: Synchronize State ---
        # Append intermediate points to the global history
        for i in range(1, len(t_boot) - 1):
            self.t_arr.append(float(t_boot[i]))
            self.y_arr.append(y_boot[i].copy())  # shape: (N,)

        self.t = float(t_boot[-1])
        self.y_vec = y_boot[-1].copy()  # shape: (N,)
        self.is_initialized = True

    def step(self) -> None:
        """
        Executes a single Predictor-Corrector step using the Nordsieck matrix.
        """
        # --- Step 1: Initialization Check ---
        if not self.is_initialized:
            self._init_nordsieck_matrix()
            return

        n_dim: int = self.y_vec.size
        t_next = self.t + self.h
        l0 = self.l_vec[0]

        # --- Step 2: Predictor Step ---
        assert self.z_mat is not None
        # z_pred = P @ z_old (Simultaneous Taylor expansion for all derivatives)
        z_pred = self.pascal_mat @ self.z_mat  # shape: (order + 1, N)

        y_pred = z_pred[0]  # shape: (N,)
        hy_prime_pred = z_pred[1]  # shape: (N,)

        # --- Step 3: Define Corrector Residual ---
        # Equation: Δ = h * f(t_next, y_pred + l₀ * Δ) - hy_prime_pred
        # Reformulated for y_next: y_next = y_pred + l₀ * Δ => Δ = (y_next - y_pred) / l₀
        def residual_fun(y_next: np.ndarray) -> np.ndarray:
            delta = (y_next - y_pred) / l0  # shape: (N,)
            return delta - (
                self.h * self.fun(t_next, y_next) - hy_prime_pred
            )  # shape: (N,)

        if self.jac is not None:
            jac_fn = self.jac
            def residual_jac(y_next: np.ndarray) -> np.ndarray:
                # J_R = (1 / l₀) I - h J_f
                return (1.0 / l0) * np.eye(n_dim) - self.h * jac_fn(
                    t_next, y_next
                )  # shape: (N, N)

        else:
            residual_jac = None

        # --- Step 4: Corrector Step (Solve System) ---
        y_next_vec = uss.solve_newton_multidim(
            f=residual_fun, x0=self.y_vec.copy(), jac=residual_jac, maxiter=30
        )  # shape: (N,)
        assert isinstance(y_next_vec, np.ndarray)

        # Compute the final prediction error vector Δ
        delta_vec = (y_next_vec - y_pred) / l0  # shape: (N,)

        # --- Step 5: Update Nordsieck Matrix ---
        # z_new = z_pred + l ⊗ Δ
        # (order + 1, N) = (order + 1, N) + outer((order + 1,), (N,))
        self.z_mat = z_pred + np.outer(self.l_vec, delta_vec)  # shape: (order + 1, N)

        # --- Step 6: Commit State ---
        self.y_vec = self.z_mat[0].copy()  # shape: (N,)
        self.t = t_next


# Реализации методов
# ==========================================
# 1. EXPLICIT RUNGE-KUTTA (RK)
# ==========================================


class RK1_CondStable_Euler(ExplicitRungeKutta):
    """
    Explicit Runge-Kutta method of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Forward Euler method
    - Class: Explicit single-step Runge-Kutta (ERK)
    - Order: 1
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h * f(tₙ, yₙ)
    - Source/Paper: L. Euler, "Institutionum calculi integralis" (1768). Standard reference: E. Hairer, S.P. Nørsett, G. Wanner, "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[0.0]])  # shape: (1, 1)
        b_vec = np.array([1.0])  # shape: (1,)
        c_vec = np.array([0.0])  # shape: (1,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class RK2_CondStable_Heun(ExplicitRungeKutta):
    """
    Explicit Runge-Kutta method of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Heun's method (Modified Euler)
    - Class: Explicit single-step Runge-Kutta (ERK)
    - Order: 2
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/2 * (f(tₙ, yₙ) + f(tₙ + h, yₙ + h*fₙ))
    - Source/Paper: K. Heun, "Neue Methoden zur approximativen Integration der Differentialgleichungen" (1900). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[0.0, 0.0], [1.0, 0.0]])  # shape: (2, 2)
        b_vec = np.array([0.5, 0.5])  # shape: (2,)
        c_vec = np.array([0.0, 1.0])  # shape: (2,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class RK3_CondStable_Kutta(ExplicitRungeKutta):
    """
    Explicit Runge-Kutta method of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Kutta's third-order method
    - Class: Explicit single-step Runge-Kutta (ERK)
    - Order: 3
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h * (1/6*k₁ + 2/3*k₂ + 1/6*k₃)
    - Source/Paper: W. Kutta, "Beitrag zur näherungsweisen Integration totaler Differentialgleichungen" (1901). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array(
            [[0.0, 0.0, 0.0], [0.5, 0.0, 0.0], [-1.0, 2.0, 0.0]]
        )  # shape: (3, 3)
        b_vec = np.array([1 / 6, 2 / 3, 1 / 6])  # shape: (3,)
        c_vec = np.array([0.0, 0.5, 1.0])  # shape: (3,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class RK4_CondStable_Classic(ExplicitRungeKutta):
    """
    Explicit Runge-Kutta method of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Classic Runge-Kutta (RK4)
    - Class: Explicit single-step Runge-Kutta (ERK)
    - Order: 4
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/6 * (k₁ + 2k₂ + 2k₃ + k₄)
    - Source/Paper: C. Runge (1895) & W. Kutta (1901). Standard reference: E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.5, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
            ]
        )  # shape: (4, 4)
        b_vec = np.array([1 / 6, 1 / 3, 1 / 3, 1 / 6])  # shape: (4,)
        c_vec = np.array([0.0, 0.5, 0.5, 1.0])  # shape: (4,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class RK8_DOP853(ExplicitRungeKutta):
    """
    Explicit Runge-Kutta method of order 8.

    Notes
    -----
    • *Method details*
    - Name/Author: Dormand-Prince 8(5,3) (DOP853)
    - Class: Explicit single-step Runge-Kutta (ERK)
    - Order: 8
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h * ∑(bᵢ * kᵢ)[12 internal explicit stages]
    - Source/Paper: P.J. Prince, J.R. Dormand, "High order embedded Runge-Kutta formulae" (1981).
      E. Hairer, S.P. Nørsett, G. Wanner, "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        from scipy.integrate._ivp.dop853_coefficients import A, B, C

        b_vec = np.array(B)
        n_stages = len(b_vec)  # Для шага метода используется 12 стадий

        # В SciPy для DOP853 матрица A — это numpy-массив размера (16, 16).
        # Последние 4 стадии (13-16) используются SciPy для интерполяции (dense output).
        # Для классического шага (интегрирования) нам нужен только блок 12x12.
        a_mat = np.array(A)[:n_stages, :n_stages]
        c_vec = np.array(C)[:n_stages]

        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


# ==========================================
# 2. IMPLICIT RUNGE-KUTTA (IRK)
# ==========================================


class IRK1_LStable_ImplicitEuler(ImplicitRungeKutta):
    """
    Fully Implicit Runge-Kutta method of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Backward Euler method
    - Class: Fully Implicit Runge-Kutta (IRK)
    - Order: 1
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + h * f(tₙ₊₁, yₙ₊₁)
    - Source/Paper: Standard Backward Euler. E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[1.0]])  # shape: (1, 1)
        b_vec = np.array([1.0])  # shape: (1,)
        c_vec = np.array([1.0])  # shape: (1,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class IRK2_AStable_ImplicitMidpoint(ImplicitRungeKutta):
    """
    Fully Implicit Runge-Kutta method of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Implicit Midpoint Rule (Gauss-Legendre 1-stage)
    - Class: Fully Implicit Runge-Kutta (IRK)
    - Order: 2
    - Stability: A-stable (not L-stable)
    - Formula: yₙ₊₁ = yₙ + h * f(tₙ + h/2, (yₙ + yₙ₊₁)/2)
    - Source/Paper: Standard Gauss-Legendre 1-stage. E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[0.5]])  # shape: (1, 1)
        b_vec = np.array([1.0])  # shape: (1,)
        c_vec = np.array([0.5])  # shape: (1,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class IRK3_LStable_RadauIIA(ImplicitRungeKutta):
    """
    Fully Implicit Runge-Kutta method of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Radau IIA (2 stages)
    - Class: Fully Implicit Runge-Kutta (IRK)
    - Order: 3
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + h * (3/4*k₁ + 1/4*k₂) [Solved implicitly]
    - Source/Paper: B.L. Ehle, "On Padé approximations to the exponential function..." (1969). E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[5 / 12, -1 / 12], [3 / 4, 1 / 4]])  # shape: (2, 2)
        b_vec = np.array([3 / 4, 1 / 4])  # shape: (2,)
        c_vec = np.array([1 / 3, 1.0])  # shape: (2,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class IRK4_AStable_GaussLegendre(ImplicitRungeKutta):
    """
    Fully Implicit Runge-Kutta method of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Gauss-Legendre (2 stages)
    - Class: Fully Implicit Runge-Kutta (IRK)
    - Order: 4
    - Stability: A-stable
    - Formula: yₙ₊₁ = yₙ + h/2 * (k₁ + k₂) [Solved implicitly]
    - Source/Paper: J.C. Butcher, "Implicit Runge-Kutta processes" (1964). E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        sq3_6 = np.sqrt(3) / 6
        a_mat = np.array([[0.25, 0.25 - sq3_6], [0.25 + sq3_6, 0.25]])  # shape: (2, 2)
        b_vec = np.array([0.5, 0.5])  # shape: (2,)
        c_vec = np.array([0.5 - sq3_6, 0.5 + sq3_6])  # shape: (2,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class IRK5_LStable_RadauIIA(ImplicitRungeKutta):
    """
    Fully Implicit Runge-Kutta method of order 5.

    Notes
    -----
    • *Method details*
    - Name/Author: Radau IIA (3 stages)
    - Class: Fully Implicit Runge-Kutta (IRK)
    - Order: 5
    - Stability: L-stable (жестко-точный метод: последняя строка A равна вектору b)
    - Formula: yₙ₊₁ = yₙ + h * (b₁k₁ + b₂k₂ + b₃k₃) [Solved implicitly]
    - Source/Paper: B.L. Ehle (1969); E. Hairer, G. Wanner, "Solving ODEs II", 2nd ed., page 74.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:

        sq6 = np.sqrt(6.0)

        a_mat = np.array(
            [
                [
                    (88.0 - 7.0 * sq6) / 360.0,
                    (296.0 - 169.0 * sq6) / 1800.0,
                    (-2.0 + 3.0 * sq6) / 225.0,
                ],
                [
                    (296.0 + 169.0 * sq6) / 1800.0,
                    (88.0 + 7.0 * sq6) / 360.0,
                    (-2.0 - 3.0 * sq6) / 225.0,
                ],
                [(16.0 - sq6) / 36.0, (16.0 + sq6) / 36.0, 1.0 / 9.0],
            ]
        )  # shape: (3, 3)

        b_vec = np.array(
            [(16.0 - sq6) / 36.0, (16.0 + sq6) / 36.0, 1.0 / 9.0]
        )  # shape: (3,)

        c_vec = np.array([(4.0 - sq6) / 10.0, (4.0 + sq6) / 10.0, 1.0])  # shape: (3,)

        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


# ==========================================
# 3. DIAGONALLY IMPLICIT RUNGE-KUTTA (DIRK)
# ==========================================


class DIRK1_LStable_ImplicitEuler(DiagonallyImplicitRungeKutta):
    """
    Diagonally Implicit Runge-Kutta method of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Backward Euler method
    - Class: Diagonally Implicit Runge-Kutta (DIRK)
    - Order: 1
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + h * f(tₙ₊₁, yₙ₊₁)
    - Source/Paper: Standard DIRK formulation. E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[1.0]])  # shape: (1, 1)
        b_vec = np.array([1.0])  # shape: (1,)
        c_vec = np.array([1.0])  # shape: (1,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class DIRK2_AStable_CrankNicolson(DiagonallyImplicitRungeKutta):
    """
    Diagonally Implicit Runge-Kutta method of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Crank-Nicolson method (Trapezoidal rule)
    - Class: Diagonally Implicit Runge-Kutta (DIRK)
    - Order: 2
    - Stability: A-stable
    - Formula: yₙ₊₁ = yₙ + h/2 * (fₙ + fₙ₊₁) [1 explicit, 1 implicit stage]
    - Source/Paper: J. Crank, P. Nicolson (1947). E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array([[0.0, 0.0], [0.5, 0.5]])  # shape: (2, 2)
        b_vec = np.array([0.5, 0.5])  # shape: (2,)
        c_vec = np.array([0.0, 1.0])  # shape: (2,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class DIRK3_LStable_Alexander(DiagonallyImplicitRungeKutta):
    """
    Diagonally Implicit Runge-Kutta method of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Alexander's DIRK3
    - Class: Diagonally Implicit Runge-Kutta (DIRK)
    - Order: 3
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + h * ∑(bᵢ * kᵢ) [3 sequential implicit stages]
    - Source/Paper: R. Alexander, "Diagonally implicit Runge-Kutta methods for stiff O.D.E.'s", SINUM (1977).
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        alpha = 0.435866521508458999416019
        tau2 = (1 + alpha) / 2
        b1 = -0.25 * (6 * alpha**2 - 16 * alpha + 1)
        b2 = 0.25 * (6 * alpha**2 - 20 * alpha + 5)

        a_mat = np.array(
            [[alpha, 0.0, 0.0], [tau2 - alpha, alpha, 0.0], [b1, b2, alpha]]
        )  # shape: (3, 3)
        b_vec = np.array([b1, b2, alpha])  # shape: (3,)
        c_vec = np.array([alpha, tau2, 1.0])  # shape: (3,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


class DIRK4_LStable_Hairer(DiagonallyImplicitRungeKutta):
    """
    Diagonally Implicit Runge-Kutta method of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Hairer's DIRK4
    - Class: Diagonally Implicit Runge-Kutta (DIRK)
    - Order: 4
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + h * ∑(bᵢ * kᵢ) [5 sequential implicit stages]
    - Source/Paper: E. Hairer, G. Wanner, "Solving ODEs II", 2nd ed. (5-stage L-stable DIRK4).
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        a_mat = np.array(
            [
                [1 / 4, 0.0, 0.0, 0.0, 0.0],
                [1 / 2, 1 / 4, 0.0, 0.0, 0.0],
                [17 / 50, -1 / 25, 1 / 4, 0.0, 0.0],
                [371 / 1360, -137 / 2720, 15 / 544, 1 / 4, 0.0],
                [25 / 24, -49 / 48, 125 / 16, -85 / 12, 1 / 4],
            ]
        )  # shape: (5, 5)
        b_vec = np.array([25 / 24, -49 / 48, 125 / 16, -85 / 12, 1 / 4])  # shape: (5,)
        c_vec = np.array([1 / 4, 3 / 4, 11 / 20, 1 / 2, 1.0])  # shape: (5,)
        super().__init__(fun, t0, y0_vec, h, t_bound, a_mat, b_vec, c_vec, jac=jac)


# ==========================================
# 4. ROSENBROCK METHODS (Ros)
# ==========================================


class Ros1_LStable_LinearImplicitEuler(Rosenbrock):
    """
    Rosenbrock method of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Linearly Implicit Euler
    - Class: Rosenbrock method (Linearly Implicit RK)
    - Order: 1
    - Stability: L-stable
    - Formula: (I - h * J) * k₁ = h * fₙ; yₙ₊₁ = yₙ + k₁
    - Source/Paper: Linearized Backward Euler. E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        gamma = 1.0
        a_mat = np.array([[0.0]])  # shape: (1, 1)
        c_mat = np.array([[0.0]])  # shape: (1, 1)
        b_vec = np.array([1.0])  # shape: (1,)
        c_vec = np.array([1.0])  # shape: (1,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            a_mat,
            c_mat,
            b_vec,
            c_vec,
            gamma,
            jac=jac,
            df_dt=df_dt,
        )


class Ros2_LStable_Wanner(Rosenbrock):
    """
    Rosenbrock method of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Wanner's ROW2 (ROS2)
    - Class: Rosenbrock method (Linearly Implicit RK)
    - Order: 2
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + 0.5 * k₁ + 0.5 * k₂ [Linearized stages]
    - Source/Paper: G. Wanner, "ROW2". E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        gamma = 1.0 - 1.0 / np.sqrt(2.0)
        a_mat = np.array([[0.0, 0.0], [1.0 / (2.0 * gamma), 0.0]])  # shape: (2, 2)
        c_mat = np.array([[0.0, 0.0], [-1.0 / gamma, 0.0]])  # shape: (2, 2)
        b_vec = np.array([0.0, 1.0])  # shape: (2,)
        c_vec = np.array([0.0, 1.0])  # shape: (2,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            a_mat,
            c_mat,
            b_vec,
            c_vec,
            gamma,
            jac=jac,
            df_dt=df_dt,
        )


class Ros3_LStable_ROW3(Rosenbrock):
    """
    Rosenbrock method of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: L-stable 3-stage ROS3
    - Class: Rosenbrock method (Linearly Implicit RK)
    - Order: 3
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + b₁*k₁ + b₂*k₂ + b₃*k₃[Linearized stages]
    - Source/Paper: P. Kaps, P. Rentrop (1979) / E. Hairer, G. Wanner, "Solving ODEs II", 2nd ed.
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        gamma = 0.435866521508459
        a_mat = np.array(
            [
                [0.0, 0.0, 0.0],
                [0.5, 0.0, 0.0],
                [1.9257290547783918, -0.9257290547783918, 0.0],
            ]
        )  # shape: (3, 3)
        c_mat = np.zeros((3, 3))  # shape: (3, 3)
        b_vec = np.array(
            [0.9824924372530492, -0.0932518314891788, 0.1107593942361304]
        )  # shape: (3,)
        c_vec = np.array([0.0, 0.5, 1.0])  # shape: (3,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            a_mat,
            c_mat,
            b_vec,
            c_vec,
            gamma,
            jac=jac,
            df_dt=df_dt,
        )


class Ros4_LStable_RODAS3(Rosenbrock):
    """
    Rosenbrock method of order 3 (RODAS3 is actually 4-stage, 3rd order).

    Notes
    -----
    • *Method details*
    - Name/Author: RODAS3
    - Class: Rosenbrock method (Linearly Implicit RK)
    - Order: 3
    - Stability: L-stable
    - Source/Paper: A. Sandu et al., "Benchmarking stiff ODE solvers for atmospheric chemistry problems I" (1997).
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        gamma = 0.5
        a_mat = np.array(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [0.75, -0.25, 0.5, 0.0],
            ]
        )  # shape: (4, 4)
        c_mat = np.array(
            [
                [0.0, 0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0, 0.0],
                [-0.25, 0.5, 0.0, 0.0],
                [1 / 12, 1 / 12, -2 / 3, 0.0],
            ]
        )  # shape: (4, 4)
        b_vec = np.array([5 / 6, -1 / 6, -1 / 6, 0.5])  # shape: (4,)
        c_vec = np.array([0.0, 0.0, 1.0, 1.0])  # shape: (4,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            a_mat,
            c_mat,
            b_vec,
            c_vec,
            gamma,
            jac=jac,
            df_dt=df_dt,
        )


# ==========================================
# 5. ADAMS-BASHFORTH (Explicit Multistep)
# ==========================================


class AB1_CondStable_Euler(AdamsBashforth):
    """
    Adams-Bashforth explicit multi-step method of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Forward Euler (in multistep form)
    - Class: Explicit Multistep (Adams-Bashforth)
    - Order: 1
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h * fₙ
    - Source/Paper: J.C. Adams, F. Bashforth (1883). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        coeffs_vec = np.array([1.0])  # shape: (1,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 1, RK1_CondStable_Euler, coeffs_vec, jac=jac
        )


class AB2_CondStable_Adams(AdamsBashforth):
    """
    Adams-Bashforth explicit multi-step method of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Adams-Bashforth 2
    - Class: Explicit Multistep (Adams-Bashforth)
    - Order: 2
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/2 * (3fₙ - fₙ₋₁)
    - Source/Paper: J.C. Adams, F. Bashforth (1883). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        coeffs_vec = np.array([3 / 2, -1 / 2])  # shape: (2,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 2, RK2_CondStable_Heun, coeffs_vec, jac=jac
        )


class AB3_CondStable_Adams(AdamsBashforth):
    """
    Adams-Bashforth explicit multi-step method of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Adams-Bashforth 3
    - Class: Explicit Multistep (Adams-Bashforth)
    - Order: 3
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/12 * (23fₙ - 16fₙ₋₁ + 5fₙ₋₂)
    - Source/Paper: J.C. Adams, F. Bashforth (1883). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        coeffs_vec = np.array([23 / 12, -16 / 12, 5 / 12])  # shape: (3,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 3, RK3_CondStable_Kutta, coeffs_vec, jac=jac
        )


class AB4_CondStable_Adams(AdamsBashforth):
    """
    Adams-Bashforth explicit multi-step method of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Adams-Bashforth 4
    - Class: Explicit Multistep (Adams-Bashforth)
    - Order: 4
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/24 * (55fₙ - 59fₙ₋₁ + 37fₙ₋₂ - 9fₙ₋₃)
    - Source/Paper: J.C. Adams, F. Bashforth (1883). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        coeffs_vec = np.array([55 / 24, -59 / 24, 37 / 24, -9 / 24])  # shape: (4,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 4, RK4_CondStable_Classic, coeffs_vec, jac=jac
        )


# ==========================================
# 6. ADAMS-MOULTON (Implicit Multistep)
# ==========================================


class AM1_LStable_ImplicitEuler(AdamsMoulton):
    """
    Adams-Moulton implicit multi-step method of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Backward Euler (in multistep form)
    - Class: Implicit Multistep (Adams-Moulton)
    - Order: 1
    - Stability: L-stable
    - Formula: yₙ₊₁ = yₙ + h * fₙ₊₁
    - Source/Paper: F.R. Moulton (1926) / Backward Euler. E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        beta_0 = 1.0
        coeffs_vec = np.array([0.0])  # shape: (1,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            1,
            IRK1_LStable_ImplicitEuler,
            coeffs_vec,
            beta_0,
            jac=jac,
        )


class AM2_AStable_CrankNicolson(AdamsMoulton):
    """
    Adams-Moulton implicit multi-step method of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Crank-Nicolson (Trapezoidal rule)
    - Class: Implicit Multistep (Adams-Moulton)
    - Order: 2
    - Stability: A-stable
    - Formula: yₙ₊₁ = yₙ + h/2 * (fₙ₊₁ + fₙ)
    - Source/Paper: F.R. Moulton (1926) / Crank-Nicolson. E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        beta_0 = 0.5
        coeffs_vec = np.array([0.5])  # shape: (1,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            1,
            IRK2_AStable_ImplicitMidpoint,
            coeffs_vec,
            beta_0,
            jac=jac,
        )


class AM3_CondStable_Adams(AdamsMoulton):
    """
    Adams-Moulton implicit multi-step method of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Adams-Moulton 3
    - Class: Implicit Multistep (Adams-Moulton)
    - Order: 3
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/12 * (5fₙ₊₁ + 8fₙ - fₙ₋₁)
    - Source/Paper: F.R. Moulton (1926). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        beta_0 = 5 / 12
        coeffs_vec = np.array([8 / 12, -1 / 12])  # shape: (2,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            2,
            IRK3_LStable_RadauIIA,
            coeffs_vec,
            beta_0,
            jac=jac,
        )


class AM4_CondStable_Adams(AdamsMoulton):
    """
    Adams-Moulton implicit multi-step method of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Adams-Moulton 4
    - Class: Implicit Multistep (Adams-Moulton)
    - Order: 4
    - Stability: Conditionally stable
    - Formula: yₙ₊₁ = yₙ + h/24 * (9fₙ₊₁ + 19fₙ - 5fₙ₋₁ + fₙ₋₂)
    - Source/Paper: F.R. Moulton (1926). E. Hairer et al., "Solving ODEs I".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        beta_0 = 9 / 24
        coeffs_vec = np.array([19 / 24, -5 / 24, 1 / 24])  # shape: (3,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            3,
            IRK4_AStable_GaussLegendre,
            coeffs_vec,
            beta_0,
            jac=jac,
        )


# ==========================================
# 7. BACKWARD DIFFERENTIATION FORMULAS (Gear BDF)
# ==========================================


class BDF1_LStable_ImplicitEuler(GearBDF):
    """
    Backward Differentiation Formula of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear BDF1 (Backward Euler)
    - Class: Implicit Multistep (BDF)
    - Order: 1
    - Stability: L-stable (A(α)-stable with α = 90°)
    - Formula: yₙ₊₁ = yₙ + h * fₙ₊₁
    - Source/Paper: C.W. Gear, "Numerical Initial Value Problems in Ordinary Differential Equations" (1971). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        alpha_vec = np.array([1.0])  # shape: (1,)
        beta = 1.0
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            1,
            IRK1_LStable_ImplicitEuler,
            alpha_vec,
            beta,
            jac=jac,
        )


class BDF2_LStable_Gear(GearBDF):
    """
    Backward Differentiation Formula of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear BDF2
    - Class: Implicit Multistep (BDF)
    - Order: 2
    - Stability: L-stable (A(α)-stable with α = 90°)
    - Formula: yₙ₊₁ = 4/3 * yₙ - 1/3 * yₙ₋₁ + 2/3 * h * fₙ₊₁
    - Source/Paper: C.W. Gear (1971). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        alpha_vec = np.array([4 / 3, -1 / 3])  # shape: (2,)
        beta = 2 / 3
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            2,
            IRK2_AStable_ImplicitMidpoint,
            alpha_vec,
            beta,
            jac=jac,
        )


class BDF3_AAlphaStable_Gear(GearBDF):
    """
    Backward Differentiation Formula of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear BDF3
    - Class: Implicit Multistep (BDF)
    - Order: 3
    - Stability: A(α)-stable (α ≈ 86.03°)
    - Formula: yₙ₊₁ = 18/11 * yₙ - 9/11 * yₙ₋₁ + 2/11 * yₙ₋₂ + 6/11 * h * fₙ₊₁
    - Source/Paper: C.W. Gear (1971). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        alpha_vec = np.array([18 / 11, -9 / 11, 2 / 11])  # shape: (3,)
        beta = 6 / 11
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            3,
            IRK3_LStable_RadauIIA,
            alpha_vec,
            beta,
            jac=jac,
        )


class BDF4_AAlphaStable_Gear(GearBDF):
    """
    Backward Differentiation Formula of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear BDF4
    - Class: Implicit Multistep (BDF)
    - Order: 4
    - Stability: A(α)-stable (α ≈ 73.35°)
    - Formula: yₙ₊₁ = 48/25 * yₙ - 36/25 * yₙ₋₁ + 16/25 * yₙ₋₂ - 3/25 * yₙ₋₃ + 12/25 * h * fₙ₊₁
    - Source/Paper: C.W. Gear (1971). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        alpha_vec = np.array([48 / 25, -36 / 25, 16 / 25, -3 / 25])  # shape: (4,)
        beta = 12 / 25
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            4,
            IRK4_AStable_GaussLegendre,
            alpha_vec,
            beta,
            jac=jac,
        )


# ==========================================
# 8. GEAR NORDSIECK (BDF via Taylor Expansion)
# ==========================================


class Nordsieck1_LStable_ImplicitEuler(GearNordsieck):
    """
    Gear method in Nordsieck representation of order 1.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear Nordsieck 1
    - Class: Implicit Multistep (Nordsieck Form)
    - Order: 1
    - Stability: L-stable (A(α)-stable with α = 90°)
    - Formula: Equivalent to BDF1; stores zₙ = [yₙ, h*y'ₙ]ᵀ
    - Source/Paper: A. Nordsieck, "On numerical integration of ordinary differential equations" (1962). E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        l_vec = np.array([1.0, 1.0])  # shape: (2,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 1, l_vec, IRK1_LStable_ImplicitEuler, jac=jac
        )


class Nordsieck2_LStable_Gear(GearNordsieck):
    """
    Gear method in Nordsieck representation of order 2.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear Nordsieck 2
    - Class: Implicit Multistep (Nordsieck Form)
    - Order: 2
    - Stability: L-stable (A(α)-stable with α = 90°)
    - Formula: Equivalent to BDF2; stores zₙ =[yₙ, h*y'ₙ, (h²/2)*y''ₙ]ᵀ
    - Source/Paper: A. Nordsieck (1962). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        l_vec = np.array([2 / 3, 1.0, 1 / 3])  # shape: (3,)
        super().__init__(
            fun,
            t0,
            y0_vec,
            h,
            t_bound,
            2,
            l_vec,
            IRK2_AStable_ImplicitMidpoint,
            jac=jac,
        )


class Nordsieck3_AAlphaStable_Gear(GearNordsieck):
    """
    Gear method in Nordsieck representation of order 3.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear Nordsieck 3
    - Class: Implicit Multistep (Nordsieck Form)
    - Order: 3
    - Stability: A(α)-stable (α ≈ 86.03°)
    - Formula: Equivalent to BDF3; stores zₙ = [yₙ, ..., (h³/6)*y'''ₙ]ᵀ
    - Source/Paper: A. Nordsieck (1962). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        l_vec = np.array([6 / 11, 1.0, 6 / 11, 1 / 11])  # shape: (4,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 3, l_vec, IRK3_LStable_RadauIIA, jac=jac
        )


class Nordsieck4_AAlphaStable_Gear(GearNordsieck):
    """
    Gear method in Nordsieck representation of order 4.

    Notes
    -----
    • *Method details*
    - Name/Author: Gear Nordsieck 4
    - Class: Implicit Multistep (Nordsieck Form)
    - Order: 4
    - Stability: A(α)-stable (α ≈ 73.35°)
    - Formula: Equivalent to BDF4; stores zₙ = [yₙ, ..., (h⁴/24)*y⁽⁴⁾ₙ]ᵀ
    - Source/Paper: A. Nordsieck (1962). Reference: E. Hairer, G. Wanner, "Solving ODEs II".
    """

    def __init__(
        self,
        fun: Callable[[float, np.ndarray], np.ndarray],
        t0: float,
        y0_vec: np.ndarray,
        h: float,
        t_bound: float,
        *,
        jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
        df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    ) -> None:
        l_vec = np.array([12 / 25, 1.0, 7 / 10, 1 / 5, 1 / 50])  # shape: (5,)
        super().__init__(
            fun, t0, y0_vec, h, t_bound, 4, l_vec, IRK4_AStable_GaussLegendre, jac=jac
        )


# Global registry of available ODE solvers
# Maps string identifiers to their corresponding solver classes


@dataclass(frozen=True)
class ODEMethodInfo:
    cls: Type[Any]
    order: int
    stability_type: str


ODE_METHODS: Dict[str, ODEMethodInfo] = {
    # Ключ идентификатора                 Класс реализации                          Порядок    Тип устойчивости
    # ------------------------------------------------------------------------------------------------------
    # Explicit Runge-Kutta
    "RK1_CondStable_Euler": ODEMethodInfo(
        RK1_CondStable_Euler, 1, "Conditionally Stable"
    ),
    "RK2_CondStable_Heun": ODEMethodInfo(
        RK2_CondStable_Heun, 2, "Conditionally Stable"
    ),
    "RK3_CondStable_Kutta": ODEMethodInfo(
        RK3_CondStable_Kutta, 3, "Conditionally Stable"
    ),
    "RK4_CondStable_Classic": ODEMethodInfo(
        RK4_CondStable_Classic, 4, "Conditionally Stable"
    ),
    "RK8_DOP853": ODEMethodInfo(RK8_DOP853, 5, "Conditionally Stable"),
    # Implicit non-linear (IRK / DIRK)
    "IRK1_LStable_ImplicitEuler": ODEMethodInfo(
        IRK1_LStable_ImplicitEuler, 1, "L-Stable"
    ),
    "IRK2_AStable_ImplicitMidpoint": ODEMethodInfo(
        IRK2_AStable_ImplicitMidpoint, 2, "A-Stable"
    ),
    "IRK3_LStable_RadauIIA": ODEMethodInfo(IRK3_LStable_RadauIIA, 3, "L-Stable"),
    "IRK4_AStable_GaussLegendre": ODEMethodInfo(
        IRK4_AStable_GaussLegendre, 4, "A-Stable"
    ),
    "IRK5_LStable_RadauIIA": ODEMethodInfo(IRK5_LStable_RadauIIA, 5, "L-Stable"),
    "DIRK1_LStable_ImplicitEuler": ODEMethodInfo(
        DIRK1_LStable_ImplicitEuler, 1, "L-Stable"
    ),
    "DIRK2_AStable_CrankNicolson": ODEMethodInfo(
        DIRK2_AStable_CrankNicolson, 2, "A-Stable"
    ),
    "DIRK3_LStable_Alexander": ODEMethodInfo(DIRK3_LStable_Alexander, 3, "L-Stable"),
    "DIRK4_LStable_Hairer": ODEMethodInfo(DIRK4_LStable_Hairer, 4, "L-Stable"),
    # Linearly implicit (Rosenbrock)
    "Ros1_LStable_LinearImplicitEuler": ODEMethodInfo(
        Ros1_LStable_LinearImplicitEuler, 1, "L-Stable"
    ),
    "Ros2_LStable_Wanner": ODEMethodInfo(Ros2_LStable_Wanner, 2, "L-Stable"),
    "Ros3_LStable_ROW3": ODEMethodInfo(Ros3_LStable_ROW3, 3, "L-Stable"),
    "Ros4_LStable_RODAS3": ODEMethodInfo(Ros4_LStable_RODAS3, 4, "L-Stable"),
    # Multistep Explicit (Adams-Bashforth)
    "AB1_CondStable_Euler": ODEMethodInfo(
        AB1_CondStable_Euler, 1, "Conditionally Stable"
    ),
    "AB2_CondStable_Adams": ODEMethodInfo(
        AB2_CondStable_Adams, 2, "Conditionally Stable"
    ),
    "AB3_CondStable_Adams": ODEMethodInfo(
        AB3_CondStable_Adams, 3, "Conditionally Stable"
    ),
    "AB4_CondStable_Adams": ODEMethodInfo(
        AB4_CondStable_Adams, 4, "Conditionally Stable"
    ),
    # Multistep Implicit (Adams-Moulton)
    "AM1_LStable_ImplicitEuler": ODEMethodInfo(
        AM1_LStable_ImplicitEuler, 1, "L-Stable"
    ),
    "AM2_AStable_CrankNicolson": ODEMethodInfo(
        AM2_AStable_CrankNicolson, 2, "A-Stable"
    ),
    "AM3_CondStable_Adams": ODEMethodInfo(
        AM3_CondStable_Adams, 3, "Conditionally Stable"
    ),
    "AM4_CondStable_Adams": ODEMethodInfo(
        AM4_CondStable_Adams, 4, "Conditionally Stable"
    ),
    # Multistep BDF (Gear)
    "BDF1_LStable_ImplicitEuler": ODEMethodInfo(
        BDF1_LStable_ImplicitEuler, 1, "L-Stable"
    ),
    "BDF2_LStable_Gear": ODEMethodInfo(BDF2_LStable_Gear, 2, "L-Stable"),
    "BDF3_AAlphaStable_Gear": ODEMethodInfo(
        BDF3_AAlphaStable_Gear, 3, "A(alpha)-Stable"
    ),
    "BDF4_AAlphaStable_Gear": ODEMethodInfo(
        BDF4_AAlphaStable_Gear, 4, "A(alpha)-Stable"
    ),
    # Nordsieck Form
    "Nordsieck1_LStable_ImplicitEuler": ODEMethodInfo(
        Nordsieck1_LStable_ImplicitEuler, 1, "L-Stable"
    ),
    "Nordsieck2_LStable_Gear": ODEMethodInfo(Nordsieck2_LStable_Gear, 2, "L-Stable"),
    "Nordsieck3_AAlphaStable_Gear": ODEMethodInfo(
        Nordsieck3_AAlphaStable_Gear, 3, "A(alpha)-Stable"
    ),
    "Nordsieck4_AAlphaStable_Gear": ODEMethodInfo(
        Nordsieck4_AAlphaStable_Gear, 4, "A(alpha)-Stable"
    ),
}


# Функция-решатель
def solve_ode(
    fun: Callable[[float, np.ndarray], np.ndarray],
    t_span: Tuple[float, float],
    y0_vec: np.ndarray,
    *,
    method_class: Type[Any] = RK4_CondStable_Classic,
    h: float = 0.01,
    jac: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
    df_dt: Optional[Callable[[float, np.ndarray], np.ndarray]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Solves an Initial Value Problem (IVP) for a system of ordinary differential equations (ODEs).

    Parameters
    ----------
    - fun : Callable[[float, ndarray], ndarray]
        Right-hand side of the ODE system: f(t, y).
    - t_span : Tuple[float, float]
        Interval of integration (t0, t_bound).
    - y0_vec : (N,) array_like
        Initial state vector.
    - method_class : Type[Any], optional
        Direct reference to the solver class to be instantiated. Defaults to RK4_CondStable_Classic.
    - h : float, optional
        Integration step size.
    - jac : Callable[[float, ndarray], ndarray], optional
        Analytical Jacobian function J(t, y) = ∂f/∂y.
    - df_dt : Callable[[float, ndarray], ndarray], optional
        Partial derivative of the right-hand side with respect to time: ∂f/∂t.

    Returns
    -------
    - t_arr : (K,) ndarray
        Array containing the time points of the integration trajectory.
    - y_mat : (K, N) ndarray
        Matrix containing the computed states at each time point.

    Notes
    -----
    • *Algorithm workflow*
    1. Parse the integration boundaries and format the initial state vector.
    2. Instantiate the provided solver class (`method_class`) with the specified parameters.
    3. Execute the internal integration loop of the solver.
    """

    # --- Step 1: Initialization ---
    t0, t_bound = t_span

    # Ensure the initial state is a floating-point numpy array
    y0_vec = np.asarray(y0_vec, dtype=np.float64)  # shape: (N,)

    # --- Step 2: Solver Instantiation ---
    # Instantiate the solver directly from the passed class reference
    solver = method_class(
        fun=fun, t0=t0, y0_vec=y0_vec, h=h, t_bound=t_bound, jac=jac, df_dt=df_dt
    )

    # --- Step 3: Integration ---
    # Integrate to get the full trajectory
    t_arr, y_mat = solver.integrate()  # shapes: (K,), (K, N)

    return t_arr, y_mat
