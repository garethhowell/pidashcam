#! /usr/bin/python -u

import ringBuffer as ringBuffer
import config
import cv2
from datetime import datetime, timedelta
import logging
import os
import threading
import time

SPEED_CONV = 2.23694 # convert m/s to mph

class Camera(threading.Thread):
  """Camera
  Capture video and store in a local folder
  """

  def __init__(self, name, src, gps_queue, flush_buffer, recording,
        recording_LED, dest_dir, video_format = 'h264',
        camera_res = {'h': 1440,'v': 1280}, buff_size = 60, extra_time = 30,
        vflip = False, hflip = False):
    """Initialise the Camera

    Keyword parameters
    name -- an informal name to identify the thread
    src -- The video source to capture
    gpsQueue -- Queue object from which to consume new fixes
    flushBuffer -- Event object that signals need to save the in-memory buffer
    recording -- Event object that signals whether or not to record video
    recordingLED -- GPIO object for the front panel LED
    destDir -- String object - where to save videos
    videoFormat -- the desired format for recorded video (default 'h264')
    width -- image width (default 1440)
    height -- image height (default 1200)
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

    self._running = False
    self._read_lock = threading.Lock()
    self.thread = None

    # Create the ring buffer
    self._ring_buffer = RingBuffer()

  def __draw_label(img, text, pos, bg_color):
    """
    Convenience function to label the image
    """

    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.4
    color = (0, 0, 0)
    thickness = cv2.FILLED
    margin = 2
    txt_size = cv2.getTextSize(text, font_face, scale, thickness)

    end_x = pos[0] + txt_size[0][0] + margin
    end_y = pos[1] - txt_size[1][1] - margin

    cv2.rectangle(img, pos, (end-x, end_y), bg_color, thickness)
    cv2.putText(img, text, pos, font_face, scale, color, 1, cv2.LINE_AA)


  def run(self):
    """
    Overrides the super run to do the actual work
    """

    self._log.debug("Camera.run()")

    # Main Loop
    while not self._shutdown.isSet():
      while self._recording.isSet():
        self._recordingLED.start(50)
        self._log.debug('Recording to ' + str(self._buff_size + self._extra_time) + ' seconds buffer')
        recording = True

        # open the camera stream
        self._cap = cv2.VideoCapture(self._src)
        time.sleep(2)

        if self._cap.isOpened():
          #Set the dimensions etc of the video frame
          self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, _width)
          self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, _height)
          self._cap.isOpened()
        else:
          self._log.error("Camera could not be opened")

        while recording:
          self._frame = cap.read()[1]
          if self._frame is None:
            self._log.error("Camera returned no frame")
            self._buffer = []
            recording = False



          # Imprint the GPS data on the frame
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
            dt = datetime.now()
            now = dt.strftime('%d-%b-%d %H:%M:%S')
            self.__draw_label(frame, now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True", (0, 0), (255, 0, 0))

          self._ring_buffer.write(frame)

          # Check if we need to save the buffer
          if self._flush_buffer.isSet():
            self._ring_buffer.flush()

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
