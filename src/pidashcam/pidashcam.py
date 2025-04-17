"""
PiDashCam Raspberry Pi dashcam

A systemd compliant multi-threaded daemon to record video and respond to button presses
"""

BOUNCE_TIME = 300

# Standard libraries
import atexit
import logging
import signal
import sys, threading, termios, tty
from time import sleep

# Custom libraries
import config
from camerathread import Camera
from gpspoller import GPSPoller
from myqueue import MyQueue

# Specials
from gpiozero import Button, LED



class PiDashCam():
    """
    PiDashCam - main thread
    """
    def __init__(self):
        self._log  = logging.getLogger(__name__)
        self._log.debug("PiDashCam.__init__()")

        self._GPS_T = None
        self._camera_T = None

        # Inter-thread communication events
        self._flush_buffer = threading.Event()
        self._recording = threading.Event()
        self._GPS_queue = MyQueue()

        # Internal event used to initiate a controlled shutdown
        self._local_shutdown = threading.Event()

        # Setup a callback to catch SIGTERM
        signal.signal(signal.SIGTERM, self.__sigcatch)

        # GPIO initialisation
        self._recording_LED = LED(config.recording_LED)


        # register function to cleanup at exit
        atexit.register(self.__cleanup)

    def __button_A_pressed(self, channel):
        """
        Button A interrupt service routine
        Flush the in-memory buffer
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != config.button_A:
            return

        self.log.debug('Button A has been pressed')
        t = threading.Timer(config.post-record, self.__set_flush_buffer)
        t.start()
        # Start flashing recording_LED more frequently
        self._recording_LED.blink(1)


    def __button_B_pressed(self, channel):
        """
        Button B interrupt service routine
        Pause/resume recording
        """

        # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
        # falling-edge signal on another GPIO pin.

        if channel != config.button_B:
            return

        self._log.debug('Button B has been pressed')
        if self._recording.is_set():
            self._flush_buffer.set()
            sleep (1)
            self._recording.clear()
            self._recording_LED.off()
            self._log.debug('Recording suspended')
        else:
            self._recording.set()
            self._log.debug('Recording resumed')
            self._recording_LED.blink(0.5)

    def __sigcatch(self, signum, frame):
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

    def __cleanup(self):
        """
        GPIO cleanup
        """

        self._log.debug("Cleanup")
        self._log.info("Stopped")

    def __set_flush_buffer(self):
        self._flush_buffer.set()

    def __getch(self):
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
        exit

        # create the GPS thread
        self._GPS_T = GPSPoller("gpsT", self._GPS_queue)
        # ditto the Camera thread
        self._camera_T = Camera("cameraT", self._GPS_queue, self._flush_buffer,
            self._recording, self._recording_LED)

        self._recording.set()

        # Start threads
        self._GPS_T.start()
        self._camera_T.start()

        # Main Loop
        while not (self._local_shutdown.is_set()) :
            # Only check for keyboard characters if a keyboard is connected!
            # This won't be the case if we are running under systemd
            if sys.stdin.isatty():
                char = self.__getch()
                if char == "s":
                    self._log.debug("save")
                    t = threading.Timer(config.post_record, self.__set_flush_buffer)
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

if __name__ == "__main__":
  import logging

  # Initialise logging
  print(config.log_level)
  logging.basicConfig(level = {'info':logging.INFO, 'debug':logging.DEBUG}[config.log_level])
  log = logging.getLogger("pidashcam")
  log.setLevel({'info':logging.INFO, 'debug':logging.DEBUG}[config.log_level])
  log.info("piDashCam started")


  dashcam = PiDashCam()
  log.debug("dashcam = " + str(dashcam))
  dashcam.run()
