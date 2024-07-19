import logging
from pyftdi import spi
from pyftdi.ftdi import Ftdi
_LOGGER = logging.getLogger(__name__)


#https://swharden.com/blog/2023-08-24-ft232h-spi-flash/+
#Windows support -> https://eblot.github.io/pyftdi/installation.html
#Need to install the lib usb
#Use Zadig, select the USB device in the list, select libusb-win32 and Replace the driver

class Platform:

    def __init__(self, gpio_cs=0):
        self.gpio_cs = gpio_cs
        self.spi = spi.SpiController()
        self.spi_port = None

    def open(self):
        #Ftdi.show_devices()

        _LOGGER.debug(f"Opening platform FT232H ...")
        self.spi.configure('ftdi://ftdi:232h:1/1')
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
