import threading
import datetime, time
        
class ThreadClass(threading.Thread):
    def run(self):
        now = datetime.datetime.now()
        print "%s was born at time: %s" % (self.getName(), now)
        for x in range(5):
            print '%s is alive' % self.getName()
            time.sleep(1)
        
for i in range(2):
    t = ThreadClass()
    t.start()
