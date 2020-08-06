import threading
from gi.repository import GLib
import dbus

from dbus.mainloop.glib import DBusGMainLoop
from signals import DbusSignal
from os import environ
from os.path import dirname, join
from sys import path

path.insert(1, join(dirname(__file__), 'ext', 'velib_python'))
# noinspection PyUnresolvedReferences
from vedbus import VeDbusService
from logging import getLogger

_log = getLogger(__name__)

# noinspection PyUnreachableCode
if False:
	from typing import Iterable, Iterable, AnyStr


class VeDbusServiceAsync(VeDbusService):

	# noinspection PyMissingConstructor
	def __init__(self, service_name, signals):
		# type: (AnyStr, Iterable[DbusSignal]) -> VeDbusServiceAsync
		"""
		Wrapper for VeDbusService that makes it async using a dedicated
		thread for DBusGMainLoop.
		Recommended usage is inside a "with" block.
		Only one instance of this class can be created per process because of how
		dbus.mainloop.glib.DBusGMainLoop() is implemented.
		"""

		self.base = super(VeDbusServiceAsync, self)
		self.signals = signals
		self.main_loop = GLib.MainLoop()  # the global, glib main loop
		self.thread = threading.Thread(target=lambda *args: self.main_loop.run())

		# this takes the global main_loop above and wraps it.
		# it really should take the loop as an argument instead...
		dbus_mainloop = DBusGMainLoop()
		bus = dbus.SessionBus if 'DBUS_SESSION_BUS_ADDRESS' in environ else dbus.SystemBus

		self.base.__init__(service_name, bus(mainloop=dbus_mainloop))
		self._init_threads()
		self._init_signals(signals)

	def _init_signals(self, signals):
		# type: (Iterable[DbusSignal]) -> ()

		for s in signals:
			def get_text(_, value, signal=s):
				return signal.get_text(value)

			self.add_path(
				path=s.dbus_path,
				value=s.initial_value,
				writeable=False,
				onchangecallback=None,
				gettextcallback=get_text)

	# noinspection PyMethodMayBeStatic
	def _init_threads(self):
		dbus.mainloop.glib.threads_init()  # can be called multiple times without causing harm

	def __setitem__(self, dbus_path, new_value):

		# Make sure VeDbusService.__setitem__ is always called from the same thread.
		# This is achieved by scheduling it on the gobject mainloop, which is single-threaded.
		# This avoids the need for locking.
		# No such thing for __getitem__ because concurrent reads are thread-safe.

		def set_item():
			_log.debug(dbus_path + " = " + str(new_value))
			self.base.__setitem__(dbus_path, new_value)
			return False  # = do not repeat this action

		GLib.timeout_add(0, set_item)  # schedule ASAP on mainloop

	def start(self):
		_log.debug('starting')
		self.thread.start()
		_log.debug('started')

	def stop(self):
		_log.debug('stopping')
		self.main_loop.quit()
		self.thread.join()
		_log.debug('stopped')

	def __enter__(self):
		self.start()
		return self  # important

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.stop()


