import asyncio
import sys

from src.interface.repl import LightBulbCLI
from src.observability import setup_logging


def main():
    setup_logging()
    cli = LightBulbCLI()
    try:
        asyncio.run(cli.run())
    except KeyboardInterrupt:
        print("\nSession terminated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
