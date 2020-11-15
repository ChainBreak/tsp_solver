from .base import BaseSolver
import numpy as np
import random

class Untwister(BaseSolver):
    def __init__(self,city_locations):
        self.num_cities = len(city_locations)
        self.city_locations = city_locations
        self.city_locations_np = np.array(city_locations,dtype="float32")
        self.city_order = list(range(self.num_cities))
        random.shuffle(self.city_order)

    def wrap(self,i):
        return i % self.num_cities

    def dist(self,city_i, city_j):
        city_i = self.wrap(city_i)
        city_j = self.wrap(city_j)
        
        li = self.city_locations_np[city_i]
        lj = self.city_locations_np[city_j]
        # print(city_i,city_j,li,lj,np.sqrt( ((li-lj)**2).sum()))
        return np.sqrt( ((li-lj)**2).sum())

        

    def __call__(self):

        # Find the city with the longest path leading to it

        city_order_np = np.array(self.city_order)
        city_locations_ordered = self.city_locations_np[city_order_np]

        diff = city_locations_ordered-np.roll(city_locations_ordered,1,axis=0)
        dists = np.sqrt( (diff**2).sum(axis=1))
        # print("Dist to city",dists)

        path_length = dists.sum()
        # print("Path length",path_length)

        #sort the distances in decending order
        city_order_indexs = np.argsort(dists,kind= 'heapsort')[::-1]

        # print("Ordered Indexes", city_order_indexs)

        # print("Initial city order",city_order_np)
        for i in city_order_indexs:
            roll = 1-i
            city_order_rolled = np.roll(city_order_np,roll)
            # print("order index",i)
            # print("Rolled order",city_order_rolled)
            city_a = city_order_rolled[0]
            city_b = city_order_rolled[1]

            best_path_length = None
            best_swap_indicies = None
            # start at this index search forward for city that would be worth swapping with
            for j in range(2,self.num_cities-1):
                city_c = city_order_rolled[j]
                city_d = city_order_rolled[j+1]

                new_path_length = path_length
                #remove old links
                new_path_length -= self.dist(city_a,city_b)
                new_path_length -= self.dist(city_c,city_d)
                # Add new hypothesis links
                new_path_length += self.dist(city_a,city_c)
                new_path_length += self.dist(city_b,city_d)

                if best_path_length is None or new_path_length < best_path_length:
                    best_path_length = new_path_length
                    best_swap_indicies = (1,j+1)

                
            if best_path_length < path_length:
                j1,j2 = best_swap_indicies
                city_order_rolled[j1:j2] = city_order_rolled[j1:j2][::-1]

                city_order_np = np.roll(city_order_rolled,-roll)
                self.city_order = city_order_np.tolist()
                # print(best_swap_indicies,best_path_length)
                # print(self.city_order)

                return self.city_order
            
            
        
   

        # Reverse order between cities
        return self.city_order


if __name__ == "__main__":
    city_locations = [
        [0,2],
        [1,1],
        [-1,-1],
        [0,-2],
        [1,-1],
        [-1,1],
    ]
    u = Untwister(city_locations)

    print(u())