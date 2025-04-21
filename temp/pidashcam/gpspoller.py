
import threading
import logging
from gps import gps, WATCH_ENABLE

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
            #Continue to loop and grab EACH fix
            self._gpsd.next()
            # We only want to update the queue if we have a valid fix
            if self._gpsd.fix.mode >= 2:
                # If we have a queue, put the fix in it
                if self._gps_queue is not None:
                    # Empty the queue before putting the new fix in
                    self._log.debug("GPSPoller.run() emptying queue")
                    self._gps_queue.empty()
                    self._log.debug("GPSPoller.run() putting fix in queue")
                    self._gps_queue.put(self._gpsd.fix)
              time.sleep(1)
        # If we get here, the thread is shutting down
        self._log.debug("GPSPoller.run() shutting down")
        self._log.debug("Ending GPSPoller thread")

    def join(self, timeout=None):
        self._shutdown.set()
        super(GPSPoller, self).join(timeout)
