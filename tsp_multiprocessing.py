from multiprocessing import Queue, Pool, Event
import time

q = Queue()
shutdown_event = Event()
s = "hello "

def run_solver(id):
    try:
        i = 0
        while not shutdown_event.is_set():
            i += 1
            q.put(f"{s} {id:2} {i}")
            time.sleep(0.5)
        
    except KeyboardInterrupt:
        pass
    time.sleep(0.5)


if __name__ == "__main__":
    p = Pool(processes=8)

    
    print("map start")
    p.map_async(run_solver,range(8))
    print("map end")

    try:
        while True:
            print(q.get(timeout=1.0))
    except KeyboardInterrupt:
        pass
    finally:
        shutdown_event.set()
    
    print("joining")
    # p.join()
    print("Joined")


