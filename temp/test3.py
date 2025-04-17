import cv2
import numpy as np
import time

from picamera2 import Picamera2

picam2 = Picamera2()
picam2.start(show_preview=True)

for time_left in range(10, 0, -1):
    colour = (0, 255, 0, 255)
    origin = (-1, 30)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1
    thickness = 2
    overlay = np.zeros((640, 480, 4), dtype=np.uint8)
    cv2.putText(overlay, str(time_left), origin, font, scale, colour, thickness)
    picam2.set_overlay(overlay)
    time.sleep(1)

picam2.stop()