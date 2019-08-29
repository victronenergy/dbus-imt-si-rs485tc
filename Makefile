VEDLIBDIR = ext/velib_python
INSTALL_CMD = install
LIBDIR = $(bindir)/ext/velib_python

APP = dbus-imt-si-rs485tc.py

FILES = \
	config.py \
	dbus-imt-si-rs485tc.py \
	imt_si_rs485_sensor.py \
	signals.py \
	ve_dbus_service_async.py \
	watchdog.py


VEDLIB_FILES = \
	$(VEDLIBDIR)/vedbus.py \
	$(VEDLIBDIR)/ve_utils.py \
	$(VEDLIBDIR)/settingsdevice.py

help:
	@echo "The following make targets are available"
	@echo " help    - print this message"
	@echo " install - install everything"
	@echo " clean   - remove temporary files"

install_app : $(FILES) $(APP)
	@if [ "$^" != "" ]; then \
		$(INSTALL_CMD) -d -m 755 $(DESTDIR)$(bindir); \
		$(INSTALL_CMD) -m 644 -t $(DESTDIR)$(bindir) $(FILES); \
		$(INSTALL_CMD) -m 755 $(APP) $(DESTDIR)$(bindir); \
		echo installed $(DESTDIR)$(bindir)/$(notdir $^); \
	fi

install_velib_python: $(VEDLIB_FILES)
	@if [ "$^" != "" ]; then \
		$(INSTALL_CMD) -d -m 755 $(DESTDIR)$(LIBDIR); \
		$(INSTALL_CMD) -m 644 -t $(DESTDIR)$(LIBDIR) $^; \
		echo installed $(DESTDIR)$(LIBDIR)/$(notdir $^); \
	fi

clean distclean: ;

install: install_velib_python install_app

.PHONY: help install_app install_velib_python install
