import pytest
from pytest_mock import mocker



@pytest.fixture(scope="function")
def mock_camera(mocker):
    mock_camera = mocker.patch('pidashcam.pidashcam.Camera')
    mock_camera.return_value = mocker.Mock()
    return mock_camera

@pytest.fixture(scope="function")
def mock_gpspoller(mocker):
    mock_gpspoller = mocker.patch('pidashcam.pidashcam.GPSPoller')
    mock_gpspoller.return_value = mocker.Mock()
    return mock_gpspoller

@pytest.fixture(scope="function")
def mock_upspico(mocker):
    mock_upspico = mocker.patch('pidashcam.pidashcam.UPSPIco')
    mock_upspico.return_value = mocker.Mock()
    return mock_upspico

@pytest.fixture(scope="function")
def mock_mqueue(mocker):
    mock_mqueue = mocker.patch('pidashcam.pidashcam.MyQueue')
    mock_mqueue.return_value = mocker.Mock()
    return mock_mqueue

@pytest.fixture(scope="function")
def mock_event(mocker):
    mock_event = mocker.patch('pidashcam.pidashcam.threading.Event')
    mock_event.return_value = mocker.Mock()
    return mock_event

@pytest.fixture(scope="function")
def mock_gpio(mocker):
    mock_gpio = mocker.patch('pidashcam.pidashcam.gpiozero')
    mock_gpio.return_value = mocker.Mock()
    return mock_gpio

@pytest.fixture(scope="function")
def mock_signal(mocker):
    mock_signal = mocker.patch('pidashcam.pidashcam.signal')
    mock_signal.return_value = mocker.Mock()
    return mock_signal

@pytest.fixture(scope="function")
def mock_keyboard(mocker):
    mock_keyboard = mocker.patch('pidashcam.pidashcam.keyboard')
    mock_keyboard.return_value = mocker.Mock()
    return mock_keyboard

@pytest.fixture(scope="function")
def mock_logging(mocker):
    mock_logging = mocker.patch('pidashcam.pidashcam.logging')
    mock_logging.return_value = mocker.Mock()
    return mock_logging

@pytest.fixture(scope="function")
def mock_atexit(mocker):
    mock_atexit = mocker.patch('pidashcam.pidashcam.atexit')
    mock_atexit.return_value = mocker.Mock()
    return mock_atexit

@pytest.fixture(scope="function")
def mock_socket(mocker):
    mock_socket = mocker.patch('pidashcam.pidashcam.socket')
    mock_socket.return_value = mocker.Mock()
    return mock_socket

@pytest.fixture(scope="function")
def mock_time(mocker):
    mock_time = mocker.patch('pidashcam.pidashcam.time')
    mock_time.return_value = mocker.Mock()
    return mock_time

@pytest.fixture(scope="function")
def mock_threading(mocker):
    mock_threading = mocker.patch('pidashcam.pidashcam.threading')
    mock_threading.return_value = mocker.Mock()
    return mock_threading

@pytest.fixture(scope="function")
def mock_signal(mocker):
    mock_signal = mocker.patch('pidashcam.pidashcam.signal')
    mock_signal.return_value = mocker.Mock()
    return mock_signal

@pytest.fixture(scope="function")
def mock_threading(mocker):
    mock_threading = mocker.patch('pidashcam.pidashcam.threading')
    mock_threading.return_value = mocker.Mock()
    return mock_threading

@pytest.fixture(scope="function")
def mock_signal(mocker):
    mock_signal = mocker.patch('pidashcam.pidashcam.signal')
    mock_signal.return_value = mocker.Mock()
    return mock_signal