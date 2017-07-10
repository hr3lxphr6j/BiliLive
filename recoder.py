import os

import utils as utils


class Recoder(object):
    def __init__(self, live_urls, room_title):
        self.config = utils.load_config()
        self.ffmpeg_opts = {
            'live_url': live_urls[self.config['URL_SELECT']],
            'output_file_name': '%s%s %s.%s' % (
                self.config['OUTPUT_DIR'], utils.get_current_time(), room_title,
                self.config['OUTPUT_FILE_EXT'])
        }
        self.ffmpeg_command = 'ffmpeg -y -i "%(live_url)s" -c copy "%(output_file_name)s"'

    def start_recoding(self):
        os.system(self.ffmpeg_command % self.ffmpeg_opts)
