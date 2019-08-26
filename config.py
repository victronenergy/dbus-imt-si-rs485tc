# coding=utf-8
import serial
import logging
from signals import DbusSignal, ModbusSignal

SERVICE_NAME = 'com.victronenergy.meteo'
DRIVER_NAME = 'dbus-imt-si-rs485tc.py'

LOG_LEVEL = logging.INFO
UPDATE_INTERVAL = 2  # seconds

# modbus configuration

BASE_ADDRESS = 0
NO_OF_REGISTERS = 9
SLAVE_ADDRESS = 1

# serial port configuration

PARITY = serial.PARITY_NONE
SERIAL_TIMEOUT = 0.5  # seconds
BAUD_RATE = 9600
BYTE_SIZE = 8
STOP_BITS = 1
MODE = 'rtu'

# signals configuration

SIGNALS = [

	DbusSignal('/Mgmt/ProcessName',    DRIVER_NAME),
	DbusSignal('/Mgmt/ProcessVersion', '1.1.0'),
	DbusSignal('/Mgmt/Connection',     'Modbus RTU'),
	DbusSignal('/DeviceInstance',      1),
	DbusSignal('/ProductId', 		   0xB030),
	DbusSignal('/ProductName',         'IMT Si-RS485 Series Solar Irradiance Sensor'),
	DbusSignal('/Connected',           True),

	ModbusSignal('/Irradiance',          register=0, gain=0.1, unit=u'W/m2'),
	ModbusSignal('/WindSpeed',           register=3, gain=0.1, unit=u'm/s'),
	ModbusSignal('/CellTemperature',     register=7, gain=0.1, unit=u'°C'),
	ModbusSignal('/ExternalTemperature', register=8, gain=0.1, unit=u'°C')
]


# subsensor settings

# keys must match with ModbusSignal's name above
# TTY will be replaced with the tty of the device

SETTINGS = {
	# object_path             #settings_path                               #default #min #max
	'/WindSpeed':           ['/Settings/Meteo/TTY/HasWindSpeedSensor',           0,   0,  1],
	'/ExternalTemperature': ['/Settings/Meteo/TTY/HasExternalTemperatureSensor', 0,   0,  1]
}





