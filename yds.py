import os
import time
import sys
import logging
import subprocess
import argparse
from multiprocessing.dummy import Pool  # dummy makes it threads

from settings import STREAM_DUMP, SL, STREAMLIST

logger = logging.getLogger('ydb_stream')
logging.basicConfig(level=logging.INFO)

SEP = '_'
RETRY_TIME = 100
PAD_SIZE = 2
F_EXT = '.mp4'


def process(args):
    output, link = args
    mpv_cmd = ["mpv", "--no-resume-playback", "--stream-dump={}".format(output), "-"]
    ydl_cmd = ["youtube-dl", "--output", "-"]
    ydl_cmd.append(link)

    yds = subprocess.Popen(ydl_cmd, stdout=subprocess.PIPE, shell=False)
    writeout = subprocess.Popen(mpv_cmd, stdin=yds.stdout, shell=False)
    writeout.communicate()


def name_rotator(ident):
    flist = os.listdir(STREAM_DUMP)

    matches = [f for f in flist if f.startswith(ident)]
    try:
        last_file = sorted(matches)[-1]
        file_head = last_file.rsplit('.')[0]
        lf_size = os.stat(os.path.join(STREAM_DUMP, last_file)).st_size
        num = int(file_head[len(ident + SEP):])

        if lf_size:
            num += 1

    except (FileNotFoundError, IndexError):
        num = 1

    NUM = str(num).zfill(PAD_SIZE)
    dump_file = ident + SEP + NUM + F_EXT
    output = os.path.join(STREAM_DUMP, dump_file)
    return output


def stream_all(streamlist):
    try:
        while True:
            pool = Pool()
            args = ((name_rotator(ident), link) for ident, link in streamlist.items())

            pool.map(process, args)
            pool.close()

            time.sleep(RETRY_TIME)
    except KeyboardInterrupt:
        sys.exit("\nExiting for you sir...!")


def main():
    parser = argparse.ArgumentParser(prog='yds')
    parser.add_argument('elements', nargs=argparse.REMAINDER,
                        help="List of streams captured simultaneously.")
    parser.add_argument('-l', '--list', action='store_true')
    args = parser.parse_args()

    if args.list:
        print("Possible choices:")
        for k in SL.keys():
            print("(*)\t", k)
        sys.exit()

    if args.elements:
        try:
            stream_dict = {k: SL[k] for k in args.elements}
        except KeyError as e:
            sys.exit("Requested Stream <{}> not found.\n"
                     "You can show available entries with the `--list` argument\n"
                     "or add new ones manually to <{}>".format(e, STREAMLIST))
    else:
        stream_dict = SL
    logger.info(" Capturing: {}\n".format(list(stream_dict.keys())))
    stream_all(stream_dict)


if __name__ == '__main__':
    main()
