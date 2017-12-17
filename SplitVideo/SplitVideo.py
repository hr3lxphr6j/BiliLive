import os
import re
import sys
import json
import math
import yaml
import logging
import datetime
import functools
import subprocess

from zlib import crc32
from hashlib import sha1, md5
from multiprocessing.dummy import Pool

logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s', level=logging.INFO)


def parse_config(filename: str) -> dict:
    """
    解析YAML
    :param filename: yaml文件路径
    :return: dict
    """
    with open(filename, encoding='utf8') as f:
        return yaml.load(f)


def file_list_to_byte(path: str, file_list: list) -> bytes:
    """
    将文件列表转为ffmpeg的Virtual Concatenation Script(https://www.ffmpeg.org/ffmpeg-all.html#concat-1)
    :param path: 文件所在路径
    :param file_list: 文件集合
    :return: Virtual Concatenation Script
    """
    b = b''
    for f in file_list:
        b += ("file '%s'\n" % (os.path.join(path, f))).encode()
    return b


def get_sha1_hex(filename: str, egg_pain: bool = False) -> bytes:
    """
    获取文件（名）的sha1值
    :param filename: 文件url
    :param egg_pain: 使用文件的SHA1值，而不是文件名的(神经病)
    :return: SHA1
    """
    sha1_obj = sha1()
    if egg_pain:
        with open(filename, 'rb') as f:
            for l in f:
                sha1_obj.update(l)
    else:
        sha1_obj.update(filename.encode())
    return sha1_obj.digest()


def get_crc32(filename: str, egg_pain: bool = False) -> int:
    """
    获取文件（名）的CRC32值
    :param filename: 文件url
    :param egg_pain: 使用文件的CRC32值，而不是文件名的(神经病)
    :return: CRC32
    """
    crc = 0
    if egg_pain:
        with open(filename, 'rb') as f:
            for l in f:
                crc = crc32(l, crc)
    else:
        crc = crc32(filename.encode())
    return crc


def get_file_list_md5(path: str, file_list: list) -> str:
    """
    根据文件集合计算md5，用于为重封装的文件命名
    计算方式：md5( sha1(文件01) + sha1(文件02) + ... + sha1(文件n) )
    :param path: 文件所在路径
    :param file_list: 文件集合
    :return: md5 string
    """
    sha1s = b''
    for f in file_list:
        sha1s += get_sha1_hex(os.path.join(path, f))
    return md5(sha1s).hexdigest()


def is_remuxed_file_exist(path: str, file_list: list) -> str:
    """
    查找已存在的重封装文件，如果存在，返回路径
    :param path: 文件所在路径
    :param file_list: 文件集合
    :return: 重封装文件url
    """
    md5_name = get_file_list_md5(path, file_list)
    for rt, dirs, files in os.walk(path):
        for file in files:
            if re.match('%s\[\w{8}\]\.mp4' % md5_name, file):
                return os.path.join(path, file)


def merge_video_to_file(path: str, file_list: list) -> str:
    """
    重封装视频
    重封装结束后，会在文件名后添加一个CRC32字符串，用来标记其完整性
    :param path: 文件所在路径
    :param file_list: 文件集合
    :return: 重封装文件url
    """
    md5_name = get_file_list_md5(path, file_list)
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
        stderr=subprocess.PIPE)
    child.communicate(file_list_to_byte(path, file_list))
    crc = get_crc32(remux_file_name)
    res_file_name = os.path.join(path, md5_name + ('[%x]' % crc) + '.mp4')
    os.rename(remux_file_name, res_file_name)
    return res_file_name


def str2time(s: str) -> datetime.timedelta:
    """
    将字符串表示的时间转为timedelta对象
    :param s: 字符串表示的时间
    :return: timedelta obj
    """
    t = s.split(':')
    return datetime.timedelta(hours=int(t[0]), minutes=int(t[1]), seconds=int(t[2]))


def get_video_duration(filename: str) -> datetime.timedelta:
    """
    获取视频长度
    :param filename: 文件url
    :return: timedelta obj
    """
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


def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
        logging.info('Splitting Video To\t%s' % args[1] or kw['output_file'])
        t = datetime.datetime.now()
        func(*args, **kw)
        logging.info(
            'Split To\t%s\tTime Spent\t%s' % (args[1] or kw['output_file'], str(datetime.datetime.now() - t)))

    return wrapper


