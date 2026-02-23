import numpy as np
import warnings

# Helper


def _get_stop_threshold(b_norm, atol=0., rtol=1e-5):
    return max(atol, rtol * b_norm)


def solve_triangular(A, b, type=None):
    """
    Solves the linear system A @ X = B for a triangular matrix A.

    See https://books.mipt.ru/book/301568

    Parameters
    ----------
    - A : (M, M) ndarray
        Triangular matrix (lower or upper).
    - b : (M,) or (M, K) array_like
        Vector or matrix of right-hand sides.
    - type : {'lower', 'upper'}
        Type of the triangular matrix A.
        - 'lower' : A is lower triangular (default), uses forward substitution.
        - 'upper' : A is upper triangular, uses backward substitution.

    Returns
    -------
    - x : (M,) or (M, K) ndarray
        Solution of the system. Shape matches b.

    Notes
    -----
    • *Working hypotheses*
    - Matrix A is non-singular (diagonal elements ≠ 0).

    • *Algorithm workflow*
    - If type='lower': xᵢ = (bᵢ - ∑_{j=0}^{i-1} A_{ij}xⱼ) / A_{ii}
    - If type='upper': xᵢ = (bᵢ - ∑_{j=i+1}^{n-1} A_{ij}xⱼ) / A_{ii}
    """
    # ----------------------------------
    # 1. Input Processing
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    is_vector = b.ndim == 1
    if is_vector:
        # Temporarily reshape vector to column-matrix for universality
        # Shape: (M, 1)
        b = b.reshape(-1, 1)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")
    if A.shape[0] != b.shape[0]:
        raise ValueError("Incompatible dimensions of A and b.")

    # ----------------------------------
    # 2. Main Algorithm
    # ----------------------------------
    n = A.shape[0]
    x = b.copy()

    if type == 'lower':
        # Forward substitution
        for i in range(n):
            # Shape: scalar
            dot_product = np.dot(A[i, :i], x[:i])
            x[i] = (x[i] - dot_product) / A[i, i]

    elif type == 'upper':
        # Backward substitution
        for i in range(n - 1, -1, -1):
            # Shape: scalar
            dot_product = np.dot(A[i, i+1:], x[i+1:])
            x[i] = (x[i] - dot_product) / A[i, i]

    else:
        raise ValueError("Parameter 'type' must be 'lower' or 'upper'.")

    # ----------------------------------
    # 3. Return Result
    # ----------------------------------
    if is_vector:
        return x.ravel()  # Convert (M, 1) back to (M,)
    else:
        return x


