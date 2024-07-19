from memory_dumper.memory.serialflash import SerialFlash

#http://ww1.microchip.com/downloads/en/DeviceDoc/20001836J.pdf
#http://ww1.microchip.com/downloads/en/DeviceDoc/20001836J.pdf
class Memory(SerialFlash):
    def __init__(self, anSPI):
        SerialFlash.__init__(self, anSPI)
        self.ERASE_SECTOR = 0xD8
        self.m_size = (128*1024)
