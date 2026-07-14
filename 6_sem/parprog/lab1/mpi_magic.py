# ------------------------------------------------------------------
# --- 0.  Import required libraries --------------------------------
# ------------------------------------------------------------------
import os
import sys
import tempfile
import subprocess
import time
import shlex

from IPython.core.magic import register_cell_magic
from IPython.core.getipython import get_ipython
import numpy as np
import cloudpickle as pkl


class AtomicRankLogger:
    """
    Stream wrapper for process-safe MPI stdout/stderr logging.

    Parameters
    ----------
    - stream (TextIO):
        The underlying output stream (e.g., `sys.stdout` or `sys.stderr`).
    - rank (int):
        The MPI rank of the current process.

    Notes
    -----
    • *Working hypotheses / Assumptions*
    - Intercepts output streams to prevent overlapping standard outputs from concurrent MPI processes.

    • *Algorithm workflow*
    1. Intercepts incoming string data.
    2. Buffers incomplete lines (without newline characters).
    3. Flushes complete lines prefixed with `[Rank X]` to the target stream.
    """

    def __init__(self, stream, rank, total_ranks=100):
        self.stream = stream
        pad = len(str(total_ranks - 1))
        self.prefix = f"[Rank {rank:>{pad}}] "
        self.buffer = ""

    def write(self, data):
        if not data:
            return

        # ------------------------------------------------------------------
        # --- 1. Split data into lines and manage buffer -------------------
        # ------------------------------------------------------------------
        lines = (self.buffer + data).splitlines(keepends=True)
        if not lines[-1].endswith('\n'):
            self.buffer = lines.pop()
        else:
            self.buffer = ""

        # ------------------------------------------------------------------
        # --- 2. Write prefixed lines to the underlying stream -------------
        # ------------------------------------------------------------------
        for line in lines:
            if line.strip():
                self.stream.write(f"{self.prefix}{line}")
            else:
                self.stream.write(line)
            self.stream.flush()

    def flush(self):
        self.stream.flush()


