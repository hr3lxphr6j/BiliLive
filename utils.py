import json
import logging
import time
import os
from threading import Lock

__config = None
__logger = None
mutex = Lock()


def load_config(file=os.path.join(os.environ['HOME'], '.bililive', 'config.json')):
    """
    加载配置
    :param file: 配置文件路径，默认位置为 $HOME/.bililive/config.json
    :return:
    """
    global __config
    if __config:
        return __config
    else:
        mutex.acquire()
        if __config:
            mutex.release()
        else:
            try:
                with open(file, 'r') as config:
                    __config = json.load(config)
            except Exception:
                logging.error('配置文件加载错误！')
                exit(1)
            # 判定输出路径是否为目录且是否存在
            if not os.path.isdir(__config['OUTPUT_DIR']):
                logging.warning('输出文件路径不合法')
                exit(1)
            # log文件不存在则创建
            if not os.path.isfile(os.path.join(__config['OUTPUT_DIR'], 'live.log')):
                try:
                    os.system('touch ' + os.path.join(__config['OUTPUT_DIR'], 'live.log'))
                except Exception:
                    logging.warning('log文件创建失败！')
                    exit(1)
            # 直播间url简单去重
            __config['ROOM_URLS'] = list(set(__config['ROOM_URLS']))
            mutex.release()
        return __config


def get_logger():
    load_config()
    global __logger
    if __logger:
        return __logger
    else:
        __logger = logging.getLogger()
        __logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(os.path.join(__config['OUTPUT_DIR'], 'live.log'), 'a')
        file_handler.setLevel(logging.INFO)
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        __logger.addHandler(file_handler)
        __logger.addHandler(stream_handler)
        return __logger


def time_cal(func):
    """
    计时装饰器
    :param func:
    :return: 函数执行时间
    """

    def _time_cal(*args, **kw):
        start_time = time.time()
        func(*args, **kw)
        end_time = time.time()
        return end_time - start_time

    return _time_cal


def get_current_time():
    """
    :return: 返回当前时间
    """
    return time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))
