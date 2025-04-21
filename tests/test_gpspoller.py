from pidashcam.gpspoller import GPSPoller
import pytest
from pytest_mock import mocker
from pidashcam.myqueue import MyQueue

@pytest.fixture
def gps_poller():
    """Fixture to create a GPSPoller instance."""
    return GPSPoller(name="TestGPSPoller", GPS_queue=None)
@pytest.fixture
def gps_poller_no_queue():
    """Fixture to create a GPSPoller instance without a queue."""
    return GPSPoller(name="TestGPSPoller", GPS_queue=None)
@pytest.fixture
def gps_poller_with_queue():
    """Fixture to create a GPSPoller instance with a queue."""
    return GPSPoller(name="TestGPSPoller", GPS_queue=MyQueue())

@pytest.fixture
def my_queue():
    """Fixture to create a MyQueue instance."""
    return MyQueue()


def test_gpspoller_init(my_queue):
    gps_poller = GPSPoller("GPSPoller", my_queue)
    assert gps_poller is not None
    assert isinstance(gps_poller, GPSPoller)
    assert gps_poller.running is True
    assert gps_poller.GPS_daemon is not None
    assert gps_poller.GPS_queue is my_queue
    assert gps_poller.shutdown is not None
    assert gps_poller.name == "GPSPoller"
    assert gps_poller.log is not None
    assert gps_poller.log.name == "pidashcam.gpspoller"

def test_gpspoller_init_no_queue():
    gps_poller = GPSPoller("GPSPoller", None)
    assert gps_poller is not None
    assert isinstance(gps_poller, GPSPoller)
    assert gps_poller.running is True
    assert gps_poller.GPS_daemon is not None
    assert gps_poller.GPS_queue is None
    assert gps_poller.shutdown is not None
    assert gps_poller.name == "GPSPoller"
    assert gps_poller.log is not None
    assert gps_poller.log.name == "pidashcam.gpspoller"

def test_gps_poller_run(mocker, gps_poller_with_queue):
    mocker.patch('pidashcam.gpspoller.gps', autospec=True)
    mock_gps = mocker.patch('pidashcam.gpspoller.gps')
    mock_gps.return_value = mock_gps
    mock_gpsd = mock_gps.return_value
    mock_gpsd.next.return_value = None

    gps_poller_with_queue.run()

    # Check that the next() method was called
    mock_gpsd.next.assert_called_once()
    # Check that the put() method was called on the queue
    gps_poller_with_queue.gpsQueue.put.assert_called_once()
    # Check that the empty() method was called on the queue
    gps_poller_with_queue.gpsQueue.empty.assert_called_once()
    # Check that the shutdown event was set
    assert gps_poller_with_queue.shutdown.isSet() is False
def test_gps_poller_join(mocker, gps_poller_with_queue):
    mocker.patch('pidashcam.gpspoller.gps', autospec=True)
    mock_gps = mocker.patch('pidashcam.gpspoller.gps')
    mock_gps.return_value = mock_gps
    mock_gpsd = mock_gps.return_value
    mock_gpsd.next.return_value = None

    gps_poller_with_queue.join(timeout=1)

    # Check that the shutdown event was set
    assert gps_poller_with_queue.shutdown.isSet() is True
    # Check that the join() method was called on the thread
    gps_poller_with_queue.join.assert_called_once_with(timeout=1)
def test_gps_poller_join_no_queue(mocker, gps_poller_no_queue):
    mocker.patch('pidashcam.gpspoller.gps', autospec=True)
    mock_gps = mocker.patch('pidashcam.gpspoller.gps')
    mock_gps.return_value = mock_gps
    mock_gpsd = mock_gps.return_value
    mock_gpsd.next.return_value = None

    gps_poller_no_queue.join(timeout=1)

    # Check that the shutdown event was set
    assert gps_poller_no_queue.shutdown.isSet() is True
    # Check that the join() method was called on the thread
    gps_poller_no_queue.join.assert_called_once_with(timeout=1)