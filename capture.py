import io
import random
import picamera

def motion_detected():
	# Randomly return True
	return random.randint(0, 10) == 0

d = '/home/pi/dev/picam/resilio/Videos'
camera = picamera.PiCamera()
camera.vflip = True
stream = picamera.PiCameraCircularIO(camera, seconds=5)
camera.start_recording(stream, format='h264')
j = 0
#print 'starting... '
try:
	while j < 2:
		camera.wait_recording(1)
		if motion_detected():
			#print 'in the loop'
			# Keep recording for 10 seconds and only write then
			camera.wait_recording(10)
			f = str(d) + '/motion' + str(j) + '.h264'
			#print 'Saving to ' + f
			stream.copy_to(f)
			j = j+1
			#print j
finally:
	#print 'stopping...'
	camera.stop_recording()
