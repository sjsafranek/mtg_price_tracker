import logging

# Create new logger instance
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
                        "%(asctime)s [%(levelname)s] [%(threadName)s] %(filename)s %(funcName)s:%(lineno)d %(message)s", 
                        datefmt='%Y-%m-%d %H:%M:%S')

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)
