""" # Импорты """

import numpy as np
from mpi4py import MPI
import sys
import matplotlib.pyplot as plt

sys.path.append(r"D:\git\MIPT\tools")

import mpi_magic
import plot_tools

def get_t_observ_idx(cfg):

    t_start = cfg['t_start']
    t_end = cfg['t_end']
    t_step = cfg['t_step']
    t_fine_end = cfg['t_fine_end']
    t_fine_step = cfg['t_fine_step']

    if (t_end - 1) in np.arange(t_start, t_end, t_step):
        t_observ_idx = np.arange(t_start, t_end, t_step)

    else:
        t_observ_idx = np.append(np.arange(t_start, t_end, t_step), t_end - 1)

    t_observ_idx = t_observ_idx[t_observ_idx >= t_fine_end]
    t_observ_idx = np.append(np.arange(t_start, t_fine_end, t_fine_step), t_observ_idx)

    return t_observ_idx

r""" # Расчет числа $\pi$ """

def estimate_pi(n_total, comm, chunk_size=1_000_000):

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

n_proc = np.arange(1, 100)
display(n_proc)

exec_time = np.empty(0)

%%mpi -n n_proc -a "-affinity" -i estimate_pi -o exec_time

import numpy as np

N_estimations = 10
N = 10_000_000
comm = MPI.COMM_WORLD

exec_time_arr = np.zeros(N_estimations)

for attempt in range(N_estimations):
    start = MPI.Wtime()
    pi = estimate_pi(N, comm)
    end = MPI.Wtime()
    
    local_exec_time = end - start
    
    exec_time_arr[attempt] = local_exec_time
    
exec_time = np.mean(exec_time_arr)

if comm.Get_rank() == 0:
    print(f"Pi = {pi}, Time = {exec_time:.4f}s")

plot_tools.plot_signals(np.array(exec_time[0]) / np.array(exec_time), np.array(n_proc), xlabel='Число процессоров', ylabel='Ускорение', as_stem=False)

""" # Замер времени общения между процессами """

%%mpi -n 2 -a "-affinity" -o avg_latency

import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

data_to_send = np.array([rank], dtype='i') 
data_to_recv = np.empty(1, dtype='i')

N_attempts = 1_000_000

# Warm-up
if rank == 0:
    for _ in range(100):
        comm.Send(data_to_send, dest=1, tag=10)
        comm.Recv(data_to_recv, source=1, tag=11)
        
elif rank == 1:
    for _ in range(100):
        comm.Recv(data_to_recv, source=0, tag=10)
        comm.Send(data_to_send, dest=0, tag=11)

comm.Barrier()

if rank == 0:
    t_start = MPI.Wtime()
    
    for _ in range(N_attempts):
        comm.Send(data_to_send, dest=1, tag=10)
        comm.Recv(data_to_recv, source=1, tag=11)
        
    t_end = MPI.Wtime()
    latency = (t_end - t_start) / (2 * N_attempts)
    
elif rank == 1:
    for _ in range(N_attempts):
        comm.Recv(data_to_recv, source=0, tag=10)
        comm.Send(data_to_send, dest=0, tag=11)

if rank == 0:
    print(f"Average Latency: {latency*1e6:.4f} µs")  # type: ignore

%%mpi -n 2 -a "-affinity" -o avg_latency

import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

data_to_send = np.array([rank], dtype='i') 
data_to_recv = np.empty(1, dtype='i')

N_attempts = 1_000_000

# Warm-up
if rank == 0:
    for _ in range(100):
        comm.send(data_to_send, dest=1, tag=10)
        data_to_recv = comm.recv(source=1, tag=11)
        
elif rank == 1:
    for _ in range(100):
        data_to_recv = comm.recv(source=0, tag=10)
        comm.send(data_to_send, dest=0, tag=11)

comm.Barrier()

if rank == 0:
    t_start = MPI.Wtime()
    
    for _ in range(N_attempts):
        comm.send(data_to_send, dest=1, tag=10)
        data_to_recv = comm.recv(source=1, tag=11)
        
    t_end = MPI.Wtime()
    latency = (t_end - t_start) / (2 * N_attempts)
    
elif rank == 1:
    for _ in range(N_attempts):
        data_to_recv = comm.recv(source=0, tag=10)
        comm.send(data_to_send, dest=0, tag=11)

if rank == 0:
    print(f"Average Latency: {latency*1e6:.4f} µs")  # type: ignore

