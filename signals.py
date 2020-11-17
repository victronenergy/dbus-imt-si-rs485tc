
# noinspection PyUnreachableCode
if False:
	from typing import Callable


# The signal metaphor used here is a bit redundant.
# Would probably be better to merge them with VeDbusItemExport from the VeDbusService module.
# But I needed a simpler interface and didn't want to touch VeDbusItemExport

class DbusSignal(object):
	def __init__(self, dbus_path, initial_value=None, get_text=str):
		# type: (unicode, object, Callable[[object], unicode]) -> DbusSignal
		"""
		:param dbus_path: unicode
			object_path on DBus where the signal needs to be published

		:param initial_value: object
			first value to publish when the signal goes onto the bus

		:param get_text: (object) -> unicode
			function called to render value as string, defaults to str
		"""

		self.get_text = get_text
		self.dbus_path = dbus_path
		self.initial_value = initial_value


class ModbusSignal(DbusSignal):
	def __init__(self, dbus_path, register, gain, unit=None, signed=False):
		# type: (unicode, int, float, unicode) -> None
		"""
		:param dbus_path: unicode
			the object path on DBus where the signal is published

		:param register: int
			the modbus register number of the datum

		:param gain: float
			value with which the value of the modbus register must be multiplied with

		:param unit: unicode
			physical unit of the datum
		"""

		self.reg_no = register
		self.gain = gain
		self.unit = unit
		self.signed = signed

		def get_text(value):
			return str(value) + ' ' + unit

		super(ModbusSignal, self).__init__(dbus_path, None, get_text if unit is not None else str)
