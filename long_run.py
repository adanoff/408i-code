import threading
import follow

class StoppableThread(threading.thread):
	def __init__(self, target=None):
		super(StoppableThread, self).__init__(target=target)
		self._stop_event = False

	def stop(self):
		self._stop_event = True

	def stopped(self):
		return self._stop_event

def follow():
	t = StoppableThread(target=follow.follow)
