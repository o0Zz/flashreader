import logging
import time
import math

_LOGGER = logging.getLogger(__name__)

SPI_MAX_BUFFER_SIZE=256

SR_WIP = 0b00000001  # Busy/Work-in-progress bit
SR_WEL = 0b00000010  # Write enable bit
SR_BP0 = 0b00000100  # bit protect #0
SR_BP1 = 0b00001000  # bit protect #1
SR_BP2 = 0b00010000  # bit protect #2
SR_BP3 = 0b00100000  # bit protect #3

class Memory:
    def __init__(self, platform):
        self.m_spi = platform.spi
        self.m_size = 0
        self.m_sector_size = 4096

        self.DEVICE_ID = 0x9F
        self.ENABLE_WRITE = 0x06
        self.READ_STATUS_REGISTER = 0x05
        self.WRITE = 0x02
        self.READ = 0x03
        self.ERASE_SECTOR = 0x20

    def open(self):
        if not self.m_spi.open():
            _LOGGER.error(f"Unable to open SPI !")
            return False

        if self.DEVICE_ID != 0:   
            data = self.m_spi.transfer([self.DEVICE_ID], 3)

            manuf_id = data[0]
            memory_type = data[1]
            memory_density = data[2]
            
            _LOGGER.debug(f"Manuf ID: {manuf_id}, Memory Type: {memory_type}, Memory Density: {memory_density}")
            self.m_size = int(math.pow(2, memory_density))

            if manuf_id == 0xFF:
                _LOGGER.error(f"Invalid device ID (Is memory connected ?)")
                return False

        _LOGGER.info(f"Memory opened ! (Size: {self.m_size}, SectorSize: {self.m_sector_size})")
        return True

    def close(self):
        return self.m_spi.close()
         
    def get_size(self):
        return self.m_size

    def __is_busy(self):
        value = self.m_spi.transfer([self.READ_STATUS_REGISTER], 1)[0]
        return bool(value & SR_WIP)

    def __enable_write(self):
        self.m_spi.transfer([self.ENABLE_WRITE], 0)

        time.sleep(0.1)
        value = self.m_spi.transfer([self.READ_STATUS_REGISTER], 1)[0]    
        if not (value & SR_WEL):
            _LOGGER.error(f"Enable write failed (Status: {value})!")
            return False

        return True        

    def erase(self, address, length = 0):
        if length == 0:
            length = self.m_size
        
        if (length % self.m_sector_size) != 0:
            _LOGGER.error(f"Erase length is not a modulo of sector size ({self.m_sector_size})")
            return False
        
        if ((address % self.m_sector_size) != 0):
            _LOGGER.error(f"Erase address is not a modulo of sector size ({self.m_sector_size})")
            return False

        _LOGGER.info(f"Erasing 0x{address:08x} (Length: {length} - PageCount: {int(length/self.m_sector_size)})")

        for i in range(0, int(length/self.m_sector_size)):
        
            if not self.__enable_write():
                _LOGGER.error(f"Erase flash failed at page {i} !")
                return False
            
            addr = address + (i * self.m_sector_size)
            buf = [self.ERASE_SECTOR, (addr & 0x00FF0000) >> 16, (addr & 0x0000FF00) >> 8, (addr & 0x000000FF)]
            self.m_spi.transfer(buf, 0)
                    
            while self.__is_busy():
                time.sleep(0.01)
            
        return True
    
    def read(self, address, length = 0):
        buffer = []
        if length == 0:
            length = self.m_size
            
        _LOGGER.info(f"Reading offset: 0x{address:08x} Length: {length}")

        prev_progress = 0
        for offset in range(0, length, SPI_MAX_BUFFER_SIZE):
            addr = address + offset
            read_size = min(length - offset, SPI_MAX_BUFFER_SIZE)
            
            buf = [self.READ, (addr & 0x00FF0000) >> 16, (addr & 0x0000FF00) >> 8, (addr & 0x000000FF)]
            buf_tmp = self.m_spi.transfer(buf, read_size)
            if len(buf_tmp) > 0:
                buffer.extend(buf_tmp)

            progress = int((len(buffer)/length) * 100)
            if progress > prev_progress:
                prev_progress = progress
                _LOGGER.info(f"Read: {progress}%")

        return buffer

    def write(self, address, data):
        _LOGGER.info(f"Write offset: 0x{address:08x} Length: {len(data)}")
        
        if ((address % self.m_sector_size) != 0):
            _LOGGER.error(f"Write destination addr is not a modulo of sector size ({self.m_sector_size})")
            return False
            
        prev_progress = 0

        for offset in range(0, len(data), SPI_MAX_BUFFER_SIZE):
            addr = address + offset

            if ((addr % self.m_sector_size) == 0):
                if not self.erase(addr, self.m_sector_size):
                    return False

            if not self.__enable_write():
                return False
            
            buf = [self.WRITE, (addr & 0x00FF0000) >> 16, (addr & 0x0000FF00) >> 8, (addr & 0x000000FF)]
            buf.extend(data[offset : offset + SPI_MAX_BUFFER_SIZE])

            self.m_spi.transfer(buf, 0)

            while self.__is_busy():
                time.sleep(0.01)

            progress = int((offset/len(data)) * 100)
            if progress > prev_progress:
                prev_progress = progress
                _LOGGER.info(f"Write: {progress}%")

        return True

