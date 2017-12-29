import utils as utils
from multiprocessing.dummy import Pool as ThreadPool
from Monitor import Monitor
import sys


def start():
    if len(sys.argv[1:]) == 0:
        config = utils.load_config()
    else:
        config = utils.load_config(sys.argv[1])
    logger = utils.get_logger()
    logger.info('BiliLive Link Start!!!')
    room_count = len(config['ROOM_URLS'])
    if room_count == 0:
        logger.info('No Live Room Found，Exit Now!')
        exit(0)
    pool = ThreadPool(room_count)
    for room_url in config['ROOM_URLS']:
        m = Monitor(room_url)
        pool.apply_async(m.run)
    pool.close()
    try:
        pool.join()
    except KeyboardInterrupt:
        logger.warning('Rua!')
        exit(1)


if __name__ == '__main__':
    start()
