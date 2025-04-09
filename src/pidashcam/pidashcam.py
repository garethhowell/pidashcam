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

import config
from buffer import RingBuffer
from camerathread import Camera
from gpspoller import GPSPoller
from myqueue import MyQueue

# Specials
import RPi.GPIO as GPIO



class PiDashCam():
    """
    PiDashCam - main thread
    """
    def __init__():
        self._log  = logging.getLogger(__name__)
        self._log.debug("PiDashCam.__init__()")

        self._src = config.src
        self._dest_dir = config.dest_dir
        self._video_format = config.video_format
        self._button_A = config.button_A
        self._button_B = config.button_B
        self._LED_1 = config.LED_1
        self._width = config.width
        self._height = config.height
        self._buff_size = config.buff_size
        self._extra_time = config.extra_time
        self._vflip = config.vflip
        self._hflip = config.hflip

        self._GPS_T = None
        self._camera_T = None

        # Inter-thread communication events
        self._flush_buffer = threading.Event()
        self._recording = threading.Event()
        self._GPS_queue = MyQueue()

        # Internal event used to initiate a controlled shutdown
        self._local_shutdown = threading.Event()
        
        # Setup a callback to catch SIGTERM
        signal.signal(signal.SIGTERM, self.sigcatch)

        # GPIO initialisation
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._button_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._button_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.setup(self._LED_1, GPIO.OUT)
        self._recording_LED = GPIO.PWM(self._LED_1, 0.5)

        GPIO.add_event_detect(self.buttonA, GPIO.FALLING, callback=self.buttonAPressed, bouncetime=BOUNCE_TIME)
        GPIO.add_event_detect(self.buttonB, GPIO.FALLING, callback=self.buttonBPressed, bouncetime=BOUNCE_TIME)

        # register function to cleanup at exit
        atexit.register(self.cleanup)

    def button_A_pressed(self, channel):
        """
        Button A interrupt service routine
        Flush the in-memory buffer
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != self._button_A:
            return

        self.log.debug('Button A has been pressed')
        t = threading.Timer(self.extraTime, self.set_flush_buffer)
        t.start()
        # Start flashing LED1 more frequently
        self.recording_LED.change_frequency(1)


    def button_B_pressed(self, channel):
        """
        Button B interrupt service routine
        Pause/resume recording
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != self._button_B:
            return

        self._log.debug('Button B has been pressed')
        if self._recording.isSet():
            self._flush_buffer.set()
            sleep (1)
            self._recording.clear()
            self._recording_LED.stop()
            self._log.debug('Recording suspended')
        else:
            self._recording.set()
            self._log.debug('Recording resumed')
            self._recording_LED.change_frequency(0.5)

    def sigcatch(self, signum, frame):
        """
        Signal handler
        """

        if signum == signal.SIGTERM:
            # Probably been sent from systemctl stop
            # shutdown gracefully
            self._log.debug("SIGTERM received, shutting down")
            self._flush_buffer.set()
            sleep(1)
            self._recording.clear()
            sleep(1)
            self._local_shutdown.set()
            sleep(1)
            sys.exit(0)

    def cleanup(self):
        """
        GPIO cleanup
        """

        self._log.debug("Cleanup")
        self._log.info("Stopped")

    def set_flush_buffer(self):
        self._flush_buffer.set()

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

        self._log.debug("PiDashCam.run()")

        # create the GPS thread
        self._GPS_T = GPSPoller("gpsT", self._GPS_queue)
        # ditto the Camera thread
        self._camera_T = Camera("cameraT", self._src, self._GPS_queue, self._flush_buffer,
            self._recording, self._recording_LED, self._dest_dir,
            self._video_format, self._width, self._height, self._buff_size, self._extra_time,
            self._vflip, self._hflip)
        
        self._recording.set()

        # Start threads
        self._GPS_T.start()
        self._camera_T.start()
        
        # Main Loop
        while not (self._local_shutdown.isSet() or self._UPS_Shutdown.isSet()) :
            # Only check for keyboard characters if a keyboard is connected!
            # This won't be the case if we are running under systemd
            if sys.stdin.isatty():
                char = self.getch()
                if char == "s":
                    self._log.debug("save")
                    t = threading.Timer(self._extra_time, self._set_flush_buffer)
                    t.start()
                elif char == "q":
                    self._log.debug("Shutdown")
                    self._local_shutdown.set()
            sleep(1)

        # Shutdown
        self._log.debug("Shutting down, waiting for threads to die")
        self._local_shutdown.set()
        self._GPS_T.join()
        self._log.debug("GPS thread died")
        self._camera_T.join()
        self._log.debug("Camera thread died.")
        self._log.info("Exiting")
