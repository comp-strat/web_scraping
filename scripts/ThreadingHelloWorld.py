import multiprocessing
import time


def worker(num):
    """thread worker function"""
    print("Hello from thread %s (process starting)" % num)
    time.sleep(num)
    print("Goodbye from thread %s (process ending)" % num)
    return


if __name__ == '__main__':
    jobs = []
    for i in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=worker, args=(i,))
        jobs.append(p)
        p.start()
