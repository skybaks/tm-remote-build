import logging
import os
import shutil
import argparse
from .api import RemoteBuildAPI
from .package import zip_plugin

logger = logging.getLogger(__name__)

games = [
    RemoteBuildAPI("TMNEXT", 30000),
    RemoteBuildAPI("MP4", 30001),
    RemoteBuildAPI("TURBO", 30002),
]


def full_path_normalized(input_path) -> str:
    return os.path.normpath(os.path.abspath(input_path))


def deploy_zip(zip_path) -> None:
    package_path = full_path_normalized(zip_path)
    plugin_id, zip_ext = os.path.splitext(os.path.basename(package_path))
    if zip_ext != ".op":
        logger.error("Unexpected file extension in zipped plugin: %s" % (package_path,))
        return
    if not os.path.isfile(package_path):
        logger.error("File not found: %s" % (package_path,))
        return

    loaded_once = False
    for game in games:
        if game.get_data_folder():
            if game.unload_plugin(plugin_id):
                shutil.copy(package_path, os.path.join(game.data_folder, "Plugins"))
                if game.load_plugin(plugin_id, "user", "zip"):
                    loaded_once = True
    if not loaded_once:
        logger.error("No game found to be running")


def load_dir(dir_path) -> None:
    source_path = full_path_normalized(dir_path)
    if not os.path.isdir(source_path):
        logger.error("Directory not found: %s" % (source_path,))
        return

    plugin_id = os.path.basename(source_path)
    for game in games:
        if game.get_data_folder():
            plugin_test_path = full_path_normalized(
                os.path.join(game.data_folder, "Plugins", plugin_id)
            )
            if os.path.samefile(source_path, plugin_test_path):
                game.load_plugin(plugin_id, "user", "folder")
                break
    else:
        logger.error("No game is running or input is not a valid Plugins folder")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_path",
        help="Path to the source code of the plugin or zipped *.op file",
    )
    parser.add_argument(
        "-z",
        "--zip",
        action="store_true",
        help="Zip the plugin from source to a *.op file",
    )
    parser.add_argument(
        "-o",
        "--zip_out_path",
        default=".build/",
        help="Intermediate output path for zipped plugin package. From here it will be copied to all active game plugins folders",
    )
    parser.add_argument(
        "-x",
        "--zip_exclude",
        default="",
        help="A semicolon ';' delimited string of file or folder patterns to exclude from the package zip",
    )
    parser.add_argument(
        "-i",
        "--zip_plugin_id",
        default="",
        help="Optionally specify the plugin ID if it is different than the name of the source directory",
    )
    args = parser.parse_args()

    source_path = full_path_normalized(args.source_path)
    plugin_id = args.plugin_id if args.zip_plugin_id else os.path.basename(source_path)

    if args.zip:
        package_path = zip_plugin(
            source_path,
            args.zip_out_path,
            plugin_id,
            [exclude for exclude in args.zip_exclude.split(";") if exclude],
        )
        if not package_path:
            return
        deploy_zip(package_path)
    else:
        if os.path.isdir(source_path):
            load_dir(source_path)
        else:
            deploy_zip(source_path)
