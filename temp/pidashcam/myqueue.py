#! /usr/bin/python

import queue

class MyQueue(queue.Queue):
  '''
  A custom queue subclass that provides a :meth: `clear` method.
  '''

  def clear(self):
    '''
    Clears all items from the queue.
    '''

    with self.mutex:
      unfinished = self.unfinished_tasks - len(self.queue)
      if unfinished <= 0:
        if unfinished < 0:
          raise ValueError('task_done() called too many times')
        self.all_tasks_done.notify_all()
      self.unfinished_tasks = unfinished
      self.queue.clear()
      self.not_full.notify_all()
