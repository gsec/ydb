""" Settings for ydb <gsec 2017>
"""

import logging
from os import environ, makedirs
from os.path import join, dirname, abspath, exists
import yaml

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DOWNLOAD_PATH = join(environ["HOME"], "vid")
CFG_PATH = join(environ["XDG_CONFIG_HOME"], "ydb")
ARCHIVE = join(CFG_PATH, "archive.id")

STREAM_DUMP = environ.get("STREAM_DUMP", join(DOWNLOAD_PATH, "stream_dump"))

VIDEO_BLANK = """
#COMMAND_PLACEHOLDER:
  #extra: [--match-title, <words_to_match>]
  #length: <max-download-length>
  #path: rel_path/to/folder
  #url: <url-to-user> or <url-to-playlist>
"""

STREAM_BLANK = """
#<NAME>:
  #<URL>
"""

MAPPINGS = {
    "video": {"name": "video_list.yaml", "blank": VIDEO_BLANK,},
    "stream": {"name": "stream_list.yaml", "blank": STREAM_BLANK,},
}


def get_list(choice):
    try:
        dic = MAPPINGS[choice]
        path = join(CFG_PATH, dic["name"])

        with open(path, "r") as handler:
            loaded = yaml.safe_load(handler)
        return loaded
    except FileNotFoundError:
        if not exists(CFG_PATH):
            makedirs(CFG_PATH)
        with open(path, "x") as handler:
            handler.write(dic["blank"])
        logger.info(f"`{dic['name']}` created. Please add urls to start.")
    except KeyError as e:
        logger.error(f"Unknown choice:\n{e}\nPlease choose from {MAPPINGS.keys()}")
