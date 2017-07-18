import logging

import utils as utils
from Monitor import Monitor

config = utils.load_config()
app_name = 'BiliBiliLiveRec'
version = "2.0.1"


def start():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('程序版本: %s' % version)
    logging.info('直播间状态查询间隔: %d 秒' % config['POLLING_INTERVAL'])
    logging.info('开始录制延时: %d 秒' % config['LAZY_TIME'])
    logging.info('输出目录: %s' % config['OUTPUT_DIR'])
    logging.info('封装格式: %s' % config['OUTPUT_FILE_EXT'])
    for room_id in config['ROOM_IDS']:
        p = Monitor(room_id)
        p.start()


if __name__ == '__main__':
    start()
