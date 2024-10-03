import numpy as np
from shapely.geometry import Polygon, Point
from shapely.strtree import STRtree
from tqdm import tqdm
import geopandas as gpd
import geojson
from geopandas import GeoDataFrame

def is_point_in_forbidden_area(point, forbidden_areas):

    point = Point(point)

    for area in forbidden_areas:
        polygon = Polygon(area)

        if polygon.contains(point):
            return True

    return False

def create_spray_route(field_size, drone, forbidden_areas):

    if not isinstance(field_size, tuple) or len(field_size) != 2:

        raise ValueError("field_size должен быть кортежем из двух элементов")

    spray_width = drone['spray_width']
    rows = int(field_size[1] // spray_width)
    spray_route = []

    for i in range(rows):

        if i % 2 == 0:
            route_row = [(x, i * spray_width) for x in range(0, field_size[0], spray_width)]

        else:
            route_row = [(x, i * spray_width) for x in range(field_size[0], 0, -spray_width)]
        route_row = [point for point in route_row if not is_point_in_forbidden_area(point, forbidden_areas)]
        spray_route.extend(route_row)

    return spray_route

    '''Чтобы выбрать размер квадрата для сетки, основываемся на ограничениях дрона:
        - Полоса распыления — 12 метров (0.012 км).
        - Площадь, покрываемая за один пролет — не более 5 гектаров (50000 м²).
        Таким образом, подходящий размер квадрата будет зависеть от эффективного времени полета и максимального радиуса дрона.
        Ширина полосы распыления: 12 метров (это ширина одного пролета). Длина одного пролета (для покрытия 5 гектаров):
        Длина пролета = 50000/12 ≈ 4166.67 метров, но это превышает радиус в 2.5 км. 
        Таким образом, придется делать несколько таких квадратов.
        Поэтому целесообразно выбрать квадрат 50x50 метров (в пределах разумного, чтобы не перегружать расчет сетки).'''

def generate_flight_grid(field_polygon, spray_width, drone_flight_radius):
    # Создаем GeoDataFrame для поля
    field_gdf = gpd.GeoDataFrame([1], geometry=[field_polygon], crs="EPSG:4326")  # EPSG:4326 для географических данных

    # Получаем границы поля
    minx, miny, maxx, maxy = field_polygon.bounds
    x_step = spray_width * 40 / 1000  # Шаг в км (0.5)
    y_step = spray_width * 40 / 1000  # Шаг в км

    # Создаем список для хранения квадратов
    grid_squares = []

    # Генерация сетки
    for x in tqdm(np.arange(minx, maxx, x_step), desc="Создание сетки"):
        for y in np.arange(miny, maxy, y_step):
            grid_square = Polygon([(x, y), (x + x_step, y), (x + x_step, y + y_step), (x, y + y_step)])
            grid_squares.append(grid_square)

    # Превращаем сетку в GeoDataFrame
    grid_gdf = gpd.GeoDataFrame(geometry=grid_squares, crs="EPSG:4326")
    #print("Generated grid (первые 5 элементов):", grid_gdf.head())  # Вывод первых 5 элементов сетки
    #print("Grid types:", [type(geom) for geom in grid_gdf.geometry])  # Проверяем типы объектов в сетке

    # Оставляем только те квадраты, которые пересекаются с полем
    intersecting_grid = gpd.overlay(grid_gdf, field_gdf, how='intersection')

    return intersecting_grid

def save_grid_to_file(grid, filename):
    """Сохраняет сетку в файл."""

    print(grid.head())  # Посмотрим на первые 5 строк данных
    print(grid.dtypes)  # Проверим типы данных в столбцах
    grid['0'] = grid['0'].astype(str)
    grid.to_file(filename, driver='GeoJSON')


def load_grid_from_file(filename):
    """Загружает сетку из файла."""

    if not os.path.exists(filename):
        print(f"Файл {filename} не существует.")
        return None
    return gpd.read_file(filename)

def remove_restricted_areas(grid, restricted_areas):
    print("Restricted areas:", restricted_areas)

    # Проверка на пересечения
    has_intersections = any(
        any(square.intersects(restricted_area) for restricted_area in restricted_areas)
        for square in grid.geometry
    )

    if not has_intersections:
        print("Нет пересечений между зоной полета и запретными зонами. Возвращаем исходную сетку.")
        return grid  # Возвращаем исходный grid, так как пересечений нет

    valid_grid = []
    for square in grid.geometry:
        #print("Square:", square)  # Отладочный вывод
        #print("Square type:", type(square))  # Проверяем тип

        # Проверка на валидность геометрии
        if square.is_valid:
            intersects = any(square.intersects(restricted_area) for restricted_area in restricted_areas)

            if not intersects:
                valid_grid.append(square)
        else:
            print("Недопустимая геометрия:", square)

    # Создаем GeoDataFrame из валидных геометрий
    if valid_grid:
        valid_grid_gdf = gpd.GeoDataFrame(geometry=valid_grid)
        print("Grid types:", valid_grid_gdf.geometry.apply(type))  # Проверяем типы объектов
        return valid_grid_gdf
    else:
        print("Нет допустимых зон для полета.")
        return gpd.GeoDataFrame(columns=['geometry'])  # Возвращаем пустой GeoDataFrame с нужной колонкой


# def calculate_flight_path(valid_grid, start_point):
#     flight_paths = []
#
#     for index, row in valid_grid.iterrows():
#         square = row.geometry  # Получаем геометрию квадрата
#         path_to_square = [processed_data['start_point'],
#                           square.centroid]  # Дрон летит из стартовой точки к центру квадрата
#
#         # Создаем словарь для маршрута
#         flight_path = {
#             'to_square': path_to_square,
#             'back': [square.centroid, processed_data['start_point']]  # Возвращаемся обратно
#         }
#
#         flight_paths.append(flight_path)
#         return flight_paths