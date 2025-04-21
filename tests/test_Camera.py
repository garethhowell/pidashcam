""" """
from pidashcam.camerathread import Camera
import pytest
from pytest_mock import mocker

@pytest.fixture
def dummy_camera():
  """Dummy Camera class"""
  name = "dummy"
  queue = None
  buffer = None
  recording = None
  led = None
  dir = "/tmp"
  video_format = "h264"
  camera_res = {'h': 1440, 'v': 1280}
  buff_size = 30
  extra_time = 30
  vflip = False
  hflip = False
  return [name, queue, buffer, recording, led, dir, video_format, camera_res, buff_size, extra_time, vflip, hflip]

def test_init(dummy_camera):
  cam = Camera(*dummy_camera)

  assert cam.name == "dummy"
  assert cam.recordingLED is None