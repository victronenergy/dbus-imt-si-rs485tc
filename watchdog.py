from threading import Thread
from time import sleep
from os import _exit as kill
from _thread import interrupt_main as terminate
import logging
_log = logging.getLogger(__name__)


class Watchdog(object):
	def __init__(self, timeout_seconds):
		# type: (float) -> Watchdog
		"""
		A watchdog service that shuts down the application, should it become unresponsive.
		The application must call Watchdog.alive() at least every timeout_seconds to signal
		it's alive. Failing to do so will prompt the watchdog to shut down all threads
		and then kill the application.
		Recommended usage is inside a "with" block.
		"""
		self._interval = timeout_seconds
		self._thread = None
		self._alive_flag = True
		self._do_watch = False

	def is_watching(self):
		# type: () -> bool
		return self._do_watch or self._thread is not None

	def start(self):
		if self.is_watching():
			return

		_log.debug('starting')

		self._do_watch = True
		self._thread = Thread(target=self._watch)
		self._thread.start()

		_log.debug('started')

	def stop(self):
		if not self.is_watching():
			return

		_log.debug('stopping')

		self._do_watch = False
		self._thread.join(self._interval * 2)
		self._thread = None

		_log.debug('stopped')

	def alive(self):
		self._alive_flag = True
		_log.debug('got alive signal')

	def _watch(self):
		while self._do_watch:
			sleep(self._interval)
			if self._alive_flag:
				self._reset_alive()
			else:
				_log.debug('no alive signal received for more than ' + str(self._interval) + ' seconds')
				self.shutdown()

	def _reset_alive(self):
		_log.debug('resetting alive flag')
		self._alive_flag = False

	def shutdown(self):

		_log.debug('terminating threads')
		terminate()

		# give the threads time to shutdown gracefully
		sleep(self._interval * 2)

		_log.debug('kill')
		kill(1)

	def __enter__(self):
		self.start()
		return self  # important

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.stop()

