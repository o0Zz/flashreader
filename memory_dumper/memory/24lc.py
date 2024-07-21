
#512 Kbits memory (64 Kbytes)
#https://ww1.microchip.com/downloads/en/devicedoc/21754m.pdf

#It's possible to set the address we want on the I2C flash, so user has to provide the correct chipselect_bits configuration
#A2=1 A1=1 A0=1 -> chipselect_bits = 0x07
#A2=0 A1=1 A0=1 -> chipselect_bits = 0x05
#A2=0 A1=0 A0=1 -> chipselect_bits = 0x01
#A2=0 A1=0 A0=0 -> chipselect_bits = 0x00

#Wiring
#VCC -> 5v
#Vss -> GND
#SDA -> SDA
#SCL -> SCL
#WP -> GND Write Protection = 0 means not protected, 1 means protected
#A0 -> GND
#A1 -> GND
#A2 -> GND

class Memory():
    def __init__(self, platform, memory_size=64*1024, chipselect_bits = 0):
        self.device_addr = 0x50 | chipselect_bits
        self.m_i2c = platform.i2c
        self.m_page_size = 64
        self.m_size = memory_size
    
    def open(self):
        if not self.m_i2c.open(self.device_addr):
            return False
        
        return True
    
    def close(self):
        return self.m_i2c.close()
    
    def read(self, address, length):
        buf = [address >> 8, address & 0xFF]

        self.m_i2c.write(buf)
        return self.m_i2c.read(length)
    
    def _write_page(self, address, data):
        buf = [address >> 8, address & 0xFF]
        buf += data

        self.m_i2c.write(buf)
        
    def write(self, address, data):
        for i in range(0, len(data), self.m_page_size):
            self._write_page(address + i, data[i:i+self.m_page_size])

    def get_size(self):
        return self.m_size
    
    def erase(self, addr, length = 0):
        data = [0x00] * self.m_page_size
        for i in range(0, length, self.m_page_size):
            self._write_page(addr + i, data)