from memory_dumper.memory.serialflash import SerialFlash

#https://docs.rs-online.com/9bfc/0900766b81704060.pdf

class Memory(SerialFlash):
    def __init__(self, anSPI):
        SerialFlash.__init__(self, anSPI)