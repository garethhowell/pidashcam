from pidashcam.myqueue import MyQueue
import pytest

def test_myQueue():
    # Create an instance of MyQueue
    queue = MyQueue()

    # Add some items to the queue
    for i in range(5):
        queue.put(i)

    # Check the size of the queue
    assert queue.qsize() == 5

    # Clear the queue
    queue.clear()

    # Check the size of the queue after clearing
    assert queue.qsize() == 0

    # Check if the queue is empty
    assert queue.empty() is True

    # Try to clear an empty queue (should not raise any exceptions)
    queue.clear()
    assert queue.qsize() == 0
    assert queue.empty() is True
    # Add items again to test the queue after clearing
    for i in range(3):
        queue.put(i)
    # Check the size of the queue
    assert queue.qsize() == 3
    # Check if the queue is empty
    assert queue.empty() is False
    # Clear the queue again
    queue.clear()
    # Check the size of the queue after clearing
    assert queue.qsize() == 0
    # Check if the queue is empty
    assert queue.empty() is True
    # Check if the queue is not full
    assert queue.full() is False
    # Check if the queue is not empty
    assert queue.empty() is True
    # Check if the queue is not full
    assert queue.full() is False