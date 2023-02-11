import logging
from api import OpenplanetTcpSocket

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    sock = OpenplanetTcpSocket()
    for i in range(3):
        if sock.try_connect(30000):
            success = sock.send({'route': 'load_plugin'})
            logger.info(sock.receive())
        else:
            logger.info("no luck...")
