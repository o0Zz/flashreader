from memory_dumper.memory.spiflash import Memory as SPIFlash

#http://ww1.microchip.com/downloads/en/DeviceDoc/20001836J.pdf

class Memory(SPIFlash):
    def __init__(self, anSPI):
        SPIFlash.__init__(self, anSPI)
        self.ERASE_SECTOR = 0xD8
        self.m_size = (128*1024)
