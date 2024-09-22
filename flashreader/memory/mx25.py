from flashreader.memory.spiflash import Memory as SPIFlash

#https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F,%203V,%2032Mb,%20v1.7.pdf
#https://www.macronix.com/Lists/Datasheet/Attachments/8800/MX25L25773G,%203V,%20256Mb,%20v1.0.pdf
#https://www.macronix.com/Lists/Datasheet/Attachments/8702/MX25R1635F,%20Wide%20Range,%2016Mb,%20v1.6.pdf

class Memory(SPIFlash):
    def __init__(self, anSPI):
        SPIFlash.__init__(self, anSPI)
