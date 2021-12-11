
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

streamhandler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(threadName)s] %(filename)s %(funcName)s:%(lineno)d %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)

filehandler = logging.FileHandler('app.log')
logger.addHandler(filehandler)
