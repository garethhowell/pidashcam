#! /usr/bin/env python

from datetime import datetime
import logging
import time

import picamera
class Camera():
    """Camera

    Capture video using the PiCamera and store in a local folder
    """

    def __init__(self, name, destDir, videoFormat = 'h264',
            cameraRes = {'h': 1440,'v': 1280}, buffSize = 30, extraTime = 30,
            vflip = False, hflip = False):
        """Initialise the Pi-Camera

        Keyword parameters
        name -- an informal name to identify the thread
        destDir -- String object - where to save videos
        videoFormat -- the desired format for recorded video (default 'h264')
        cameraRes -- the desired resolution of the recorded video (default 1440x1280)
        buffSize -- the size (in seconds) of the in-memory buffer (default 60s)
        extraTime -- how long to continue recording after flushBuffer is set
                before saving (default 30s)
        vflip -- whether or not to flip the video vertically (default False)
        hflip -- whether or not to flip the video horizontally (default False)
        """
        self.destDir = destDir
        self.videoFormat = videoFormat
        self.cameraRes = cameraRes
        self.buffSize = buffSize
        self.extraTime = extraTime
        self.vflip = vflip
        self.hflip = hflip

        self.log = logging.getLogger(__name__)
        self.log.debug("Camera.__init__()")
        self.running = True
        self.camera = picamera.PiCamera()

    def run(self):
        """
        Do the actual work
        """

        self.log.debug("Camera.run()")

        # Set up the camera
        self.camera.resolution = (self.cameraRes['h'], self.cameraRes['v'])
        self.camera.vflip = self.vflip
        self.camera.hflip = self.hflip
        self.camera.annotate_background = picamera.Color('black')

        # Create in-memory circular buffer
        # Needs to be big enough for pre and post record
        stream = picamera.PiCameraCircularIO(self.camera, seconds=self.buffSize + self.extraTime)

        # Main Loop

        self.log.debug('Recording to ' + str(self.buffSize + self.extraTime) + ' seconds buffer')
        self.camera.start_recording(stream, format=self.videoFormat)
        self.camera.wait_recording(0.2)
        self.camera.annotate_text = "Label"

        # Save the buffer
        if True:
            i = datetime.now()
            f = i.strftime('%Y%m%d-%H%M%S.' + self.videoFormat)
            outFile = str(self.destDir) + '/' + f
            self.log.debug('Flushing buffer to ' + outFile)
            stream.copy_to(outFile)
            self.log.debug('Switching back to recording to buffer..')
        time.sleep(1)
        self.camera.close()
        self.log.debug("Ending camera thread")

if __name__ == "__main__":
    cam =