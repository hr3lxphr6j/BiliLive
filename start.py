import utils as utils
from multiprocessing.dummy import Pool as ThreadPool
from Monitor import Monitor
import sys


def start():
    if len(sys.argv[1:]) == 0:
        config = utils.load_config(sys.argv[1])
    else:
        config = utils.load_config()
    logger = utils.get_logger()
    logger.info('程序启动')
    room_count = len(config['ROOM_URLS'])
    if room_count == 0:
        logger.info('没有发现直播间，程序退出！')
        exit(0)
    pool = ThreadPool(room_count)
    for room_url in config['ROOM_URLS']:
        m = Monitor(room_url)
        pool.apply_async(m.run)
    pool.close()
    try:
        pool.join()
    except KeyboardInterrupt:
        logger.warning('用户中断')
        exit(1)


if __name__ == '__main__':
    start()
