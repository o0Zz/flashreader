import logging
import time
from memory_dumper.utils.timeutils import TIMER_START_MS, TIMER_ELAPSED_MS

_LOGGER = logging.getLogger(__name__)

#https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F,%203V,%2032Mb,%20v1.7.pdf

class MemoryMX25:
    def __init__(self, anSPI):
        self.mSPI = anSPI
        self.disable_CS()

    def disable_CS(self):
        self.mSPI.spi_cs(1)
        time.sleep(0.001)

    def enable_CS(self):
        self.mSPI.spi_cs(0)
        time.sleep(0.001)

    def send_address(self, aSrcFlashAddr):
        theBuffer = [(aSrcFlashAddr & 0x00FF0000) >> 16, (aSrcFlashAddr & 0x0000FF00) >> 8, (aSrcFlashAddr & 0x000000FF)]
        return self.mSPI.transfer(theBuffer)

    def exit_DPD(self):
        self.enable_CS()
        self.disable_CS()
        time.sleep(0.001)

    def read_status_register(self):
        self.mSPI.transfer([0x05])
        return self.mSPI.readbytes(1)

    def enable_write(self):
        self.enable_CS()
        self.mSPI.transfer([0x06])
        self.disable_CS()

    def erase(self, aPageAddr, aPageCount):
        self.exit_DPD()

        for i in range(aPageCount):
            self.enable_write()
            
            self.enable_CS()
            self.mSPI.transfer([0x20])
            self.send_address(aPageAddr + (i * 256))
            self.disable_CS()

            self.enable_CS()
        
            theStartTime = TIMER_START_MS()
            while True:
                value = self.read_status_register()
                if not (value & 0x01) and TIMER_ELAPSED_MS(theStartTime) < 1000:
                    break

            self.disable_CS()

            if value & 0x01:
                _LOGGER.error("MX25 Erase failed (Timeout) !")
                return False

        return True
    
    def read(self, aPageAddr, aLength):
        buffer = []
        self.exit_DPD()

        self.enable_CS()

        self.mSPI.transfer([0x03])
        self.send_address(aPageAddr)
       
        for theOffset in range(0, aLength, 256):
            lSize = min(aLength - theOffset, 256)
            
            buf_tmp = self.mSPI.readbytes(lSize)
            if len(buf_tmp) > 0:
                buffer.extend(buf_tmp)

        self.disable_CS()

        return buffer

    def write(self, aDstAddr, aSrcBuffer):
        self.exit_DPD()
        
        theEndAddr = aDstAddr + len(aSrcBuffer)
        theAddr = aDstAddr
        while theAddr < theEndAddr:
            theLengthToWrite = 256

            if theAddr % 0x100 != 0:
                theLengthToWrite = 0x100 - (theAddr % 0x100)

            if theLengthToWrite > theEndAddr - theAddr:
                theLengthToWrite = theEndAddr - theAddr

            theOffset = theAddr - aDstAddr

            self.enable_write()
           
            self.enable_CS()
            self.mSPI.transfer([0x02])
            self.send_address(theAddr)
            self.mSPI.transfer(aSrcBuffer[theOffset : theOffset + theLengthToWrite])
            self.disable_CS()

            self.enable_CS()
            theValue = 0x00
            lStartTime = TIMER_START_MS()
            while True:
                theValue = self.read_status_register()
                if not (theValue & 0x01) and TIMER_ELAPSED_MS(lStartTime) < 1000:
                    break
            self.disable_CS()

            if theValue & 0x01:
                _LOGGER.error("MX25 write failed (Timeout) !")
                return False

            theAddr += theLengthToWrite

        return True

