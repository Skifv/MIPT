def left_corner_solver(comm, T, X, a, t_intervals, x_intervals, f):
      
    rank = comm.Get_rank()
    size = comm.Get_size()  
    
    t_points = t_intervals + 1
    x_points = x_intervals + 1

    dt = T / t_intervals
    dx = X / x_intervals

    sigma = a * dt / dx

    if sigma > 1:
        raise ValueError("Метод неустойчивый")

    x_points_local = int(x_points / size)

    points_left = x_points % size

    x_start_local = (rank * x_points_local + min(rank, points_left)) * dx

    if rank < points_left:
        x_points_local += 1

    x_intervals_local = x_points_local - 1

    x_end_local = x_start_local + x_intervals_local * dx

    t_arr = np.linspace(0, T, t_points)  # 0, dt, ..., T

    if rank == 0: 
        x_arr_local = np.linspace(x_start_local, x_end_local, x_points_local)  # 0, ..., x_points_local - 1
        u_local = np.empty((t_points, x_points_local), dtype=np.double)
        u_local[:, 0] = u_t_0(t_arr)
        u_local[0, :] = u_0_x(x_arr_local)
    else:
        x_arr_local = np.linspace(x_start_local - dx, x_end_local, x_points_local + 1)
        u_local = np.empty((t_points, x_points_local + 1), dtype=np.double)  # Дополнительная точка слева для передачи данных
        u_local[0, 1:] = u_0_x(x_arr_local[1:])

    for t_curr_idx, t_curr in enumerate(t_arr[:-1]):

        left_neighbor = rank - 1 if rank > 0 else MPI.PROC_NULL
        right_neighbor = rank + 1 if rank < size - 1 else MPI.PROC_NULL
        
        comm.Sendrecv(sendbuf=u_local[t_curr_idx, -1:], dest=right_neighbor, recvbuf=u_local[t_curr_idx, 0:1], source=left_neighbor)
            
        u_local[t_curr_idx + 1, 1:] = u_local[t_curr_idx, 1:] - \
                                sigma * (u_local[t_curr_idx, 1:] - u_local[t_curr_idx, :-1]) + \
                                dt * f(t_curr, x_arr_local[1:])
                                
    if rank == 0:
        send_data = u_local[:, :]
    else:
        send_data = u_local[:, 1:]
    
    gathered_list = comm.gather(send_data, root=0)

    if rank == 0:
        u = np.concatenate(gathered_list, axis=1)
        return u    
    else:
        return None    