import time

import utils as utils
from api import LiveRoom
from recoder import Recoder

config = utils.load_config()
room_id = config['ROOM_IDS']
app_name = 'BiliBiliLiveRec'
version = "1.1"
room = LiveRoom(room_id)


def start():
    print('[%s]: 程序版本: %s' % (app_name, version))
    print('[%s]: 直播间ID: %d' % (app_name, room_id))
    print('[%s]: UP: %s' % (app_name, room.get_room_info()['ANCHOR_NICK_NAME']))
    print('[%s]: 直播间状态查询间隔: %d 秒' % (app_name, config['POLLING_INTERVAL']))
    print('[%s]: 开始录制延时: %d 秒' % (app_name, config['LAZY_TIME']))
    print('[%s]: 输出目录: %s' % (app_name, config['OUTPUT_DIR']))
    print('[%s]: 封装格式: %s' % (app_name, config['OUTPUT_FILE_EXT']))
    while True:
        current_time = utils.get_current_time()
        if room.get_room_info()['_status'] == 'on':
            print('\r[%s] 直播间: %d 敬业了!,%ds 后开始录制' % (current_time, room_id, config['LAZY_TIME']))
            time.sleep(config['LAZY_TIME'])
            Recoder(room.get_live_urls(), room.get_room_info()['ROOMTITLE']).start_recoding()
            if not config['CYCLE']:
                break
        else:
            print('\r[%s] 直播间: %d 摸了' % (current_time, room_id), end='')
        time.sleep(config['POLLING_INTERVAL'])
    pass


if __name__ == '__main__':
    start()
