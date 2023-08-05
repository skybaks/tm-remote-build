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


def get_port(args) -> int:
    if args.port is not None:
        return args.port
    else:
        return DEFAULT_PORTS.get(args.openplanet, 0)


def unload(args) -> None:
    api = RemoteBuildAPI(get_port(args))
    unloaded = api.unload_plugin(args.plugin_id)
    if unloaded:
        logger.info('Commanded unload for plugin with ID "%s"' % (args.plugin_id,))
    else:
        logger.error(
            'Problem commanding unload for plugin with ID "%s"' % (args.plugin_id,)
        )


def load(args) -> None:
    api = RemoteBuildAPI(get_port(args))
    loaded = api.load_plugin(
        args.plugin_id, plugin_src=args.plugin_src, plugin_type=args.plugin_type
    )
    if loaded:
        logger.info('Commanded load for plugin with ID "%s"' % (args.plugin_id,))
    else:
        logger.error(
            'Problem commanding load for plugin with ID "%s"' % (args.plugin_id,)
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="tm-remote-build", description="Load or unload Openplanet plugins"
    )
    subparser = parser.add_subparsers(required=True)

    def common_args(sub_input) -> None:
        sub_input.add_argument(
            "plugin_id",
            help="The plugin ID to be targeted. For a folder source plugin this would be the folder name. For a zipped source plugin this would be the filename without extension.",
        )
        comm_group = sub_input.add_mutually_exclusive_group(required=True)
        comm_group.add_argument(
            "-p",
            "--port",
            type=int,
            help="The port used to communicate with Openplanet",
        )
        comm_group.add_argument(
            "-op",
            "--openplanet",
            choices=DEFAULT_PORTS.keys(),
            help="Alternative to entering port number. Will use the default port for that game.",
        )
        sub_input.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Enable verbose logging for debugging Remote Build to Openplanet communication",
        )
        sub_input.description = "Specify at one of [--port, --openplanet] to enable communication with the Remote Build plugin running in the game."

    sub_unload = subparser.add_parser("unload", help="Unload a plugin")
    sub_unload.set_defaults(func=unload)
    common_args(sub_unload)

    sub_load = subparser.add_parser("load", help="Load a plugin")
    sub_load.set_defaults(func=load)
    sub_load.add_argument(
        "plugin_type",
        choices=["folder", "zip"],
        help="The type of plugin source to load from.",
    )
    common_args(sub_load)
    sub_load.add_argument(
        "--plugin_src",
        choices=["user", "app"],
        default="user",
        help='The source location to load plugin from where "user" is the C:/Users/User/OpenplanetX/Plugins folder and "app" is the Openplanet/Plugins folder in the game directory. Default is "user" if unspecified.',
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR)
    args.func(args)
