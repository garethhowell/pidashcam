import cv2
import numpy as np
import time

from picamera2 import MappedArray, Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput

picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (640, 480), "format": "RGB888"}, lores={
                                                 "size": (320, 240), "format": "YUV420"})
picam2.configure(video_config)

timestamp = time.strftime("%Y%m%d-%H%M%S")
filename = f"/home/garethhowell/Videos/video_clip_{timestamp}.h264"

colour = (0, 255, 0, 255)
origin = (-1, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2

def apply_timestamp(request):
  with MappedArray(request, "main") as m:
    cv2.putText(m.array, annotation, origin, font, scale, colour, thickness)

annotation = "No Fix"
picam2.pre_callback = apply_timestamp

encoder = H264Encoder(bitrate=1000000)
output = FileOutput(filename)


picam2.start_preview(Preview.QT)
picam2.start_recording(encoder, output)

for n in range(6):
  annotation = str(n)
  time.sleep(1)

picam2.stop_recording()