@log
def cut_video(input_file: str, output_file: str, start_time: str, end_time: str, is_concat: bool = True):
    """
    分割视频
    :param input_file: 输入文件
    :param output_file: 输出文件
    :param start_time: 起始时间
    :param end_time: 结束时间
    :param is_concat: 输入是否为Virtual Concatenation Script
    :return:
    """
    if is_concat:
        child = subprocess.Popen(
            ['ffmpeg',
             '-y',
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
             '-i', input_file,
             '-ss', start_time,
             '-to', end_time,
             '-c', 'copy',
             output_file],
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        child.communicate()


@log
def cut_video_and_rip(input_file: str, output_file: str, start_time: str, end_time: str, is_concat: bool = True):
    """
    分割并压制视频
    :param input_file: 输入文件
    :param output_file: 输出文件
    :param start_time: 起始时间
    :param end_time: 结束时间
    :param is_concat: 输入是否为Virtual Concatenation Script
    :return:
    """
    log_file_prefix = md5(output_file.encode()).hexdigest()
    if is_concat:
        pass1 = subprocess.Popen([
            'ffmpeg',
            '-y',
            '-protocol_whitelist', 'file,pipe',
            '-safe', '0',
            '-f', 'concat',
            '-i', '-',
            '-max_muxing_queue_size', '2048',
            '-ss', start_time,
            '-to', end_time,
            '-c:v', 'libx264',
            '-pass', '1',
            '-passlogfile', log_file_prefix,
            '-b:v', '1750k',
            '-an',
            '-f', 'mp4',
            '-'
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        pass1.communicate(input_file)
        pass2 = subprocess.Popen([
            'ffmpeg',
            '-y',
            '-protocol_whitelist', 'file,pipe',
            '-safe', '0',
            '-f', 'concat',
            '-i', '-',
            '-max_muxing_queue_size', '2048',
            '-ss', start_time,
            '-to', end_time,
            '-c:v', 'libx264',
            '-pass', '1',
            '-passlogfile', log_file_prefix,
            '-b:v', '1750k',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_file
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        pass2.communicate()
    else:
        pass1 = subprocess.Popen([
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-max_muxing_queue_size', '2048',
            '-ss', start_time,
            '-to', end_time,
            '-c:v', 'libx264',
            '-pass', '2',
            '-passlogfile', log_file_prefix,
            '-b:v', '1750k',
            '-an',
            '-f', 'mp4',
            '-'
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        pass1.communicate()
        pass2 = subprocess.Popen([
            'ffmpeg',
            '-y',
            '-protocol_whitelist', 'file,pipe',
            '-safe', '0',
            '-f', 'concat',
            '-i', '-',
            '-max_muxing_queue_size', '2048',
            '-ss', start_time,
            '-to', end_time,
            '-c:v', 'libx264',
            '-pass', '1',
            '-passlogfile', log_file_prefix,
            '-b:v', '1750k',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_file
        ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
        pass2.communicate()

    pass


def get_abs_time(time: datetime.timedelta, part: int, time_line: list, is_end: bool = False) -> datetime.timedelta:
    """
    将相对于每个文件的时间点转化为相对于所有文件合并后总时长中对应的时间点
    :param time: 输入时间
    :param part: 所处文件
    :param time_line: 时间线
    :param is_end: 是否为结尾时间
    :return: timedelta obj
    """
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
            return min(time + time_line[part], time_line[part + 1])


def limit_part_length(storyboard: list, part_time: datetime.timedelta, greedy_percentage: float) -> list:
    """
    限制每一部分时长不超过规定值
    :param storyboard: 故事板
    :param part_time: 每段的最大时间长度
    :param greedy_percentage: 视频长度对part_time取余数(最后1Part长度)，如果时长不超过part_time * greedy_percentage则不独立分段
    :return: 新的故事板
    """
    new_storyboard = []
    for part in storyboard:
        if part['duration'] >= (part_time * (1 + greedy_percentage)):
            duration = part['duration']
            new_part = []
            for i in range(int(math.ceil(duration / part_time))):
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
                new_part[-2]['duration'] += new_part[-1]['duration']
                new_part.pop()
            new_storyboard.extend(new_part)
        else:
            new_storyboard.append(part)
    return new_storyboard


def main():
    global config, global_config, projects

    if len(sys.argv[1:]) == 0:
        logging.error('One YAML Config File Should Be Input!')

    config_file = sys.argv[1]

    try:
        config = parse_config(config_file)
    except Exception:
        logging.error('Can Not Parse Config File: %s' % config_file)
        exit(1)

    try:
        global_config = config['GlobalConfig']
        projects = config['Projects']
    except KeyError as e:
        logging.error('Config File Error, "%s" Node Did Not Exist!' % e)

    # 是否限制Part长度
    is_limit_part_length = global_config.get('LimitPartLength', True)
    # 每段视频最大长度
    part_time = str2time(global_config.get('PartTime', '1:00:00'))
    # 视频长度对part_time取余数(最后1Part长度)，如果时长不超过part_time * greedy_percentage则不独立分段
    greedy_percentage = global_config.get('GreedyPercentage', 0.2)
    # 是否先重封装为Mp4，提供索引加快分段速度
    is_remux = global_config.get('RemuxToMp4', False)
    # 并行处理数量(线程池大小)
    thread_num = global_config.get('ProcessThread', os.cpu_count() or 1)

    # 打印全局配置信息
    logging.info('+' * 40)
    logging.info('Global Config Info:')
    logging.info('LimitPartLength: %s' % is_limit_part_length)
    if is_limit_part_length:
        logging.info('PartTime: %s' % str(part_time))
        logging.info('GreedyPercentage: %0.02f' % greedy_percentage)
    logging.info('RemuxToMp4: %s' % is_remux)
    logging.info('ProcessThread: %d' % thread_num)
    logging.info('+' * 40 + '\n')

    # 初始化线程池
    pool = Pool(thread_num)
    # 记录重封装文件
    remux_file_names = []

    for project in projects:

        logging.info('Start Process Project %d' % (config['Projects'].index(project) + 1))

        # 文件所在路径
        path = project['Path']
        # 视频文件集合
        file_list = project['Files']
        # 分段集合
        parts = project['Parts']

        # 记录每个视频文件在总长度的起始位置，末尾为总视频长度
        time_line = [datetime.timedelta()]
        for file in file_list:
            duration = get_video_duration(os.path.join(path, file))
            time_line.append(time_line[-1] + duration)
            logging.info('File: %s, Duration: %s' % (file, str(duration)))
        logging.info('Total Video Duration: %s' % str(time_line[-1]))

        # 重封装文件名
        remux_file_name = None

        # 处理重封装逻辑
        if is_remux:
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
            remux_file_names.append(remux_file_name)

        # 故事板，记录经过解析的分段信息
        storyboard = []

        # 解析分段信息
        if len(parts) == 0:
            logging.error('No Part Info Defined!')
            exit(1)
        for part in parts:
            if part.get('StartTime'):
                start = get_abs_time(str2time(part['StartTime'][0]), part['StartTime'][1], time_line)
            elif len(storyboard) > 0:
                start = storyboard[-1]['end']
            else:
                start = datetime.timedelta()
            end = get_abs_time(str2time(part['EndTime'][0]), part['EndTime'][1], time_line, True)
            if end - start <= datetime.timedelta():
                logging.error('Part No: %d Was Wrong, Skipped!')
                continue
            storyboard.append({
                'name': part['Name'],
                'start': start,
                'end': end,
                'duration': end - start
            })

        # 处理分段长度限制逻辑
        if is_limit_part_length:
            storyboard = limit_part_length(storyboard, part_time, greedy_percentage)

        # 打印分段信息
        logging.info('+' * 40)
        logging.info('Project No: %02d, Part Info:' % (projects.index(project) + 1))
        for part in storyboard:
            logging.info('Part No\t%02d' % (storyboard.index(part) + 1))
            logging.info('PartName\t%s' % part['name'])
            logging.info('StartTime\t%s' % str(part['start']))
            logging.info('EndTime\t%s' % str(part['end']))
            logging.info('Duration\t%s' % str(part['duration']))
            if part != storyboard[-1]:
                logging.info('=' * 35)
        logging.info('+' * 40)

        # 向线程池中异步提交任务
        for part in storyboard:
            pool.apply_async(cut_video, (
                remux_file_name if is_remux else file_list_to_byte(path, file_list),
                os.path.join(path, '%02d.%s.mp4' % (storyboard.index(part) + 1, part['name'])),
                str(part['start']),
                str(part['end']),
                not is_remux
            ))

    # 关闭线程池，并等待其中所有任务完成
    pool.close()
    pool.join()
    logging.info('All Project Completed!')
    for f in remux_file_names:
        os.remove(f)


if __name__ == '__main__':
    main()
