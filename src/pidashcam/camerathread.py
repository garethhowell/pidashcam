from datetime import datetime, timedelta
import logging
import os
import queue
import threading
import time

import cv2
from gpiozero import Button, LED
from libcamera import Transform
import numpy as np
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder, MJPEGEncoder
from picamera2.outputs import CircularOutput

import config
from myqueue import MyQueue

FPS = 30 # How fast do we want to capture frames
SPEED_CONV = 2.23694 # convert m/s to mph

class Camera(threading.Thread):
  """Camera

  Capture video using the PiCamera and store in a local folder
  """

  def __init__(self, name, gps_queue, flush_now, recording_LED):
    """Initialise the camera

    Keyword parameters
    name -- an informal name to identify the thread
    gps_queue -- Queue object from which to consume new fixes
    flush_now -- Event object that signals that we need to save the in-memory buffer
    recording_LED -- GPIO object for the front panel LED
    """
    super(Camera, self).__init__()
    self.log = logging.getLogger(__name__)
    self.log.debug("Camera.__init__()")

    self._name = name
    self._gps_queue = gps_queue
    self._flush_now = flush_now
    self._flush_now.clear()
    self._recording_LED = recording_LED

    self._shutdown = threading.Event()
    self._running = True

    self._camera = Picamera2()
    video_config = self._camera.create_video_configuration(
                  main={"size": (config.width, config.height),
                        "format": "RGB888"},
                  lores={"size":(320, 240), "format": "YUV420"},
                  transform=Transform(hflip=config.hflip, vflip=config.vflip)
                  )
    self._camera.configure(video_config)
    self._encoder = H264Encoder()

    # Calculate how many buffers we need
    buffer_size = config.pre_record * FPS
    self._encoder.output = CircularOutput(buffersize = buffer_size)

  def __update_annotation(self):
    """Update the annotation text"""

    fix = self._gps_queue.get(False)
    self._gps_queue.clear()
    lat = fix.latitude
    lon = fix.longitude
    speed = fix.speed * SPEED_CONV
    track = fix.track
    i = datetime.now()
    now = i.strftime('%d-%b-%d %H:%M:%S')
    annotation = now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True"
    return annotation

  def __flush_to_file():
    """Flush the contents of the buffer to disk"""

    # Construct the desired filename
    self._recording_LED.blink(0.5)
    epoch = int(time.time())
    out_file = str(config.dest_dir) + '/' + f"{epoch}." + config.video_format

    # Start to flush
    self.log.debug('Flushing buffer to ' + out_file)
    self._encoder.output.fileoutput = out_file
    self._encoder.output.start()
    self._camera.start_encoder(self._encoder)

    # Wait for the desired amount of post_record time
    time.sleep(config.post_record)

    # Stop saving video
    self._encoder.output.stop()
    self._encoder.output.fileoutput = None
    self.log.debug('Switching back to recording to buffer..')
    self._flush_now.clear()
    self._recording_LED.blink(1)

  def run(self):
    """
    Override the super run to do the actual work
    """

    self.log.debug("Camera.run()")
    annotation = "No Fix"
    colour = (0, 255, 0, 255)
    origin = (-1, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1
    thickness = 2

    # Main Loop
    self._camera.start_preview(Preview.QT)  # Can also use Preview.NULL if headless
    while not self._shutdown.isSet():
      self._recording_LED.blink(.5)
      self.log.debug('Recording to ' + str(config.pre_record) + ' seconds buffer')

      annotation = self.__update_annotation()
      overlay = np.zeros((640, 480, 4), dtype=np.uint8)
      cv2.putText(overlay, annotation, origin, font, scale, colour, thickness)
      self._camera.set_overlay(overlay)

      # Check if we need to save the video
      if self._flush_now.isSet():
        self.__flush_to_file()
        self._flush_now.clear()
      time.sleep(1)

    self._camera.close()
    self.log.debug("Ending camera thread")

  def join(self, timeout=None):
      """Shutdown the camera"""
      self._shutdown.set()
      super(Camera, self).join(timeout)
