# Python Memory Dumper 
This memory dumper allow to dump and/or write any memory EEPROM or flash.
Usefull for reverse ingineer memories on embedded systems

## Supported platform
- [x] Raspberry pi 4

## Support memory
- [x] Macronix MX25 (MX25RXXXX, MX25LXXXX, ...)

## Quick start (Raspberry pi 4)
### Setup Raspbian

```
apt-get install python3 python3-pip python3-spidev python3-monotonic
sudo raspi-config
go to "Interfacing Options" > "SPI" > "Enable"
```
Reboot the RPI

### Wiring
- SPI0 has to be used (Pin 19, 21, 23)
- CS need to be on GPIO17(Pin 11)

### Run
Read all memory

`python -m memory_dumper --platform raspberrypi --memory mx25 --read ./dump.bin --offset 0`

Write all memory

`python -m memory_dumper --platform raspberrypi --memory mx25 --write ./dump.bin --offset 0`


