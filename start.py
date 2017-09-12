import utils as utils
from multiprocessing.dummy import Pool as ThreadPool
from Monitor import Monitor


def start():
    config = utils.load_config()
    logger = utils.get_logger()
    logger.info('程序启动')
    pool = ThreadPool(16)
    for room_url in config['ROOM_URLS']:
        m = Monitor(room_url)
        pool.apply_async(m.run)
    pool.close()
    try:
        pool.join()
    except KeyboardInterrupt:
        logger.warning('用户中断')


if __name__ == '__main__':
    start()
