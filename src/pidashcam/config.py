src = 0
pre_record = 30
post_record = 30
width = 1440
height = 1200
button_A = 37
button_B = 38
LED_1 = 16
dest_dir = '/tmp'
video_format = 'h264'
log_level = 'debug'
vflip = False
hflip = False

# specify the desired video length (seconds).
# this will determine the number of frames to be
# kept in each camera buffer.  A 10 second clip
# will capture 300 frames (10s * 30fps)
video_length = 5 * 60
buffer_size = pre_record + video_length + post_record
