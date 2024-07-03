import argparse
import logging
    
if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Memory Dumper')
    parser.add_argument('--platform', type=str, help='Platform how to access SPI (raspberrypi etc ...)')
    parser.add_argument('--memory', type=str, help='Type of flash to use (mx25 etc ...)')
    parser.add_argument('--read', type=str, help='Path to the destination file')
    parser.add_argument('--write', type=str, help='Path to the source file')
    parser.add_argument('--offset', type=int, help='Offset in bytes (default: 0)', default=0)
    parser.add_argument('--length', type=int, help='Number of bytes to dump (default: 4MB)', default=4*1024*1024)
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    platform = None
    if args.platform == 'raspberrypi':
        from memory_dumper.platform.raspberrypi import RaspberryPi
        platform = RaspberryPi()

    memory = None
    if args.memory == 'mx25':
        from memory_dumper.memory.mx25 import MemoryMX25
        memory = MemoryMX25(platform)

    if args.read:
        data = memory.read(args.offset, args.length)
        with open(args.read, "wb") as fd:
            fd.write(bytes(data))

    elif args.write:
        data = None
        with open(args.write, "rb") as fd:
            data = fd.read()
        memory.write(args.offset, bytearray(data))