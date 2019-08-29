# dbus-imt-si-rs485tc

Driver for the [imt-si-rs485tc Solar Irradiance Sensor](https://www.imt-solar.com/products/solar-irradiance-sensor/si-sensor/).  

  

A separate _USB to RS485_ converter cable is required for each sensor. The driver works with the factory settings of the sensor. No manual configuration required.  
  

The sensor measures 
* Solar Irradiance [W/m2]
* Temperature [°C]
* Wind Speed [m/s], _optional_
* External Temperature [°C], _optional_

The object paths of the measurements are
```
/Irradiance
/WindSpeed
/CellTemperature
/ExternalTemperature
```


The measurements are published on DBus under the service `com.victronenergy.meteo.ttyUSBx`  

The _optional_ measurements are only available if the corresponding subsensor is attached.  
The subsensors can be configured in the settings:
```
/Settings/Meteo/TTY/WindSpeedSensor
/Settings/Meteo/TTY/ExternalTemperatureSensor
```
where TTY stands for the tty of the device (e.g. ttyUSB0)

A settings can be one of the following (strings):
- **enabled**: Measurements will be reported on DBus. If there is no subsensor present, zero values are reported
- **disabled**: Measurements will *not* be reported on DBus
- **auto-detect**: Default. Zero value measurements are not reported. If a non zero value is read (subsensor detected), the setting will switch itself to 'enabled'


