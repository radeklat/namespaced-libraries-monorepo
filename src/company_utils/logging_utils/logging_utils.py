import logging


def initialize_logging(level: int = logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)-15s %(level)s %(message)s")
