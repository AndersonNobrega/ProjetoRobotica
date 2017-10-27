#!/usr/bin/env python3

import threading

class MyPausableThread(threading.Thread):

    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        self._event = threading.Event()
        if target:
            args = ((lambda: self._event.wait()),) + args
        super(MyPausableThread, self).__init__(group, target, name, args, kwargs)

    def pause(self):
        self._event.clear()

    def resume(self):
        self._event.set()
