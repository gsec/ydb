""" Settings for ydb <gsec 2017>
"""

import logging
import yaml
from os import environ, makedirs
from os.path import join, dirname, abspath

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DOWNLOAD_PATH = join(environ['HOME'], 'vid')
CFG_PATH = join(dirname(abspath(__file__)), 'cfg')
ARCHIVE = join(CFG_PATH, "archive.id")

VIDEOLIST = "video_list.yaml"
STREAMLIST = "stream_list.yaml"

try:
    makedirs(CFG_PATH)
except FileExistsError:
    pass

try:
    STREAM_DUMP = environ['STREAM_DUMP']
except KeyError:
    STREAM_DUMP = join(DOWNLOAD_PATH, 'stream_dump')
    logger.info("STREAM_DUMP variable not found.\n Using default:{}".format(STREAM_DUMP))

VLIST_BLANK = """
#COMMAND_PLACEHOLDER:
  #extra: [--match-title, <words_to_match>]
  #length: <max-download-length>
  #path: rel_path/to/folder
  #url: <url-to-user> or <url-to-playlist>
"""

SLIST_BLANK = """
#<NAME>:
  #<URL>
"""


def open_with_default(fname, blank):
    fpath = join(CFG_PATH, fname)
    try:
        with open(fpath, 'r') as handler:
            loaded = yaml.safe_load(handler)
        return loaded
    except FileNotFoundError:
        with open(fpath, 'x') as handler:
            handler.write(blank)
        logger.info("`{}` created. Please add urls to start.".format(VIDEOLIST))
    except Exception as err:
        logger.warning("We got a problem with the list {}: {}\n"
                       "List should be in {}".format(fname, err, str(CFG_PATH)))


VL = open_with_default(VIDEOLIST, VLIST_BLANK)
SL = open_with_default(STREAMLIST, SLIST_BLANK)
