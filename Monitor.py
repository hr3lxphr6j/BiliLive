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
        self.room_id = urlparse(self.room_url)[2].replace('/', '')
        # 配置文件
        self.config = utils.load_config()
        # Logger
        self.logger = utils.get_logger()
        if self.site_domain == 'live.bilibili.com':
            self.room = BiliBiliLive(self.room_id)
        elif self.site_domain == 'www.panda.tv':
            self.room = PandaTVLive(self.room_id)
        elif self.site_domain == 'www.huomao.com':
            self.room = HuoMaoLive(self.room_id)
        elif self.site_domain == 'www.zhanqi.tv':
            self.room = ZhanqiLive(self.room_id)

    def run(self):
        logging_title = u'[Platform:%s Room:%s Up:%s]' % (
            self.site_domain, self.room_id, self.room.get_room_info()['hostname'])
        self.logger.info(u'%s Start Monitoring' % logging_title)
        while 1:
            try:
                if self.room.get_room_info()['status']:
                    self.logger.info(u'%s Begin Recoding' % logging_title)
                    time.sleep(self.config['LAZY_TIME'])
                    self.logger.info(u'%s Start Recoding' % logging_title)
                    t = Recoder(self.room.get_live_urls()[0], self.config['OUTPUT_DIR'],
                                '%s %s.%s' % (utils.get_current_time(), self.room.get_room_info()['roomname'],
                                              self.config['OUTPUT_FILE_EXT'])).start_recoding()
                    if t > 30:
                        self.logger.info(u'%s Recoded Over!\tTime:%s s' % (logging_title, str(round(t))))
                else:
                    time.sleep(self.config['POLLING_INTERVAL'])
            except Exception:
                time.sleep(self.config['POLLING_INTERVAL'])
