"""Allow `python -m citation_formatter` without installing."""

import sys

from .cli import main

if __name__ == "__main__":
    sys.exit(main())
