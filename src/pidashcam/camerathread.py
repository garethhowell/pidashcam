#! /usr/bin/python -u
import picamera2
from picamera2 import CircularIO
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

  def __init__(self, name, gps_queue, flush_buffer, recording):
    """Initialise the Camera

    Keyword parameters
    name -- an informal name to identify the thread
    gpsQueue -- Queue object from which to consume new fixes
    flushBuffer -- Event object that signals need to save the in-memory buffer
    recording -- Event object that signals whether or not to record video
    """
    super(Camera, self).__init__()
    self._name = name
    self._src = config.src
    self._gps_queue = gps_queue
    self._flush_buffer = flush_buffer
    self._recording = recording
    self._recording_LED = config.LED_1

    self._dest_dir = config.dest_dir
    self._video_format = config.video_format
    self._width = config.width
    self._height = config.height
    self._buff_size = config.buff_size
    self._vflip = config.vflip
    self._hflip = config.hflip

    self._shutdown = threading.Event()

    self._log = logging.getLogger(__name__)
    self._log.debug("Camera.__init__()")

    self._running = False
    self._read_lock = threading.Lock()
    self.thread = None

    # Create the ring buffer
    self._ring_buffer = RingBuffer(self)

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

  def flush_buffer(self):
    """
    Save the contents of the ring buffer to a file
    """
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d_%H.%M.%S")
    fn = "output/{}/{}.{}".format(self._src, date, self._video_format)
    writer = cv2.VideoWriter(fn, cv2.VideoWriter_dourcc(*"mp4v"), 30.0, (config.width, config.height))
    self._log.info("Saving file {}".format(fn))
    for frame in self._buffer:
      writer.write(frame)
    writer.release()



  def run(self):
    """
    Overrides the super run to do the actual work
    """

    self._log.debug("Camera.run()")

    # Main Loop
    while not self._shutdown.isSet():
      while self._recording.isSet():
        self._recordingLED.start(50)
        self._log.debug('Recording to ' + str(self._buff_size) + ' seconds buffer')
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

          self._ring_buffer.add(frame)

          # Check if we need to save the buffer
          if self._flush_buffer.isSet():
            self.flush_buffer()

            self._log.debug('Switching back to recording to buffer..')
            self._ring_buffer.empty()
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
