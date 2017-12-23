#! /usr/bin/python -u

import os, threading, time, logging, picamera
from datetime import datetime, timedelta

import Queue
from .myqueue import MyQueue

SPEED_CONV = 2.23694 # convert m/s to mph

class Camera(threading.Thread):
    """Camera

    Capture video using the PiCamera and store in a local folder
    """

    def __init__(self, name, gpsQueue, flushBuffer, recording,
            recordingLED, destDir, videoFormat = 'h264',
            cameraRes = {'h': 1440,'v': 1280}, buffSize = 30, extraTime = 30,
            vflip = False, hflip = False):
        """Initialise the Pi-Camera

        Keyword parameters
        name -- an informal name to identify the thread
        gpsQueue -- Queue object from which to consume new fixes
        flushBuffer -- Event object that signals need to save the in-memory buffer
        recording -- Event object that signals whether or not to record video
        recordingLED -- GPIO object for the front panel LED
        destDir -- String object - where to save videos
        videoFormat -- the desired format for recorded video (default 'h264')
        cameraRes -- the desired resolution of the recorded video (default 1440x1280)
        buffSize -- the size (in seconds) of the in-memory buffer (default 60s)
        extraTime -- how long to continue recording after flushBuffer is set
                before saving (default 30s)
        vflip -- whether or not to flip the video vertically (default False)
        hflip -- whether or not to flip the video horizontally (default False)
        """
        super(Camera, self).__init__()
        self.name = name
        self.gpsQueue = gpsQueue
        self.flushBuffer = flushBuffer
        self.recording = recording
        self.recordingLED = recordingLED

        self.destDir = destDir
        self.videoFormat = videoFormat
        self.cameraRes = cameraRes
        self.buffSize = buffSize
        self.extraTime = extraTime
        self.vflip = vflip
        self.hflip = hflip

        self.shutdown = threading.Event()

        self.log = logging.getLogger(__name__)
        self.log.debug("Camera.__init__()")
        self.running = True
        self.camera = picamera.PiCamera()

    def run(self):
        """
        Overrides the super run to do the actual work
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
        while not self.shutdown.isSet():
            while self.recording.isSet():
                self.recordingLED.start(50)
                self.log.debug('Recording to ' + str(self.buffSize + self.extraTime) + ' seconds buffer')
                self.camera.start_recording(stream, format=self.videoFormat)
                while self.recording.isSet():
                    self.camera.wait_recording(0.2)
                    # Update the annotation text
                    try:
                        fix = self.gpsQueue.get(False)
                    except Queue.Empty:
                        pass
                    else:
                        self.gpsQueue.clear()
                        lat = fix.latitude
                        lon = fix.longitude
                        speed = fix.speed * SPEED_CONV
                        track = fix.track
                        i = datetime.now()
                        now = i.strftime('%d-%b-%d %H:%M:%S')
                        self.camera.annotate_text = now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True"

                    # Check if we need to save the buffer
                    if self.flushBuffer.isSet():
                        i = datetime.now()
                        f = i.strftime('%Y%m%d-%H%M%S.' + self.videoFormat)
                        outFile = str(self.destDir) + '/' + f
                        self.log.debug('Flushing buffer to ' + outFile)
                        stream.copy_to(outFile)
                        self.log.debug('Switching back to recording to buffer..')
                        self.flushBuffer.clear()
                        self.recordingLED.ChangeFrequency(0.5)

                    # Pause recording if necessary
                    if not self.recording.isSet():
                        self.log.debug("Recording paused")
                        self.recordingLED.stop()
                    if self.shutdown.isSet():
                        self.flushBuffer.set()
                        self.recording.clear()
            time.sleep(1)
        self.camera.close()
        self.log.debug("Ending camera thread")

    def join(self, timeout=None):
        """Shutdown the camera"""
        self.shutdown.set()
        super(Camera, self).join(timeout)
