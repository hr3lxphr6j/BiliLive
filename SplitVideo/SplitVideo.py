import os
import sys
import json
import math
import yaml
import logging
import datetime
import subprocess

from zlib import crc32
from hashlib import sha1, md5
from multiprocessing.dummy import Pool as ThreadPool

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


def parse_config(filename):
    try:
        with open(filename, encoding='utf8') as f:
            return yaml.load(f)
    except Exception as e:
        logging.error(e)
        exit(1)


def file_list_to_byte(path, file_list):
    b = b''
    for f in file_list:
        b += ("file '%s'\n" % (os.path.join(path, f))).encode()
    return b


def get_sha1_hex(filename):
    sha1_obj = sha1()
    with open(filename, 'rb') as f:
        for l in f:
            sha1_obj.update(l)
    return sha1_obj.digest()


def get_crc32(filename):
    crc = 0
    with open(filename, 'rb') as f:
        for l in f:
            crc = crc32(l, crc)
    return crc


def get_remux_file_name(path, file_list):
    sha1s = b''
    for f in file_list:
        sha1s += get_sha1_hex(os.path.join(path, f))
    return md5(sha1s).hexdigest()


def is_remuxed_file_exist(path, file_list):
    md5_name = get_remux_file_name(path, file_list)
    for rt, dirs, files in os.walk(path):
        for file in files:
            if md5_name in file:
                return os.path.join(path, file)