def solve_gauss(A, b, pivoting='full'):
    """
    Solves the linear system A @ x = b using Gaussian elimination with pivoting.
    Supports both vector b and matrix B right-hand sides.

    See https://books.mipt.ru/book/301568

    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) or (M, K) array_like
        Vector or matrix of right-hand sides.
    - pivoting : {'full', 'partial'}
        Pivoting strategy:
        - 'full' : Search for pivot in the entire submatrix (default).
        - 'partial' : Search for pivot in the current column.

    Returns
    -------
    - x : (M,) or (M, K) ndarray
        Solution of the system. Shape matches b.

    Notes
    -----
    • *Algorithm workflow*
    1. **Forward Elimination**: Transform A to upper triangular form.
       - Select pivot element based on strategy.
       - Swap rows (and columns for full pivoting).
       - Eliminate elements below pivot.
    2. **Backward Substitution**: Solve the resulting triangular system.
    3. **Restoration**: Restore variable order if full pivoting was used.
    """
    # np.result_type ensures that if A or b are complex, dtype will be complex
    # If both are float/int, dtype will be float64
    dtype = np.result_type(A, b, np.float64)
    A = np.asarray(A, dtype=dtype)
    b = np.asarray(b, dtype=dtype)

    # ----------------------------------
    # 1. Input/Output Shape Processing
    # ----------------------------------
    is_vector = b.ndim == 1
    if is_vector:
        # Temporarily reshape vector to column-matrix for universality
        # Shape: (M, 1)
        b = b.reshape(-1, 1)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix must be square")
    if A.shape[0] != b.shape[0]:
        raise ValueError("Incompatible dimensions of A and b")

    n = A.shape[0]
    A = A.copy()
    b_copy = b.copy()

    # Singularity check
    matrix_max_abs = np.max(np.abs(A))

    singularity_threshold = matrix_max_abs * np.finfo(np.float64).eps * n

    if matrix_max_abs < singularity_threshold:
        raise ValueError(
            f"Singular matrix, abs(A[{n-1}, {n-1}])="
            f"{np.abs(A[n-1, n-1])}, "
            f"threshold={singularity_threshold}"
        )

    # Permutation vector to track variable order when pivoting == 'full'
    # permutations[i] = j means i-th column corresponds to variable x_j
    permutations = np.arange(n)

    # ----------------------------------
    # 2. Forward Elimination
    # ----------------------------------

    for pivot_idx in range(n - 1):
        pivot_row, pivot_col = pivot_idx, pivot_idx

        # ==================================
        # 2a. Pivot Search
        # ==================================

        if pivoting == 'partial':
            # Search for max in current column, starting from pivot_idx row
            sub_matrix = A[pivot_idx:, pivot_idx]
            relative_row_idx = np.argmax(np.abs(sub_matrix))
            pivot_row = pivot_idx + relative_row_idx

        elif pivoting == 'full':
            # Search for max in remaining submatrix
            sub_matrix = A[pivot_idx:, pivot_idx:]
            relative_row_idx, relative_col_idx = np.unravel_index(
                np.argmax(np.abs(sub_matrix)),
                sub_matrix.shape
            )
            pivot_row = pivot_idx + relative_row_idx
            pivot_col = pivot_idx + relative_col_idx

        else:
            raise ValueError('Invalid pivoting strategy')

        # ==================================
        # 2b. Permutations
        # ==================================

        if pivot_row != pivot_idx:  # Swap rows
            A[[pivot_idx, pivot_row], :] = A[[pivot_row, pivot_idx], :]
            b_copy[[pivot_idx, pivot_row]] = b_copy[[pivot_row, pivot_idx]]

        if pivoting == 'full' and pivot_col != pivot_idx:  # Swap columns
            A[:, [pivot_idx, pivot_col]] = A[:, [pivot_col, pivot_idx]]
            permutations[[pivot_idx, pivot_col]] = permutations[[pivot_col, pivot_idx]]

        # Singularity check
        if np.abs(A[pivot_idx, pivot_idx]) < singularity_threshold:
            raise ValueError(
                f"Singular matrix, abs(A[{pivot_idx}, {pivot_idx}])="
                f"{np.abs(A[pivot_idx, pivot_idx])}, "
                f"threshold={singularity_threshold}"
            )

        # ==================================
        # 2c. Elimination
        # ==================================

        factors = A[pivot_idx+1:, pivot_idx] / A[pivot_idx, pivot_idx]
        # Shape: (N-k-1, N-k)
        A[pivot_idx+1:, pivot_idx:] -= np.outer(factors, A[pivot_idx, pivot_idx:])

        # Broadcasting for b_copy (works if b_copy is a matrix)
        # Shape: (N-k-1, K)
        b_copy[pivot_idx+1:] -= factors[:, np.newaxis] * b_copy[pivot_idx]

    # Check last element for singularity
    if np.abs(A[n - 1, n - 1]) < singularity_threshold:
        raise ValueError(
            f"Singular matrix, abs(A[{n-1}, {n-1}])="
            f"{np.abs(A[n-1, n-1])}, "
            f"threshold={singularity_threshold}"
        )

    # ----------------------------------
    # 3. Backward Substitution
    # ----------------------------------

    x_solution = solve_triangular(A, b_copy, type='upper')

    # ----------------------------------
    # 4. Restoration of Order and Shape
    # ----------------------------------
    if pivoting == 'full':
        sorted_x = np.zeros_like(x_solution)
        sorted_x[permutations] = x_solution
        final_solution = sorted_x
    else:
        final_solution = x_solution

    # Return result in original shape
    if is_vector:
        return final_solution.reshape(-1)  # Convert (M, 1) back to (M,)
    else:
        return final_solution


