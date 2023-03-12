import logging
import os
import shutil
import argparse
from api import RemoteBuildAPI
from package import zip_plugin

logger = logging.getLogger(__name__)

games = [
    RemoteBuildAPI("TMNEXT", 30000),
    RemoteBuildAPI("MP4", 30001),
    RemoteBuildAPI("TURBO", 30002),
]


def package_and_load(source_path, plugin_id) -> None:
    zipped_plugin_path = zip_plugin(
        source_path, os.path.join(source_path, ".build"), plugin_id
    )

    if not zipped_plugin_path:
        logger.error("Error zipping plugin")
        return

    for game in games:
        if game.get_data_folder():
            if game.unload_plugin(plugin_id):
                shutil.copy(
                    zipped_plugin_path, os.path.join(game.data_folder, "Plugins")
                )
                game.load_plugin(plugin_id, "user", "zip")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", help="Path to the source code of the plugin")
    parser.add_argument(
        "-id",
        "--plugin_id",
        help="Provide the plugin ID if it is different than the name of the source folder",
    )
    args = parser.parse_args()

    if not args.plugin_id:
        args.plugin_id = os.path.basename(args.source_path)
        if not args.plugin_id:
            args.plugin_id = os.path.basename(os.path.dirname(args.source_path))

    package_and_load(args.source_path, args.plugin_id)