def merge_video_to_file(path, file_list):
    md5_name = get_remux_file_name(path, file_list)
    remux_file_name = os.path.join(path, md5_name + '.mp4')
    child = subprocess.Popen(
        ['ffmpeg',
         '-y',
         '-hide_banner', '-nostats',
         '-protocol_whitelist', 'file,pipe',
         '-safe', '0',
         '-f', 'concat',
         '-i', '-',
         '-c', 'copy',
         remux_file_name],
        stdin=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    child.communicate(file_list_to_byte(path, file_list))
    crc = get_crc32(remux_file_name)
    res_file_name = os.path.join(path, md5_name + ('[%x]' % crc) + '.mp4')
    os.rename(remux_file_name, res_file_name)
    return res_file_name


def str2time(s):
    t = s.split(':')
    return datetime.timedelta(hours=int(t[0]), minutes=int(t[1]), seconds=int(t[2]))


def get_video_duration(filename):
    child = subprocess.Popen(
        ['ffprobe',
         '-loglevel', '-8',
         '-print_format', 'json',
         '-show_format',
         filename],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)
    out, _ = child.communicate()
    return datetime.timedelta(seconds=float(json.loads(out)['format']['duration']))


def cut_video(input_file, output_file, start_time, end_time, is_concat=True):
    logging.info('Splitting To: %s' % output_file)
    if is_concat:
        child = subprocess.Popen(
            ['ffmpeg',
             '-y',
             '-hide_banner', '-nostats',
             '-protocol_whitelist', 'file,pipe',
             '-safe', '0',
             '-f', 'concat',
             '-i', '-',
             '-ss', start_time,
             '-to', end_time,
             '-c', 'copy',
             output_file],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE)
        child.communicate(input_file)
    else:
        child = subprocess.Popen(
            ['ffmpeg',
             '-y',
             '-hide_banner', '-nostats',
             '-i', input_file,
             '-ss', start_time,
             '-to', end_time,
             '-c', 'copy',
             output_file],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        child.communicate()
    logging.info('Split Completed: %s' % output_file)


def get_abs_time(time, part, time_line, is_end=False):
    if not -1 <= part < len(time_line) - 1:
        logging.error('Part Index: %d Was Out Of Range!' % part)
        exit(1)
    if is_end and time == datetime.timedelta():
        if part == -1:
            return time_line[-1]
        else:
            return time_line[part + 1]
    else:
        if part == -1:
            return time
        else:
            return time + time_line[part]


def limit_part_length(storyboard, part_time, greedy_percentage):
    new_storyboard = []
    for part in storyboard:
        if part['duration'] >= part_time:
            duration = part['duration']
            new_part = []
            for i in range(int(math.ceil(part['duration'] / part_time))):
                start = new_part[-1]['end'] if len(new_part) != 0 else part['start']
                dur = min(duration, part_time)
                duration -= dur
                end = start + dur
                new_part.append({
                    'name': '%s_part%d' % (part['name'], i + 1),
                    'start': start,
                    'end': end,
                    'duration': dur
                })
            if new_part[-1]['duration'] <= part_time * greedy_percentage:
                new_part[-2]['end'] += new_part[-1]['duration']
                new_part.pop()
            new_storyboard.extend(new_part)
        else:
            new_storyboard.append(part)
    return new_storyboard


def main():
    if len(sys.argv[1:]) == 0:
        logging.error('One YAML Config File Should Be Input!')
    config = parse_config(sys.argv[1])
    thread_num = config['GlobalConfig']['ProcessThread']
    for proj in config['Projects']:
        logging.info('Start Process Project %d' % (config['Projects'].index(proj) + 1))
        path = proj['Path']
        file_list = proj['Files']
        parts = proj['Parts']
        video_durations = []
        time_line = [datetime.timedelta()]
        total_video_duration = datetime.timedelta()
        for file in file_list:
            duration = get_video_duration(os.path.join(path, file))
            logging.info('File: %s, Duration: %s' % (file, str(duration)))
            video_durations.append(duration)
            time_line.append(time_line[-1] + duration)
            total_video_duration += duration
        logging.info('Total Video Duration: %s' % str(total_video_duration))
        remux_file_name = None
        if config['GlobalConfig']['RemuxToMp4']:
            remux_file_name = is_remuxed_file_exist(path, file_list)
            if not remux_file_name:
                logging.info('No Remuxed File Found, Begin To Remux...')
                remux_file_name = merge_video_to_file(path, file_list)
                logging.info('Remux Completed, File Name: %s' % remux_file_name)
                logging.info('Do you Want Exit Now To Edit Part? [Y/n]')
                if not input().upper() == 'N':
                    exit(0)
            else:
                logging.info('Remuxed File Found, File Name: %s' % remux_file_name)
        if len(parts) == 0:
            logging.error('No Part Info Defined!')
            exit(1)
        storyboard = []
        for part in parts:
            start = get_abs_time(str2time(part['StartTime'][0]), part['StartTime'][1], time_line)
            end = get_abs_time(str2time(part['EndTime'][0]), part['EndTime'][1], time_line, True)
            storyboard.append({
                'name': part['Name'],
                'start': start,
                'end': end,
                'duration': end - start
            })
        if config['GlobalConfig']['LimitPartLength']:
            storyboard = limit_part_length(storyboard, str2time(config['GlobalConfig']['PartTime']),
                                           config['GlobalConfig']['GreedyPercentage'])
        logging.info('Part Info:')
        for part in storyboard:
            logging.info('=' * 40)
            logging.info('Part No: %d' % (storyboard.index(part) + 1))
            logging.info('PartName: %s' % part['name'])
            logging.info('StartTime: %s' % str(part['start']))
            logging.info('EndTime: %s' % str(part['end']))
            logging.info('Duration: %s' % str(part['duration']))
            logging.info('=' * 40)
        logging.info('Begin To Split Video, Process Thread Num: %d' % thread_num)
        pool = ThreadPool(thread_num)
        for part in storyboard:
            pool.apply_async(cut_video, (
                remux_file_name if config['GlobalConfig']['RemuxToMp4'] else file_list_to_byte(path, file_list),
                os.path.join(path, part['name'] + '.mp4'),
                str(part['start']),
                str(part['end']),
                not config['GlobalConfig']['RemuxToMp4']
            ))
        pool.close()
        pool.join()
        logging.info('Process Project %d Completed!' % (config['Projects'].index(proj) + 1))
    logging.info('All Project Completed!')


if __name__ == '__main__':
    main()
