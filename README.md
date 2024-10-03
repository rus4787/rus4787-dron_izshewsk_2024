# Agricultural Drone Flight Planner

## Описание

Этот проект представляет собой систему планирования полета сельскохозяйственного дрона. Он позволяет рассчитать оптимальные маршруты полета, учитывая запретные зоны, выбрать подходящий дрон и рассчитать необходимые ресурсы для обработки поля. Результаты могут быть экспортированы в формате GeoJSON для дальнейшего использования.

## Основные функции

1. Расчет метрик полета: Рассчитывает количество сессий, время полета, количество посадок, необходимый раствор и батареи, а также затраты времени на обработку поля.
2. Генерация сетки полета: Создает сетку полета, учитывая размеры поля и характеристики дрона.
3. Удаление запретных зон: Удаляет из сетки полетные зоны, пересекающиеся с запретными зонами.
4. Расчет маршрута полета: Рассчитывает оптимальный маршрут полета дрона.
5. Экспорт маршрутов в GeoJSON: Экспортирует маршруты полета в файл GeoJSON.
6. Обработка команд оператора: Обрабатывает команды оператора, такие как возврат на базу, экстренная посадка и удержание позиции.

## Структура проекта

- main.py: Основной скрипт, который запускает процесс планирования полета.
- drones.py: Определяет класс Drone и содержит словарь с доступными моделями дронов.
- fields.py: Обрабатывает данные поля, загружает координаты поля, запретных зон и начальной точки, а также рассчитывает площадь поля.
- geojson_export.py: Экспортирует маршруты полета в файл GeoJSON.
- operator_commands.py: Обрабатывает команды оператора и выполняет маршруты полета.
- routing.py: Содержит функции для генерации сетки полета, удаления запретных зон и расчета маршрута полета.

## Установка и запуск

### Требования

- Python 3.7+
- Библиотеки: numpy, geojson, shapely, pyproj

### Установка

1. Клонируйте репозиторий:
   
   git clone https://github.com/yourusername/agricultural-drone-flight-planner.git
   cd agricultural-drone-flight-planner
   

2. Установите необходимые зависимости:
   
   pip install numpy geojson shapely pyproj
   

### Запуск

1. Поместите файлы GeoJSON с данными поля, запретных зон и начальной точки в корневую директорию проекта.
2. Запустите основной скрипт:
   
   python main.py
   

## Пример использования

1. Загрузка данных поля:
   
   field_processor = FieldProcessor('field.geojson', 'restrict_area.geojson', 'point_start.geojson')
   processed_data = field_processor.process_field()
   

2. Выбор дрона:
   
   drone_name = "New Agricultural Drone"
   drone = drones[drone_name].get_properties()
   

3. Расчет метрик полета:
   
   flight_metrics = calculate_flight_metrics(drone, processed_data['field_area'])
   

4. Генерация сетки полета и расчет маршрута:
   
   grid = generate_flight_grid(Polygon(processed_data['field_coords']), drone['spray_width'], drone['flight_radius'])
   valid_grid = remove_restricted_areas(grid, processed_data['restricted_zones'])
   flight_paths = calculate_flight_path(valid_grid, processed_data['start_point'])
   

5. Экспорт маршрутов в GeoJSON:
   
   export_flight_paths_to_geojson(flight_paths, "flight_paths.geojson")
