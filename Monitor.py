import time
from urllib.parse import urlparse
from Live import *
import utils as utils
from Recoder import Recoder


# 直播间监听
class Monitor:
    def __init__(self, room_url):
        """
        :param room_url: 直播间url
        """
        # Process.__init__(self)
        # 鸡脖间url
        self.room_url = room_url
        # 域名
        self.site_domain = urlparse(self.room_url)[1]
        # 房间号
        self.room_id = int(urlparse(self.room_url)[2].replace('/', ''))
        # 配置文件
        self.config = utils.load_config()
        # Logger
        self.logger = utils.get_logger()
        if self.site_domain == 'live.bilibili.com':
            self.room = BiliBiliLive(self.room_id)
        elif self.site_domain == 'www.panda.tv':
            self.room = PandaTVLive(self.room_id)

    def run(self):
        logging_title = '[平台:%s 直播间:%s 主播:%s]' % (
            self.site_domain, self.room_id, self.room.get_room_info()['hostname'])
        self.logger.info('%s 开始监控' % logging_title)
        while 1:
            try:
                if self.room.get_room_info()['status']:
                    self.logger.info('%s 准备录制' % logging_title)
                    time.sleep(self.config['LAZY_TIME'])
                    self.logger.info('%s 开始录制' % logging_title)
                    t = Recoder(self.room.get_live_urls()[0], self.config['OUTPUT_DIR'],
                                '%s %s.%s' % (utils.get_current_time(), self.room.get_room_info()['roomname'],
                                              self.config['OUTPUT_FILE_EXT'])).start_recoding()
                    self.logger.info('%s 录制结束!录制时长:%s秒' % (logging_title, str(round(t))))
                else:
                    time.sleep(self.config['POLLING_INTERVAL'])
            except Exception:
                time.sleep(self.config['POLLING_INTERVAL'])
