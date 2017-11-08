=====
PiDashCam - Raspberry Pi DashCam
=====

Initialise interrupt handlers
  Button A
    Start Long Timer1
  Timer1
    Signal flush buffer

Initialise camera
Do forever
  record into X secs in-memory buffer
  update annotate_text every 0.2 secs
  if flush buffer
    save video
    carry on recording
    fi
  if shutdown
    save video
    cleanup and exit
    fi
  od

Power failure
  signal camera to shutdown
  wait a short time
  
