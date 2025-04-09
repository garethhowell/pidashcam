src = 0
prerecord = 30
postrecord = 30
width = 1440
height = 1200
button_a = 23
button_b = 24
led = 16
destdir = '/tmp'
video_format = 'h264'
log-level = 'info'
vflip = False
hflip = False

# specify the desired video length (seconds).
# this will determine the number of frames to be
# kept in each camera buffer.  A 10 second clip
# will capture 300 frames (10s * 30fps)
video_length = 5 * 60
