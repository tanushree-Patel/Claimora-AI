import logging
import sys
from app.core.config import get_settings

def configure_logging()->None:
    settings=get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        stream=sys.stdout
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name:str)->logging.Logger:
    return logging.getLogger(name)