# Which camera are we capturing from?
# If installed, the picamera will be source 0
src = 0

# How far ahead of the point at which we choose to save
# do we need to keep so it can be flushed (seconds)
pre_record = 30

# How long after the point at which we choose to save
# do we need to keep saving (seconds)
post_record = 30

# define the size of the video
width = 1440
height = 1200

# Define the GPIO pin used to trigger saving (BCM pins, not connector)
button_A = 23

# Ditto for the button that defines whether or not we are recording
button_B = 24

# Define the GPIO pin to which the "Recording" LED is connected
recording_LED = 25

# Where do we save the video files
dest_dir = '/home/garethhowell/Videos'

# What format do we save in
video_format = 'h264'

# Log level (set to error in production)
log_level = 'debug'

# Do we need to transform the image:
# e.g. because the camera is upside down
vflip = False
hflip = False

# Computed - DO NOT CHANGE
buffer_size = pre_record + post_record
