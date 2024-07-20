import spidev
import smbus
import RPi.GPIO as GPIO
import logging
import time

_LOGGER = logging.getLogger(__name__)

class PlatformSPI:
    def __init__(self, spi_bus=0, spi_device=0, spi_cs=0):
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.spi_cs = spi_cs
        self.spi = spidev.SpiDev()

    def open(self):
        _LOGGER.debug(f"Opening RPI SPI ...")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.spi_cs, GPIO.OUT) 

        self.__spi_cs(1) #Disable CS

        self.spi.open(self.spi_bus, self.spi_device)
        self.spi.max_speed_hz = 1000000  # Set SPI clock speed to 4MHz
        return True
        
    def close(self):
        _LOGGER.debug("Closing RPI SPI ...")
        GPIO.cleanup()

        if self.spi is not None:
            self.spi.close()
        return True
        
    def __read(self, length):
        ret = self.spi.readbytes(length)
        _LOGGER.debug(f"SPI read: {ret}")
        return ret
    
    def __write(self, data):
        _LOGGER.debug(f"SPI write: {data}")
        self.spi.writebytes(data)

    def __cs(self, value):
        GPIO.output(self.gpio_cs, value)
        time.sleep(0.001)

    def transfer(self, out_buffer, read_length = 0):
        ret = None
        
        self.__cs(0)

        if out_buffer is not None:
            self.__write(out_buffer)
        if read_length > 0:
            ret = self.__read(read_length)

        self.__cs(1)
        
        return ret

class PlatformI2C:
    def __init__(self):
        self.bus = smbus.SMBus(0)
        
    def open(self):
        _LOGGER.debug(f"Opening RPI I2C ...")
        return True
        
    def close(self):
        _LOGGER.debug("Closing RPI I2C ...")
        return True
        
    def read(self, address, length):
        ret = self.bus.read_i2c_block_data(address, 0, length)
        _LOGGER.debug(f"I2C read: {ret}")
        return ret

    def write(self, address, data):
        _LOGGER.debug(f"I2C write: {data}")
        self.bus.write_i2c_block_data(address, 0, data)

class Platform:
        #RPI4 pinout https://dnycf48t040dh.cloudfront.net/fit-in/840x473/GPIO-diagram-Raspberry-Pi-4.png
        #bus=0, device=0 refer to SPI0
        #bus=0, device=1 refer to SPI1
        
        #/dev/spidev<bus>.<device>
    def __init__(self, spi_bus=0, spi_device=0, spi_cs=11):
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.spi_cs = spi_cs

    def open(self):
        return True
    
    def close(self):
        return True
    
    def get_spi(self):
        return PlatformSPI(self.spi_bus, self.spi_device, self.spi_cs)

    def get_i2c(self):
        return PlatformI2C()
