import logging
from pyftdi import spi
from pyftdi import i2c
from pyftdi.ftdi import Ftdi
from pyftdi.usbtools import UsbTools

_LOGGER = logging.getLogger(__name__)

#On windows:
#You need to replace the windows driver by libusb-win32
#Use Zadig (https://zadig.akeo.ie/), select the USB device in the list, select libusb-win32 and replace the driver (DO NOT USE WINUSB and others)

#PIN OUT SPI
# D0 -> SCK
# D1 -> MOSI
# D2 -> MISO
# D3 -> CS
class PlatformSPI:
    def __init__(self, url=None, gpio_cs=3):
        self.url = url
        self.gpio_cs = gpio_cs
        self.spi = None

    def is_open(self):
        return self.spi is not None
    
    def open(self):
        _LOGGER.debug(f"Opening platform FT232H: {self.url}...")
        self.spi = spi.SpiController()
        self.spi.configure(self.url)
        self.spi_port = self.spi.get_port(cs=self.gpio_cs, freq=4000000, mode=0) #4Mhz        
        return True
        
    def close(self):
        if self.spi is None:
            return True
        
        _LOGGER.debug("Closing platform FT232H ...")
        self.spi.close()
        return True

    def transfer(self, out_buffer, read_length = 0):
        _LOGGER.debug(f"SPI transfer: {out_buffer} (Read: {read_length})")
        ret = self.spi_port.exchange(out_buffer, read_length)
        if read_length > 0:
            _LOGGER.debug(f"SPI transfer read: {ret}")

        return ret


# PIN OUT I2C
# D0 -> SCL
# D1 -> SDA
# + PullUP 4.7KOhm between D0 and 5v
# + PullUP 4.7KOhm between D1 and 5v
class PlatformI2C:
    def __init__(self, url=None):
        self.url = url 
        self.i2c = None

    def is_open(self):
        return self.i2c is not None
    
    def open(self, slave_address):
        _LOGGER.debug(f"Opening platform FT232H I2C ...")
        self.i2c = i2c.I2cController()
        self.i2c.configure(self.url)
        self.i2c_port = self.i2c.get_port(slave_address)
        return True
    
    def close(self):
        if self.i2c is None:
            return True
        
        _LOGGER.debug("Closing platform FT232H I2C ...")
        self.i2c.close()
        self.i2c = None
        return True
    
    def read(self, length):
        ret = self.i2c_port.read(length)
        _LOGGER.debug(f"I2C read {ret}")
        return ret
    
    def write(self, data):
        _LOGGER.debug(f"I2C write: {data}")
        self.i2c_port.write(data)

class Platform:

    def __init__(self, url=None, gpio_cs=0):
        self.url = url
        self.gpio_cs = gpio_cs
        self.spi = None
        self.i2c = None

    def open(self):
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
        
        self.spi = PlatformSPI(self.url, self.gpio_cs)

        self.i2c = PlatformI2C(self.url)

        return self.url != None
    
    def close(self):
        if self.spi is not None and self.spi.is_open():
            self.spi.close()
        if self.i2c is not None and self.i2c.is_open():
            self.i2c.close()
        return True