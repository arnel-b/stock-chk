import threading
import time


class TestThreading(object):

    def __init__(self, interval=3):
        self.interval = interval
        self.proceed = True
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()        # start the execution

    def inside(self):
        x = 0
        while x <= 20:
            print("Background Thread : " + str(x))
            x += 1
            time.sleep(self.interval)
            print("INSIDE", self.proceed)
            if not self.proceed:
                break

    def run(self):

        self.inside()

        print('Program terminated by User')