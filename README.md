# PiDashCam - Raspberry Pi DashCam

A python package to deliver dashcam functionality using a Raspberry Pi.

## Prerequisites

- python-camera
- python-gps
- python-rpi.gpio

## Hardware
- Raspberry Pi (I used a Model B+)
- Raspberry Pi Camera Module V2
- Adafruit Ultimate GPS breakout board connected using the UART on GPIO 14 and 15 (pins 8 and 10)
- PiCo UPS with 450mAh battery from [ModMyPi](https://www.modmypi.com/). PiCo uses GPIO x and x (pins x and x)
- Pi Camera HDMI extender from [Tindie](https://www.tindie.com)
- Two momentary push buttons
    - Button A uses GPIO x (pin x)
    - Button B uses GPIO x (Pin x)
- Two LEDs
    - LED1 uses GPIO x (pin x)
    - LED2 uses GPIO x (pin x)

## Functional Overview
- On startup, the camera starts recording to an in-memory buffer.
The video stream is overlaid with current date-time, speed, location and direction of travel.
- LED1 is illuminated whenever the camera is recording.

- If button A is pressed, the current contents of the buffer are flushed to a file, together with the following few seconds of video. (This can be used to capture the before and after of some event). The camera then goes back to recording into the buffer. LED1 flashes twice to confirm that the buffer has been saved.

- If button B is pressed, the current contents of the buffer are flushed to a file and the recording is stopped. LED1 is switched off.

- If button B is pressed again, recording is re-started from new.

- In the background, Resilio Sync is monitoring the folder containing the h264 format video files. If the Pi is connected to my home Wi-Fi, Resilio syncs the contents of the folder to a Mac in the house.

- If the power if switched off (e.g. ignition is turned off) and the Pi is connected to Wi-Fi, the attached UPS keeps the Pi powered for long enough to allow the video files to be synced to my Mac (after checking that the Pi is connected to my home Wi-Fi). It then shuts the Pi down gracefully. LED2 flashes when the Pi is running on UPS power.

- On the Mac, Hazel is monitoring the sync folder. When it sees h264 format files appear, it moves them to another non-syncing folder and converts them to mpeg4 using ffmpeg. By moving the videos to another folder, the limited disk space on the Pi is preserved.

## PiDashCam Code Overview
The code comprises an installed system daemon with four threads:
1. Main thread
2. Timer thread that is kicked off as needed
3. Camera thread
4. GPS thread

There are interrupt routines to handle the two buttons.

There are also Events to manage communications to and from the threads


## Pseudo Code
```
Button A interrupt handler (flush video)
  Start Timer thread

Button B interrupt handler (stop recording)
  set the flushBuffer event
  toggle the record flag

Timer thread
  wait for a defined period of time
  set flushBuffer event

Camera thread
  Do until shutDown
    If recording flag is set
      Initialise Camera
      While recording flag is set
        start recording into buffer
        if flushBuffer is set
          flush buffer to new file
          if shutdown is set
            reset recording event
        else
          update annotation with current date-time, position and speed
    wait for 1 second

GPS Thread
    Initialise connection to gpsd
    Do until shutDown
        update current GPS info
        
Power failure
  Start Timer thread
  set shutdown Event

Main thread
  Kick off Camera thread
  Kick off GPS thread
  reset the flush video flag
  reset the shutdown flag
  set the record flag
  while shutdown flag is not set
    wait for 1 second
  while LAN is connected and there are videos in the sync folder
    wait for 1 second
  Kill threads
  initiate system shutdown
  exit
```  
