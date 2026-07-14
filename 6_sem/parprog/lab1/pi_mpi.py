from mpi4py import MPI
import numpy as np
import time


def estimate_pi(n_total, chunk_size=1_000_000):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    n_local = (n_total // size)

    if rank < (n_total % size):
        n_local += 1  # Первые процессы забирают по одной лишней точке из остатка

    rng = np.random.default_rng(seed=rank)

    processed_points = 0
    local_hits = 0

    while processed_points < n_local:
        current_chunk = min(chunk_size, n_local - processed_points)
        points = rng.random((current_chunk, 2))

        hits = np.count_nonzero(np.sum(points**2, axis=1) <= 1.0)
        local_hits += hits
        processed_points += current_chunk

    total_hits = comm.reduce(local_hits, op=MPI.SUM, root=0)

    if rank == 0:
        return 4.0 * total_hits / n_total  # type: ignore
    return None


N = 1_000_000_000
comm = MPI.COMM_WORLD
start = time.time()
pi = estimate_pi(N)
end = time.time()

if comm.Get_rank() == 0:
    print(f"Python: Pi = {pi}, Time = {end - start:.4f}s")
