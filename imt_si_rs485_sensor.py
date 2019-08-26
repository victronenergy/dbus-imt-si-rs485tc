# coding=utf-8

import struct
import config as c
import logging

from sys import exc_info
from pymodbus.client.sync import ModbusSerialClient
from pymodbus.factory import ClientDecoder
from pymodbus.pdu import ModbusResponse, ModbusRequest

_log = logging.getLogger(__name__)

# noinspection PyUnreachableCode
if False:
	from typing import Sequence


class ImtSiRs485Sensor(object):
	"""
	Class that represents an ImtSiRs485 sensor attached via modbus RTU
	"""

	def __init__(self, tty):
		# type: (unicode) -> ImtSiRs485Sensor

		self.tty = '/dev/' + tty
		self.serial = ModbusSerialClient(
			port=self.tty,
			method=c.MODE,
			baudrate=c.BAUD_RATE,
			stopbits=c.STOP_BITS,
			bytesize=c.BYTE_SIZE,
			timeout=c.SERIAL_TIMEOUT,
			parity=c.PARITY)

		self.serial.close()  # close for now, only open while in use

	def identify(self):
		# type: () -> (float, float)
		_log.info('searching for IMT SI-RS485 sensor on ' + self.tty)

		# noinspection PyBroadException
		try:
			self.serial.connect()

			request = FirmwareVersionModbusRequest(unit=c.SLAVE_ADDRESS)
			response = self.serial.execute(request)

			hw_ver = response.hardware_version
			fw_ver = response.firmware_version

			_log.info('found IMT SI-RS485 sensor')
			_log.info('hardware version: ' + str(hw_ver))
			_log.info('firmware version: ' + str(fw_ver))

			return hw_ver, fw_ver

		except Exception:
			msg = 'no IMT SI-RS485 sensor found'

			if c.LOG_LEVEL > logging.DEBUG:
				raise Exception(msg)
			else:
				_log.info(msg)
				ex = exc_info()
				raise ex[0], ex[1], ex[2]

		finally:
			self.serial.close()  # close in any case

	def read_modbus_registers(self):
		# type: () -> (Sequence[int])

		_log.debug(
			'requesting modbus registers {0}-{1}'.format(c.BASE_ADDRESS, c.BASE_ADDRESS + c.NO_OF_REGISTERS - 1))

		try:
			self.serial.connect()

			reply = self.serial.read_input_registers(c.BASE_ADDRESS, c.NO_OF_REGISTERS, unit=c.SLAVE_ADDRESS)

			if reply.function_code > 0x80:
				raise Exception('sensor signaled an error')

			if not hasattr(reply, 'function_code') or not hasattr(reply, 'registers'):
				raise Exception('received an unexpected reply from sensor')

			if len(reply.registers) != c.NO_OF_REGISTERS:
				raise Exception('received unexpected number of registers')

			return reply.registers

		finally:
			self.serial.close()  # close in any case


class FirmwareVersionModbusRequest(ModbusRequest):
	"""
	A nonstandard modbus function used to retrieve the hardware and firmware version of the IMT sensor.
	"""
	function_code = 0x46

	def __init__(self, **kwargs):
		ModbusRequest.__init__(self, **kwargs)
		self.sub_function = 7

	def encode(self):
		return struct.pack('>b', self.sub_function)

	def decode(self, data):
		self.sub_function = struct.unpack('>b', data)


class FirmwareVersionModbusResponse(ModbusResponse):
	"""
	Response to the nonstandard modbus function above.
	"""
	function_code = 0x46
	_rtu_frame_size = 9

	def __init__(self, **kwargs):
		super(FirmwareVersionModbusResponse, self).__init__(**kwargs)
		self.sub_function = None
		self.hardware_version = None
		self.firmware_version = None

	def decode(self, data):
		self.sub_function = struct.unpack('>b', data[0])
		self.hardware_version = struct.unpack('>H', data[1:3])[0]/100.0
		self.firmware_version = struct.unpack('>H', data[3:5])[0]/100.0


# monkey-patching monkey doing its thing...
ClientDecoder._ClientDecoder__function_table.append(FirmwareVersionModbusResponse)
