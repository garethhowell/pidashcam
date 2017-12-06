
import threading, logging
from gps import *
from .myqueue import MyQueue

## GpsPoller Thread

class GpsPoller(threading.Thread):
    """
    GPSPoller thread

    Sets up a connection to the GPS system daemon and enters Loop
    to update the current GPS information
    """

    def __init__(self, name, gpsQueue, shutdown):
        threading.Thread.__init__(self)
        self.name = name
        self.log = logging.getLogger(__name__)
        self.log.debug("GPSPoller.__init__()")
        #start updating the GPS info
        self.gpsd = gps(mode=WATCH_ENABLE)
        self.gpsQueue = gpsQueue
        self.shutdown = shutdown
        current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        self.log.debug("GPSPoller.run()")
        while not self.shutdown.isSet():
            #Continue to loop and grab EACH set of gpsd info
            self.gpsd.next()
            self.gpsQueue.put(self.gpsd.fix)
        self.log.debug("Ending GPS thread")
