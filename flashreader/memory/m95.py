from flashreader.memory.spiflash import Memory as SPIFlash

#https://www.st.com/resource/en/datasheet/m95m01-df.pdf

class Memory(SPIFlash):
    def __init__(self, anSPI):
        SPIFlash.__init__(self, anSPI)
        self.DEVICE_ID = 0x00 #This chipset don't have Device ID and Erase command
        self.ERASE_SECTOR = 0x00