import funcy
import threading


@funcy.decorator
def run_in_thread(call):
    t_worker = threading.Thread(target=call)
    t_worker.start()
    t_worker.join()
