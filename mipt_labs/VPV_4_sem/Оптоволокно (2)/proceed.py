import csv
import matplotlib.pyplot as plt
import numpy as np

def plot_graphs(x_values, y_values_list, labels=None, 
                title="Графики функций", x_label="x", y_label="y", filename="data.png"):
    """
    Строит графики с белым фоном и сплошными линиями.
    
    Параметры:
        x_values (array): Массив значений по оси X
        y_values_list (list): Список массивов значений Y
        labels (list): Подписи для легенды
        title (str): Заголовок графика
        x_label (str): Подпись оси X
        y_label (str): Подпись оси Y
    """
    # Настройка стиля
    plt.figure(figsize=(10, 6), dpi=100, facecolor='white')
    ax = plt.gca()
    ax.set_facecolor('white')

    # Палитра цветов для графиков
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # Построение графиков
    for i, y_values in enumerate(y_values_list):
        if len(y_values) != len(x_values):
            continue
        style = {
            'linestyle': '-',  # Сплошная линия для всех
            'color': colors[i % len(colors)],
            'linewidth': 2,
            'alpha': 0.9,
            'label': labels[i] if labels and i < len(labels) else f'График {i+1}'
        }
        plt.plot(x_values, y_values, **style)

    # Оформление осей
    plt.title(title, fontsize=14, fontweight='bold', pad=20)
    plt.xlabel(x_label, fontsize=12, labelpad=10)
    plt.ylabel(y_label, fontsize=12, labelpad=10)
    
    # Настройка сетки
    ax.grid(True, linestyle='--', color='lightgray', alpha=0.7)
    
    # Легенда
    if labels or len(y_values_list) > 1:
        plt.legend(
            title="Легенда",
            frameon=True,
            shadow=False,
            facecolor='white',
            edgecolor='gray',
            bbox_to_anchor=(1.02, 1),
            loc='upper left',
            fontsize=10,
            title_fontsize=11
        )
    
    # Убираем черную рамку
    for spine in ax.spines.values():
        spine.set_color('gray')
        spine.set_linewidth(0.8)

    # Оптимизация разметки
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.show()

def find_local_minima_indices(arr, m):
    """
    Находит индексы элементов массива, которые меньше 5 соседей слева и 5 справа.
    
    Параметры:
        arr (list/np.array): Входной массив чисел
    
    Возвращает:
        list: Массив индексов, удовлетворяющих условию
    """
    indices = []
    n = len(arr)
    
    for i in range(m, n - m):
        current = arr[i]
        left = arr[i-m:i]    # 5 элементов слева
        right = arr[i+1:i+1+m] # 5 элементов справа
        
        if all(current < x for x in left) and all(current <= x for x in right):
            indices.append(i)  # Теперь сохраняем индекс
    
    return indices











with open('L0000.CSV') as trivialfile:
    temp = list(map(lambda x: list(map(lambda y: float(y), x.split(','))), trivialfile.readlines()))
    lambdas = list(map(lambda x: x[0], temp))
    trivial = list(map(lambda x: x[1], temp))
lengths = [4.97, 10.2, 20.5]
files = ['L4,97.CSV', 'L10,2.CSV', 'L20,5.CSV']
cols  = [4,           6,           6          ]
masses = range(50, 350, 50)
data = []

for i in range(3):
    with open(files[i]) as csvfile:
        d = list(csv.reader(csvfile, delimiter=','))
        print(len(list(d)))
        temp = []
        for j in range(cols[i]):
            temp.append(list(map(lambda x: float(x[2*j + 1]), d)))
        data.append(temp)
        #print(temp[0])
#print(data)
difdata = []
for i in range(3):
    temp = []
    print(lengths[i])
    for j in range(len(data[i])):
        temp.append(list(map(lambda x: x - trivial[j], data[i][j])))
        print(len(temp))
        print(list(map(lambda x: lambdas[x], find_local_minima_indices(temp[j], 100))))
    difdata.append(temp)
    #plot_graphs(lambdas, temp, masses, filename=(files[i]) + ".png", x_label="λ, нм", y_label="db", title=f"Растяжение оптоволокна длиной {lengths[i]} под нагрузкой")
    
