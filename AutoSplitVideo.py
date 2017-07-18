import os
import sys

from pymediainfo import MediaInfo


# 一小时1part，最后1part小于10min不切分
def cut_video(input_file):
    video = MediaInfo.parse(input_file)
    video_duration = video.tracks[0].duration
    hour = int(video_duration / 1000 / 60 // 60)
    minute = int(video_duration / 1000 / 60 % 60)
    part = hour if minute < 10 else hour + 1
    for i in range(0, part):
        part_index = i + 1
        ffmpeg_command = 'ffmpeg -ss %(start)d:00:00 -i "%(input)s" -c copy %(end)s "%(out)s"'
        ffmpeg_opts = {
            'start': i,
            'input': input_file,
            'end': '' if part == hour and i == part - 1 else '-t 1:00:00',
            'out': os.path.splitext(input_file)[0] + '_part' + str(part_index) + '.mp4'
        }
        os.system(ffmpeg_command % ffmpeg_opts)
        pass


if __name__ == '__main__':
    if len(sys.argv[1:]) == 0:
        print("请至少输入一个文件")
    for file in sys.argv[1:]:
        cut_video(file)
