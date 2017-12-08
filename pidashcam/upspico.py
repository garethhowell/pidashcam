#! /usr/bin/python -p

import sys
import time
import logging
import logging.handlers
import rpI2C as i2c
import threading
import os

BUS = 1
UPS_ADD = 0x69
PWR_MODE_REG = 0x00
RUNTIME_REG = 0x01
LINE_MODE = 0x01
BAT_MODE = 0x02
RUNTIME = 0x0A

class UPSPIco(threading.Thread):
    def __init__(self, name, destDir, recording, shutdown,
            address=UPS_ADD, bus=BUS):
        super(UPSPIco, self).__init__()
        self.name = name
        self.log = logging.getLogger(__name__)
        self.log.debug("UPSPico.__init__()")
        self.ups = i2c.I2C(address, bus)
        self.destDir = destDir
        self.recording = recording
        self.UPSShutdown = shutdown
        self.localShutdown = threading.Event()

        # Ensure the UPS PIco will stay up long enough
        self.ups.write_byte(RUNTIME_REG, RUNTIME)


    def run(self):
        self.log.debug("UPSPIco.monitor()")
        while not (self.UPSShutdown.isSet() or self.localShutdown.isSet()):
            mode = self.ups.read_unsigned_byte(PWR_MODE_REG)
            if mode == BAT_MODE:
                self.log.debug("UPS is running on battery power")

                # Signal stop recording
                self.recording.clear()

                # Check if we are connected to WLAN

                # Checking number of files in video folder
                # .sync folder will always exist, so check for more than 1
                n = len(os.listdir(self.destDir))
                if n == 1:
                    self.UPSShutdown.set()
                else:
                    self.log.debug("%s has %s files in it" %
                        (self.destDir, str(n)))
            elif mode == LINE_MODE:
                self.log.debug("UPS is running on line power")
            else:
                self.log.debug("mode is " + str(mode))
            time.sleep(2)
        if self.UPSShutdown.isSet():
            self.log.debug("UPS is shutting system down")
            #os.system("shutdown -P now")
        elif self.localShutdown.isSet():
            self.log.debug("Signal is shutting system down")
        else:
            self.log.debug("Not sure why we are shutting system down")

    def join(self,timeout=None):
        self.localShutdown.set()
        super(UPSPIco, self).join()
