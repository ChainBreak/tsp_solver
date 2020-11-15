from multiprocessing import Queue, Process, Event
import time
from solvers.random import Random


class Multi():
    def __init__(self):
        self.shutdown_event = Event()
        self.queue = Queue()

    def run_solver(self,id):
        try:
            i = 0
            while not self.shutdown_event.is_set():
                i += 1
                print(f"{id} {i}")
                time.sleep(0.5)
            
        except KeyboardInterrupt:
            pass
            self.queue.put(i)
            time.sleep(0.5)
        except Exception as e:
            print(e)

    def run(self):
        process_list = []

        try:
            for i in range(8):
                p = Process(target=self.run_solver,args=(i,))
                p.start()
                process_list.append(p)
            
            time.sleep(3)

        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown_event.set()
            print("joining")
            for p in process_list:
                p.join()
            print("Joined")


if __name__ == "__main__":
    m = Multi()
    m.run()