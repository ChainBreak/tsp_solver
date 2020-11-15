import numpy as np
from scipy.spatial import distance_matrix
class PathLengthCalculator():

    def __init__(self,city_locations):
        self.city_locations_np = np.array(city_locations)
        self.num_cities = len(city_locations)

    def __call__(self,city_order_list):
        
        #Convert this city index list into an array
        city_order = np.array(city_order_list)

        #order the city locations by the city order
        ordered_city_locations = self.city_locations_np[city_order]

        # Subtract the current city positions from the next city positions in the path
        diff = ordered_city_locations - np.roll(ordered_city_locations,1,axis=0)

        # Calculate the distance between cities and sum this to get the whole path length
        path_length = np.sqrt((diff*diff).sum(axis=1)).sum()

        return path_length


