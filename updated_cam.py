from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import CircularOutput
import time
import cv2
import threading

# Constants
BUFFER_DURATION = 10  # seconds
ANNOTATE_TEXT = True

# Setup Picamera2
picam2 = Picamera2()
video_config = picam2.create_video_configuration(main={"size": (1280, 720)})
picam2.configure(video_config)

# Create circular output (buffered stream)
circular_output = CircularOutput(buffersize=BUFFER_DURATION)
encoder = H264Encoder(bitrate=1000000)
picam2.start_recording(encoder, circular_output)

# Function to overlay annotations using OpenCV
def annotate_frame(frame):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if ANNOTATE_TEXT:
        cv2.putText(frame, timestamp, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (255, 255, 255), 2, cv2.LINE_AA)
    return frame

# Live preview with annotation (optional, needs display)
def start_annotated_preview():
    picam2.start_preview(Preview.QTGL)  # Can also use Preview.NULL if headless

    def preview_loop():
        while True:
            frame = picam2.capture_array()
            frame = annotate_frame(frame)
            # You can display it or just annotate it for recording
            cv2.imshow("Preview", frame)
            if cv2.waitKey(1) == ord('q'):
                break

    threading.Thread(target=preview_loop, daemon=True).start()

# Start the annotated preview in a background thread
start_annotated_preview()

print("Recording... Press Ctrl+C to stop or trigger save logic.")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    # Save last N seconds to file
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"/home/pi/video_clip_{timestamp}.h264"
    circular_output.copy_to(filename)
    print(f"Saved circular buffer to {filename}")

    picam2.stop_recording()
    cv2.destroyAllWindows()
