#!/usr/bin/python3 -u
# coding=utf-8
from functools import partial
from time import sleep
from ve_dbus_service_async import VeDbusServiceAsync
from imt_si_rs485_sensor import ImtSiRs485Sensor
from watchdog import Watchdog
from signals import DbusSignal, ModbusSignal

import sys
import config as c
import logging

from os.path import dirname, join
from sys import path

path.insert(1, join(dirname(__file__), 'ext', 'velib_python'))

from settingsdevice import SettingsDevice

logging.basicConfig(level=c.LOG_LEVEL)
log = logging.getLogger('main')


def print_usage():
	print('Usage:   ' + __file__ + ' <serial device>')
	print('Example: ' + __file__ + ' ttyUSB0')


# noinspection PyShadowingBuiltins,PyShadowingNames
def get_settings_for_tty(tty):
	return {
		name: [path.replace('TTY', tty), value, min, max]
		for name, (path, value, min, max)
		in c.SETTINGS.items()
	}


def parse_cmdline_args():
	# type: () -> str

	args = sys.argv[1:]
	if len(args) == 0:
		log.info('missing command line argument for tty device')
		print_usage()
		exit(1)

	return args[0]


# noinspection PyProtectedMember
def is_subsensor_present(subsensor_settings, dbus_path, value):
	# type: (SettingsDevice, unicode, float) -> object

	if dbus_path not in subsensor_settings._settings:
		return True                                # it's not an optional subsensor

	if subsensor_settings[dbus_path] == 'enabled':
		return True

	if subsensor_settings[dbus_path] == 'disabled':
		return False

	# subsensor_settings is 'auto-detect'

	if value == 0.0:
		log.debug('ignoring zero value for subsensor ' + dbus_path)
		return False

	# got a non-zero value form subsensor.
	# subsensor is definitely present, but not marked as present in the settings.
	# update settings.

	log.info('found subsensor ' + dbus_path + '. updating settings')
	subsensor_settings[dbus_path] = 'enabled'
	return True


def main():

	log.info('starting ' + c.DRIVER_NAME)

	tty = parse_cmdline_args()
	sensor = ImtSiRs485Sensor(tty)

	hw_ver, fw_ver = sensor.identify()

	# add hw and fw version to the signals, they are mandatory
	signals = c.SIGNALS + [DbusSignal('/HardwareVersion', hw_ver), DbusSignal('/FirmwareVersion', fw_ver)]

	service_name = c.SERVICE_NAME + '.' + tty
	watchdog_timeout = (c.UPDATE_INTERVAL + c.SERIAL_TIMEOUT) * 2

	# starting watchdog here, because with VeDbusServiceAsync we are going multi-threaded
	with Watchdog(watchdog_timeout) as watchdog, VeDbusServiceAsync(service_name, signals) as dbus:

		settings_for_tty = get_settings_for_tty(tty)
		settings = SettingsDevice(dbus.dbusconn, settings_for_tty, None)
		_is_subsensor_present = partial(is_subsensor_present, settings)

		# only the modbus signals are updated, the others are const
		modbus_signals = [s for s in signals if isinstance(s, ModbusSignal)]

		while True:

			watchdog.alive()  # signal the watchdog that we are still alive

			registers = sensor.read_modbus_registers()

			for s in modbus_signals:
				value = registers[s.reg_no]
				if s.signed and value & 0x8000:
					value -= 0x10000
				value *= s.gain

				if _is_subsensor_present(s.dbus_path, value):
					dbus[s.dbus_path] = value
				else:
					dbus[s.dbus_path] = None

			log.debug('iteration completed, sleeping for ' + str(c.UPDATE_INTERVAL) + ' seconds')
			sleep(c.UPDATE_INTERVAL)


# noinspection PyBroadException
try:
	main()

except Exception as e:

	log.error(str(e))

	# show stacktrace only in debug mode
	if c.LOG_LEVEL <= logging.DEBUG:
		ex = sys.exc_info()
		raise ex[0](ex[1]).with_traceback(ex[2])

finally:
	log.info(c.DRIVER_NAME + ' has shut down')