def solve_lu(PLU, b):
    """
    Solves the linear system A @ x = b using LU decomposition (PA = LU).

    Parameters
    ----------
    - PLU : tuple (P, L, U)
        Result from lu_factor():
        - P : (M, M) ndarray - Permutation matrix.
        - L : (M, M) ndarray - Lower triangular matrix.
        - U : (M, M) ndarray - Upper triangular matrix.
    - b : (M,) array_like
        Vector of right-hand sides.

    Returns
    -------
    - x : (M,) ndarray
        Solution of the system.

    Notes
    -----
    • *Algorithm workflow*
    1. Solve L @ y = P @ b (Forward substitution).
    2. Solve U @ x = y (Backward substitution).
    """
    P, L, U = PLU
    b = np.asarray(b, dtype=np.float64)

    # ----------------------------------
    # 1. Forward Substitution
    # ----------------------------------
    # Solve L @ y = P @ b
    b_permuted = P @ b
    y = solve_triangular(L, b_permuted, type='lower')

    # ----------------------------------
    # 2. Backward Substitution
    # ----------------------------------
    # Solve U @ x = y
    x = solve_triangular(U, y, type='upper')

    return x


def lu_factor(A):
    """
    Computes LU decomposition with partial pivoting: P @ A = L @ U.


    Parameters
    ----------
    - A : (M, M) array_like
        Matrix to decompose.

    Returns
    -------
    - P : (M, M) ndarray
        Permutation matrix.
    - L : (M, M) ndarray
        Lower triangular matrix with unit diagonal.
    - U : (M, M) ndarray
        Upper triangular matrix.

    Notes
    -----
    • *Algorithm workflow*
    1. Initialize P, L, U.
    2. Iterate through columns k=0 to n-2:
       - Find pivot in column k.
       - Swap rows in A and P.
       - Compute multipliers for L.
       - Update submatrix of A (Schur complement).
    """
    # ----------------------------------
    # 1. Initialization
    # ----------------------------------
    A = np.asarray(A)
    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix must be square")

    n = A.shape[0]

    # Create a copy of the matrix to be transformed into compact LU form
    lu_matrix = A.copy()

    # Initialize permutation vector
    piv = np.arange(n)

    # Singularity threshold
    matrix_max_abs = np.max(np.abs(A))
    if matrix_max_abs == 0:
        raise ValueError("Singular matrix")
    singularity_threshold = matrix_max_abs * np.finfo(np.float64).eps * n

    # ----------------------------------
    # 2. Main Decomposition Loop
    # ----------------------------------
    for k in range(n - 1):
        # Pivot search (partial pivoting)
        i_max = k + np.argmax(np.abs(lu_matrix[k:, k]))

        if i_max != k:
            # Swap rows in working matrix
            lu_matrix[[k, i_max], :] = lu_matrix[[i_max, k], :]
            # Record permutation
            piv[[k, i_max]] = piv[[i_max, k]]

        # Singularity check
        pivot_element = lu_matrix[k, k]
        if abs(pivot_element) < singularity_threshold:
            raise ValueError(f"Singular matrix, pivot at index {k} is near zero.")

        # Compute multipliers for L and store them in-place
        factors = lu_matrix[k+1:, k] / pivot_element
        lu_matrix[k+1:, k] = factors

        # Update remaining submatrix
        # Shape: (N-k-1, N-k-1)
        lu_matrix[k+1:, k+1:] -= np.outer(factors, lu_matrix[k, k+1:])

    # ----------------------------------
    # 3. Form P, L, U Matrices
    # ----------------------------------

    # L: lower triangular with unit diagonal
    L = np.tril(lu_matrix, k=-1) + np.eye(n, dtype=np.float64)

    # U: upper triangular
    U = np.triu(lu_matrix)

    # P: permutation matrix from vector piv
    P = np.eye(n, dtype=np.float64)[piv, :]

    return P, L, U


