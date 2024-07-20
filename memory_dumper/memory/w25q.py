from memory_dumper.memory.spiflash import SPIFlash

#https://docs.rs-online.com/9bfc/0900766b81704060.pdf

class Memory(SPIFlash):
    def __init__(self, anSPI):
        SPIFlash.__init__(self, anSPI)