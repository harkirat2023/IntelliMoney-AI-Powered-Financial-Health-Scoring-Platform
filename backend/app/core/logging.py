import logging
import sys


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        fmt="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    ))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    logging.getLogger("passlib").setLevel(logging.ERROR)
    logging.getLogger("jose").setLevel(logging.ERROR)


logger = logging.getLogger("intellimoney")
