
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

    def __init__(self, name, GPS_queue):
        super(GPSPoller, self).__init__()
        self.name = name
        self.log = logging.getLogger(__name__)
        self.log.debug("GPSPoller.__init__()")
        self.GPS_queue = GPS_queue

        # Open the GPS Daemon process
        self.GPS_daemon = gps(mode=WATCH_ENABLE)

        self.running = True

        self.shutdown = threading.Event()

    def run(self):
        self.log.debug("GPSPoller.run()")
        while not self.shutdown.is_set():
            #Continue to loop and grab EACH fix
            # Note that gpsd may take a while to get a fix
            # and may not have a fix at all
            # This is a blocking call
            # and will wait for a fix to be available
            self.log.debug("GPSPoller.run() - waiting for fix")
            self.GPS_daemon.next()
            self.log.debug("GPSPoller.run() - got fix")
            # Check if we have a fix
            if self.GPS_daemon.fix.mode >= 2:
                self.log.debug("GPSPoller.run() - got fix")
                # Put the fix in the queue, but only if queue is empty
                # This is to prevent the queue from getting too large
                # and to prevent the GPS daemon from blocking
                #self.log.debug("GPSPoller.run() - queue size: %d" % self.GPS_queue.qsize())
                # If we have a queue, put the fix in it
                if self._gps_queue is not None:
                    # Empty the queue before putting the new fix in
                    self._log.debug("GPSPoller.run() emptying queue")
                    self._gps_queue.empty()
                    self._log.debug("GPSPoller.run() putting fix in queue")
                    self._gps_queue.put(self._gpsd.fix)

            else:
                self.log.debug("GPSPoller.run() - no fix")
                pass
            # Sleep for a bit to prevent the loop from running too fast
            # and to give the GPS daemon time to get a fix
            time.sleep(1)
        # If we get here, the thread is shutting down
        self.log.debug("Ending GPSPoller thread")

    def join(self, timeout=None):
        self.shutdown.set()
        super(GPSPoller, self).join(timeout)
