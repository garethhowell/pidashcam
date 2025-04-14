""" """
from pidashcam import Camera
import pytest

@pytest.fixture
def dummy_camera():
  name = "dummy"
  queue = None
  buffer = None
  flag = None
  return [name, queue, buffer, flag]

def test_init(dummy_camera):
  cam = Camera(dummy_camera[0], dummy_camera[1], dummy_camera[2], dummy_camera[3])

  assert cam._name == "dummy"