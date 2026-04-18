import logging
import os
import shutil
import argparse
import time
from .api import RemoteBuildAPI
from .log import PLUGIN_ID

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_PORTS = {
    "OpenplanetNext": 30000,
    "Openplanet4": 30001,
    "OpenplanetTurbo": 30002,
    "OpenplanetUnited": 30003
}


def get_port(args) -> int:
    if args.port is not None:
        return args.port
    else:
        return DEFAULT_PORTS.get(args.openplanet, 0)

def get_host(args) -> str:
    if args.host is not None:
        return args.host
    else:
        return "127.0.0.1"


def unload(args) -> None:
    api = RemoteBuildAPI(get_port(args), get_host(args), op_dir=args.op_dir)
    unloaded = api.unload_plugin(args.plugin_id)
    if unloaded:
        logger.info('Commanded unload for plugin with ID "%s"' % (args.plugin_id,))
    else:
        logger.error(
            'Problem commanding unload for plugin with ID "%s"' % (args.plugin_id,)
        )


def load(args) -> None:
    global PLUGIN_ID
    PLUGIN_ID = args.plugin_id
    print(f"Set PLUGIN_ID to {PLUGIN_ID}")
    api = RemoteBuildAPI(get_port(args), host=get_host(args), op_dir=args.op_dir)
    loaded = api.load_plugin(
        args.plugin_id, plugin_src=args.plugin_src, plugin_type=args.plugin_type,
        log_done_limit=args.log_done_limit, log_check_interval=args.log_check_interval
    )
    if loaded:
        logger.info('Commanded load for plugin with ID "%s"' % (args.plugin_id,))
    else:
        logger.error(
            'Problem commanding load for plugin with ID "%s"' % (args.plugin_id,)
        )

def cmd_watch(args) -> None:
    global PLUGIN_ID
    PLUGIN_ID = args.plugin_id
    api = RemoteBuildAPI(get_port(args), host=get_host(args), op_dir=args.op_dir)
    with api.op_log as opl:
        opl.seek_back(args.back)
        while not opl.check_if_log_done(args.log_done_limit):
            time.sleep(args.log_check_interval)



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
        # sub_input.add_argument(
        #     "-l", "--logs-only", action="store_true",
        #     help="Don't reload the plugin, but wait for logs from a reload.",
        # )
        sub_input.add_argument(
            "-d", "--op-dir", type=str,
            help="Specify the directory to look for Openplanet.log (auto-detected by default)",
        )
        sub_input.add_argument(
            "--host", type=str,
            help="The host to connect to (IP or hostname)",
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

    sub_watch = subparser.add_parser("getlogs", help="Get compilation logs")
    sub_watch.set_defaults(func=cmd_watch)
    common_args(sub_watch)
    sub_watch.add_argument(
        "-b", "--back", type=int, default=0,
        help="Go back this many lines in the log file when starting to watch.",
    )

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

    for sub in [sub_load, sub_watch]:
        sub.add_argument(
            "-l", "--log-done-limit", type=int, default=3,
            help="After logs begin, the number of consecutive checks that find no relevant updates to wait for before stopping.",
        )
        sub.add_argument(
            "-i", "--log-check-interval", type=float, default=1.0,
            help="The interval in seconds to wait between checks for new log messages.",
        )

    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.ERROR)
    args.func(args)

