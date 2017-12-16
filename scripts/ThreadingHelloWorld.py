import multiprocessing
import time
from multiprocessing import Process, Value


def worker(thread_num, counter):
    """thread worker function"""
    print("Hello from thread %s (process starting)" % thread_num)
    with counter.get_lock():
        counter.value += 1
        print(counter.value)
    time.sleep(thread_num)
    print("Goodbye from thread %s (process ending)" % thread_num)
    return


if __name__ == '__main__':
    processes = []
    counter = Value("i", 0)
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(i, counter))
        processes.append(p)
        p.start()
    for i in processes:
        p.join()
    print(counter.value)
