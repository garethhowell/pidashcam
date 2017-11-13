# PiDashCam - Raspberry Pi DashCam

A python package to deliver dashcam functionality using a Raspberry Pi

## Prerequisites

- python-camera
- python-gps

## Hardware
- Raspberry Pi (I used a Model B+)
- Raspberry Pi Camera Module V2
- Adafruit Ultimate GPS breakout board
- PIco UPS with 450mAh battery from [ModMyPi](https://www.modmypi.com/)
- Pi Camera HDMI extender from [Tindie](https://www.tindie.com)
- Two momentary push buttons

## Functional Overview
- On startup, the camera starts recording to an in-memory buffer.
The video stream is overlaid with current date-time, speed, location and direction of travel.

- If button A is pressed, the current contents of the buffer are flushed to a file, together with the following few seconds of video. (This can be used to capture the before and aftr of some event). The camera then goes back to recording into the buffer.

- If button B is pressed, the current contents of the buffer are flushed to a file and the recording is stopped.

- If button B is pressed again, recording is re-started from new.

- In the background, Resilio Sync is monitoring the folder containing the h264 format video files. If the Pi is connected to my home Wi-Fi, resilio syncs the contents of the folder to a Mac in the house.

- If the power if switched off (e.g. ignition is turned off), the attached UPS keeps the Pi powered for long enough to allow the video files to be synced. It then shuts the Pi down gracefully

- On the Mac, Hazel is monitoring the resilio folder. When it sees h264 format files appear, it moves them to another folder and converts them to mpeg4 using ffmpeg. By moving the videos to another folder, the limited disk space on the Pi is preserved.

## PiDashCam Code Overview
The code comprises an installed system daemon with two threads:
1. A main thread that controls the camera
2. a timer thread that is kicked off as needed



## Pseudo Code
```
Initialise interrupt handlers
  Button A (flush video)
    Start background thread that sets flush video flag when it times out
  Button B (stop recording)
    set the flush video flag
    toggle the record flag

Initialise camera
set the record flag
reset the flush video flag
Do Forever
  if record flag is set
    record into X secs in-memory buffer
    update annotate_text every 0.2 secs
    if flush video flag set
        save video
        reset flush video flag
    fi
  else
    wait for 1 second
  fi
loop


Power failure
  Start background thread that sets flush video flag when it times out
  wait 1 second
  reset record flag
```  
