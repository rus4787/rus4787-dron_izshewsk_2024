import numpy as np

def handle_operator_command(command, drone_position, processed_data):

    base_position = processed_data['start_point']

    if command == "return_to_base":
        # Логика возврата на место взлета
        print("Drone is returning to base...")
        return "Drone is returning to base", base_position

    elif command == "emergency_landing":
        # Логика экстренной посадки
        print("Drone is performing emergency landing...")

        # Безопасное место для посадки — последняя точка поворота
        landing_position = drone_position  # Позиция, где дрон остановился
        print(f"Landing at position: {landing_position}")
        return "Drone is performing emergency landing", landing_position

    elif command == "hold_position":
        # Логика приостановки
        print("Drone is holding position...")
        # Дрон зависает в текущей позиции
        print(f"Drone is hovering at position: {drone_position}")
        return "Drone is holding position", drone_position

    else:
        return "Unknown command", drone_position

def execute_spray_route(drone, route, processed_data):

    current_position = processed_data['start_point']
    total_distance = 0
    battery_life = drone.flight_time * 60  # Время в секундах
    spray_remaining = drone.tank_capacity

    for i in range(len(route) - 1):
        start = route[i]
        end = route[i + 1]

        # Расчет расстояния между точками
        distance = np.linalg.norm(np.array(end) - np.array(start))
        flight_time = distance / drone.speed

        # Проверка на необходимость возвращения на базу для заправки или подзарядки
        if battery_life < flight_time or spray_remaining <= 0:
            print(f"Drone is returning to base from {start} for recharge or refill.")

            # Возвращаем дрон на базу и обновляем заряд батареи и бак
            current_position = processed_data['start_point']
            total_distance += np.linalg.norm(np.array(current_position) - np.array(start))
            battery_life = drone.flight_time * 60  # Сброс заряда батареи
            spray_remaining = drone.tank_capacity  # Сброс объема распыляемого вещества

        # Обновление позиции дрона и вычисление общей дистанции
        current_position = end
        total_distance += distance
        battery_life -= flight_time
        spray_remaining -= (distance / drone.speed) * 0.1  # потребление раствора

        print(f"Drone moved to {end}, Total Distance: {total_distance}m")

    print(f"Total route covered: {total_distance} meters")