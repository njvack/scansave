#!/usr/bin/env python

import threading
import time

class ExamHandler(threading.Thread):

    def __init__(self, timeout):
        self.timeout = timeout
        self.file_notifier = threading.Event()
        self.file_notifier.set()
        threading.Thread.__init__(self)

    def run(self):
        print("Starting.")
        while self.file_notifier.is_set():
            self.file_notifier.clear()
            self.file_notifier.wait(self.timeout)

    def add_item(self, item):
        if not self.is_alive():
            raise RuntimeError("I'm not started!")
        print("Adding %s" % (item))
        self.file_notifier.set()


def main():
    eh = ExamHandler(1)
    eh.start()
    #time.sleep(2)
    for i in range(4):
        eh.add_item(i)
        time.sleep(0.5)
    eh.join()
    print(eh)

if __name__ == '__main__':
    main()