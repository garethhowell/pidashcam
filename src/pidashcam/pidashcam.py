#!/usr/bin/python -p

"""PiDashCam Raspberry Pi dashcam

A systemd compliant multi-threaded daemon to record video and respond to button presses

"""

BOUNCE_TIME = 300

# Standard libraries
import atexit
import io
import keyboard
import logging
import os
import signal
from signal import pause
import sys
import termios
import threading
import tty
import socket
from time import time, sleep

# Third party libraries
from gpiozero import Button, LED

# Local modules
from pidashcam.camerathread import Camera
from pidashcam.gpspoller import GPSPoller
from pidashcam.upspico import UPSPIco
from pidashcam.myqueue import MyQueue




class PiDashCam():
    """
    PiDashCam - main thread
    """
    def __init__(self, dest_dir, button_A, button_B, recording_LED, video_format = 'h264',
        camera_res = {'h': 1440,'v': 1280}, buffer_size = 30, extra_time = 30,
        vflip = False, hflip = False):
        self.log  = logging.getLogger(__name__)
        self.log.debug("PiDashCam.__init__()")

        self.dest_dir = dest_dir
        self.video_format = video_format
        self.camera_res = camera_res
        self.buffer_size = buffer_size
        self.extra_time = extra_time
        self.vflip = vflip
        self.hflip = hflip

        self.GPS_thread = None
        self.camera_thread = None

        # Inter-thread communication events
        self.flush_buffer_event = threading.Event()
        self.recording_event = threading.Event()
        self.GPS_queue = MyQueue()

        # Internal event used to initiate a controlled shutdown
        self.local_shutdown_event = threading.Event()
        # So UPS can signal immediate Shutdown
        self.UPS_shutdown_event = threading.Event()

        # GPIO initialisation
        self.button_A = Button(button_A, bounce_time=BOUNCE_TIME)
        self.button_A.when_pressed = self.button_A_pressed
        self.button_B = Button(button_B, bounce_time=BOUNCE_TIME)
        self.button_B.when_pressed = self.button_B_pressed
        self.recording_LED = LED(recording_LED)

        # Setup a callback to catch SIGTERM
        signal.signal(signal.SIGTERM, self.sigcatch)

        # register function to cleanup at exit
        atexit.register(self.cleanup)

    def button_A_pressed(self, channel):
        """
        Button A interrupt service routine
        Flush the in-memory buffer
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != self.button_A:
            return

        self.log.debug('Button A has been pressed')
        t = threading.Timer(self.extra_time, self.set_flush_buffer_event)
        t.start()
        # Start flashing recording_LED more frequently
        self.recording_LED.ChangeFrequency(1)


    def button_B_pressed(self, channel):
        """
        Button B interrupt service routine
        Pause/resume recording
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != self.button_B:
            return

        self.log.debug('Button B has been pressed')
        if self.recording_event.isSet():
            self.flush_buffer_event.set()
            sleep (1)
            self.recording_event.clear()
            self.recording_LED.stop()
            self.log.debug('Recording suspended')
        else:
            self.recording_event.set()
            self.log.debug('Recording resumed')
            self.recording_LED.ChangeFrequency(0.5)

    def sigcatch(self, signum, frame):
        """
        Signal handler
        """

        if signum == signal.SIGTERM:
            # Probably been sent from systemctl stop
            # shutdown gracefully
            self.log.debug("SIGTERM received, shutting down")
            self.flush_buffer_event.set()
            sleep(1)
            self.recording_event.clear()
            sleep(1)
            self.local_shutdown_event.set()
            sleep(1)
            sys.exit(0)

    def cleanup(self):
        """
        GPIO cleanup
        """

        self.log.debug("Cleanup")
        self.log.info("Stopped")

    def set_flush_buffer_event(self):
        self.flush_buffer_event.set()

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
        self.GPS_thread = GPSPoller("GPS_thread", self.GPS_queue)
        # ditto the Camera thread
        self.camera_thread = Camera("camera_thread", self.GPS_queue, self.flush_buffer_event,
            self.recording_event, self.recording_LED, self.dest_dir,
            self.video_format, self.camera_res, self.buffer_size, self.extra_time,
            self.vflip, self.hflip)
        # ditto UPS thread
        self.UPS_thread = UPSPIco("UPST", self.dest_dir, self.recording_event, self.UPS_shutdown_event)

        self.recording_event.set()

        # Start threads
        self.GPS_thread.start()
        self.camera_thread.start()
        self.UPS_thread.start()

        # Main Loop
        while not (self.local_shutdown_event.isSet() or self.UPS_shutdown_event.isSet()) :
            # Only check for keyboard characters if a keyboard is connected!
            # This won't be the case if we are running under systemd
            if sys.stdin.isatty():
                char = self.getch()
                if char == "s":
                    self.log.debug("save")
                    t = threading.Timer(self.extra_time, self.set_flush_buffer_event)
                    t.start()
                elif char == "q":
                    self.log.debug("Shutdown")
                    self.local_shutdown_event.set()
            sleep(1)

        # Shutdown
        self.log.debug("Shutting down, waiting for threads to die")
        self.local_shutdown_event.set()
        self.GPS_thread.join()
        self.log.debug("GPS thread died")
        self.camera_thread.join()
        self.log.debug("Camera thread died.")
        self.UPS_thread.join()
        self.log.debug("UPS thread died.")
        self.log.info("Exiting")
