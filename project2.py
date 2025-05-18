import tkinter as tk
import math

# Параметры для ацетилена (C2H2)
a = 4.936  # л^2·бар/моль^2
b = 0.05136  # л/моль
R = 0.08314  # л·бар/(моль·К)

# Уравнение Ван-дер-Ваальса
def P_vdw(V, T):
    if V <= b or V <= 0:
        return float('inf')  # Избегаем деления на ноль
    return R * T / (V - b) - a / (V * V)

# Уравнение идеального газа
def P_ideal(V, T):
    if V <= 0:
        return float('inf')
    return R * T / V

# Численное интегрирование методом трапеций
def integrate_trapezoid(f, V_start, V_end, n, T):
    h = (V_end - V_start) / n
    result = 0.5 * (f(V_start, T) + f(V_end, T))
    for i in range(1, n):
        result += f(V_start + i * h, T)
    return h * result

# Поиск максимума и минимума для определения области фазового перехода
def find_extrema(V_min, V_max, n, T):
    pressures = [(V, P_vdw(V, T)) for V in [V_min + i * (V_max - V_min) / n for i in range(n + 1)]]
    max_P = max(pressures, key=lambda x: x[1])
    min_P = min(pressures, key=lambda x: x[1])
    return max_P[0], max_P[1], min_P[0], min_P[1]

# Поиск давления насыщения и объёмов
def find_coexistence_volumes(T):
    V_min = b + 0.01
    V_max = 0.45  # Ограничиваем значение
    n = 10000    # Увеличиваем число шагов
    tolerance = 1e-4
    P_guess = 39.0

    for iteration in range(200):
        # Находим максимум и минимум
        V_max_p, P_max, V_min_p, P_min = find_extrema(V_min, V_max, n, T)
        # Ищем точки пересечения с P_guess
        pressures = [(V, P_vdw(V, T)) for V in [V_min + i * (V_max - V_min) / n for i in range(n + 1)]]
        candidates = sorted([V for V, P in pressures if abs(P - P_guess) < tolerance and V > b])

        if len(candidates) >= 2:
            V1 = min(candidates)  # Первая точка (жидкая фаза)
            V2 = max(candidates)  # Вторая точка (газовая фаза)
        else:
            V1, V2 = V_min, V_max  # Если не нашли, используем границы

        # Проверяем правило Максвелла
        area1 = integrate_trapezoid(lambda V, T: max(0, P_vdw(V, T) - P_guess), V1, V2, n, T)
        area2 = integrate_trapezoid(lambda V, T: max(0, P_guess - P_vdw(V, T)), V1, V2, n, T)
        difference = area1 - area2

        if abs(difference) < tolerance:
            break
        P_guess += difference * 0.00001  # Очень маленький шаг

    return V1, V2, P_guess

# Вычисление давления насыщения для T = 300 K
T_ref = 300
V1, V2, P_saturation = find_coexistence_volumes(T_ref)
print(f"Для T = {T_ref} K: V1 = {V1:.3f} л/моль, V2 = {V2:.3f} л/моль, P_eq = {P_saturation:.2f} бар")

# График с tkinter
root = tk.Tk()
root.title("Изотермы C2H2")
canvas = tk.Canvas(root, width=600, height=400, bg="white")
canvas.pack()

# Диапазон для осей
V_min, V_max = b + 0.001, 1.0  # Расширенный диапазон
P_min, P_max = 0.0, 100.0     # Ограничим давление для лучшей видимости

def scale_V(V): 
    return 25 + math.log10(V / V_min + 1) / math.log10(V_max / V_min + 1) * 550

def scale_P(P): 
    return 375 - (P - P_min) / (P_max - P_min) * 350

# Оси
canvas.create_line(25, 375, 575, 375, fill="black")  # Ось X
canvas.create_line(25, 375, 25, 25, fill="black")    # Ось Y
canvas.create_text(300, 390, text="Объём (л/моль)")
canvas.create_text(10, 200, text="Давление (бар)", angle=90)

# Температуры для изотерм
temperatures = [250, 275, 308.3, 325, 350]  # Температуры из LaTeX-документа
colors = ['blue', 'cyan', 'purple', 'orange', 'red']  # Разные цвета для изотерм

# Построение изотерм Ван-дер-Ваальса
for T, color in zip(temperatures, colors):
    points_vdw = []
    for V in [V_min + i * (V_max - V_min) / 1000 for i in range(1001)]:
        P = P_vdw(V, T)
        if P_min <= P <= P_max:
            points_vdw.append((scale_V(V), scale_P(P)))
    for i in range(len(points_vdw) - 1):
        canvas.create_line(points_vdw[i], points_vdw[i+1], fill=color)

# Линия давления насыщения для T = 300 K
canvas.create_line(25, scale_P(P_saturation), 575, scale_P(P_saturation), fill="black", dash=(4, 4))

# Легенда
y_legend = 50
for T, color in zip(temperatures, colors):
    canvas.create_text(500, y_legend, text=f"T = {T} K", fill=color)
    y_legend += 20
canvas.create_text(500, y_legend, text=f"P_eq (T = {T_ref} K)", fill="black")

root.mainloop()
