


from memory_dumper.memory.spiflash import SPIFlash

#https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/25LCXXX-8K-256K-SPI-Serial-EEPROM-High-Temp-Family-Data-Sheet-20002131E.pdf
class Memory(SPIFlash):
    def __init__(self, anSPI):
        SPIFlash.__init__(self, anSPI)
        self.ERASE_SECTOR = 0xD8
        self.m_size = (256*1024)
