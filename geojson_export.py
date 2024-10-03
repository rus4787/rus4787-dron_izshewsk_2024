from shapely.geometry import LineString
import geojson
from fields import convert_to_utm


def export_flight_paths_to_geojson(flight_paths, output_path):
    """Экспортирует полетные маршруты в GeoJSON."""
    features = []
    if not flight_paths:
        print("Нет данных для экспорта.")
        return

    for path in flight_paths:
        # проверка на корректность данных координат
        if path.get('to_square') and isinstance(path['to_square'], list):
            try:
                # line = LineString(path['to_square'])
                utm_coordinates_to_square = [convert_to_utm(point.x, point.y) for point in path['to_square']]
                line = LineString(utm_coordinates_to_square)
                features.append(geojson.Feature(geometry=line, properties={"type": "to"}))
            except ValueError:
                print(f"Неправильные координаты для маршрута 'to_square': {path['to_square']}")

        if path.get('back') and isinstance(path['back'], list):
            try:
                # line = LineString(path['back'])
                utm_coordinates_back = [convert_to_utm(point.x, point.y) for point in path['back']]
                line = LineString(utm_coordinates_back)
                features.append(geojson.Feature(geometry=line, properties={"type": "back"}))
            except ValueError:
                print(f"Неправильные координаты для маршрута 'back': {path['back']}")

    feature_collection = geojson.FeatureCollection(features)

    with open(output_path, 'w') as f:
        geojson.dump(feature_collection, f)

    print("Сгенерированные маршруты полета сохранены в:", output_path)