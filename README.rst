PiDashCam - Raspberry Pi DashCam
================================

A python package to deliver dashcam functionality using a Raspberry Pi.

Prerequisites
-------------

-   various standard libraries
-   python-camera
-   python-gps
-   python-rpi.gpio

Hardware
--------

-   Raspberry Pi (I used a Model B+)
-   Raspberry Pi Camera Module V2
-   Adafruit Ultimate GPS breakout board connected using the UART on GPIO
    14 and 15
-   UPS PIco with 450mAh battery from
    `ModMyPi <https://www.modmypi.com/>`__. PICo uses GPIO 22 and 27
-   Pi Camera HDMI extender from `Tindie <https://www.tindie.com>`__
-   Two momentary push buttons

    -   Button A uses GPIO 23
    -   Button B uses GPIO 24

-   One LED

    -   LED1 uses GPIO 16

Functional Overview
-------------------

-   On startup, the camera starts recording to an in-memory buffer
    of configurable size (default 60s).
    The video stream is overlaid with current date-time, speed, location and
    direction of travel.
-   LED1 flashes slowly whenever the camera is recording.

-   If button A is pressed, the current contents of the buffer are
    flushed to a file, together with the following few seconds of video.
    (This can be used to capture the before and after of some event). The
    camera then goes back to recording into the buffer.
    LED1 flashes faster whilst the buffer is being saved.

-   If button B is pressed, the current contents of the buffer are
    flushed to a file and recording stopped. LED1 is switched off.

-   If button B is pressed again, recording is re-started from new and
    LED1 flashes slowly again.

-   The UPS PIco ensures that recording can continue even if power has been
    lost (e.g. in a crash)

Syncing videos files from PiDashCam to some other PC/Mac
--------------------------------------------------------

-   In the background, Resilio Sync monitors the folder containing
    the h264 format video files. If the Pi is connected to my home Wi-Fi,
    Resilio syncs the contents of the folder to a Mac in the house.

-   If the power if switched off (e.g. ignition is turned off) and the Pi
    is connected to Wi-Fi, the attached UPS keeps the Pi powered for long
    enough to allow the video files to be synced to my Mac. It then shuts
    the Pi down gracefully.

-   On the Mac, Hazel is monitoring the sync folder. When it sees h264
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
      Start Timer thread
      set flushBuffer flag on timeout

    Button B interrupt handler (toggle recording)
      If we are recording
        flush the buffer immediately
        clear the recording flag
      Else
        set the recording flag
      EndIf

    Camera thread
        While shutdown flag is not set
            While recording flag is set
                Initialise Camera
                start recording into buffer
                While recording flag is set - inner recording loop
                    update annotation with current date-time, position and speed
                    If flushBuffer is set
                        flush buffer to new file
                    EndIf
                EndWhile
            wait for 1 second
        EndWhile
        Exit

    GPS Thread
        Initialise connection to gpsd
        While shutdown flag is not set
            add current GPS fix to inter-thread queue
        Exit

    Power failure
        Start Timer thread
        set shutdown Event on timeout

    Main thread
        Set the record flag
        Kick off Camera thread
        Kick off GPS thread

        While shutdown flag is not set
            wait for 1 second
        While LAN is connected and there are videos in the sync folder
            wait for 1 second
        Kill threads
        Initiate system shutdown
        Exit
