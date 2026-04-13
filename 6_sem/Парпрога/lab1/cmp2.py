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

    # --- Декомпозиция области (ваша логика без изменений) ---
    x_points_local = x_points // size
    points_left = x_points % size
    x_start_local = (rank * x_points_local + min(rank, points_left)) * dx
    if rank < points_left:
        x_points_local += 1
    
    x_intervals_local = x_points_local - 1
    x_end_local = x_start_local + x_intervals_local * dx

    # --- Подготовка векторов (Экономия памяти!) ---
    # Для rank > 0 добавляем одну точку слева (ghost cell)
    # Для rank == 0 ghost cell не нужен, так как там граничное условие
    actual_local_size = x_points_local if rank == 0 else x_points_local + 1
    
    u_prev = np.empty(actual_local_size, dtype=np.double)
    u_curr = np.empty(actual_local_size, dtype=np.double)
    
    # Инициализация t = 0
    if rank == 0:
        x_arr_local = np.linspace(x_start_local, x_end_local, x_points_local)
        u_prev[:] = u_0_x(x_arr_local)
    else:
        x_arr_local = np.linspace(x_start_local - dx, x_end_local, x_points_local + 1)
        u_prev[:] = u_0_x(x_arr_local)  # Включая ghost cell в начале

    # Превращаем индексы наблюдения в set для быстрой проверки
    t_observ_idx_set = set(t_observ_idx.astype(int))
    snapshots = []

    # Если t=0 есть в списке наблюдений
    if 0 in t_observ_idx_set:
        snapshots.append(u_prev[0:] if rank == 0 else u_prev[1:])

    # --- Основной цикл по времени ---
    t_arr = np.linspace(0, T, t_points)

    for t_curr_idx, t_curr in enumerate(t_arr[:-1]):

        # 1. Обмен граничными значениями
        left_neighbor = rank - 1 if rank > 0 else MPI.PROC_NULL
        right_neighbor = rank + 1 if rank < size - 1 else MPI.PROC_NULL

        # Передаем правую границу, получаем в левую (ghost cell)
        comm.Sendrecv(
            sendbuf=u_prev[-1:], dest=right_neighbor,
            recvbuf=u_prev[0:1], source=left_neighbor
        )

        # 2. Граничное условие на x=0 (только для первого процесса)
        if rank == 0:
            # На rank 0 первая точка u[0] берется из u_t_0
            u_curr[0] = u_t_0(t_curr + dt)

        u_curr[1:] = u_prev[1:] - sigma * (u_prev[1:] - u_prev[:-1]) + dt * f(t_curr, x_arr_local[1:])

        # Переходим к следующему шагу
        u_prev[:] = u_curr[:]

        # 3. Делаем снапшот, если текущий шаг (t_curr_idx + 1) в списке
        if (t_curr_idx + 1) in t_observ_idx_set:
            # Сохраняем только "чистые" данные без ghost cell
            snapshots.append(u_curr[0:].copy() if rank == 0 else u_curr[1:].copy())

    # --- Сборка всех снапшотов ---
    # Превращаем список векторов в локальную матрицу для сбора
    local_matrix = np.array(snapshots)  # Shape: (len(snapshots), x_points_local)
    
    gathered_data = comm.gather(local_matrix, root=0)

    if rank == 0:
        # Склеиваем по оси X (axis=1), так как каждый процесс прислал (T_snapshots, X_local)
        u_final = np.concatenate(gathered_data, axis=1)
        return u_final
    
    return None