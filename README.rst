PiDashCam - Raspberry Pi DashCam
================================

A python package to deliver dashcam functionality using a Raspberry Pi.

Prerequisites
-------------

-  python-camera
-  python-gps
-  python-rpi.gpio

Hardware
--------

-  Raspberry Pi (I used a Model B+)
-  Raspberry Pi Camera Module V2
-  Adafruit Ultimate GPS breakout board connected using the UART on GPIO
   14 and 15 (pins 8 and 10)
-  PiCo UPS with 450mAh battery from
   `ModMyPi <https://www.modmypi.com/>`__. PiCo uses GPIO x and x (pins
   x and x)
-  Pi Camera HDMI extender from `Tindie <https://www.tindie.com>`__
-  Two momentary push buttons

   -  Button A uses GPIO 23 (pin 16)
   -  Button B uses GPIO 24 (Pin 18)

-  One LED

   -  LED1 uses GPIO 16 (pin 36)

Functional Overview
-------------------

-  On startup, the camera starts recording to an in-memory buffer. The
   video stream is overlaid with current date-time, speed, location and
   direction of travel.
-  LED1 is flashing slowly whenever the camera is recording.

-  If button A is pressed, the current contents of the buffer are
   flushed to a file, together with the following few seconds of video.
   (This can be used to capture the before and after of some event). The
   camera then goes back to recording into the buffer. LED1 flashes
   faster whilst the buffer is being saved.

-  If button B is pressed, the current contents of the buffer are
   flushed to a file and the recording is stopped. LED1 is switched off.

-  If button B is pressed again, recording is re-started from new and
   LED1 flashes slowly.

-  In the background, Resilio Sync is monitoring the folder containing
   the h264 format video files. If the Pi is connected to my home Wi-Fi,
   Resilio syncs the contents of the folder to a Mac in the house.

-  If the power if switched off (e.g. ignition is turned off) and the Pi
   is connected to Wi-Fi, the attached UPS keeps the Pi powered for long
   enough to allow the video files to be synced to my Mac (after
   checking that the Pi is connected to my home Wi-Fi). It then shuts
   the Pi down gracefully. LED2 flashes when the Pi is running on UPS
   power.

-  On the Mac, Hazel is monitoring the sync folder. When it sees h264
   format files appear, it moves them to another non-syncing folder and
   converts them to mpeg4 using ffmpeg. By moving the videos to another
   folder, the limited disk space on the Pi is preserved.

PiDashCam Code Overview
-----------------------

The code comprises an installed system daemon with four threads: 1. Main
thread 2. Timer thread that is kicked off as needed 3. Camera thread 4.
GPS thread

There are interrupt routines to handle the two buttons.

There are also Events to manage communications to and from the threads

Pseudo Code
-----------

::

    Button A interrupt handler (notable event)
      Start Timer thread, set flushBuffer flag on timeout

    Button B interrupt handler (toggle recording)
      If we are recording
        flush the buffer immediately
        clear the recording flag
      else
        set the record flag
      EndIf

    Camera thread
      While shutDown flag is not set
        While recording flag is set
          Initialise Camera
          start recording into buffer
          While recording flag is set - inner recording loop
            update annotation with current date-time, position and speed
            if flushBuffer is set
              flush buffer to new file
            EndIf
          EndWhile
        wait for 1 second
      EndWhile

    GPS Thread
        Initialise connection to gpsd
        While shutDown flag is not set
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