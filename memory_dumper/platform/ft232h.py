import logging
from pyftdi import spi
from pyftdi.ftdi import Ftdi
from pyftdi.usbtools import UsbTools

_LOGGER = logging.getLogger(__name__)

#PIN OUT SPI
# D0 -> SCK
# D1 -> MOSI
# D2 -> MISO
# D3 -> CS

# PIN OUT I2C
# D0 -> SCL
# D1 -> SDA
# + PullUP 4.7KOhm between D0 and 5v
# + PullUP 4.7KOhm between D1 and 5v

#On windows:
#You need to replace the windows driver by libusb-win32
#Use Zadig (https://zadig.akeo.ie/), select the USB device in the list, select libusb-win32 and replace the driver (DO NOT USE WINUSB and others)

class Platform:

    def __init__(self, url=None, gpio_cs=0):
        self.url = url
        self.gpio_cs = gpio_cs
        self.spi = spi.SpiController()
        self.spi_port = None

    def open(self):
        Ftdi.show_devices()
        if self.url == None:
            #Find the first FTDI device
            devdescs = UsbTools.list_devices('ftdi:///?', Ftdi.VENDOR_IDS, Ftdi.PRODUCT_IDS, Ftdi.DEFAULT_VENDOR)
            if len(devdescs) == 0:
                _LOGGER.error("No FTDI device found !")
                return False

            devstrs = UsbTools.build_dev_strings('ftdi', Ftdi.VENDOR_IDS, Ftdi.PRODUCT_IDS, devdescs)
            for dev in devstrs:
                self.url = dev[0]
                break

        _LOGGER.debug(f"Opening platform FT232H: {self.url}...")
        self.spi.configure(self.url)
        self.spi_port = self.spi.get_port(cs=self.gpio_cs, freq=4000000, mode=0) #4Mhz        
        return True
        
    def close(self):
        _LOGGER.debug("Closing platform FT232H ...")
        self.spi.close()
        return True

    def spi_transfer(self, out_buffer, read_length = 0):
        _LOGGER.debug(f"SPI transfer: {out_buffer} (Read: {read_length})")
        ret = self.spi_port.exchange(out_buffer, read_length)
        if read_length > 0:
            _LOGGER.debug(f"SPI transfer read: {ret}")

        return ret

