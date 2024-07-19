import spidev
import RPi.GPIO as GPIO
import logging
import time

_LOGGER = logging.getLogger(__name__)

class Platform:
        #RPI4 pinout https://dnycf48t040dh.cloudfront.net/fit-in/840x473/GPIO-diagram-Raspberry-Pi-4.png
        #bus=0, device=0 refer to SPI0
        #bus=0, device=1 refer to SPI1
        
        #/dev/spidev<bus>.<device>
    def __init__(self, bus=0, device=0, gpio_cs=11):
        self.bus = bus
        self.device = device
        self.gpio_cs = gpio_cs
        self.spi = spidev.SpiDev()

    def open(self):
        _LOGGER.debug(f"Opening platform RPI ...")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.gpio_cs, GPIO.OUT) 

        self.__spi_cs(1) #Disable CS

        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 1000000  # Set SPI clock speed to 4MHz
        return True
        
    def close(self):
        _LOGGER.debug("Closing platform RPI ...")
        GPIO.cleanup()
        self.spi.close()
        return True
        
    def __read(self, length):
        ret = self.spi.readbytes(length)
        _LOGGER.debug(f"SPI read: {ret}")
        return ret
    
    def __write(self, data):
        _LOGGER.debug(f"SPI write: {data}")
        self.spi.writebytes(data)

    def __spi_cs(self, value):
        GPIO.output(self.gpio_cs, value)
        time.sleep(0.001)

    def spi_transfer(self, out_buffer, read_length = 0):
        ret = None
        
        self.__spi_cs(0)

        if out_buffer is not None:
            self.__write(out_buffer)
        if read_length > 0:
            ret = self.__read(read_length)

        self.__spi_cs(1)
        
        return ret
