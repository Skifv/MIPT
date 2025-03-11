import heapq
import random


# -------------------------------
# Класс пользователя (клиента)
# -------------------------------
class User:
    def __init__(self, name, channel_rate):
        self.name = name                   # идентификатор (например, "A")
        self.channel_rate = channel_rate   # скорость канала в кбит/с
        self.queue = 0                     # число кадров в очереди
        self.tx_bits = 0.0                 # суммарно переданных кбит
        # Можно собирать и другие статистики (например, задержки)

# -------------------------------
# Функция планирования следующего прихода кадра для пользователя
# -------------------------------
def schedule_next_arrival(current_time, arrival_mode):
    if arrival_mode == 'CBR':
        return current_time + 0.02  # фиксированный интервал 0.02 с (50 кадров/с)
    elif arrival_mode == 'exponential':
        # random.expovariate(lambda): lambda = 1/mean, здесь mean = 0.02, lambda = 50
        return current_time + random.expovariate(50)
    else:
        raise ValueError("Неизвестный режим поступления")

# -------------------------------
# Функция выбора пользователя согласно выбранному алгоритму планирования
# -------------------------------
def scheduler(users, scheduler_type):
    # Выбираем тех, у кого очередь не пуста
    available = [user for user in users if user.queue > 0]
    if not available:
        return None
    if scheduler_type == 'PF':
        # PF: выбираем по метрике максимальная скорость * (1 / средняя пропускная способность)
        return max(available, key=lambda u: u.channel_rate / (u.tx_bits if u.tx_bits > 0 else 1))
    elif scheduler_type == 'MAX_rate':
        # Выбираем пользователя с максимальной скоростью
        return max(available, key=lambda u: u.channel_rate)
    elif scheduler_type == 'MAX_min':
        # Выбираем пользователя, у которого наименьшее число переданных кбит
        return min(available, key=lambda u: u.tx_bits)
    else:
        raise ValueError("Неизвестный тип планировщика")

# -------------------------------
# Функция симуляции работы базовой станции
# -------------------------------
def simulate(sim_time, arrival_mode, scheduler_type, seed=42):
    random.seed(seed)
    
    # Инициализация пользователей: A, B, C
    users = [User("A", 72), User("B", 54), User("C", 36)]
    
    # Очередь событий: каждый элемент — кортеж (время_события, счетчик, тип_события, пользователь)
    # типы событий: 'arrival' (приход кадра) и 'tx_end' (окончание передачи)
    events = []
    event_counter = 0  # для корректного упорядочивания событий с одинаковым временем
    
    # Планируем первое событие для каждого пользователя
    for user in users:
        arrival_time = schedule_next_arrival(0, arrival_mode)
        heapq.heappush(events, (arrival_time, event_counter, 'arrival', user))
        event_counter += 1

    current_time = 0.0
    channel_busy = False  # состояние канала (занят/свободен)
    
    # Для сбора статистики: число завершённых передач по каждому пользователю
    transmissions = {user.name: 0 for user in users}

    # Главный цикл симуляции
    while current_time < sim_time and events:
        event = heapq.heappop(events)
        event_time, _, event_type, event_user = event
        current_time = event_time  # продвигаем симуляционное время

        if event_type == 'arrival':
            # Приход кадра: увеличиваем длину очереди для данного пользователя
            event_user.queue += 1
            # Планируем следующий приход для этого пользователя, если не вышли за предел симуляции
            next_arrival = schedule_next_arrival(current_time, arrival_mode)
            if next_arrival < sim_time:
                heapq.heappush(events, (next_arrival, event_counter, 'arrival', event_user))
                event_counter += 1

            # Если канал свободен — пробуем начать передачу
            if not channel_busy:
                chosen = scheduler(users, scheduler_type)
                if chosen is not None:
                    # Время передачи одного кадра = (1 кбит) / (канальная скорость пользователя, кбит/с)
                    transmission_time = 1 / chosen.channel_rate
                    tx_end_time = current_time + transmission_time
                    heapq.heappush(events, (tx_end_time, event_counter, 'tx_end', chosen))
                    event_counter += 1
                    channel_busy = True

        elif event_type == 'tx_end':
            # Окончание передачи: снимаем один кадр из очереди пользователя
            if event_user.queue > 0:
                event_user.queue -= 1
            event_user.tx_bits += 1  # передано 1 кбит
            transmissions[event_user.name] += 1

            # Освобождаем канал и сразу проверяем, есть ли кадры в очередях
            channel_busy = False
            chosen = scheduler(users, scheduler_type)
            if chosen is not None:
                transmission_time = 1 / chosen.channel_rate
                tx_end_time = current_time + transmission_time
                heapq.heappush(events, (tx_end_time, event_counter, 'tx_end', chosen))
                event_counter += 1
                channel_busy = True

    # По окончании симуляции вычисляем средний через­пуск (кбит/с) для каждого пользователя
    throughput = {user.name: user.tx_bits / sim_time for user in users}
    return throughput, transmissions, current_time, users

# -------------------------------
# Основной блок: запуск симуляции для разных режимов и планировщиков
# -------------------------------
if __name__ == "__main__":
    sim_time = 20  # время симуляции, сек.
    arrival_modes = ['CBR', 'exponential']
    scheduler_types = ['PF', 'MAX_rate', 'MAX_min']

    for mode in arrival_modes:
        for sched in scheduler_types:
            thr, trans, end_time, users = simulate(sim_time, mode, sched)
            print(f"Режим поступления: {mode}, Планировщик: {sched}")
            for user in users:
                print(f"  Пользователь {user.name}: Пропускная способность = {thr[user.name]:.2f} кбит/с, "
                      f"передач = {trans[user.name]}, очередь = {user.queue}, доля канального времени = {thr[user.name] / user.channel_rate * 100:.2f} %")
            print("-" * 50)
