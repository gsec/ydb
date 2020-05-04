"""
ydb --  a thin API to manage automated downloads of youtube channels.

`ydb` is licensed under the GPLv3. See LICENSE file for more details

Copyright(2017)  ::  Guilherme Stein  ::  <o0v0o.ix@gmail.com>


The main idea is that you just have your favorite user/urls/playlists etc. in a nice yaml
file and can check/download the newest items easy into seperate folders creating an
independency buffer from connectivity.
"""

import os
import sys
import logging
import argparse
import subprocess
from os.path import join
from collections import OrderedDict as OD

from settings import VL, DOWNLOAD_PATH, ARCHIVE

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger("ydb_main")


def match_channels(ident, **kwargs):
    """ Checks for identifiers in the dict and overwrites any kwargs that are explicitly
    passed. If no identifiers are given, takes all in `DIC_DEFS` with only one letter,
    i.e. the main ones.
    """

    qwargs = {k: v for k, v in kwargs.items() if v}

    for each in identifier(ident):
        myDic = VL[each]
        myDic.update(qwargs)
        logger.debug("myDic: {}".format(myDic))
        ydl_caller(**myDic)


def identifier(ident):
    msg = "For available entries see `ydb --list`\n"

    if not ident:
        ident = list(x for x in VL.keys() if len(x) == 1)
    elif type(ident) is str:
        ident = [ident]
    for entry in ident:
        if entry not in VL:
            raise KeyError("< {} > not found in video list.\n".format(entry) + msg)
    return ident


def ydl_caller(
    url=None,
    start=None,
    length=None,
    path=None,
    restrict=False,
    extra=[],
    nomtime=False,
):
    """ Calls youtube-dl with optional parameters and url shortcuts.
    """
    if not path:
        path = DOWNLOAD_PATH
    elif path.startswith("/"):
        pass
    else:
        path = join(DOWNLOAD_PATH, path)

    extra.extend(["-f", "bestvideo[ext!=webm]+bestaudio[ext!=webm]/best[ext!=webm]"])

    if nomtime:
        extra.extend(["--no-mtime"])
    if restrict:
        extra.extend(["-r", "1M"])

    if not start:
        start = 1

    if not length:
        length = 3

    end = start + length - 1
    fpath = path.rstrip("/") + "/" + "%(title)s.%(ext)s"

    cmd = ["youtube-dl"]
    cmd.extend(["-o", fpath])
    cmd.extend(["--playlist-start", str(start)])
    cmd.extend(["--playlist-end", str(end)])
    cmd.extend(["--download-archive", ARCHIVE])
    cmd.extend(extra)
    cmd.extend([url])

    try:
        subprocess.call(cmd)
    except KeyboardInterrupt:
        sys.exit("\nCancelled due to user request.")


def clear(ident):
    """ Delete video files, depending on the length given in the video list.
    """
    entries = ((VL[entry]["path"], VL[entry]["length"]) for entry in identifier(ident))

    del_files = []
    for entry in entries:
        try:
            del_files.extend(mtime_truncate(*entry))
        except FileNotFoundError:
            logger.info("Path does not exist: {}\nSkipping.".format(entry))

    if not del_files:
        sys.exit("Nothing to be removed.")

    print(
        "The following files are going to be deleted:",
        "\n\t".join(del_files),
        sep="\n\t",
    )

    if input("\nAre you sure? [Y/n] ") in "yY":
        print("Deleting ...")
        for fname in del_files:
            os.remove(fname)
    else:
        logger.info("Aborting!")


def attribute_dict(path, stat_key="st_mtime", reverse=True):
    files = (join(path, fname) for fname in os.listdir(path))

    sortdict = OD(
        sorted(
            ((os.stat(f).__getattribute__(stat_key), f) for f in files), reverse=reverse
        )
    )
    logger.debug("orderedDict: {}".format(sortdict))

    return sortdict


def mtime_truncate(path, length):
    full_path = join(DOWNLOAD_PATH, path)

    return list(attribute_dict(full_path).values())[length + 1 :]


def show_list():
    from pprint import PrettyPrinter

    PrettyPrinter(indent=4).pprint(VL)


def main():
    parser = argparse.ArgumentParser(prog="ydb")

    parser.add_argument(
        "ident",
        type=str,
        nargs="*",
        default=None,
        help="Selects entry based on the identifier in " "`video_list.yaml`",
    )
    parser.add_argument(
        "-s",
        "--start",
        type=int,
        nargs="?",
        default=None,
        help="Starting position of the download list.",
    )
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        nargs="?",
        default=None,
        help="Length of the download list.",
    )
    parser.add_argument(
        "-t", "--nomtime", action="store_true", help="Set access time to download time."
    )
    parser.add_argument(
        "-r", "--restrict", action="store_true", help="Restrict download speed to 1M."
    )
    parser.add_argument(
        "-c",
        "--clear",
        action="store_true",
        help="Clear latest video entries. Files are shown and "
        "optionally deleted after user confirmation.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Output complete listing of available entries",
    )

    args = parser.parse_args()

    if args.list:
        show_list()
    elif args.clear:
        clear(args.ident)
    else:
        match_channels(**vars(args))


if __name__ == "__main__":
    main()
