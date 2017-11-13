#!/usr/bin/env python3
rev = '0.3'
destDir = '/home/pi/dev/Videos'
buffSize = 10 # size of in-memory buffer: 5 mins
extraTime = 10 # extra seconds to save: 5 mins

## PiDashCam
## Use picamera to maintain an in-memory buffer of buffSize seconds of video
## until Button A is pressed.
## If Button A is pressed, save the buffer plus the next extraTime seconds into a file.
## Then goes back to the in-memory buffer.

import io, os, sys
import RPi.GPIO as GPIO #to access the GPIO pins
from time import time, sleep
import picamera
from signal import pause
from datetime import datetime, timedelta
import keyboard, logging, logging.handlers
import threading
import termios, tty

## Setup

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s',)



GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def buttonAPressed():
#  global flushBuffer
  logging.info('Button A has been pressed')
  timerThread = Thread(target=myTimerThread)
  timerThread.start()

def buttonBPressed():
#  global recording
  logging.info('Button B has been pressed')
#  recording = False
  stopRecording.set()

GPIO.add_event_detect(23, GPIO.FALLING, callback=buttonAPressed, bouncetime=300)
GPIO.add_event_detect(17, GPIO.FALLING, callback=buttonBPressed, bouncetime=300)

def updateAnnotation(camera):
    i = datetime.now()
    now = i.strftime('%d/%b/%d %H:%M:%S')
    camera.annotate_text = now

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

button_delay = 0.2

def myTimerThread():
  logging.info('starting timer thread')
  global extraTime
#  global flushBuffer
  logging.info('sleeping for ' + str(extraTime) + ' seconds')
  sleep(extraTime)
  logging.info('stopping timer thread')
#  flushBuffer = True
  flushBuffer.set()

#---------------------------------------------------------

## Start capturing video

if __name__ == '__main__':
  stopRecording = threading.Event()
  flushBuffer = threading.Event()
  with picamera.PiCamera() as camera:
    camera.resolution = (1024, 960)
    camera.framerate = 25
    camera.vflip = True
    camera.hflip = True
    camera.annotate_background = picamera.Color('black')
    stream = picamera.PiCameraCircularIO(camera, seconds=buffSize)
    j = 0
    try:
      logging.info('starting piDashCam version ' + str(rev))
      stopRecording.clear()
      flushBuffer.clear()
#    while i < endTime:
      while not stopRecording.isSet():
        i = datetime.now()
        now = i.strftime('%d %b %d %H:%M:%S')
        logging.info('started recording to ' + str(buffSize) + ' seconds buffer at ' + now)
        camera.led = True
        camera.start_recording(stream, bitrate = 500000, format='h264')
        while not stopRecording.isSet():
          camera.wait_recording(0.2)
          char = ''
          char = getch()
          updateAnnotation(camera)
          if flushBuffer.isSet() or (char == "s") or (char == 'q'):
            if char == 's':
              timerThread = threading.Thread(target=myTimerThread)
              timerThread.start()
            else:
              i = datetime.now()
              f = i.strftime('%Y%m%d-%H%M%S.h264')
              outFile = str(destDir) + '/' + f
              logging.info('saving file... ' + outFile)
              stream.copy_to(outFile)
              if flushBuffer.isSet():
                logging.info('switching back to recording to buffer..')
                flushBuffer.clear()
              else:
                flushBuffer.clear()
                stopRecording.set()

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
