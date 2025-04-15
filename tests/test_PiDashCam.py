""" """
from pidashcam import PiDashCam
import pytest

def test_init():
   pi = PiDashCam()
   assert pi._src == 0
   assert pi._camera_T == None