""" # Численное интегрирование """

r"""
Схема из методички

$$\frac{u_m^{k+1} - u_m^k}{\tau} + a \frac{u_m^k - u_{m-1}^k}{h} = f_m^k$$

Выраженное значение $u_m^{k+1}$
$$u_m^{k+1} = u_m^k - \frac{a\tau}{h}(u_m^k - u_{m-1}^k) + \tau \cdot f_m^k$$

Обозначим $\frac{a\tau}{h} = \sigma$
"""

def left_corner_solver(comm, T, X, a, t_intervals, x_intervals, u_t_0, u_0_x, f, t_observ_idx):
    
    rank = comm.Get_rank()
    size = comm.Get_size()  
    
    t_points = t_intervals + 1
    x_points = x_intervals + 1
    dt = T / t_intervals
    dx = X / x_intervals
    sigma = a * dt / dx

    if sigma > 1:
        raise ValueError(f"Метод неустойчивый: sigma = {sigma:.4f} > 1")

    x_points_local = x_points // size
    points_left = x_points % size
    x_start_local = (rank * x_points_local + min(rank, points_left)) * dx
    if rank < points_left:
        x_points_local += 1
    
    x_intervals_local = x_points_local - 1
    x_end_local = x_start_local + x_intervals_local * dx

    actual_local_size = x_points_local if rank == 0 else x_points_local + 1
    
    u_prev = np.empty(actual_local_size, dtype=np.double)
    u_curr = np.empty(actual_local_size, dtype=np.double)
    
    # Инициализация t = 0
    if rank == 0:
        x_arr_local = np.linspace(x_start_local, x_end_local, x_points_local)
        u_prev[:] = u_0_x(x_arr_local)
    else:
        x_arr_local = np.linspace(x_start_local - dx, x_end_local, x_points_local + 1)
        u_prev[:] = u_0_x(x_arr_local)  # ghost cell в начале

    t_observ_idx_set = set(t_observ_idx.astype(int))
    snapshots = []

    if 0 in t_observ_idx_set:
        snapshots.append(u_prev[0:] if rank == 0 else u_prev[1:])

    # --- Основной цикл по времени ---
    t_arr = np.linspace(0, T, t_points)

    for t_curr_idx, t_curr in enumerate(t_arr[:-1]):

        # 1. Обмен граничными значениями
        left_neighbor = rank - 1 if rank > 0 else MPI.PROC_NULL
        right_neighbor = rank + 1 if rank < size - 1 else MPI.PROC_NULL

        comm.Sendrecv(
            sendbuf=u_prev[-1:], dest=right_neighbor,
            recvbuf=u_prev[0:1], source=left_neighbor
        )

        # 2. Граничное условие на x=0 (только для первого процесса)
        if rank == 0:
            u_curr[0] = u_t_0(t_curr + dt)

        u_curr[1:] = u_prev[1:] - sigma * (u_prev[1:] - u_prev[:-1]) + dt * f(t_curr, x_arr_local[1:])

        u_prev[:] = u_curr[:]

        # 3. Делаем снапшот, если текущий шаг (t_curr_idx + 1) в списке
        if (t_curr_idx + 1) in t_observ_idx_set:
            snapshots.append(u_curr[0:].copy() if rank == 0 else u_curr[1:].copy())


    local_matrix = np.array(snapshots)  # Shape: (len(snapshots), x_points_local)
    
    gathered_data = comm.gather(local_matrix, root=0)

    if rank == 0:
        # Склеиваем по оси X (axis=1)
        u_final = np.concatenate(gathered_data, axis=1)
        return u_final
    
    return None

# 1. Начальное условие: изначальное пятно загрязнения в трубе
def u_0_x(x):
    return 10.0 * np.exp(-10.0 * (x - 1.0)**2)

# 2. Граничное условие на левом конце (x=0) - подаем загрязнитель
def u_t_0(t):
    return 0 # 2.5 * (1.0 - np.cos(2.0 * np.pi * 0.1 * t))

# 3. Функция внешнего источника - труба/вентиль, впрыскивающая примесь в точке x=2.0.
def f(t, x):
    # С течением времени напор впрыска плавно падает (np.exp(-t)).
    # Само сопло имеет ширину, описываемую Гауссианой.
    intensity = 10.0 * np.exp(-(t-10)) if t >= 10 else 0
    spatial_distribution = np.exp(-20.0 * (x - 6.0)**2)
    return intensity * spatial_distribution

