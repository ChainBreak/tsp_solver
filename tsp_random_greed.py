import requests #pip install requests
import random
import numpy as np
import time
from scipy.spatial import distance_matrix

base_url = "http://10.90.185.46:8000/"

class GlobalGreedy():
    def __init__(self,city_locations):
        self.city_locations = city_locations
        self.city_locations_np = np.array(city_locations)
        self.num_cities = len(city_locations)
        self.best_length = 0

        self.dist_matrix = distance_matrix(self.city_locations_np,self.city_locations_np)


    def __call__(self):
        
        # Each city gets a unique label (integer id). 
        # As cities get linked they share their labels such that each connected city has the same label.
        
        city_labels     = list(range(self.num_cities))
        city_links      = []
        city_link_count = [ 0]*self.num_cities

        for segment in range(self.num_cities):
            
            # Keep looping until all connected cities has the same label
            # The label should be the minimum of all the connected cities
            # At the end all cities should be all connected and all have a minimum label of 0
            label_changed = True
            while label_changed:
                label_changed = False
                for i,j in city_links:
                    if city_labels[i] != city_labels[j]:
                        label_changed = True
                        city_labels[i] = city_labels[j] = min(city_labels[i],city_labels[j])
            

            # Create a list of all the cities that could be linked
            # Cities can only be linked if they have different labels and they have less than
            # two links
            possible_links = []
            possible_links_dist = []
            for i in range(self.num_cities):
                if city_link_count[i] < 2:
                    for j in range(i+1,self.num_cities):
                        if city_link_count[j] < 2:
                            if city_labels[i] != city_labels[j]:
                                possible_links.append((i,j))
                                possible_links_dist.append(self.dist_matrix[i,j])
            
            
            # Find the shortest possible link and take it
            if len(possible_links) > 0 :
                link_index = np.argmin(possible_links_dist)
                i,j = possible_links[link_index]
            else:
                # If there are no links then just its the last link that will close the circle
                j = city_link_count.index(1)
                i = city_link_count.index(1,j+1)
            
            # Add this new link and increment the link count for these two cities
            city_links.append((i,j))
            city_link_count[i] += 1
            city_link_count[j] += 1
 
        
        city_neighbour_lookup = [ [] for _ in range(self.num_cities)]  
        for i,j in city_links:
            city_neighbour_lookup[i].append(j)
            city_neighbour_lookup[j].append(i)


        # print(city_neighbour_lookup)
        city_order = []
        city_visited = [False]*self.num_cities
        
        i = 0
        for _ in range(self.num_cities):
            city_visited[i] = True
            city_order.append(i)
            il = city_neighbour_lookup[i][0]
            ir = city_neighbour_lookup[i][1]

            if not city_visited[il]:
                i = il 
            elif not city_visited[ir]:
                i = ir 

        return city_order

class RandomCityGreedy():
    def __init__(self,city_locations):
        self.city_locations = city_locations
        self.city_locations_np = np.array(city_locations)
        self.num_cities = len(city_locations)
        self.best_length = 0

        self.dist_matrix = distance_matrix(self.city_locations_np,self.city_locations_np)


    def __call__(self):
        
        # Each city gets a unique label (integer id). 
        # As cities get linked they share their labels such that each connected city has the same label.
        
        city_labels     = list(range(self.num_cities))
        city_links      = []
        city_link_count = [ 0]*self.num_cities

     
        for segment in range(self.num_cities):
            
            # Keep looping until all connected cities has the same label
            # The label should be the minimum of all the connected cities
            # At the end all cities should be all connected and all have a minimum label of 0
            label_changed = True
            while label_changed:
                label_changed = False
                for i,j in city_links:
                    if city_labels[i] != city_labels[j]:
                        label_changed = True
                        city_labels[i] = city_labels[j] = min(city_labels[i],city_labels[j])
            

            # Create a list of all the cities that could be linked
            # Cities can only be linked if they have different labels and they have less than
            # two links
            possible_links = []
            possible_links_dist = []

            possible_cities = []
            for i in range(self.num_cities):
                if city_link_count[i] < 2:
                    possible_cities.append(i)

            if len(possible_cities) > 0:
                i = random.choice(possible_cities)
                for j in range(self.num_cities):
                    if city_link_count[j] < 2:
                        if city_labels[i] != city_labels[j]:
                            possible_links.append((i,j))
                            possible_links_dist.append(self.dist_matrix[i,j])
            
            
            # Find the shortest possible link and take it
            if len(possible_links) > 0 :
                # possible_links_dist = np.array(possible_links_dist)
                # # print(possible_links_dist)
                # probability = 1 / possible_links_dist * 1000
                # probability = np.exp(probability)
                # probability /= probability.sum()
                # # print(probability)

                # link_index = np.random.choice(len(possible_links),p=probability)
                link_index = np.argmin(possible_links_dist)
                i,j = possible_links[link_index]
            else:
                # If there are no links then just its the last link that will close the circle
                j = city_link_count.index(1)
                i = city_link_count.index(1,j+1)
            
            # Add this new link and increment the link count for these two cities
            city_links.append((i,j))
            city_link_count[i] += 1
            city_link_count[j] += 1
 
        
        city_neighbour_lookup = [ [] for _ in range(self.num_cities)]  
        for i,j in city_links:
            city_neighbour_lookup[i].append(j)
            city_neighbour_lookup[j].append(i)


        # print(city_neighbour_lookup)
        city_order = []
        city_visited = [False]*self.num_cities
        
        i = 0
        for _ in range(self.num_cities):
            city_visited[i] = True
            city_order.append(i)
            il = city_neighbour_lookup[i][0]
            ir = city_neighbour_lookup[i][1]

            if not city_visited[il]:
                i = il 
            elif not city_visited[ir]:
                i = ir 

        return city_order


