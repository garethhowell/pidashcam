#!/usr/bin/env python
rev = '0.4'
destDir = '/home/pi/dev/Videos'
buffSize = 10 # size of in-memory buffer: 5 mins
extraTime = 10 # extra seconds to save: 5 mins
button_delay = 0.2
gpsd = None #setting the global variable
camera = None

## PiDashCam
## Use picamera to maintain an in-memory buffer of buffSize seconds of video
## until Button A is pressed.
## If Button A is pressed, save the buffer plus the next extraTime seconds into a file.
## Then goes back to the in-memory buffer.

import io, os, sys, picamera, threading, termios, tty
import RPi.GPIO as GPIO #to access the GPIO pins
from time import time, sleep
from signal import pause
from datetime import datetime, timedelta
import keyboard, logging, logging.handlers
from gps import *

## Setup

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def buttonAPressed():
#  global flushBuffer
    logging.info('Button A has been pressed')
    timerThread=Thread(target=myTimerThread, args=(flushBuffer, extraTime), daemon=True)
    timerThread.start()

def buttonBPressed():
#  global recording
    logging.info('Button B has been pressed')
    recording.clear()

GPIO.add_event_detect(23, GPIO.FALLING, callback=buttonAPressed, bouncetime=300)
GPIO.add_event_detect(17, GPIO.FALLING, callback=buttonBPressed, bouncetime=300)

def updateAnnotation():
    global gpsd, camera

    i = datetime.now()
    now = i.strftime('%d/%b/%d %H:%M:%S')
    lat = gpsd.fix.latitude
    lon = gpsd.fix.longitude
    speed = gpsd.fix.speed
    camera.annotate_text = now + " " + str(lat) + " " + str(lon)

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

def saveBuffer():
    global destDir
    i = datetime.now()
    f = i.strftime('%Y%m%d-%H%M%S.h264')
    outFile = str(destDir) + '/' + f
    logging.debug('saving file... ' + outFile)
    stream.copy_to(outFile)

## Timer thread

def myTimerThread(e, t):
    logging.debug('starting timer thread')
    logging.debug('sleeping for ' + str(t) + ' seconds')
    sleep(t)
    logging.debug('stopping timer thread')
    e.set()

#os.system('clear') #clear the terminal (optional)

class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd #bring it in scope
        gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
        self.current_value = None
        self.running = True #setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
#---------------------------------------------------------

## Main thread

if __name__ == '__main__':
    gpsp = GpsPoller() # create the thread
    gpsp.start()
    recording = threading.Event()
    flushBuffer = threading.Event()
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 960)
        camera.framerate = 25
        camera.vflip = True
        camera.hflip = True
        camera.annotate_background = picamera.Color('black')
        stream = picamera.PiCameraCircularIO(camera, seconds=buffSize)
        try:
            logging.info('starting piDashCam version ' + str(rev))
            recording.set()
            flushBuffer.clear()
            while recording.isSet():
                i = datetime.now()
                now = i.strftime('%d %b %d %H:%M:%S')
                logging.debug('started recording to ' + str(buffSize) + ' seconds  buffer at ' + now)
                camera.led = True
                camera.start_recording(stream, bitrate = 500000, format='h264')
                while recording.isSet():
                    camera.wait_recording(0.2)
                    updateAnnotation()
                    char = getch()
                    if char == "s":
                        logging.debug("save")
                        flushBuffer.clear()
                        timerThread=threading.Thread(target=myTimerThread, args=(flushBuffer, extraTime), daemon=True)
                        timerThread.start()
                    elif char == "q":
                        logging.debug("quit")
                        saveBuffer()
                        recording.clear()
                    elif flushBuffer.isSet():
                        logging.debug("flush")
                        saveBuffer()
                        logging.debug('switching back to recording to buffer..')
                        flushBuffer.clear()

        except KeyboardInterrupt as SystemExit: #when you press ctrl+c
            logging.warn('KeyboardInterrupt')
            i = datetime.now()
            f = i.strftime('%Y%m%d-%H%M%S.h264')
            outFile = str(destDir) + '/' + f
            logging.debug('saving stream to ' + outFile)
            stream.copy_to(outFile)
            logging.warn("Killing Thread...")

        finally:
            logging.info('stopping...')
            camera.led = False
            camera.stop_recording()
            camera.close()
