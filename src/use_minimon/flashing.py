"""This is a entrypoint to instance a Reponder class"""
import argparse
import logging
import sys
import time
from typing import List

from use_minimon.responder import Responder


logger = logging.getLogger("Flashing")


def setup_logging(level):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)


def get_parser() -> argparse.ArgumentParser:
    description = (
        "\n"
        "Sending answers and a file to MiniMonitor.\n"
        "\n"
    )
    available_partitions = \
        Responder(target='starter-kit-cr', port='loop://').get_available_partitions()
    epilog = (
        "\n"
        f"Available partition NAMEs: {available_partitions}"
        "\n"
    )
    parser = argparse.ArgumentParser(
        usage='%(prog)s [OPTIONS] [[NAME FILE] ...]',
        description=description,
        epilog=epilog)
    parser.add_argument("-p", "--port", dest="port", default="/dev/ttyUSB0",
                        help="Specify a serial port")
    parser.add_argument('-s', '--show-partitions', action='store_true',
                        help='Show information of available partitions')
    parser.add_argument("paths", metavar="NAME FILE", nargs='*',
                        help="A pair of partition name and file")

    return parser


def main(argv: List[str] = sys.argv[1:]) -> int:
    setup_logging(logging.DEBUG)

    # TODO: check the DIP switches before flashing

    parser = get_parser()
    _args = parser.parse_args(argv)
    args = vars(_args)

    responder = Responder(target="starter-kit-cr", port=str(args.get("port")))

    if args.get('show_partitions', False):
        responder.show_partitions()
        sys.exit(0)

    paths = args.get('paths', [])
    try:
        for name, path in zip(paths[::2], paths[1::2]):
            responder.send_file(name, path)
            # FIXME: If writing binaries continuously, wait until MiniMonitor writes it.
            if len(paths) > 2:
                time.sleep(5)
    except ValueError as err:
        logger.error(err)
        sys.exit(1)

    return 0
