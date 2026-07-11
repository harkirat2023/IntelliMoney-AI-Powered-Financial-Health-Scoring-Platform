import json
import logging
import sys

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "level": record.levelname,
            "timestamp": self.formatTime(record, self.datefmt),
            "name": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log["request_id"] = record.request_id
        if record.exc_info and record.exc_info[0]:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, default=str)


def setup_logging() -> None:
    settings = get_settings()
    is_production = settings.environment == "production"

    if is_production:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter(
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        ))
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            fmt="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        ))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    logging.getLogger("passlib").setLevel(logging.ERROR)
    logging.getLogger("jose").setLevel(logging.ERROR)


logger = logging.getLogger("intellimoney")
