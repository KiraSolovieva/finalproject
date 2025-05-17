import tkinter as tk

# Параметры для ацетилена (C2H2)
a = 4.936  # л^2·атм/моль^2
b = 0.05136  # л/моль
R = 0.08314  # л·атм/(моль·К)
T = 300     # К (температура ниже критической)

# Уравнение Ван-дер-Ваальса: давление как функция объёма (для ацетилена)
def P_vdw(V, T):
    return R * T / (V - b) - a / (V * V)

# Уравнение состояния для идеального газа: P = RT/V
def P_ideal(V, T):
    return R * T / V

# Численное интегрирование методом трапеций
def integrate_trapezoid(f, V_start, V_end, n, T):
    h = (V_end - V_start) / n
    result = 0.5 * (f(V_start, T) + f(V_end, T))
    for i in range(1, n):
        result += f(V_start + i * h, T)
    return h * result

# Поиск давления насыщения и объёмов по правилу Максвелла (для Ван-дер-Ваальса)
def find_coexistence_volumes():
    V_min = b + 0.01  # Начальный объём (чуть больше b)
    V_max = 10.0      # Большой объём (газовая фаза)
    n = 1000          # Число шагов для интегрирования
    tolerance = 1e-3  # Допустимая погрешность
    P_guess = 1.0     # Начальное предположение для давления насыщения

    for iteration in range(100):
        V1, V2 = V_min, V_max
        for V in [V_min + i * (V_max - V_min) / n for i in range(n + 1)]:
            pressure = P_vdw(V, T)
            if abs(pressure - P_guess) < tolerance:
                if V < 0.5:  # Примерное разделение на жидкость и газ
                    V1 = V
                else:
                    V2 = V

        area1 = integrate_trapezoid(lambda V, T: P_vdw(V, T) - P_guess, V1, V2, n, T)
        area2 = integrate_trapezoid(lambda V, T: P_guess - P_vdw(V, T), V1, V2, n, T)
        difference = area1 + area2

        if abs(difference) < tolerance:
            break
        P_guess += difference * 0.01

    return V1, V2, P_guess

# Вычисление объёмов и давления
V1, V2, P_saturation = find_coexistence_volumes()
print(f"V1 (жидкость) = {V1:.3f} л/моль")
print(f"V2 (газ) = {V2:.3f} л/моль")
print(f"Давление насыщения = {P_saturation:.3f} атм")

# Построение графика с помощью tkinter
root = tk.Tk()
root.title("Изотермы для ацетилена и идеального газа")

# Создаём холст
canvas_width = 600
canvas_height = 400
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Определяем масштабы для графика
V_min, V_max = 0.0, 10.0  # Диапазон объёма (л/моль)
P_min, P_max = -5.0, 15.0  # Диапазон давления (атм)

# Функции для масштабирования значений в координаты холста
def scale_V(V):
    return (V - V_min) / (V_max - V_min) * (canvas_width - 50) + 25

def scale_P(P):
    return canvas_height - ((P - P_min) / (P_max - P_min) * (canvas_height - 50) + 25)

# Рисуем оси
canvas.create_line(25, canvas_height - 25, canvas_width - 25, canvas_height - 25, fill="black")  # Ось X (V)
canvas.create_line(25, canvas_height - 25, 25, 25, fill="black")  # Ось Y (P)

# Подписи осей
canvas.create_text(canvas_width // 2, canvas_height - 10, text="Объём (л/моль)", fill="black")
canvas.create_text(10, canvas_height // 2, text="Давление (атм)", fill="black", angle=90)

# Рисуем изотерму Ван-дер-Ваальса (ацетилен)
points_vdw = []
for V in [V_min + i * (V_max - V_min) / 1000 for i in range(1001)]:
    try:
        P_value = P_vdw(V, T)
        if P_min <= P_value <= P_max:
            x = scale_V(V)
            y = scale_P(P_value)
            points_vdw.append((x, y))
    except:
        continue

for i in range(len(points_vdw) - 1):
    x1, y1 = points_vdw[i]
    x2, y2 = points_vdw[i + 1]
    canvas.create_line(x1, y1, x2, y2, fill="blue")

# Рисуем изотерму идеального газа
points_ideal = []
for V in [V_min + i * (V_max - V_min) / 1000 for i in range(1001)]:
    try:
        P_value = P_ideal(V, T)
        if P_min <= P_value <= P_max:
            x = scale_V(V)
            y = scale_P(P_value)
            points_ideal.append((x, y))
    except:
        continue

for i in range(len(points_ideal) - 1):
    x1, y1 = points_ideal[i]
    x2, y2 = points_ideal[i + 1]
    canvas.create_line(x1, y1, x2, y2, fill="green")

# Рисуем линию давления насыщения (для Ван-дер-Ваальса)
P_scaled = scale_P(P_saturation)
canvas.create_line(25, P_scaled, canvas_width - 25, P_scaled, fill="red", dash=(4, 4))

# Добавляем текст для обозначения линий
canvas.create_text(canvas_width - 100, 50, text="Ацетилен ", fill="blue")
canvas.create_text(canvas_width - 100, 70, text="Идеальный газ", fill="green")
canvas.create_text(canvas_width - 100, 90, text="P насыщения", fill="red")

# Запускаем окно
root.mainloop()
