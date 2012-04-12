#!/usr/bin/env python

import threading
import time

class ExamHandler(threading.Thread):

    def __init__(self, timeout):
        self.timeout = timeout
        self.file_notifier = threading.Condition()
        self.adds = []
        self.added = False
        threading.Thread.__init__(self)

    def run(self):
        print("Starting.")
        while len(self.adds) == 0 or self.added:
            self.added = False
            self.file_notifier.acquire()
            self.file_notifier.wait(self.timeout)
            self.file_notifier.release()
        print("Done acquiring files - list: %s" % (self.adds))

    def add_item(self, item):
        print("Adding %s" % (item))
        self.file_notifier.acquire()
        self.adds.append(item)
        self.added = True
        self.file_notifier.notify()
        self.file_notifier.release()


def main():
    eh = ExamHandler(2)
    eh.start()
    for i in range(4):
        eh.add_item(i)
        time.sleep(1)
    eh.join()
    print(eh)

if __name__ == '__main__':
    main()