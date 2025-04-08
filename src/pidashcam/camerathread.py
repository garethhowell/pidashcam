#! /usr/bin/python -u

import cv2
from datetime import datetime, timedelta
import logging
import os
import threading
import time
import Queue
from myqueue import MyQueue

SPEED_CONV = 2.23694 # convert m/s to mph

class Camera(threading.Thread):
    """Camera

    Capture video and store in a local folder
    """

    def __init__(self, name, src, driver, gps_queue, flush_buffer, recording,
            recording_LED, dest_dir, video_format = 'h264',
            camera_res = {'h': 1440,'v': 1280}, buff_size = 30, extra_time = 30,
            vflip = False, hflip = False):
        """Initialise the Camera

        Keyword parameters
        name -- an informal name to identify the thread
        src -- The video source to capture
        driver -- The video driver to use
        gpsQueue -- Queue object from which to consume new fixes
        flushBuffer -- Event object that signals need to save the in-memory buffer
        recording -- Event object that signals whether or not to record video
        recordingLED -- GPIO object for the front panel LED
        destDir -- String object - where to save videos
        videoFormat -- the desired format for recorded video (default 'h264')
        width -- image width (default 1440)
        height -- image height (default 1200)
        buffSize -- the size (in seconds) of the in-memory buffer (default 60s)
        extraTime -- how long to continue recording after flushBuffer is set
                before saving (default 30s)
        vflip -- whether or not to flip the video vertically (default False)
        hflip -- whether or not to flip the video horizontally (default False)
        """
        super(Camera, self).__init__()
        self._name = name
        self._src = src
        self._gps_queue = gps_queue
        self._flush_buffer = flush_buffer
        self._recording = recording
        self._recording_LED = recording_LED

        self._dest_dir = dest_dir
        self._video_format = video_format
        self._width = width
        self._height = height
        self._buff_size = buff_size
        self._extra_time = extra_time
        self._vflip = vflip
        self._hflip = hflip

        self._shutdown = threading.Event()

        self._log = logging.getLogger(__name__)
        self._log.debug("Camera.__init__()")
        
        if driver is None:
          self._cap = cv2.VideoCapture(self._src)
        else:
          self._cap = cv2.VideoCapture(self.src, driver)
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, _width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _height)
        self._grabbed, self._frame = self.cap.read()
        self._running = False
        self._read_lock = threading.Lock()
        self.thread = None

    def run(self):
        """
        Overrides the super run to do the actual work
        """

        self._log.debug("Camera.run()")

        # Set up the camera
        self._camera.resolution = (self._camera_res['h'], self._camera_res['v'])
        self._camera.vflip = self._vflip
        self._camera.hflip = self._hflip
        self._camera.annotate_background = picamera.Color('black')

        # Create in-memory circular buffer
        # Needs to be big enough for pre and post record
        stream = picamera.PiCameraCircularIO(self._camera, seconds=self._buff_size + self._extra_time)

        # Main Loop
        while not self._shutdown.isSet():
            while self._recording.isSet():
                self._recordingLED.start(50)
                self._log.debug('Recording to ' + str(self._buff_size + self._extra_time) + ' seconds buffer')
                self._camera.start_recording(stream, format=self._video_format)
                while self._recording.isSet():
                    self._camera.wait_recording(0.2)
                    # Update the annotation text
                    try:
                        fix = self._gpsQueue.get(False)
                    except Queue.Empty:
                        pass
                    else:
                        self._gps_queue.clear()
                        lat = fix.latitude
                        lon = fix.longitude
                        speed = fix.speed * SPEED_CONV
                        track = fix.track
                        i = datetime.now()
                        now = i.strftime('%d-%b-%d %H:%M:%S')
                        self._camera.annotate_text = now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True"

                    # Check if we need to save the buffer
                    if self._flush_buffer.isSet():
                        i = datetime.now()
                        f = i.strftime('%Y%m%d-%H%M%S.' + self._video_format)
                        out_file = str(self.destDir) + '/' + f
                        self._log.debug('Flushing buffer to ' + out_file)
                        stream.copy_to(out_file)
                        self._log.debug('Switching back to recording to buffer..')
                        self._flush_buffer.clear()
                        self._recording_LED.change_frequency(0.5)

                    # Pause recording if necessary
                    if not self._recording.isSet():
                        self._log.debug("Recording paused")
                        self._recording_LED.stop()
                    if self._shutdown.isSet():
                        self._flush_buffer.set()
                        self._recording.clear()
            time.sleep(1)
        self._camera.close()
        self._log.debug("Ending camera thread")

    def join(self, timeout=None):
        """Shutdown the camera"""
        self._shutdown.set()
        super(Camera, self).join(timeout)
