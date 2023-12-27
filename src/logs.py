import logging
from logging import StreamHandler

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

handler = StreamHandler()
log_formatter = logging.Formatter('[%(asctime)s] - %(funcName)s - [%(filename)s - %(lineno)d] - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(log_formatter)
logger.addHandler(handler)