"""PiDashCam Raspberry Pi dashcam
"""
from __future__ import annotations

__version__ = "2.0.0"

from .pidashcam import PiDashCam
from .gpspoller import GPSPoller
from .camerathread import Camera
import config
from .myqueue import MyQueue
