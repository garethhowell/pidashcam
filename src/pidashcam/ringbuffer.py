import cv2
import datetime

class RingBuffer():
  """
  Class to implement a ring buffer
  """

  def __init__(self, parent, max_size):

    self._buffer = []
    self._max_size = max_size
    self._parent = parent
    self._size = 0
    self._pointer = 0

  def empty(self):
    """Empty the buffer """
    self._buffer = []
    self._size = 0
    self._pointer = 0

  def add(self, frame):
    """
    Add a frame to the buffer
    """
    if len(self._buffer) > self._max_size:
      self._buffer = self._buffer[1:] + [frame]
      self._pointer += 1
    else:
      self._buffer[self._pointer] += [frame]

  def size(self):
    return self._size

