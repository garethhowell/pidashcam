
import threading, logging
from gps import *
from .myqueue import MyQueue

## GPSPoller Thread

class GPSPoller(threading.Thread):
    """
    GPSPoller thread

    Sets up a connection to the GPS system daemon and enters Loop
    to update the current GPS information
    """

    def __init__(self, name, gpsQueue):
        super(GPSPoller, self).__init__()
        self.name = name
        self.log = logging.getLogger(__name__)
        self.log.debug("GPSPoller.__init__()")
        #start updating the GPS info
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.gpsQueue = gpsQueue
        #current_value = None
        self.running = True #setting the thread running to true

        self.shutdown = threading.Event()

    def run(self):
        self.log.debug("GPSPoller.run()")
        while not self.shutdown.isSet():
            #Continue to loop and grab EACH set of gpsd info
            self.gpsd.next()
            self.gpsQueue.put(self.gpsd.fix)
        self.log.debug("Ending GPSPoller thread")

    def join(self, timeout=None):
        self.shutdown.set()
        super(GPSPoller, self).join(timeout)
