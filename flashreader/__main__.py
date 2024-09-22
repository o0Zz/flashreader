import argparse
import logging
import sys
import importlib

_LOGGER = logging.getLogger(__name__)

memory = None
platform = None

def exit(exit_code):
    global memory
    global platform

    if platform is not None:
        platform.close()

    if memory is not None:
        memory.close()

    sys.exit(exit_code)

def main():
    parser = argparse.ArgumentParser(description='Memory Dumper')
    parser.add_argument('--platform', type=str, help='Platform how to access SPI (raspberrypi etc ...)', required=True)
    parser.add_argument('--memory', type=str, help='Type of flash to use (mx25 etc ...)', required=True)
    parser.add_argument('--read', type=str, help='Path to the destination file')
    parser.add_argument('--write', type=str, help='Path to the source file')
    parser.add_argument('--erase', action='store_true', help='Erase a part of the memory (Use offset/length to define it)')
    parser.add_argument('--offset', type=lambda x: int(x, 16), help='Offset in bytes in hex (default: 0)', default=0x00000000)
    parser.add_argument('--length', type=int, help='Number of bytes to dump (default: 0 - means all memory)', default=0)
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        platform_module = importlib.import_module(f'flashreader.platform.{args.platform}')
    except ModuleNotFoundError as e:
        _LOGGER.error(f"Unable to import platform module: {args.platform} (Module not found !)")
        exit(1)
    except:
        _LOGGER.exception(f"Import platform exception: {args.platform}")
        exit(1)

    platform = getattr(platform_module, 'Platform')()
    if not platform.open():
        _LOGGER.error("Unable to open platform !")
        exit(1)

    try:
        memory_module = importlib.import_module(f'flashreader.memory.{args.memory}')
    except ModuleNotFoundError as e:
        _LOGGER.error(f"Unable to import memory module: {args.memory} (Module not found !)")
        exit(1)
    except:
        _LOGGER.exception(f"Import memory exception: {args.memory}")
        exit(1)

    memory = getattr(memory_module, 'Memory')(platform)
    if not memory.open():
        _LOGGER.error("Unable to open memory !")
        exit(1)

    if args.read:
        with open(args.read, "wb") as fd:
            data = memory.read(args.offset, args.length)
            fd.write(bytes(data))

    elif args.write:
        data = None
        with open(args.write, "rb") as fd:
            data = fd.read()
        
        if not memory.write(args.offset, list(data)):
            _LOGGER.error("Write failed !")
            exit(2)
        
    elif args.erase:
        if not memory.erase(args.offset, args.length):
            _LOGGER.error("Erase failed !")
            exit(2)

    exit(0)
    
if __name__ == '__main__':
    main()