def inverse(A):
    """
    Computes the inverse matrix A⁻¹ using LU decomposition.

    Parameters
    ----------
    - A : (M, M) array_like
        Square matrix.

    Returns
    -------
    - A_inv : (M, M) ndarray
        Inverse matrix A⁻¹.
    """
    return solve_lu(lu_factor(A), np.eye(A.shape[0]))


# Итерационные методы
def solve_jacobi(A, b, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using the Jacobi method.


    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - x0 : (M,) array_like, optional
        Initial guess. If None, zero vector is used.
    - rtol, atol : float, optional
        Relative and absolute tolerances for stopping criterion.
    - maxiter : int, optional
        Maximum number of iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution of the system.
    - info : int
        Convergence info:
        - >0 : Success (number of iterations).
        - 0  : Convergence not reached within `maxiter`.
    - r_norm_arr: List[float]
        History of residual norms.

    Notes
    -----
    • *Mathematical foundation*
    - Decomposition: A = L + D + U
    - Iteration: x⁽ᵏ⁺¹⁾ = D⁻¹(b - (L + U)x⁽ᵏ⁾)

    • *Algorithm workflow*
    1. Initialize x₀.
    2. Compute D⁻¹ and (L+U).
    3. Iterate until ||Ax - b|| < max(atol, rtol * ||b||).
    """
    # ----------------------------------
    # 1. Initialization and Decomposition
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    b_norm = np.linalg.norm(b)
    stop_threshold = _get_stop_threshold(b_norm, atol=atol, rtol=rtol)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")

    n = A.shape[0]

    if x0 is None:
        x = np.zeros(n, dtype=np.float64)
    else:
        x = np.asarray(x0, dtype=np.float64).copy()

    # Decompose A = L + D + U
    diag_A_vec = np.diag(A)
    if np.any(np.isclose(diag_A_vec, 0)):
        raise ValueError("Method not applicable: zero elements on the main diagonal.")

    # D_inv is a diagonal matrix with 1/diag_A.
    # Computing full D and inverting it via np.linalg.inv() is inefficient.
    D_inv = np.diag(1 / diag_A_vec)

    # L_plus_U is A without the diagonal
    L_plus_U = A - np.diag(diag_A_vec)

    # Residual norm history
    r_norm_arr = []

    # ----------------------------------
    # 2. Main Iteration Loop
    # ----------------------------------
    for iter_counter in range(maxiter):

        # x_new = D_inv @ (b - (L+U) @ x_old)
        x = D_inv @ (b - L_plus_U @ x)

        # Check stopping criterion
        r_norm = np.linalg.norm(A @ x - b)
        r_norm_arr.append(r_norm)
        if r_norm < stop_threshold:
            return x, iter_counter + 1, r_norm_arr  # Success

    return x, 0, r_norm_arr  # Convergence not reached


def solve_sor(A, b, omega, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using Successive Over-Relaxation (SOR).


    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - omega : float
        Relaxation parameter (0 < omega < 2).
    - x0 : (M,) array_like, optional
        Initial guess.
    - rtol, atol : float, optional
        Tolerances.
    - maxiter : int, optional
        Max iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution.
    - info : int
        Convergence info.
    - r_norm_arr: List[float]
        Residual history.

    Notes
    -----
    • *Mathematical foundation*
    - A = D + L + U
    - Iteration: (D + ωL)x⁽ᵏ⁺¹⁾ = ((1 - ω)D - ωU)x⁽ᵏ⁾ + ωb

    • *Algorithm workflow*
    1. Precompute M = D + ωL and N = (1 - ω)D - ωU.
    2. Solve triangular system M @ x_new = N @ x_old + ωb at each step.
    """
    # ----------------------------------
    # 1. Initialization and Checks
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    b_norm = np.linalg.norm(b)
    stop_threshold = _get_stop_threshold(b_norm, atol=atol, rtol=rtol)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")
    if not (0 < omega < 2):
        raise ValueError("Parameter omega must be in (0, 2).")

    n = A.shape[0]

    if x0 is None:
        x = np.zeros(n, dtype=np.float64)
    else:
        x = np.asarray(x0, dtype=np.float64).copy()

    # ----------------------------------
    # 2. Precompute Iteration Matrices
    # ----------------------------------
    D = np.diag(np.diag(A))
    if np.any(np.isclose(np.diag(D), 0)):
        raise ValueError("Method not applicable: zero elements on the main diagonal.")

    L = np.tril(A, k=-1)
    U = np.triu(A, k=1)

    # M @ x^(k+1) = N @ x^k + c
    M = D + omega * L
    N = (1 - omega) * D - omega * U
    c = omega * b

    # Residual norm history
    r_norm_arr = []

    # ----------------------------------
    # 3. Main Iteration Loop
    # ----------------------------------
    for iter_counter in range(maxiter):

        # Solve lower triangular system M @ x = N @ x + c
        x = solve_triangular(M, N @ x + c, type='lower')

        r_norm = np.linalg.norm(A @ x - b)
        r_norm_arr.append(r_norm)

        # Check stopping criterion
        if r_norm < stop_threshold:
            return x, iter_counter + 1, r_norm_arr  # Success

    return x, 0, r_norm_arr  # Not converged


def solve_seidel(A, b, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using the Gauss-Seidel method.


    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - x0 : (M,) array_like, optional
        Initial guess.
    - rtol, atol : float, optional
        Tolerances.
    - maxiter : int, optional
        Max iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution.
    - info : int
        Convergence info.
    - r_norm_arr: List[float]
        Residual history.

    Notes
    -----
    Wrapper for solve_sor with omega = 1.0.
    """
    # Call solve_sor with fixed omega = 1.0
    return solve_sor(A, b, omega=1.0, x0=x0, rtol=rtol, atol=atol, maxiter=maxiter)


def solve_gradient_descent(A, b, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using the Steepest Descent Method.

    Parameters
    ----------
    - A : (M, M) array_like
        Symmetric positive-definite coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - x0 : (M,) array_like, optional
        Initial guess.
    - rtol, atol : float, optional
        Tolerances.
    - maxiter : int, optional
        Max iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution.
    - info : int
        Convergence info:
        - >0 : Success.
        - 0  : Not converged.
        - -1 : Matrix not symmetric.
    - r_norm_arr: List[float]
        Residual history.

    Notes
    -----
    • *Algorithm workflow*
    1. Compute residual: rₖ = A @ xₖ - b
    2. Compute step size: τₖ = (rₖᵀ rₖ) / (rₖᵀ A rₖ)
    3. Update solution: xₖ₊₁ = xₖ - τₖ rₖ
    """
    # ----------------------------------
    # 1. Initialization and Checks
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")

    # Symmetry check - required condition
    if not np.allclose(A, A.T):
        warnings.warn("Matrix is not symmetric. Gradient descent not applicable.",
                      RuntimeWarning)
        return np.full_like(b, np.nan), -1

    n = A.shape[0]
    if x0 is None:
        x = np.zeros(n, dtype=np.float64)
    else:
        x = np.asarray(x0, dtype=np.float64).copy()

    # ----------------------------------
    # 2. Main Iteration Loop
    # ----------------------------------

    # Stopping criterion: ||A@x - b|| <= atol + rtol*||b||
    b_norm = np.linalg.norm(b)
    stop_threshold = _get_stop_threshold(b_norm, atol=atol, rtol=rtol)

    # Initial residual
    r = A @ x - b

    r_norm_arr = []

    for iter_counter in range(maxiter):

        r_norm = np.linalg.norm(r)
        r_norm_arr.append(r_norm)

        # Check convergence
        if r_norm < stop_threshold:
            return x, iter_counter + 1, r_norm_arr  # Success

        Ar = A @ r

        # tau = (r.T @ r) / (r.T @ A @ r)
        tau_numerator = np.dot(r, r)
        tau_denominator = np.dot(r, Ar)

        # Protection against division by zero
        if tau_denominator == 0:
            return x, iter_counter + 1, r_norm_arr  # Exact solution found

        tau = tau_numerator / tau_denominator

        # Update solution and residual
        x = x - tau * r
        r = r - tau * Ar

    r_norm = np.linalg.norm(r)
    r_norm_arr.append(r_norm)

    # Final check
    if r_norm < stop_threshold:
        return x, maxiter, r_norm_arr

    return x, 0, r_norm_arr  # Not converged


def solve_mres(A, b, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using the Minimal Residual Method (MRES).

    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - x0 : (M,) array_like, optional
        Initial guess.
    - rtol, atol : float, optional
        Tolerances.
    - maxiter : int, optional
        Max iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution.
    - info : int
        Convergence info.
    - r_norm_arr: List[float]
        Residual history.

    Notes
    -----
    • *Algorithm workflow*
    1. Compute residual: rₖ = A @ xₖ - b
    2. Compute step size: τₖ = (Arₖ, rₖ) / (Arₖ, Arₖ)
    3. Update solution: xₖ₊₁ = xₖ - τₖ rₖ
    """
    # ----------------------------------
    # 1. Initialization and Checks
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")

    n = A.shape[0]
    if x0 is None:
        x = np.zeros(n, dtype=np.float64)
    else:
        x = np.asarray(x0, dtype=np.float64).copy()

    # ----------------------------------
    # 2. Main Iteration Loop
    # ----------------------------------

    # Stopping criterion
    b_norm = np.linalg.norm(b)
    stop_threshold = _get_stop_threshold(b_norm, atol=atol, rtol=rtol)

    # Initial residual
    r = A @ x - b

    r_norm_arr = []

    # ----------------------------------
    # 3. Main Iteration Loop
    # ----------------------------------
    for iter_counter in range(maxiter):

        r_norm = np.linalg.norm(r)
        r_norm_arr.append(r_norm)

        # Check convergence
        if r_norm < stop_threshold:
            return x, iter_counter + 1, r_norm_arr  # Success

        # 1. Compute A @ r_k
        Ar = A @ r

        # 2. Compute optimal step tau_k
        # tau = (Ar.T @ r) / (Ar.T @ Ar)
        tau_numerator = np.dot(Ar, r)
        tau_denominator = np.dot(Ar, Ar)

        # Protection against division by zero
        if tau_denominator == 0:
            return x, iter_counter + 1, r_norm_arr  # Exact solution found

        tau = tau_numerator / tau_denominator

        # 3. Update solution and residual
        x = x - tau * r
        r = r - tau * Ar  # Efficient residual update

    r_norm = np.linalg.norm(r)
    r_norm_arr.append(r_norm)

    # Final check
    if r_norm < stop_threshold:
        return x, maxiter, r_norm_arr

    return x, 0, r_norm_arr  # Not converged


def solve_conjugate_gradient(A, b, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using the Conjugate Gradient (CG) method.

    Parameters
    ----------
    - A : (M, M) array_like
        Symmetric positive-definite coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - x0 : (M,) array_like, optional
        Initial guess.
    - rtol, atol : float, optional
        Tolerances.
    - maxiter : int, optional
        Max iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution.
    - info : int
        Convergence info:
        - >0 : Success.
        - 0  : Not converged.
        - -1 : Matrix not symmetric.
    - r_norm_arr: List[float]
        Residual history.

    Notes
    -----
    • *Algorithm workflow*
    1. Initialize: r₀ = Ax₀ - b, p₀ = r₀
    2. Loop k = 0, 1, ...
       a. τₖ = (rₖᵀ rₖ) / (pₖᵀ A pₖ)
       b. xₖ₊₁ = xₖ - τₖ pₖ
       c. rₖ₊₁ = rₖ - τₖ A pₖ
       d. βₖ = (rₖ₊₁ᵀ rₖ₊₁) / (rₖᵀ rₖ)
       e. pₖ₊₁ = rₖ₊₁ + βₖ pₖ
    """
    # ----------------------------------
    # 1. Initialization and Checks
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")

    # Symmetry check
    if not np.allclose(A, A.T):
        warnings.warn("Matrix is not symmetric. CG method not applicable.",
                      RuntimeWarning)
        return np.full_like(b, np.nan), -1

    n = A.shape[0]
    if x0 is None:
        x = np.zeros(n, dtype=np.float64)
    else:
        x = np.asarray(x0, dtype=np.float64).copy()

    # ----------------------------------
    # 2. Preparation
    # ----------------------------------

    # Stopping criterion
    b_norm = np.linalg.norm(b)
    stop_threshold = _get_stop_threshold(b_norm, atol=atol, rtol=rtol)

    # r_0 = A @ x_0 - b
    r = A @ x - b

    r_norm_arr = []

    # p_0 = r_0
    p = r.copy()

    # rs_old = r_k^T @ r_k
    # Residual Squared
    rs_old = np.dot(r, r)

    # ----------------------------------
    # 3. Main Iteration Loop
    # ----------------------------------
    for iter_counter in range(maxiter):

        r_norm = np.sqrt(rs_old)
        r_norm_arr.append(r_norm)

        # Check convergence
        if r_norm < stop_threshold:
            return x, iter_counter + 1, r_norm_arr  # Success

        # Compute A @ p_k
        Ap = A @ p

        # tau_k = (r_k^T @ r_k) / (p_k^T @ A @ p_k)
        tau = rs_old / np.dot(p, Ap)

        # x_{k+1} = x_k - tau_k * p_k
        x = x - tau * p

        # r_{k+1} = r_k - tau_k * A @ p_k
        r = r - tau * Ap

        # rs_new = r_{k+1}^T @ r_{k+1}
        rs_new = np.dot(r, r)

        # β_k = (r_{k+1}^T @ r_{k+1}) / (r_k^T @ r_k)
        # p_{k+1} = r_{k+1} + β_k * p_k
        p = r + (rs_new / rs_old) * p

        # Prepare for next iteration
        rs_old = rs_new

    r_norm = np.sqrt(rs_old)
    r_norm_arr.append(r_norm)

    # Final check
    if r_norm < stop_threshold:
        return x, maxiter, r_norm_arr

    return x, 0, r_norm_arr  # Not converged


def solve_bicgstab(A, b, x0=None, rtol=1e-5, atol=1e-8, maxiter=1000):
    """
    Solves the linear system A @ x = b using BiCGSTAB.

    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) array_like
        Vector of right-hand sides.
    - x0 : (M,) array_like, optional
        Initial guess.
    - rtol, atol : float, optional
        Tolerances.
    - maxiter : int, optional
        Max iterations.

    Returns
    -------
    - x : (M,) ndarray
        Solution.
    - info : int
        Convergence info.
    - r_norm_arr: List[float]
        Residual history.

    Notes
    -----
    • *Algorithm workflow*
    1. Initialize r₀, r̂₀, p₀, v₀.
    2. Iterate through BiCGSTAB steps (ρ, α, ω updates).
    """
    # ----------------------------------
    # 1. Initialization and Checks
    # ----------------------------------
    A = np.asarray(A, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if A.shape[0] != A.shape[1]:
        raise ValueError("Matrix A must be square.")

    n = A.shape[0]
    if x0 is None:
        x = np.zeros(n, dtype=np.float64)
    else:
        x = np.asarray(x0, dtype=np.float64).copy()

    # ----------------------------------
    # 2. Preparation
    # ----------------------------------

    # Stopping criterion
    b_norm = np.linalg.norm(b)
    stop_threshold = _get_stop_threshold(b_norm, atol=atol, rtol=rtol)

    # r_0 = b - A @ x_0
    r = b - A @ x

    r_norm_arr = []

    # Check if initial guess is solution
    if np.linalg.norm(r) < stop_threshold:
        return x, 0, r_norm_arr  # 0 iterations

    # r̂_0 = r_0 (standard choice for shadow vector)
    r_hat = r.copy()

    # Initialize loop variables
    rho_old = 1.0
    alpha = 1.0
    omega = 1.0
    p = np.zeros_like(r)
    v = np.zeros_like(r)

    # ----------------------------------
    # 3. Main Iteration Loop
    # ----------------------------------
    for iter_counter in range(maxiter):

        r_norm = np.linalg.norm(r)
        r_norm_arr.append(r_norm)

        # Check convergence
        if r_norm < stop_threshold:
            return x, iter_counter + 1, r_norm_arr  # Success

        # 1. ρ_k = r̂_0^T @ r_{k-1}
        rho_new = np.dot(r_hat, r)

        # Breakdown check
        if rho_new == 0.0:
            warnings.warn("rho_new == 0.", RuntimeWarning)
            return x, 0, r_norm_arr

        # 2. β = (ρ_k / ρ_{k-1}) * (α / ω_{k-1})
        beta = (rho_new / rho_old) * (alpha / omega)

        # 3. p_k = r_{k-1} + β * (p_{k-1} - ω_{k-1} * v_{k-1})
        p = r + beta * (p - omega * v)

        # 4. v_k = A @ p_k
        v = A @ p

        # 5. α = ρ_k / (r̂_0^T @ v_k)
        r_hat_dot_v = np.dot(r_hat, v)
        if r_hat_dot_v == 0.0:
            warnings.warn("dot(r_hat, v) == 0.", RuntimeWarning)
            return x, 0, r_norm_arr
        alpha = rho_new / r_hat_dot_v

        # 6. s = r_{k-1} - α * v_k
        s = r - alpha * v

        # 7. t = A @ s
        t = A @ s

        # 8. ω_k = (t^T @ s) / (t^T @ t)
        t_dot_t = np.dot(t, t)
        if t_dot_t == 0.0:
            # s is almost solution
            x = x + alpha * p
            return x, iter_counter + 1
        omega = np.dot(t, s) / t_dot_t

        # 9. x_k = x_{k-1} + α * p_k + ω_k * s
        x = x + alpha * p + omega * s

        # 10. r_k = s - ω_k * t
        r = s - omega * t

        # Prepare for next iteration
        rho_old = rho_new

    r_norm = np.linalg.norm(r)
    r_norm_arr.append(r_norm)

    # Final check
    if r_norm < stop_threshold:
        return x, maxiter, r_norm_arr

    return x, 0, r_norm_arr  # Not converged


def solve(A, b):
    """
    Solves the linear system A @ x = b using LU decomposition.

    Parameters
    ----------
    - A : (M, M) array_like
        Square coefficient matrix.
    - b : (M,) or (M, K) array_like
        Vector(s) of right-hand sides.

    Returns
    -------
    - x : (M,) or (M, K) ndarray
        Solution.
    """
    # 1. Get explicit P, L, U matrices
    P, L, U = lu_factor(A)

    # 2. Pass them to solver
    return solve_lu((P, L, U), b)