@register_cell_magic
def mpi(line, cell):
    """
    IPython cell magic for executing MPI (Message Passing Interface) code within Jupyter.

    Parameters
    ----------
    - line (str):
        Arguments passed on the magic line (e.g., `-n 4 -i data -o result`).
    - cell (str):
        The block of Python code to be executed in the MPI environment.

    Returns
    -------
    - None (NoneType):
        Results are dynamically injected into the IPython user namespace.

    Notes
    -----
    • *Working hypotheses*
    - The host system has a working MPI implementation (e.g., OpenMPI, MPICH).
    - `mpi4py` is available in the target environment.
    - Code within the cell acts as the MPI payload and runs independently in separate processes.

    • *Expected keys for magic line arguments*
    =========  ================================================================
    Argument   Comment
    ---------  ----------------------------------------------------------------
    -n         Number of MPI processes. Can be int, comma-separated, or list variable.
    -i         Comma-separated list of input variable names from Jupyter namespace.
    -o         Comma-separated list of output variable names to retrieve.
    -a         Extra arguments passed directly to `mpiexec`.
    -sysinfo   Flag to print hardware topology and process affinity.
    =========  ================================================================

    • *Algorithm workflow*
    1. Parse the magic line arguments.
    2. Serialize input variables via `cloudpickle` to a temporary directory.
    3. Generate a wrapper Python script (`payload.py`) embedding the cell code.
    4. Execute `mpiexec` via `subprocess.Popen` for each requested process count.
    5. Capture and format `stdout`/`stderr` asynchronously.
    6. Deserialize output variables and inject them back into the Jupyter namespace.

    Examples
    --------
    • *1. Basic Execution (Hello World)*
    Execute MPI code on a fixed number of cores (-n 4).
    >>> %%mpi -n 4
    >>> from mpi4py import MPI
    >>> print(f"Hello from rank {MPI.COMM_WORLD.Get_rank()}")

    • *2. Input/Output and Variable Injection*
    Pass `local_data` to MPI, compute, and return `total_sum` to Jupyter.
    >>> local_data = np.arange(100) # Defined in standard Jupyter cell
    >>> %%mpi -n 4 -i local_data -o total_sum
    >>> from mpi4py import MPI
    >>> import numpy as np
    >>> comm = MPI.COMM_WORLD
    >>> rank, size = comm.Get_rank(), comm.Get_size()
    >>> my_chunk = local_data[rank::size] # Simple workload distribution
    >>> total_sum = comm.reduce(np.sum(my_chunk), op=MPI.SUM, root=0)

    • *3. Parameter Sweep (Core Scaling)*
    Run payload sequentially for 1, 2, 4, and 8 processes.
    `elapsed_time` becomes a NumPy array of shape (4,).
    >>> %%mpi -n 1,2,4,8 -o elapsed_time
    >>> import time, numpy as np
    >>> from mpi4py import MPI
    >>> start = time.time()
    >>> _ = np.random.rand(1000, 1000) @ np.random.rand(1000, 1000)
    >>> if MPI.COMM_WORLD.Get_rank() == 0:
    >>>     elapsed_time = time.time() - start

    • *4. Advanced System Flags*
    Use `-sysinfo` for CPU affinity and `-a` for custom `mpiexec` arguments.
    >>> %%mpi -n 8 -a "--oversubscribe" -sysinfo
    >>> from mpi4py import MPI
    >>> if MPI.COMM_WORLD.Get_rank() == 0: print("Master running")
    """

    # ------------------------------------------------------------------
    # --- 1. Initialization and magic line expansion -------------------
    # ------------------------------------------------------------------
    ipy = get_ipython()
    if not ipy:
        return

    line_expanded = ipy.var_expand(line)

    try:
        tokens = shlex.split(line_expanded)
    except ValueError as e:
        print(f"[MPI Magic] Parsing error: {e}")
        return

    # ------------------------------------------------------------------
    # --- 2. Parse arguments from tokens -------------------------------
    # ------------------------------------------------------------------
    args = {'n': '2', 'i': '', 'o': '', 'a': '', 'sysinfo': False}

    idx = 0
    while idx < len(tokens):
        token = tokens[idx]
        if token == '-n' and idx + 1 < len(tokens):
            args['n'] = tokens[idx + 1]
            idx += 2
        elif token == '-i' and idx + 1 < len(tokens):
            args['i'] = tokens[idx + 1]
            idx += 2
        elif token == '-o' and idx + 1 < len(tokens):
            args['o'] = tokens[idx + 1]
            idx += 2
        elif token == '-a' and idx + 1 < len(tokens):
            args['a'] = tokens[idx + 1]
            idx += 2
        elif token in ['-sysinfo']:
            args['sysinfo'] = True
            idx += 1
        else:
            for key in ['n', 'i', 'o', 'a']:
                if token.startswith(f"-{key}="):
                    args[key] = token.split('=', 1)[1]
                    break
            idx += 1

    # ------------------------------------------------------------------
    # --- 3. Process parsed arguments and namespace variables ----------
    # ------------------------------------------------------------------
    n_val = args['n']
    if n_val in ipy.user_ns:
        n_raw = ipy.user_ns[n_val]
        # Shape: (len(n_raw),)
        process_counts = [int(x) for x in n_raw] if isinstance(n_raw, (list, tuple, np.ndarray)) else [int(n_raw)]
    else:
        # Shape: (len(split),)
        process_counts = [int(x) for x in n_val.split(',')]

    input_vars = [v.strip() for v in args['i'].split(',') if v.strip()]
    output_vars = [v.strip() for v in args['o'].split(',') if v.strip()]
    extra_mpi_args = args['a']
    sysinfo_enabled = args['sysinfo']

    is_sweep = len(process_counts) > 1
    sweep_results = {var: [] for var in output_vars}

    if sysinfo_enabled:
        import psutil
        phys_cores = psutil.cpu_count(logical=False)
        log_cores = psutil.cpu_count(logical=True)
        print(f"[SysInfo] Physical CPU Cores: {phys_cores}, Logical CPU Cores: {log_cores}")

    # ------------------------------------------------------------------
    # --- 4. Main execution loop (Temporary environment) ---------------
    # ------------------------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="mpi_jupyter_") as tmpdir:
        payload_path = os.path.join(tmpdir, "payload.py")
        in_pkl = os.path.join(tmpdir, "in.pkl")
        out_pkl = os.path.join(tmpdir, "out.pkl")

        # ==============================================================
        # 4a. Serialize input variables to pickle
        # ==============================================================
        if input_vars:
            with open(in_pkl, 'wb') as f:
                pkl.dump({v: ipy.user_ns[v] for v in input_vars}, f)

        # ==============================================================
        # 4b. Generate the payload script
        # ==============================================================
        with open(payload_path, 'w', encoding='utf-8') as f:
            f.write(f"""
import sys, os
from mpi4py import MPI
__mpi_magic_comm = MPI.COMM_WORLD
__mpi_magic_rank = __mpi_magic_comm.Get_rank()
__mpi_magic_size = __mpi_magic_comm.Get_size()
# Вычисляем необходимый отступ на основе общего количества процессов
__mpi_pad = len(str(__mpi_magic_size - 1))

if __mpi_magic_comm:
    class __MPI_Logger:
        def __init__(self, s, r, p):
            self.s, self.r, self.p, self.b = s, r, p, ""
            # Создаем шаблон префикса с выравниванием по правому краю
            self.prefix = f"[Rank {{self.r:>{{self.p}}}}] "

        def write(self, d):
            if not d: return
            lines = (self.b + d).splitlines(keepends=True)
            if not lines[-1].endswith('\\n'): self.b = lines.pop()
            else: self.b = ""
            for l in lines:
                # Печатаем префикс только если строка не пустая
                self.s.write(f"{{self.prefix}}{{l}}" if l.strip() else l)
                self.s.flush()
        def flush(self): self.s.flush()

    # Передаем __mpi_pad третьим аргументом
    sys.stdout = __MPI_Logger(sys.stdout, __mpi_magic_rank, __mpi_pad)
    sys.stderr = __MPI_Logger(sys.stderr, __mpi_magic_rank, __mpi_pad)

import cloudpickle as __mpi_pkl
if os.path.exists({repr(in_pkl)}):
    with open({repr(in_pkl)}, 'rb') as __f:
        globals().update(__mpi_pkl.load(__f))
""")

            if sysinfo_enabled:
                f.write("""
# --- SYSINFO LOGGING ---
import os
import psutil

affinity =[]
if hasattr(os, 'sched_getaffinity'):
    affinity = list(os.sched_getaffinity(0))
elif hasattr(psutil.Process(), 'cpu_affinity'):
    affinity = psutil.Process().cpu_affinity()

if affinity:
    core_display = affinity[0] if len(affinity) == 1 else affinity
else:
    core_display = "Unknown"

print(f"[Init] CPU Core: {core_display}")

__mpi_magic_comm.Barrier()
# -----------------------
""")

            f.write("\n# --- USER CODE START ---\n")
            f.write(cell)
            f.write(f"""
# --- USER CODE END ---
if __mpi_magic_comm and __mpi_magic_rank == 0 and {output_vars}:
    __mpi_magic_res = {{v: globals().get(v) for v in {output_vars}}}
    with open({repr(out_pkl)}, 'wb') as __f:
        __mpi_pkl.dump(__mpi_magic_res, __f)
""")

        # ==============================================================
        # 4c. Execute payload over specified process counts
        # ==============================================================
        for count in process_counts:
            start_time = time.time()
            print(f"\n[MPI] Running {count} processes...")

            cmd = ["mpiexec", "-n", str(count)]
            if extra_mpi_args:
                cmd.extend(shlex.split(extra_mpi_args))
            cmd.extend([sys.executable, payload_path])

            proc_env = os.environ.copy()
            proc_env["PYTHONUNBUFFERED"] = "1"

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, env=proc_env, bufsize=1
            )

            # ==========================================================
            # 4d. Intercept stream asynchronous logic
            # ==========================================================
            try:
                while True:
                    line_out = process.stdout.readline()  # type: ignore
                    if not line_out and process.poll() is not None:
                        break
                    if line_out:
                        sys.stdout.write(line_out)
                        sys.stdout.flush()
            except KeyboardInterrupt:
                print("\n[MPI] Interrupted. Killing processes...")
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                return

            process.wait()
            elapsed = time.time() - start_time

            if process.returncode != 0:
                print(f"[MPI Error] Exit code {process.returncode}")
                return

            print(f"[MPI] Completed in {elapsed:.2f}s")

            # ==========================================================
            # 4e. Extract simulation results from Rank 0
            # ==========================================================
            if output_vars and os.path.exists(out_pkl):
                with open(out_pkl, 'rb') as f:
                    data = pkl.load(f)
                    for v in output_vars:
                        val = data.get(v)
                        if is_sweep:
                            sweep_results[v].append(val)
                        else:
                            ipy.user_ns[v] = val
                os.remove(out_pkl)

    # ------------------------------------------------------------------
    # --- 5. Return sweep data and update IPython namespace ------------
    # ------------------------------------------------------------------
    if is_sweep and output_vars:
        for v in output_vars:
            # Shape: (len(process_counts), *val_shape)
            ipy.user_ns[v] = np.array(sweep_results[v]) if 'np' in globals() else sweep_results[v]
