#! /usr/bin/python -p

import logging
from ../pidashcam.ups_pico import upspico

logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger("ups_monitor")
log.setLevel(logging.DEBUG)

ups = UPSPico()
ups.monitor()
