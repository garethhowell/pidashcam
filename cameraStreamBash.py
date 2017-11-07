#!/usr/bin/env python3
rev = '0.2'
destDir = '/home/pi/dev/Videos'
buffSize = 30 # size of in-memory buffer: 5 mins
extraTime = 30 # extra seconds to save: 5 mins
 
## Use picamera to maintain an in-memory buffer of buffSize seconds of video
## until Button A is pressed.
## If Button A is pressed, save the buffer plus the next extraTime seconds into a file.
## Then goes back to the in-memory buffer.
 
import io #to access the GPIO pins
import os
from time import time 
import picamera
import sys
from signal import pause
from datetime import datetime, timedelta
import keyboard

def buttonAPressed():
#  if keyboard.is_pressed('q'):
#    print('You pressed a key')
#    return 1
#  else:
    return 0

#---------------------------------------------------------
 
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
    print 'starting...'
#    while i < endTime:
    while True:
      i = datetime.now()
      now = i.strftime('%d/%b/%d %H:%M:%S')
      print 'recording to buffer...'
      camera.start_recording(stream, bitrate = 500000, format='h264')
      while True:
        camera.wait_recording(0.2)
        i = datetime.now()
        now = i.strftime('%d/%b/%d %H:%M:%S')
        camera.annotate_text = now
        if buttonAPressed(): #continue recording for extraTime seconds and save the buffer
          print 'Button A has been pressed'
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

          f = str(destDir) + '/' + outFile
          print 'saving file... ' + f
          stream.copy_to(f)
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print "\nKilling Thread..."
    
  finally:
    print 'stopping...'
    camera.stop_recording()

    
