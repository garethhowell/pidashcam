""" """
import pytest
from pytest_mock import mocker
from time import sleep
import signal
import logging
import socket
import threading
import atexit
import keyboard
import gpiozero
from gpiozero import Button, LED
import time

from pidashcam.pidashcam import PiDashCam
from pidashcam.myqueue import MyQueue
from pidashcam.camerathread import Camera
from pidashcam.gpspoller import GPSPoller
from pidashcam.upspico import UPSPIco

@pytest.fixture(scope="function")
def event():
  event = threading.Event()
  return event

@pytest.fixture(scope="function")
def mock_event(mocker):
    mock_event = mocker.patch('pidashcam.pidashcam.threading.Event')
    mock_event.return_value = mocker.Mock()
    return mock_event

@pytest.fixture(scope="function")
def mock_mqueue(mocker):
    mock_mqueue = mocker.patch('pidashcam.pidashcam.MyQueue')
    mock_mqueue.return_value = mocker.Mock()
    return mock_mqueue


@pytest.fixture(scope="function")
def dummy_pidashcam():
  dest_dir = "/tmp"
  button_A = 23
  button_B = 24
  recording_LED = 25
  video_format = 'h264'
  camera_res = {'h': 1440, 'v': 1280}
  buffer_size = 30
  extra_time = 30
  vflip = False
  hflip = False
  return (dest_dir, button_A, button_B, recording_LED, video_format,
          camera_res, buffer_size, extra_time, vflip, hflip)

def test_init(mocker, dummy_pidashcam, mock_signal,
              mock_keyboard, mock_logging, mock_atexit,
              mock_socket, mock_time):
    """Test the initialization of PiDashCam."""
    mocker.patch('pidashcam.pidashcam.Button')
    mock_button_A = mocker.patch('pidashcam.pidashcam.Button')
    mock_button_A.return_value = mocker.Mock(pin=23)


    mocker.patch('pidashcam.pidashcam.LED')
    mock_LED = mocker.patch('pidashcam.pidashcam.LED')
    mock_LED.return_value = mocker.Mock(pin=25)

    pidashcam = PiDashCam(*dummy_pidashcam)
    assert pidashcam is not None
    assert isinstance(pidashcam, PiDashCam)
    assert pidashcam.dest_dir == "/tmp"
    assert pidashcam.video_format == 'h264'
    assert pidashcam.button_A.pin == 23
    assert pidashcam.recording_LED.pin == 25
    assert pidashcam.camera_res == {'h': 1440, 'v': 1280}
    assert pidashcam.buffer_size == 30
    assert pidashcam.extra_time == 30
    assert pidashcam.vflip is False
    assert pidashcam.hflip is False
    assert pidashcam.GPS_thread is None
    assert pidashcam.camera_thread is None
    assert isinstance(pidashcam.flush_buffer_event, threading.Event)
    assert isinstance(pidashcam.recording_event, threading.Event)
    assert isinstance(pidashcam.GPS_queue, MyQueue)
    assert isinstance(pidashcam.local_shutdown_event, threading.Event)
    assert isinstance(pidashcam.UPS_shutdown_event, threading.Event)


