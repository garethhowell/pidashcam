#!/usr/bin/python -p

"""PiDashCam Raspberry Pi dashcam

A systemd compliant multi-threaded daemon to record video and respond to button presses

"""

BOUNCE_TIME = 300

# Standard libraries
import io, os, sys, threading, termios, tty
import atexit, socket
from time import time, sleep
from signal import pause
import keyboard
#import argparse
import logging
#import logging.handlers
#import xmltodict
import signal

from .camerathread import Camera
from .gpspoller import GPSPoller
from .upspico import UPSPIco
from .myqueue import MyQueue

# Specials
import RPi.GPIO as GPIO



class PiDashCam():
    """
    PiDashCam - main thread
    """
    def __init__(self, destDir, buttonA, buttonB, led1, videoFormat = 'h264',
        cameraRes = {'h': 1440,'v': 1280}, buffSize = 30, extraTime = 30,
        vflip = False, hflip = False):
        self.log  = logging.getLogger(__name__)
        self.log.debug("PiDashCam.__init__()")

        self.destDir = destDir
        self.videoFormat = videoFormat
        self.buttonA = buttonA
        self.buttonB = buttonB
        self.led1 = led1
        self.cameraRes = cameraRes
        self.buffSize = buffSize
        self.extraTime = extraTime
        self.vflip = vflip
        self.hflip = hflip

        self.gpsT = None
        self.cameraT = None

        # Inter-thread communication events
        self.flushBuffer = threading.Event()
        self.recording = threading.Event()
        self.gpsQueue = MyQueue()

        # Internal event used to initiate a controlled shutdown
        self.localShutdown = threading.Event()
        # So UPS can signal immediate Shutdown
        self.UPSShutdown = threading.Event()

        # Setup a callback to catch SIGTERM
        signal.signal(signal.SIGTERM, self.sigcatch)

        # GPIO initialisation
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.buttonA, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.buttonB, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(self.led1, GPIO.OUT)
        self.recordingLED = GPIO.PWM(self.led1, 0.5)

        GPIO.add_event_detect(self.buttonA, GPIO.FALLING, callback=self.buttonAPressed, bouncetime=BOUNCE_TIME)
        GPIO.add_event_detect(self.buttonB, GPIO.FALLING, callback=self.buttonBPressed, bouncetime=BOUNCE_TIME)

        # register function to cleanup at exit
        atexit.register(self.cleanup)

    def buttonAPressed(self, channel):
        """
        Button A interrupt service routine
        Flush the in-memory buffer
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != self.buttonA:
            return

        self.log.debug('Button A has been pressed')
        t = threading.Timer(self.extraTime, self.setFlushBuffer)
        t.start()
        # Start flashing LED1 more frequently
        self.recordingLED.ChangeFrequency(1)


    def buttonBPressed(self, channel):
        """
        Button B interrupt service routine
        Pause/resume recording
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != self.buttonB:
            return

        self.log.debug('Button B has been pressed')
        if self.recording.isSet():
            self.flushBuffer.set()
            sleep (1)
            self.recording.clear()
            self.recordingLED.stop()
            self.log.debug('Recording suspended')
        else:
            self.recording.set()
            self.log.debug('Recording resumed')
            self.recordingLED.ChangeFrequency(0.5)

    def sigcatch(self, signum, frame):
        """
        Signal handler
        """

        if signum == signal.SIGTERM:
            # Probably been sent from systemctl stop
            # shutdown gracefully
            self.log.debug("SIGTERM received, shutting down")
            self.flushBuffer.set()
            sleep(1)
            self.recording.clear()
            sleep(1)
            self.localShutdown.set()
            sleep(1)
            sys.exit(0)

    def cleanup(self):
        """
        GPIO cleanup
        """

        self.log.debug("Cleanup")
        self.log.info("Stopped")

    def setFlushBuffer(self):
        self.flushBuffer.set()

    def getch(self):
        """ getch - utility function to read a character from the keyboard
        """

        ch = ' '
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def run(self):

        self.log.debug("PiDashCam.run()")

        # create the GPS thread
        self.gpsT = GPSPoller("gpsT", self.gpsQueue)
        # ditto the Camera thread
        self.cameraT = Camera("cameraT", self.gpsQueue, self.flushBuffer,
            self.recording, self.recordingLED, self.destDir,
            self.videoFormat, self.cameraRes, self.buffSize, self.extraTime,
            self.vflip, self.hflip)
        # ditto UPS thread
        self.UPST = UPSPIco("UPST", self.destDir, self.recording, self.UPSShutdown)

        self.recording.set()

        # Start threads
        self.gpsT.start()
        self.cameraT.start()
        self.UPST.start()

        # Main Loop
        while not (self.localShutdown.isSet() or self.UPSShutdown.isSet()) :
            # Only check for keyboard characters if a keyboard is connected!
            # This won't be the case if we are running under systemd
            if sys.stdin.isatty():
                char = self.getch()
                if char == "s":
                    self.log.debug("save")
                    t = threading.Timer(self.extraTime, self.setFlushBuffer)
                    t.start()
                elif char == "q":
                    self.log.debug("Shutdown")
                    self.localShutdown.set()
            sleep(1)

        # Shutdown
        self.log.debug("Shutting down, waiting for threads to die")
        self.localShutdown.set()
        self.gpsT.join()
        self.log.debug("GPS thread died")
        self.cameraT.join()
        self.log.debug("Camera thread died.")
        self.UPST.join()
        self.log.debug("UPS thread died.")
        self.log.info("Exiting")
