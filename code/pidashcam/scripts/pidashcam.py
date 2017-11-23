#!/usr/bin/env python
rev = '0.2.0'
destDir = '/home/pi/PiDashCam/Videos'
fileExt = "h264"
buffSize = 10 # size of in-memory buffer: secs
extraTime = 10 # extra seconds to save: secs
button_delay = 0.2
speedConv = 2.23694 # convert m/s to mph
cameraRes = {'h': 1280,'v': 960}
cameraFormat = 'h264'
BUTTON_A = 23
BUTTON_B = 24

gpsd = None #setting the global variable
camera = None



## PiDashCam

import io, os, sys, picamera, threading, termios, tty
import RPi.GPIO as GPIO #to access the GPIO pins
from time import time, sleep
from signal import pause
from datetime import datetime, timedelta
import keyboard, logging, logging.handlers
from gps import *



## Setup

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)


def buttonAPressed(channel):
    """
    Button A interrupt service routine
    Flush the in-memory buffer
    """

    # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
    # falling-edge signal on another GPIO pin.
    if channel != BUTTON_A:
        return

    logging.info('Button A has been pressed')
    global extraTime
    t = threading.Timer(extraTime, setFlushBuffer)
    t.start()

def buttonBPressed(channel):
    """
    Button B interrupt service routine
    Pause/resume recording
    """

    # This test is here because the user *might* have another HAT plugged in or another circuit that produces a
    # falling-edge signal on another GPIO pin.
    if channel != BUTTON_B:
        return

    logging.info('Button B has been pressed')
    recording.clear()

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(BUTTON_A, GPIO.FALLING, callback=buttonAPressed, bouncetime=300)
GPIO.add_event_detect(BUTTON_B, GPIO.FALLING, callback=buttonBPressed, bouncetime=300)


class CameraThread(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        logging.debug("CameraT init")
        self.running = True

    def run(self):
        global gpsd, camera, destDir, speedConv, cameraRes, cameraFormat, fileExt
        logging.debug("cameraT running")
        camera = picamera.PiCamera()
        camera.resolution = (cameraRes['h'], cameraRes['v'])
        camera.vflip = True
        camera.hflip = True
        camera.annotate_background = picamera.Color('black')
        stream = picamera.PiCameraCircularIO(camera, seconds=buffSize)
        while not shutdown.isSet():
            while recording.isSet():
                i = datetime.now()
                now = i.strftime('%d %b %d %H:%M:%S')
                logging.debug('started recording to ' + str(buffSize) + ' seconds buffer at ' + now)
                camera.led = True
                camera.start_recording(stream, format=cameraFormat)
                while recording.isSet():
                    camera.wait_recording(0.2)
                    i = datetime.now()
                    now = i.strftime('%d-%b-%d %H:%M:%S')
                    lat = gpsd.fix.latitude
                    lon = gpsd.fix.longitude
                    speed = gpsd.fix.speed * speedConv
                    track = gpsd.fix.track
                    camera.annotate_text = now + " " + "{0:0.3f}".format(lat) + " " + "{0:0.3f}".format(lon) + " " + "{0:0.0f}".format(speed) + " m/s " + "{0:0.0f}".format(track) + " True"
                    if flushBuffer.isSet():
                        logging.debug("flush")
                        i = datetime.now()
                        f = i.strftime('%Y%m%d-%H%M%S.' + fileExt)
                        outFile = str(destDir) + '/' + f
                        logging.debug('saving file... ' + outFile)
                        stream.copy_to(outFile)
                        logging.debug('switching back to recording to buffer..')
                        flushBuffer.clear()
            logging.debug("stopped recording")
            sleep(1)
        camera.close()
        logging.debug("stopping camera thread")

## GpsPoller Thread

class GpsPoller(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        logging.debug("GPS thread initialised")
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        logging.debug("GPS thread running")
        while not shutdown.isSet():
            gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
        logging.debug("stopping GPS thread")

## Timer timeout function

def setFlushBuffer():
  global flushBuffer
  flushBuffer.set()

def getch():
    ch = ' '
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

#---------------------------------------------------------

## Main thread

if __name__ == '__main__':
    ## Inter thread events

    flushBuffer = threading.Event()
    recording = threading.Event()
    shutdown = threading.Event()

    logging.info('piDashCam version ' + str(rev) + " main thread")
    gpsT = GpsPoller("gpsT") # create the GPS thread
    gpsT.start()
    cameraT = CameraThread("cameraT") # ditto the Camera thread
    cameraT.start()
    recording.set()
    flushBuffer.clear()
    while recording.isSet():
        char = getch()
        if char == "s":
            logging.debug("save")
            t = threading.Timer(extraTime, setFlushBuffer)
            t.start()
        elif char == "q":
            logging.debug("quit")
            flushBuffer.set()
            recording.clear()
            sleep(1)
    logging.info("Shutting down, waiting for threads to die")
    shutdown.set()
    gpsT.join()
    logging.debug("GPS thread died")
    cameraT.join()
    logging.debug("Camera thread died. Exiting")