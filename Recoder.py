import os
import subprocess

import utils as utils


# 录制
class Recoder(object):
    def __init__(self, live_url, output_path, filename):
        """
        :param live_url: 直播地址
        :param output_path: 输出路径
        :param filename: 输出文件名
        """
        self.ffmpeg_command = 'ffmpeg' \
                              ' -re -y -loglevel -8 -i' \
                              ' "%(live_url)s"' \
                              ' -c copy -bsf:a aac_adtstoasc' \
                              ' "%(output)s"'
        self.ffmpeg_opts = {
            'live_url': live_url,
            'output': os.path.join(output_path, filename)
        }

    @utils.time_cal
    def start_recoding(self):
        # os.system(self.ffmpeg_command % self.ffmpeg_opts)
        child = subprocess.Popen(self.ffmpeg_command % self.ffmpeg_opts, shell=True,
                                 stdout=os.open(os.devnull, os.O_RDWR),
                                 stderr=os.open(os.devnull, os.O_RDWR))
        child.wait()
