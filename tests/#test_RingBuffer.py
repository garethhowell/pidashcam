""" """

import pytest
from pidashcam.ringbuffer import RingBuffer

@pytest.fixture
def empty_buf():
  return []

def test_init(empty_buf):
  parent = None
  buf = RingBuffer(parent, 6)

  assert buf._buffer == empty_buf
  assert buf._max_frames == 6

def test_add(empty_buf):
  parent = None
  buf = RinBuffer(parent, 6)

  frame = []

  buf.add()

