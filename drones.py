# Определение дронов
class Drone:
    def __init__(self, name, flight_radius, speed, tank_capacity, flight_time, spray_width, efficiency):
        self.name = name
        self.flight_radius = flight_radius  # in km
        self.speed = speed  # in m/s
        self.tank_capacity = tank_capacity  # in liters
        self.flight_time = flight_time  # in minutes
        self.spray_width = spray_width  # in meters
        self.efficiency = efficiency  # Га, которые обрабатывает дрон за сессию

    def get_properties(self):
        return {
            "name": self.name,
            "flight_radius": self.flight_radius,
            "speed": self.speed,
            "tank_capacity": self.tank_capacity,
            "flight_time": self.flight_time,
            "spray_width": self.spray_width,
            "efficiency": self.efficiency
        }

# Существующие модели дронов
drones = {
    "Agrocopter A16": Drone("Agrocopter A16",
                            10,
                            13.8,
                            16,
                            11,
                            5,
                            4
                            ),
    "DJI Agras T30": Drone("DJI Agras T30",
                           7,
                           10,
                           30,
                           15,
                           7,
                           9.2
                           ),
    "DJI Agras T20": Drone("DJI Agras T20",
                           6,
                           8.5,
                           20,
                           14,
                           6,
                           6.4
                           ),
    "New Agricultural Drone": Drone("New Agricultural Drone",
                                    2.5,
                                    5,
                                    50,
                                    20,
                                    10,
                                    12
                                    )
}