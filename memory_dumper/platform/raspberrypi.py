import spidev
import RPi.GPIO as GPIO
import logging

_LOGGER = logging.getLogger(__name__)

class RaspberryPi:
        #RPI4 pinout https://dnycf48t040dh.cloudfront.net/fit-in/840x473/GPIO-diagram-Raspberry-Pi-4.png
        #bus=0, device=0 refer to SPI0
        #bus=0, device=1 refer to SPI1
        
        #/dev/spidev<bus>.<device>
    def __init__(self, bus=0, device=0, gpio_cs=11):
        self.gpio_cs = gpio_cs
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.gpio_cs, GPIO.OUT) 
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 1000000  # Set SPI clock speed to 4MHz
        
    def readbytes(self, length):
        ret = self.spi.readbytes(length)
        _LOGGER.debug(f"SPI readbytes: {ret}")
        return ret
    
    def transfer(self, data):
        _LOGGER.debug(f"SPI xfer2 send: {data}")
        ret = self.spi.xfer2(data)
        _LOGGER.debug(f"SPI xfer2 rcv: {ret}")
        return ret

    def spi_cs(self, value):
        GPIO.output(self.gpio_cs, value)

    def close(self):
        self.spi.close()