import requests #pip install requests
import time
from queue import Full, Empty
from multiprocessing import Queue, Pool, Event, Process# Manager
# from concurrent.futures import ProcessPoolExecutor
from solvers.helpers import PathLengthCalculator

class SolverEngine():
    def __init__(self,user_name,message,base_url,solver_class_list):
        self.user_name = user_name
        self.message = message
        self.base_url = base_url
        self.solver_class_list = solver_class_list
        self.next_request_time = 0
        self.next_submit_time = 0
        self.shutdown_event = Event()
        self.queue = Queue()

    def get_cities(self):
        # Request for all the cities.
        city_locations = requests.get(f"{self.base_url}cities").json()["city_locations"]
        # city_locations = city_locations[:20]
        return city_locations

    def cities_not_changed(self,city_locations):
        if time.time() > self.next_request_time:
            self.next_request_time = time.time() + 10
            try:
                return city_locations == self.get_cities()
            except:
                pass
        return True

    def submit_city_order(self,city_order):
        if time.time() > self.next_submit_time:
            self.next_submit_time = time.time() + 10
            try:

                # Create a submission dict with the details of our submission
                submit_json = {
                    "user_name"     : self.user_name,
                    "algorithm_name": "Untwister",
                    "message"       : self.message,
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
            except Exception as e:
                print(e)


    def solver_worker(self,solver,path_length_calculator):
        
        try:
            best_path_length = None
            best_city_order = None
            while not self.shutdown_event.is_set():
                try:
                    city_order = solver()
                    path_length = path_length_calculator(city_order)
                    if best_path_length is None or path_length < best_path_length:
                        best_path_length = path_length
                        best_city_order = city_order
                        self.queue.put(city_order,timeout=0.1)
                except Full:
                    print("full")
                    time.sleep(1.0)
               
        except KeyboardInterrupt:
            pass

        except Exception as e:
            print("solver_worker",e)


    def run(self):
        alive = True
        while alive:
            process_list = []
            try:
                city_locations = self.get_cities()
                num_cities = len(city_locations)
                path_length_calculator = PathLengthCalculator(city_locations)

                self.shutdown_event.clear()
                for solver_class in self.solver_class_list:
                    solver = solver_class(city_locations)
                    proc = Process(target=self.solver_worker, args=(solver,path_length_calculator))
                    proc.start()
                    process_list.append(proc)

                best_path_length = None
                best_city_order = None
                        
                while self.cities_not_changed(city_locations):
                    try:
                        city_order = self.queue.get(timeout=1)
                        if len(city_order) == num_cities:
                            path_length = path_length_calculator(city_order)

                            if best_path_length is None or path_length < best_path_length:
                                best_path_length = path_length
                                best_city_order = city_order
                                print("BEST",path_length)
                    except Empty:
                        print("empty")


                    self.submit_city_order(best_city_order)
                print("Cities changed")
                
            
            except Exception as e:
                print("main",e)
                raise e
                time.sleep(1)

            except KeyboardInterrupt:
                alive = False

            finally:
                self.shutdown_event.set()
                print("Joining")
                for p in process_list:
                    p.join()
                    print("Joined",p)
                print("All Joined")





if __name__ == "__main__":
    base_url = "http://10.90.185.46:8000/"
    # base_url = "http://127.0.0.1:8000/"
    user_name = "Hamiltonian Harlot"
    message = "Catch you outside how bout that"

    from solvers.randomsolver import Random
    from solvers.untwister import Untwister



    engine = SolverEngine(user_name, message, base_url,[Untwister]*8)
    engine.run()