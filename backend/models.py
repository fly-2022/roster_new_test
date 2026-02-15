from datetime import datetime


class Officer:
    def __init__(self, id, name, type="regular", available=True,
                 start_time=None, end_time=None, zones=None,
                 actual_arrival=None, actual_leave=None):
        self.id = id
        self.name = name
        self.type = type
        self.available = available
        self.start_time = start_time
        self.end_time = end_time
        self.zones = zones or []
        self.actual_arrival = actual_arrival or start_time
        self.actual_leave = actual_leave or end_time
