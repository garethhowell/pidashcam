import os, threading, time, logging
import picamera2 as picamera
from datetime import datetime, timedelta
import config

import queue
#from .myqueue import MyQueue

SPEED_CONV = 2.23694 # convert m/s to mph

class Camera(threading.Thread):
    """Camera

    Capture video using the PiCamera and store in a local folder
    """

    def __init__(self, name, gps_queue, flush_buffer, recording,
            recording_LED):
        """Initialise the Pi-Camera

        Keyword parameters
        name -- an informal name to identify the thread
        gps_queue -- Queue object from which to consume new fixes
        flush_buffer -- Event object that signals need to save the in-memory buffer
        recording -- Event object that signals whether or not to record video
        recording_LED -- GPIO object for the front panel LED
        """
        super(Camera, self).__init__()
        self._name = name
        self._gps_queue = gps_queue
        self._flush_buffer = flush_buffer
        self._recording = recording
        self._recording_LED = recording_LED

        self._dest_dir = config.dest_dir
        self._video_format = config.video_format

        self._shutdown = threading.Event()

        self.log = logging.getLogger(__name__)
        self.log.debug("Camera.__init__()")
        self._running = True
        self._camera = picamera.Picamera2()

    def run(self):
        """
        Overrides the super run to do the actual work
        """

        self.log.debug("Camera.run()")

        # Set up the camera
        self._camera.resolution = (config.width, config.height)
        self._camera.vflip = config.vflip
        self._camera.hflip = config.hflip
        self._camera.annotate_background = picamera.Color('black')

        # Create in-memory circular buffer
        # Needs to be big enough for pre and post record
        stream = picamera.PiCameraCircularIO(self._camera, seconds=config.buffer_size)

        # Main Loop
        while not self._shutdown.isSet():
            while self._recording.isSet():
                self._recording_LED.start(50)
                self.log.debug('Recording to ' + str(config.buffer_size) + ' seconds buffer')
                self._camera.start_recording(stream, format=config.video_format)
                while self._recording.isSet():
                    self._camera.wait_recording(0.2)
                    # Update the annotation text
                    try:
                        fix = self._gpsQueue.get(False)
                    except Queue.Empty:
                        pass
                    else:
                        self._gpsQueue.clear()
                        lat = fix.latitude
                        lon = fix.longitude
                        speed = fix.speed * SPEED_CONV
                        track = fix.track
                        i = datetime.now()
                        now = i.strftime('%d-%b-%d %H:%M:%S')
                        self._camera.annotate_text = now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True"

                    # Check if we need to save the buffer
                    if self._flushBuffer.isSet():
                        i = datetime.now()
                        f = i.strftime('%Y%m%d-%H%M%S.' + config.video_format)
                        out_file = str(config.dest_dir) + '/' + f
                        self.log.debug('Flushing buffer to ' + out_file)
                        stream.copy_to(out_file)
                        self.log.debug('Switching back to recording to buffer..')
                        self._flushBuffer.clear()
                        self._recording_LED.ChangeFrequency(0.5)

                    # Pause recording if necessary
                    if not self._recording.isSet():
                        self.log.debug("Recording paused")
                        self._recording_LED.stop()
                    if self._shutdown.isSet():
                        self._flushBuffer.set()
                        self._recording.clear()
            time.sleep(1)
        self._camera.close()
        self.log.debug("Ending camera thread")

    def join(self, timeout=None):
        """Shutdown the camera"""
        self._shutdown.set()
        super(Camera, self).join(timeout)