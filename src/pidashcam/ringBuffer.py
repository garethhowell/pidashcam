import config
import cv2
import datetime

class RingBuffer():
  """
  Class to implement a ring buffer
  """

  def __init__(self, parent):
    
    self._buffer = []
    self._max_frames = int(config.video_length * 30)
    self._parent = parent

  def clear(self):
    self._buffer = []
    
  def flush(self):
    """
    Save the buffer to a file
    """
    now = datetime.datetime.now()
    date = now.strftime("%Y%m%d_%H.%M.%S")
    fn = "output/{}/{}.mp4".format(config.src, date)
    writer = cv2.VideoWriter(fn, cv2.VideoWriter_dourcc(*"mp4v"), 30.0, (config.width, config.height))
    self.parent._log.info("Saving file {}".format(fn))
    for frame in self._buffer:
      writer.write(frame)
    writer.release()

  def write(self, frame):
    """
    Add a frame to the buffer
    """
    if len(self._buffer) > self._max_frames:
      self._buffer = self._buffer[1:] + [frame]
    else:
      self._buffer += [frame]

