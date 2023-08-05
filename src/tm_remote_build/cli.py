import logging
import os
import shutil
import argparse
from .api import RemoteBuildAPI

logger = logging.getLogger(__name__)

DEFAULT_PORTS = {
    "OpenplanetNext": 30000,
    "Openplanet4": 30001,
    "OpenplanetTurbo": 30002,
}


def unload(args) -> None:
    api = RemoteBuildAPI(args.port)
    unloaded = api.unload_plugin(args.plugin_id)
    if unloaded:
        logger.info('Commanded unload for plugin with ID "%s"' % (args.plugin_id,))
    else:
        logger.error(
            'Problem commanding unload for plugin with ID "%s"' % (args.plugin_id,)
        )


def load(args) -> None:
    api = RemoteBuildAPI(args.port)
    loaded = api.load_plugin(
        args.plugin_id, plugin_src="user", plugin_type=args.plugin_type
    )
    if loaded:
        logger.info('Commanded load for plugin with ID "%s"' % (args.plugin_id,))
    else:
        logger.error(
            'Problem commanding load for plugin with ID "%s"' % (args.plugin_id,)
        )


def main() -> None:
    parser = argparse.ArgumentParser(prog="tm-remote-build")
    subparser = parser.add_subparsers()

    def common_args(subparser) -> None:
        subparser.add_argument(
            "plugin_id",
            help="The plugin ID to be unloaded. For a folder source plugin this would be the folder name. For a zipped source plugin this would be the filename without extension.",
        )
        subparser.add_argument(
            "-p",
            "--port",
            default=30000,
            type=int,
            help="The port used to communicate with Openplanet",
        )
        subparser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose logging for debugging Remote Build to Openplanet communication",
        )

    sub_unload = subparser.add_parser("unload", help="Unload a plugin")
    common_args(sub_unload)
    sub_unload.set_defaults(func=unload)

    sub_load = subparser.add_parser("load", help="Load a plugin")
    sub_load.add_argument(
        "plugin_type",
        choices=["folder", "zip"],
        help="The type of plugin source to load from.",
    )
    common_args(sub_load)
    sub_load.set_defaults(func=load)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR)
    args.func(args)
