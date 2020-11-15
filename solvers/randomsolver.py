from .base import BaseSolver
import random

class Random(BaseSolver):
    def __init__(self,city_locations):
        self.num_cities = len(city_locations)

    def __call__(self):
        city_order = list(range(self.num_cities))
        random.shuffle(city_order)
        return city_order