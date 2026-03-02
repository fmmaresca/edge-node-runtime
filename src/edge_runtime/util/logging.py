import logging
import os
import sys
from typing import Literal

Level = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

def setup_logging(level: Level = "INFO") -> None:
    lvl = os.getenv("EDGE_LOG_LEVEL", level).upper()
    logging.basicConfig(
        level=getattr(logging, lvl, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
