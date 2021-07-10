__all__ = ('send', 'search')


import re
import time

from bs4 import BeautifulSoup

from ..util.session import session
from ..util.others import bv2av


class send:
    @classmethod
    def message(cls, text, from_id, to_id):
        '''发送私信

        Argument:
            - text: str
            - from_id: int
            - to_id: int
        '''
        url = 'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg'
        data = {
            'msg[receiver_type]': '1', 'msg[msg_type]': '1', 'msg[msg_status]': '0',
            'build': '0', 'mobi_app': 'web',
            'msg[sender_uid]': from_id, 'msg[receiver_id]': to_id,
            'msg[content]': f'{{"content":"{text}"}}', 'msg[timestamp]': int(time.time()),
        }
        return cls._post(url, data).json()['code'] == 0

    @classmethod
    def _post(cls, url, data):
        data['csrf_token'] = data['csrf'] = session.session.cookies['bili_jct']
        cookies = dict(
            SESSDATA=session.session.cookies['SESSDATA'],
            bili_jct=session.session.cookies['bili_jct'],
        )
        headers = dict(Referer='https://message.bilibili.com/')
        response = session.requests.post(url, data=data, headers=headers, cookies=cookies)
        return response


def search(keyword, pages=[1], order='', duration=0, typeid=0, tag=False):
    '''Bilibili 综合搜索

    :Argument:
        - keyword
        - pages: Iterable
        - order: {totalrank: 综合排序, click: 最多点击, pubdate: 最新发布, dm: 最多弹幕, stow: 最多收藏}
        - duration: {0: 全部时长, 1: 10分钟以下, 2: 10-30分钟, 3: 30-60分钟, 4: 60分钟以上}
        - typeid: {0: 全部分区, 1: 动画, 13: 番剧, 167: 国创, 3: 音乐, 129: 舞蹈, 4: 游戏, 36: 科技,
            188: 数码, 160: 生活, 119: 鬼畜, 155: 时尚, 165: 广告, 5: 娱乐, 181: 影视, 177: 纪录片,
            23: 电影, 11: 电视剧}
    '''
    url = 'https://search.bilibili.com/all'
    params = dict(keyword=keyword, order=order, duration=duration, tids_1=typeid)
    if tag:
        params['from_source'] = 'video_tag'
    find_bv = re.compile(r'BV[a-zA-Z0-9]+')
    find_author = re.compile(r'\d+')
    for page in pages:
        params['page'] = page
        response = session.requests.get(url, params=params, headers=dict(referer=url))
        soup = BeautifulSoup(response.content, 'lxml')
        for card in soup.find_all(class_='video-item matrix'):
            part_1, part_2 = card.children
            yield dict(
                av=int(bv2av(find_bv.findall(part_1.attrs['href'])[0])[2:]),
                title=part_1.attrs['title'],
                duration=part_1.find(class_='so-imgTag_rb').text,
                playtime=part_2.find(class_='so-icon watch-num').text.strip(),
                date=part_2.find(class_='so-icon time').text.strip(),
                author=int(find_author.findall(part_2.find(class_='up-name').attrs['href'])[0]),
            )


def channels(channel_id, order='hot', pn=30):
    '''频道

    Argument:
        - channel_id: int
        - order: {'hot', 'view', 'new'}
        - pn: int, page size
    '''
    url = 'https://api.bilibili.com/x/web-interface/web/channel/multiple/list'
    params = dict(channel_id=channel_id, sort_type=order, page_size=pn)
    data = session.requests.get(url, params=params).json()['data']
    yield from data['list'][1:]
    while data['has_more']:
        params['offset'] = data['offset']
        data = session.requests.get(url, params=params).json()['data']
        yield from data['list']


def ranking(day=1, type=1):
    '''
    Argument:
        - day: int, in {1, 3, 7, 30}
        - type: int, in {1, 2, 3}
    '''
    keys = ('aid', 'author', 'coins', 'duration', 'pic', 'play', 'pts', 'title', 'video_review')
    func = lambda x: {key: x[key] for key in keys}
    url = 'https://api.bilibili.com/x/web-interface/ranking'
    params = dict(rid=0, arc_type=0, day=day, type=type)
    headers = dict(referer='https://www.bilibili.com/')
    data = session.requests.get(url, params=params, headers=headers).json()
    for video in data['data']['list']:
        yield {key: video[key] for key in keys}
        if 'others' in video:
            for v in video['others']:
                v['author'] = video['author']
                yield {key: v[key] for key in keys}
