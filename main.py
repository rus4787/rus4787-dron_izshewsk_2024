import numpy as np
from fields import FieldProcessor
from drones import drones
from routing import (generate_flight_grid,
                     remove_restricted_areas,
                     # calculate_flight_path,
                     save_grid_to_file,
                     load_grid_from_file
                     )
from geojson_export import export_flight_paths_to_geojson
from shapely.geometry import Polygon
import pandas as pd
from tqdm import tqdm
import geojson
import os
from time_class import timex


def calculate_flight_metrics(drone, area):
    """Рассчитывает метрики полета дрона для оператора."""
    # Максимальная площадь, которую дрон может обработать за один вылет
    max_area_per_flight = drone['efficiency'] / 3  # 5 Га
    # Максимальное время полета за один вылет
    max_flight_time = drone['flight_time']   # 20 Минут
    # Ширина распыления
    spray_width = drone['spray_width']   # 10 Метров
    # Сдвиг дрона при полете методом "косилки"
    shift_width = 8  # Метров

    # Расчет количества сессий
    num_sessions = np.ceil(area / max_area_per_flight)

    # Расчет времени полета на сессию
    flight_time_per_session = max_flight_time

    # Количество заправок равно количеству сессий
    refuels = int(num_sessions)

    # Общий расход раствора
    total_solution_usage = drone['tank_capacity'] * num_sessions

    # Количество замен батарей
    total_battery_usage = refuels

    # Общие затраты времени (часы)
    total_man_hours = (flight_time_per_session * num_sessions) / 60

    return {
        "количество_сессий": np.round(num_sessions, 2),
        "время_полета_в_сессию": np.round(flight_time_per_session, 2),
        "количество_посадок": refuels,
        "необходимо_раствора": np.round(total_solution_usage, 2),
        "необходимо_батарей": refuels,
        "затраты_человек_в_час": np.round(total_man_hours, 2)
    }


def save_flight_paths_to_excel(flight_paths, output_path):
    """Сохраняет маршруты полета в Excel файл."""
    data = []
    for path in tqdm(flight_paths, desc="Сохранение маршрутов в Excel"):
        to_square = path['to_square']
        back = path['back']
        for point in to_square:
            data.append({'type': 'to', 'lat': point[0], 'lon': point[1]})
        for point in back:
            data.append({'type': 'back', 'lat': point[0], 'lon': point[1]})

    df = pd.DataFrame(data)
    df.to_excel(output_path, index=False)
    print("Сгенерированные маршруты полета сохранены в:", output_path)


if __name__ == '__main__':

    # Загружаем данные поля
    field_processor = FieldProcessor('field.geojson', 'restrict_area.geojson', 'point_start.geojson')
    processed_data = field_processor.process_field()

    grid_filename = 'flight_grid_net.geojson'

    # Выбор дрона
    drone_name = "New Agricultural Drone"
    drone = drones[drone_name].get_properties()

    # Проверяем свойства дрона
    print(f"Свойства дрона: {drone}")

    # Расчет метрик для оператора
    flight_metrics = calculate_flight_metrics(drone, processed_data['field_area'])
    print("Метрики полета дрона:")

    for metric, value in flight_metrics.items():
        print(f"{metric}: {value}")

    # Генерация сетки полета
    print("Генерация сетки полета...")
    #try:
        #grid = load_grid_from_file(grid_filename)
        #print("Сетка загружена из файла.")
    #except:
    grid = generate_flight_grid(Polygon(processed_data['field_coords']),
                                    drone['spray_width'],
                                    drone['flight_radius'])

        #save_folder = os.getenv("SAVE_FOLDER", "C:/Users/khabi/PycharmProjects/dron_hakkaton/.venv/dron_model_3")
        # Проверка существования папки и создание, если она не существует
        #if not os.path.exists(save_folder):
            #os.makedirs(save_folder)
        # Сохранение файла
        #filename = os.path.join(save_folder, "flight_grid_net.geojson")
        #save_grid_to_file(grid, grid_filename)
        #print("Сетка сгенерирована и сохранена в файл.")

    # Удаляем зоны, пересекающиеся с запретными
    print("Удаление запретных зон...")

    restricted_areas = processed_data['restricted_zones']
    has_intersections = any( any(square.intersects(restricted_area) for restricted_area in restricted_areas) for square in grid.geometry)

    if not has_intersections:
        valid_grid = grid
    else:
        valid_grid = remove_restricted_areas(grid, processed_data['restricted_zones'])
    #print("Grid (первые 5 элементов):", valid_grid.head())             # Если valid_grid - GeoDataFrame
    #print("Grid types:", valid_grid.geometry.apply(type))              # Проверяем типы объектов в сетке
    #print("Restricted areas:", processed_data['restricted_zones'])     # Проверяем содержимое

    # Рассчитываем маршрут полета
    print("Расчет маршрута полета...")
    with timex():
        flight_paths = []

        # Итерация по каждому элементу сетки
        for index, row in valid_grid.iterrows():
            square = row.geometry  # Получаем геометрию квадрата
            path_to_square = [processed_data['start_point'],
                              square.centroid]  # Дрон летит из стартовой точки к центру квадрата

            # Создаем словарь для маршрута
            flight_path = {
                'to_square': path_to_square,
                'back': [square.centroid, processed_data['start_point']]  # Возвращаемся обратно
            }

            flight_paths.append(flight_path)


    # Экспорт маршрутов в GeoJSON
    print("Экспорт маршрутов в GeoJSON...")
    export_flight_paths_to_geojson(flight_paths, "flight_paths.geojson")

    # Сохраняем маршруты в Excel
    # print("Сохранение маршрутов в Excel...")
    # save_flight_paths_to_excel(flight_paths, "flight_paths.xlsx")
