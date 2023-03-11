import logging
from api import RemoteBuildAPI

logger = logging.getLogger(__name__)

games = [
    RemoteBuildAPI('TMNEXT', 30000),
    RemoteBuildAPI('MP4', 30001),
    RemoteBuildAPI('TURBO', 30002),
]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    for game in games:
        game.get_data_folder()
        game.load_plugin('Testbed', 'user', 'folder')