class SolverEngine():
    def __init__(self,base_url,solver_class):
        self.base_url = base_url
        self.solver_class = solver_class

        self.next_request_time = 0
        self.next_submit_time = 0

    def get_cities(self):
        # Request for all the cities.
        city_locations = requests.get(f"{self.base_url}cities").json()["city_locations"]
        # city_locations = city_locations[:20]
        return city_locations

    def cities_not_changed(self,city_locations):
        if time.time() > self.next_request_time:
            self.next_request_time = time.time() + 60
            try:
                return city_locations == self.get_cities()
            except:
                pass
        return True

    def submit_city_order(self,city_order):
        if time.time() > self.next_submit_time:
            self.next_submit_time = time.time() + 60
            try:
                # Create a submission dict with the details of our submission
                submit_json = {
                    "user_name"     : "Hitchhiker",
                    "algorithm_name": "Greedy",
                    "message"       : "Its about the journey",
                    "city_order"    : city_order
                }

                # Post our submission to the server
                submission_response = requests.post(f"{self.base_url}submit",json=submit_json)

                # Get the json from the response to our submission
                submission_response_json = submission_response.json()

                # Print the details of our submission to see how we went
                print(f"Submit Success: {submission_response_json['success']}")
                print(f"Path Length   : {submission_response_json['path_length']}")
                print(f"Error Message : {submission_response_json['error_msg']}")
            except:
                pass

    def compute_path_length(self,city_locations,city_order):
        
        num_cities = len(city_locations)

        #Convert this city index list into an array
        city_order = np.array(city_order)
        city_locations = np.array(city_locations)

        #make sure the smallest index is in range
        if city_order.min() < 0:
            raise Exception(f"City {city_order.min()} does not exist. The min city index is 0")
        
        #make sure the largest index is in range
        if city_order.max() >= num_cities:
            raise Exception(f"City {city_order.max()} does not exist. The max city index is {num_cities-1}")

        #create a check list to ensure every city is visited
        city_checklist = np.zeros(num_cities)
        
        #put a 1 in the check list for every city visited
        city_checklist[city_order] = 1
        
        #ensure that the checklist sums to the number of cities
        if city_checklist.sum() != num_cities:
            missing_city = int(np.where(city_checklist==0)[0][0])
            raise Exception(f"Did not visit city {missing_city}")

        #order the city locations by the city order
        ordered_city_locations = city_locations[city_order]

        # Subtract the current city positions from the next city positions in the path
        diff = ordered_city_locations - np.roll(ordered_city_locations,1,axis=0)

        # Calculate the distance between cities and sum this to get the whole path length
        path_length = np.sqrt((diff*diff).sum(axis=1)).sum()

        return path_length

    def run(self):
        while True:
            try:
                city_locations = self.get_cities()

                solver = self.solver_class(city_locations)

                best_city_order = solver()
                best_path_length = self.compute_path_length(city_locations,best_city_order)

                while self.cities_not_changed(city_locations):
                   
                    city_order = solver()

                    path_length = self.compute_path_length(city_locations,city_order)
                    # print(path_length)
                    if path_length < best_path_length:
                        best_path_length = path_length
                        best_city_order = city_order
                        print("BEST",path_length)

                    self.submit_city_order(best_city_order)


            except Exception as e:
                print(e)
                time.sleep(1)



if __name__ == "__main__":

    se = SolverEngine(base_url, RandomCityGreedy)
    se.run()





