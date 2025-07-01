import matplotlib.pyplot as plt
import numpy as np
import csv
import math

def MNK(x,y):
	mdx = 0.0
	mdy = 0.0
	mdxx = 0.0
	mdyy = 0.0
	mdxy = 0.0
	n = 0
	for e in x:
		mdx = mdx + e
		mdxx = mdxx + e**2
		n = n + 1
	for f in y:
		mdy = mdy + f
		mdyy = mdyy + f**2
	for i in range(n):
		mdxy = mdxy + x[i]*y[i]
	mdx = mdx/n
	mdxx = mdxx/n
	mdy = mdy/n
	mdyy = mdyy/n
	mdxy = mdxy/n
	
	b = (mdxy - mdx*mdy)/(mdxx - mdx*mdx)
	a = mdy - b*mdx
	delta_b = math.sqrt(((mdyy-mdy*mdy)/(mdxx-mdx*mdx)-b*b)/n)
	delta_a = delta_b*math.sqrt(mdxx-mdx*mdx)
	
	return b, delta_b, a, delta_a


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
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', "#ff00ae"]

    xmin = min(x_values)
    xmax = max(x_values)

    coefs_list = []

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
        k, d_k, a, d_a = MNK(x_values, y_values)
        coefs_list += [[k, d_k, a, d_a]]
        print(f"Угол наклона графика {labels[i]} :{k}+-{d_k}")

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
    return coefs_list


mnk_results = []

with open('lambda(m).csv') as file:
    d = list(csv.reader(file, delimiter=','))
    print(d)
    n = int(d[0][0])
    c = 1
    for i in range(n):
        l = float(d[c][0].replace(",","."))
        rows = int(d[c][1])
        cols = int(d[c][2])
        c += 1
        labels = [float(d[c][i+1]) for i in range(cols)]
        c += 1
        x = []
        y = []
        for k in range(rows):
            x += [float(d[c+k][0])]
        for j in range(cols):
            temp = []
            for k in range(rows):
                temp += [float(d[c+k][1+j].replace(',','.'))]
            y += [temp]
        print(f"")
        result = plot_graphs(x, y, labels, "Графики зависимости длины волны провала от массы высящего груза для провалов на разных длинах волн", "m, г", "lambda, нм", filename=f"lambda_m{l}.png")
        c += rows
        mnk_results += [[l, labels[j], result[j][0], result[j][1]] for j in range(cols)]

with open('dlambda-dm.csv', 'w', newline='') as csvfile:
    reswriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    reswriter.writerow(['l, см', 'lambda, нм', 'k, нм/г', 'delta k'])
    for row in mnk_results:
        reswriter.writerow(list(map(lambda x: f"{x}".replace('.',','), row)))
