import argparse
import logging
import sys

_LOGGER = logging.getLogger(__name__)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Memory Dumper')
    parser.add_argument('--platform', type=str, help='Platform how to access SPI (raspberrypi etc ...)')
    parser.add_argument('--memory', type=str, help='Type of flash to use (mx25 etc ...)')
    parser.add_argument('--read', type=str, help='Path to the destination file')
    parser.add_argument('--write', type=str, help='Path to the source file')
    parser.add_argument('--erase', action='store_true', help='Erase a part of the memory (Use offset/length to define it)')
    parser.add_argument('--force', action='store_true', help='Force to open and use memory even if sanity check fails')
    parser.add_argument('--offset', type=lambda x: int(x, 16), help='Offset in bytes in hex (default: 0)', default=0x00000000)
    parser.add_argument('--length', type=int, help='Number of bytes to dump (default: 0 - means all memory)', default=0)
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    memory = None
    platform = None
    
    try:
      if args.platform == 'raspberrypi':
          from memory_dumper.platform.raspberrypi import RaspberryPi
          platform = RaspberryPi()
  
      if not platform.open():
          _LOGGER.error("Unable to open platform !")
          sys.exit(1)
      
      if args.memory == 'mx25':
          from memory_dumper.memory.mx25 import MemoryMX25
          memory = MemoryMX25(platform)
   
      if not memory.open(args.force):
          _LOGGER.error("Unable to open memory !")
          sys.exit(1)
        
      if args.read:
          with open(args.read, "wb") as fd:
              data = memory.read(args.offset, args.length)
              fd.write(bytes(data))
  
      elif args.write:
          data = None
          with open(args.write, "rb") as fd:
              data = fd.read()
          memory.write(args.offset, list(data))
         
      elif args.erase:
          memory.erase(args.offset, args.length)
          
    except:
        _LOGGER.exception("Main")
        
    finally:

        if memory is not None:
            memory.close()

        if platform is not None:
            platform.close()
    