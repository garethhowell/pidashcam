import threading
import time
import logging


class SimpleClass():

    def __init__(self, kwargs=None):
        print('SimpleClass kwargs= ', kwargs)
        self.kwargs = kwargs
        print('SimpleClass self.kwargs= ',self.kwargs)

    def pront(self):
        print('In pront, SimpleClass kwargs= ', self.kwargs)


class MyThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None,                  args=(), kwargs=None, verbose=None):
        super(MyThread,self).__init__(group=group, target=target,             name=name, verbose=verbose)
        self.args = args
        print('MyThread.__init__ kwargs=', kwargs)

        self.kwargs = kwargs
        print(dir(self.kwargs['a']))
        print('MyThread.__init__ self.kwargs= ', self.kwargs)
        return

    def run(self):
        print('running with kwargs = %s and %s', self.kwargs, self.kwargs['a'].kwargs)
        self.kwargs['a'].pront()
        return

if __name__ == '__main__':
    o1 = SimpleClass(kwargs={'fred':6})
    t = MyThread(kwargs={'a':o1, 'b':2})
    t.start()
