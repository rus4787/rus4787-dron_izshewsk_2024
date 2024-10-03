from pyproj import Proj, Transformer
import geojson
from shapely.geometry import Polygon

def convert_to_utm(lon, lat):

    wgs84 = Proj("EPSG:4326")  # WGS84
    utm = Proj("EPSG:32640")  # UTM зона 40 - северная широта
    transformer = Transformer.from_proj(wgs84, utm)
    x, y = transformer.transform(lon, lat)

    return x, y

class FieldProcessor:

    def __init__(self, field_geojson_path, restricted_geojson_path, start_point_geojson_path):
        self.field_geojson_path = field_geojson_path
        self.restricted_geojson_path = restricted_geojson_path
        self.start_point_geojson_path = start_point_geojson_path
        self.field_coords = self.load_field_coords()
        self.restricted_zones = self.load_restricted_zones()
        self.start_point = self.load_start_point()

    def load_field_coords(self):
        """Загружает координаты поля из файла GeoJSON и преобразует их в метры."""
        try:
            with open(self.field_geojson_path) as f:
                field_data = geojson.load(f)
            field_coords = field_data['features'][0]['geometry']['coordinates'][0]

            # Преобразуем координаты из градусов в метры
            transformed_coords = [convert_to_utm(lon, lat) for lon, lat in field_coords]
            return transformed_coords

        except (FileNotFoundError, KeyError, IndexError) as e:
            print(f"Ошибка при загрузке координат поля: {e}")
            return []

    def load_restricted_zones(self):
        """Загружает координаты запретных зон из файла GeoJSON."""

        try:
            with open(self.restricted_geojson_path) as f:
                restricted_data = geojson.load(f)
            restricted_zones = [Polygon(zone['geometry']['coordinates'][0]) for zone in restricted_data['features']]
            return restricted_zones

        except (FileNotFoundError, KeyError, IndexError) as e:
            print(f"Ошибка при загрузке запретных зон: {e}")
            return []

    def load_start_point(self):
        """Загружает координаты начальной точки из файла GeoJSON."""

        try:
            with open(self.start_point_geojson_path) as f:
                start_data = geojson.load(f)
            start_point = start_data['features'][0]['geometry']['coordinates']
            return start_point

        except (FileNotFoundError, KeyError, IndexError) as e:
            print(f"Ошибка при загрузке начальной точки: {e}")
            return []

    def calculate_field_area(self):
        """Вычисляет площадь поля в гектарах."""
        polygon = Polygon(self.field_coords)
        return polygon.area / 10000  # Преобразование в гектары

    def process_field(self):
        """Обрабатывает поле и возвращает необходимые данные для дальнейшего использования."""
        field_area = self.calculate_field_area()
        processed_data = {
            'field_coords': self.field_coords,
            'restricted_zones': self.restricted_zones,
            'start_point': self.start_point,
            'field_area': field_area
        }
        return processed_data


field_processor = FieldProcessor('field.geojson',
                                 'restrict_area.geojson',
                                 'point_start.geojson'
                                 )
processed_data = field_processor.process_field()
print(f"Площадь поля: {processed_data['field_area']} га")