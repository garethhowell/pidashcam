""" """
from pidashcam import Camera
import pytest

@pytest.fixture
def dummy_camera():
  name = "dummy"
  queue = None
  buffer = None
  recording = None
  led = None
  return [name, queue, buffer, recording, led]

def test_init(dummy_camera):
  cam = Camera(dummy_camera[0], dummy_camera[1], dummy_camera[2], dummy_camera[3], dummy_camera[4])

  assert cam._name == "dummy"
  assert cam._recording_LED is None