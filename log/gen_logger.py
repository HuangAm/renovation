import logging
import logging.config

logging.config.fileConfig("log/logging.conf")
logger = logging.getLogger("downloadLog")


