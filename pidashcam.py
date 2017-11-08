#!/usr/bin/env python3
rev = '0.2'
destDir = '/home/pi/dev/Videos'
buffSize = 30 # size of in-memory buffer: 5 mins
extraTime = 30 # extra seconds to save: 5 mins

## PiDashCam
## Use picamera to maintain an in-memory buffer of buffSize seconds of video
## until Button A is pressed.
## If Button A is pressed, save the buffer plus the next extraTime seconds into a file.
## Then goes back to the in-memory buffer.

import io
import RPi.GPIO as GPIO #to access the GPIO pins
import os
from time import time
import picamera
import sys
from signal import pause
from datetime import datetime, timedelta
import keyboard
import logging
import logging.handlers

myLogger = logging.getLogger(__name__)
myLogger.setLevel(logging.DEBUG)
syslogHandler = logging.handlers.SysLogHandler(address='/dev/log')
myLogger.addHandler(syslogHandler)

saveRecording = False
shutdownNow = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def buttonAPressed():
  global saveRecording
  myLogger.info('Button A has been pressed')
  saveRecording = True

def buttonBPressed():
  global shutdownNow
  myLogger.info('Button B has been pressed')
  shutdownNow = True

GPIO.add_event_detect(23, GPIO.FALLING, callback=buttonAPressed, bouncetime=300)
GPIO.add_event_detect(17, GPIO.FALLING, callback=buttonBPressed, bouncetime=300)

def updateAnnotation(camera):
    i = datetime.now()
    now = i.strftime('%d/%b/%d %H:%M:%S')
    camera.annotate_text = now

#---------------------------------------------------------

## Setup


## Start capturing video


with picamera.PiCamera() as camera:
  camera.resolution = (1024, 960)
  camera.framerate = 25
  camera.vflip = True
  camera.hflip = True
  camera.annotate_background = picamera.Color('black')
  stream = picamera.PiCameraCircularIO(camera, seconds=buffSize)
  j = 0
  try:
#    x = timedelta(minutes=2)
#    i = datetime.now()
#    endTime = i + x
#    print i
#    print endTime
    myLogger.info('starting piDashCam version ' + str(rev))
#    while i < endTime:
    while True:
      i = datetime.now()
      now = i.strftime('%d/%b/%d %H:%M:%S')
      myLogger.info('started recording to ' + str(buffSize) + ' seconds buffer at ' + now)
      camera.start_recording(stream, bitrate = 500000, format='h264')
      while True:
        camera.wait_recording(0.2)
        updateAnnotation(camera)
        if saveRecording: #continue recording for extraTime seconds and save the buffer
          myLogger.info('Continue for ' + str(extraTime) + ' seconds')
          f = i.strftime('%Y%m%d-%H%M%S.h264')
          outFile = str(destDir) + '/' + f

          i = datetime.now()
          delta = timedelta(seconds=extraTime)
          j = i + delta
	      #print now
          #print j.strftime('%d/%b/%d %H:%M:%S')
          while i < j:
            updateAnnotation(camera)
            camera.wait_recording(0.2)
            i = datetime.now()

          myLogger.info('saving file... ' + outFile)
          stream.copy_to(outFile)
          myLogger.info('switching back to recording to buffer..')
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    myLogger.warn('KeyboardInterrupt')
    i = datetime.now()
    f = i.strftime('%Y%m%d-%H%M%S.h264')
    outFile = str(destDir) + '/' + f
    myLogger.debug('saving stream to ' + outFile)
    stream.copy_to(outFile)
    myLogger.warn("Killing Thread...")

  finally:
    logging.info('stopping...')
    camera.stop_recording()
    camera.close()