T = 100  # с, рассматриваемый отрезок времени [0, T]
X = 10  # м, рассматриваемый отрезок по оси x [0, X]
a = 0.1  # м/с

t_intervals = 20000  # Число интервалов по оси t
x_intervals = 100  # Число интервалов по оси x

dt = T / t_intervals
dx = X / x_intervals

cfg = {
    "t_start": 0,
    "t_end": t_intervals + 1,
    "t_step": 20,
    "t_fine_end": 0,
    "t_fine_step": 1
}

t_observ_idx = get_t_observ_idx(cfg)

sigma = a*dt/dx
display(sigma)

u = np.empty(0)

%%mpi -n 5 -a "-affinity" -i T,X,a,t_intervals,x_intervals,dt,dx,t_observ_idx,u_0_x,u_t_0,f,left_corner_solver -o u

from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD

if comm.Get_rank() == 0:
    print(f"dt = {dt}, dx = {dx}, sigma = {a*dt/dx}")

u = left_corner_solver(MPI.COMM_WORLD, T, X, a, t_intervals, x_intervals, u_t_0, u_0_x, f, t_observ_idx=t_observ_idx)

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML

# Восстанавливаем сетки для осей графика
x_arr = np.linspace(0, X, x_intervals + 1)
t_arr_full = np.linspace(0, T, t_intervals + 1)

# Достаем реальное время для каждого сохраненного снапшота
t_snapshots = t_arr_full[t_observ_idx.astype(int)]

fig, ax = plt.subplots(figsize=(8, 5))

# Настраиваем оси. Лимиты по Y берем из глобального минимума и максимума u
u_min, u_max = np.min(u), np.max(u)
margin = 0.1 * (u_max - u_min) if u_max != u_min else 1.0
ax.set_xlim(0, X)
ax.set_ylim(u_min - margin, u_max + margin)
ax.set_xlabel('Координата $x$, [м]')
ax.set_ylabel('Значение $u(t, x)$')
ax.set_title('Эволюция уравнения переноса')
ax.grid(True)

# Инициализируем пустую линию
line, = ax.plot([],[], color='blue', lw=2)
time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes, fontsize=12)

def init():
    line.set_data([],[])
    time_text.set_text('')
    return line, time_text

def update(frame):
    # На каждом кадре обновляем Y-координаты линии
    line.set_data(x_arr, u[frame, :])
    time_text.set_text(f'Время t = {t_snapshots[frame]:.3f} c')
    return line, time_text

# Создаем анимацию (интервал в миллисекундах между кадрами)
anim = FuncAnimation(fig, update, frames=len(u), init_func=init, 
                        interval=100, blit=True)

display(HTML(anim.to_jshtml()))

plt.figure(figsize=(10, 6))

# extent=[x_min, x_max, t_min, t_max]
plt.imshow(u, origin='lower', extent=[0, X, 0, T], aspect='auto', cmap='jet')

plt.colorbar(label='Значение $u(t, x)$')
plt.xlabel('Координата $x$')
plt.ylabel('Время $t$')

plt.show()

n_proc = np.arange(1, 12 + 1)
display(n_proc)

exec_time = np.empty(0)

%%mpi -n n_proc -a "-affinity" -i T,X,a,t_intervals,x_intervals,dt,dx,t_observ_idx,u_0_x,u_t_0,f,left_corner_solver -o u,exec_time

import numpy as np

N_estimations = 10
comm = MPI.COMM_WORLD

exec_time_arr = np.zeros(N_estimations)

for attempt in range(N_estimations):
    
    start = MPI.Wtime()
    left_corner_solver(MPI.COMM_WORLD, T, X, a, t_intervals, x_intervals, u_t_0, u_0_x, f, t_observ_idx=t_observ_idx)
    end = MPI.Wtime()
    
    local_exec_time = end - start
    
    exec_time_arr[attempt] = local_exec_time
    
exec_time = np.mean(exec_time_arr)

if comm.Get_rank() == 0:
    print(f"dt = {dt}, dx = {dx}, sigma = {a*dt/dx}, Time = {exec_time:.4f}s")

plot_tools.plot_signals(np.array(exec_time[0]) / np.array(exec_time), np.array(n_proc), xlabel='Число процессоров', ylabel='Ускорение', limits=(None, (0, None)))
