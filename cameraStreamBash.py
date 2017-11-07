#!/usr/bin/env python3
rev = '0.2'
destDir = '/home/pi/dev/Videos'
buffSize = 10 # size of in-memory buffer
extraTime = 10 # extra seconds to save
 
## This Python script uses picamera to maintain an in-memory buffer of 5 mins video
## until Button A is pressed.
## When Button A is pressed, the script saves the buffer plus the next 5 mins into a file.
## It then goes back to the in-memory buffer.
 
import io
import random
import os
from time import time 
import picamera
import sys
from signal import pause
from datetime import datetime, timedelta

def motion_detected():
  return random.randint(0,10) == 0

#---------------------------------------------------------
 
## Start capturing video
 
with picamera.PiCamera() as camera:
  camera.resolution = (1024, 960)
  camera.framerate = 25
  camera.vflip = True
  camera.hflip = True
  camera.annotate_background = picamera.Color('black')
  stream = picamera.PiCameraCircularIO(camera, seconds=buffSize)
  camera.start_recording(stream, bitrate = 500000, format='h264')
  j = 0
  try:
    print 'starting...'
    x = timedelta(minutes=1)
    i = datetime.now()
    endTime = i + x
    while i < endTime:
      camera.wait_recording(0.2)
      i = datetime.now()
      now = i.strftime('%d/%b/%d %H:%M:%S')
      if motion_detected():
        print 'motion detected'
        outFile = i.strftime('%Y%m%d-%H%M%S.h264')
        i = datetime.now()
        delta = timedelta(seconds=extraTime)
        j = i + delta
	print now
        print j.strftime('%d/%b/%d %H:%M:%S')
        while i < j:
          now = i.strftime('%d/%b/%y-%H:%M:%S')
          camera.annotate_text = now
          camera.wait_recording(0.2)
          i = datetime.now()
#        f = str(d) + '/motion' + str(j) + '.h264'
        f = str(destDir) + '/' + outFile
        print f
        stream.copy_to(f)
        break
  finally:
	print 'stopping...'
	camera.stop_recording()

    
