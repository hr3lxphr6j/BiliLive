from .BaseLive import BaseLive
import re
from lxml import etree


class HuoMaoLive(BaseLive):
    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id
        self.site_name = 'HuoMao'
        self.site_domain = 'www.huomao.com'

    def get_room_info(self):
        dom = self.common_request('GET', 'https://' + self.site_domain + '/' + str(self.room_id)).text
        tree = etree.HTML(dom)
        video_id = re.findall('"stream":"(\w*)"', dom)[0]
        url = 'https://www.huomao.com/swf/live_data'
        data = self.common_request('POST', url, data={
            'VideoIDS': video_id,
            'streamtype': 'live',
            'cdns': 1
        }).json()
        status = (data['roomStatus'] == '1')
        room_name = tree.cssselect('.title-name title-name h1')[0].text
        host_name = tree.cssselect('.title-box p span')[0].text.strip()
        return {
            'hostname': host_name,
            'roomname': room_name,
            'site_name': self.site_name,
            'site_domain': self.site_domain,
            'status': status
        }

    def get_live_urls(self):
        dom = self.common_request('GET', 'https://' + self.site_domain + '/' + str(self.room_id)).text
        video_id = re.findall('"stream":"(\w*)"', dom)[0]
        url = 'https://www.huomao.com/swf/live_data'
        data = self.common_request('POST', url, data={
            'VideoIDS': video_id,
            'streamtype': 'live',
            'cdns': 1
        }).json()
        return [data['streamList'][-1]['list'][0]['url']]
