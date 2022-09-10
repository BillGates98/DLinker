import logging

# config the logging behavior
logging.basicConfig(filename='logs/running.log',level=logging.DEBUG)

# some sample log messages

def debug(message):
    logging.debug(message)

def info(message):
    logging.info(message)

def error(message):
    logging.error(message)

def warning(message):
    logging.warning(message)

def exception(message):
    logging.exception(message)

def critical(message):
    logging.critical(message)
