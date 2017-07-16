import logging
import time
from multiprocessing import Process

import utils as utils
from LiveRoom import LiveRoom
from Recoder import Recoder


# 直播间监听
class Monitor(Process):
    def __init__(self, room_id):
        Process.__init__(self)
        self.room_id = room_id
        self.config = utils.load_config()
        self.room = LiveRoom(room_id)
        self.room_info = '[直播间:%s,up主:%s]' % (self.room_id, self.room.anchor_name)

    def run(self):
        logging.info('%s 开始监控...' % self.room_info)
        while True:
            try:
                if self.room.get_room_info()['_status'] == 'on':
                    logging.info('%s 准备录制...' % self.room_info)
                    time.sleep(self.config['LAZY_TIME'])
                    logging.info('%s 开始录制...' % self.room_info)
                    t = Recoder(self.room.get_live_urls(), self.room.get_room_info()['ROOMTITLE']).start_recoding()
                    logging.info('%s 录制结束!录制时长:%s秒' % (self.room_info, str(round(t))))
                else:
                    time.sleep(self.config['POLLING_INTERVAL'])
            except Exception:
                logging.warning('%s 发生错误 %s' % (self.room_info, Exception))
                time.sleep(10)
