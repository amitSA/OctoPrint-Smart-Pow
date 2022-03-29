import funcy
import threading


@funcy.decorator
def run_in_thread(call, wait=True):
    t_worker = threading.Thread(target=call)
    t_worker.start()
    if wait:
        t_worker.join()
