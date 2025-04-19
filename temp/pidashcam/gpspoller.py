
import threading
import logging
from gps import *

## GPSPoller Thread

class GPSPoller(threading.Thread):
    """
    GPSPoller thread

    Sets up a connection to the GPS system daemon and enters Loop
    to update the current GPS information
    """

    def __init__(self, name, gps_queue):
        super(GPSPoller, self).__init__()
        self._name = name
        self._log = logging.getLogger(__name__)
        self._log.debug("GPSPoller.__init__()")
        #start updating the GPS info
        self._gpsd = gps(mode=WATCH_ENABLE)
        self._gps_queue = gps_queue
        #current_value = None
        self._running = True #setting the thread running to true

        self._shutdown = threading.Event()

    def run(self):
        self._log.debug("GPSPoller.run()")
        while not self._shutdown.isSet():
            #Continue to loop and grab EACH set of gpsd info
            self._gpsd.next()
            self._gps_queue.put(self._gpsd.fix)
        self._log.debug("Ending GPSPoller thread")

    def join(self, timeout=None):
        self._shutdown.set()
        super(GPSPoller, self).join(timeout)
