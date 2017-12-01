#!/usr/bin/env python3
rev = '0.2'
destDir = '/home/pi/dev/Videos'
buffSize = 10 # size of in-memory buffer
extraTime = 10 # extra seconds to save
 
import io
import random
import os
from time import time 
import picamera
import sys
from signal import pause
from datetime import datetime, timedelta

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
    print endTime
    print i
    while i < endTime:
      camera.wait_recording(0.2)
      i = datetime.now()
      now = i.strftime('%d/%b/%d %H:%M:%S')
      camera.annotate_text = now
    print i
    outFile = i.strftime('%Y%m%d-%H%M%S.h264')
    f = str(destDir) + '/' + outFile
    print f
    stream.copy_to(f)
  finally:
	print 'stopping...'
	camera.stop_recording()

    
