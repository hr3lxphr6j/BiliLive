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
        self.ffmpeg_command = [
            'ffmpeg',
            '-y', '-re',
            '-i', live_url,
            '-c', 'copy',
            '-bsf:a', 'aac_adtstoasc',
            os.path.join(output_path, filename)
        ]

    @utils.time_cal
    def start_recoding(self):
        child = subprocess.Popen(self.ffmpeg_command,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        child.communicate()
