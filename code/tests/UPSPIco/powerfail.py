#! /usr/bin/python -p

import sys
import time
import logging
import logging.handlers
import rpI2C as i2c

BUS = 1
UPS_ADD = 0x69
PWR_MODE_REG = 0x00
LINE_MODE = 0x01
BAT_MODE = 0x02

class UPSPico(object):
    def __init__(self,address=UPS_ADD, bus=BUS):
        self.log = logging.getLogger(__name__)
        self.log.debug("UPSPico.__init__()")
        self.ups = i2c.I2C(address, bus)

    def monitor(self):
        self.log.debug("UPSPIco.monitor()")
        transferred = False
        while not transferred:
            mode = self.ups.read_unsigned_byte(PWR_MODE_REG)
            if mode == BAT_MODE:
                self.log.debug("UPS is running on battery power")
                #go into loop checking video folder
            elif mode == LINE_MODE:
                self.log.debug("UPS is running on line power")
            else:
                self.log.debug("mode is " + str(mode))
            time.sleep(1)

logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger("ups_monitor")
log.setLevel(logging.DEBUG)

ups = UPSPico()
ups.monitor()
