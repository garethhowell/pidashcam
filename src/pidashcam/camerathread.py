from datetime import datetime, timedelta
from gpiozero import Button, LED
from libcamera import Transform
import logging
import os
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
import queue
import threading
import time

import config

from myqueue import MyQueue

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

        self._shutdown = threading.Event()

        self.log = logging.getLogger(__name__)
        self.log.debug("Camera.__init__()")
        self._running = True

        self._camera = Picamera2()
        video_config = self._camera.create_video_configuration(
                      main={"size": (config.width, config.height)},
                      transform=Transform(hflip=config.hflip, vflip=config.vflip)
                      )
        self._camera.configure(video_config)
        self._encoder = H264Encoder()
        self._output = CircularOutput()

    def __update_annotation():
      # Update the annotation text
      try:
          fix = self._gps_queue.get(False)
      except self._gps_queue.empty():
          pass
      else:
          self._gps_queue.clear()
          lat = fix.latitude
          lon = fix.longitude
          speed = fix.speed * SPEED_CONV
          track = fix.track
          i = datetime.now()
          now = i.strftime('%d-%b-%d %H:%M:%S')
          annotation = now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True"
          return(annotation)

    # Function to overlay annotations using OpenCV
    def __annotate_frame(frame, annotation):

      cv2.putText(frame, annotation, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                  1, (255, 255, 255), 2, cv2.LINE_AA)
      return frame

    # Live preview with annotation (optional, needs display)
    def __start_annotated_preview(self):
      self._camera.start_preview(Preview.NULL)  # Can also use Preview.NULL if headless

      def preview_loop():
          while True:
              frame = self._camera.capture_array()
              annotation = self.__update_annotation()
              frame = self.__annotate_frame(frame, annotation)
              # You can display it or just annotate it for recording
              cv2.imshow("Preview", frame)
              if cv2.waitKey(1) == ord('q'):
                  break

      threading.Thread(target=preview_loop, daemon=True).start()

    def run(self):
        """
        Overrides the super run to do the actual work
        """

        self.log.debug("Camera.run()")

        # Main Loop
        while not self._shutdown.isSet():
            while self._recording.isSet():
                self._recording_LED.blink(.5)
                self.log.debug('Recording to ' + str(config.buffer_size) + ' seconds buffer')
                self.__start_annotated_preview()

                while self._recording.isSet():
                    #self._camera.wait_recording(0.2)
                    # Check if we need to save the video
                    if self._flush_buffer.isSet():
                        i = datetime.now()
                        f = i.strftime('%Y%m%d-%H%M%S.' + config.video_format)
                        out_file = str(config.dest_dir) + '/' + f
                        self.log.debug('Flushing buffer to ' + out_file)
                        self._output.fileout = out_file
                        self._output.start()

                        # wait for  while
                        # Stop saving video
                        self._output.stop()
                        self.log.debug('Switching back to recording to buffer..')
                        self._flush_buffer.clear()
                        #self._recording_LED.ChangeFrequency(0.5)

                    # Pause recording if necessary
                    if not self._recording.isSet():
                        self.log.debug("Recording paused")
                        self._recording_LED.stop()
                    if self._shutdown.isSet():
                        self._flush_buffer.set()
                        self._recording.clear()
            time.sleep(1)
        self._camera.close()
        self.log.debug("Ending camera thread")

    def join(self, timeout=None):
        """Shutdown the camera"""
        self._shutdown.set()
        super(Camera, self).join(timeout)
