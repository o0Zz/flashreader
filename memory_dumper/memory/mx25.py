import logging
import time
import math
from memory_dumper.utils.timeutils import TIMER_START_MS, TIMER_ELAPSED_MS

_LOGGER = logging.getLogger(__name__)

#https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F,%203V,%2032Mb,%20v1.7.pdf
#https://www.macronix.com/Lists/Datasheet/Attachments/8800/MX25L25773G,%203V,%20256Mb,%20v1.0.pdf
#https://www.macronix.com/Lists/Datasheet/Attachments/8702/MX25R1635F,%20Wide%20Range,%2016Mb,%20v1.6.pdf

SPI_MAX_BUFFER_SIZE=256

class MemoryMX25:
    def __init__(self, anSPI):
        self.mSPI = anSPI
        self.m_size = 0
        self.m_sector_size = 4096
        self.disable_CS()

    def open(self, force):
        self.exit_DPD()
    
        data = self.read_device_id()
        
        manufId = data[0]
        memoryType = data[1]
        memoryDensity = data[2]
        
        if manufId == 0xC2:
            self.m_size = int(math.pow(2, memoryDensity))
            
            #if memoryType == 0x20: #MX25L
            #elif memoryType == 0x28: #MX25R (Ultra low power)
                
        elif not force:
            _LOGGER.error(f"MX25 not properly connected OR not an MX25 (DeviceID Received: {data}) !")
            return False
            
        _LOGGER.info(f"MX25 opened ! ( Force: {force}, Size: {self.m_size}, SectorSize: {self.m_sector_size} ({data}) )")
        return True
        
    def close(self):
        self.disable_CS()
        return True
         
    def get_size(self):
        return self.m_size
        
    def read_device_id(self):
        self.enable_CS()
        self.mSPI.transfer([0x9F])
        data = self.mSPI.readbytes(3)
        self.disable_CS()
        return data

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

    def read_status_register(self):
        self.mSPI.transfer([0x05])
        return self.mSPI.readbytes(1)[0]

    def enable_write(self):
        self.enable_CS()
        self.mSPI.transfer([0x06])
        self.disable_CS()
        
        self.enable_CS()
        value = self.read_status_register()
        self.disable_CS()
        
        if not (value & 0x02):
            _LOGGER.error(f"MX25 enable write failed (Status: {value})!")
            return False
            
        return True        

    def erase(self, addr, length = 0):
    
        if length == 0:
            length = self.m_size

        
        if ((addr % self.m_sector_size) != 0):
            _LOGGER.error(f"Erase addr is not a modulo of sector size ({self.m_sector_size})")
            return False

        _LOGGER.info(f"Erasing 0x{addr:08x} (Length: {length} - PageCount: {int(length/self.m_sector_size)})")
        
        self.exit_DPD()
        
        for i in range(0, int(length/self.m_sector_size)):
        
            if not self.enable_write():
                _LOGGER.error(f"Erase flash failed at page {i} !")
                return False

            self.enable_CS()
            self.mSPI.transfer([0x20])
            self.send_address(addr + (i * self.m_sector_size))
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
            
            #Wait a bit between 2 erase
            time.sleep(0.01)
            
        return True
    
    def read(self, aPageAddr, length = 0):
        buffer = []
        if length == 0:
            length = self.m_size
            
        _LOGGER.info(f"Reading offset: 0x{aPageAddr:08x} Length: {length}")
        
        self.exit_DPD()

        self.enable_CS()

        self.mSPI.transfer([0x03])
        self.send_address(aPageAddr)
       
        prev_progress = 0
        for theOffset in range(0, length, SPI_MAX_BUFFER_SIZE):
            lSize = min(length - theOffset, SPI_MAX_BUFFER_SIZE)
            
            buf_tmp = self.mSPI.readbytes(lSize)
            if len(buf_tmp) > 0:
                buffer.extend(buf_tmp)

            progress = int((len(buffer)/length) * 100)
            if progress > prev_progress:
                prev_progress = progress
                _LOGGER.info(f"Read: {progress}%")
            
        
        self.disable_CS()

        return buffer

    def write(self, aDstAddr, aSrcBuffer):
        self.exit_DPD()
        
        _LOGGER.info(f"Writing offset: 0x{aDstAddr:08x} Length: {len(aSrcBuffer)}")
        
        if ((aDstAddr % self.m_sector_size) != 0):
            _LOGGER.error(f"Write destination addr is not a modulo of sector size ({self.m_sector_size})")
            return False
            
        prev_progress = 0
        theEndAddr = aDstAddr + len(aSrcBuffer)
        theAddr = aDstAddr
        while theAddr < theEndAddr:
        
            if ((theAddr % self.m_sector_size) == 0):
                self.erase(theAddr, self.m_sector_size)
                
            theLengthToWrite = SPI_MAX_BUFFER_SIZE

            if theAddr % 0x100 != 0:
                theLengthToWrite = 0x100 - (theAddr % 0x100)

            if theLengthToWrite > theEndAddr - theAddr:
                theLengthToWrite = theEndAddr - theAddr

            theOffset = theAddr - aDstAddr

            if not self.enable_write():
                return False
           
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

            progress = int((theOffset/len(aSrcBuffer)) * 100)
            if progress > prev_progress:
                prev_progress = progress
                _LOGGER.info(f"Write: {progress}%")
                
            theAddr += theLengthToWrite
            
            #Wait a bit between 2 write
            time.sleep(0.01)
            
        return True

