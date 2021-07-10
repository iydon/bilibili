__all__ = ('send', 'stream', 'get')


import itertools
import time

from ..space.model import User
from ..util.session import session


class send:
    @classmethod
    def danmaku(cls, text, room_id, color=16777215, fontsize=25, mode=1, limit=20, scale=0.1):
        '''发送弹幕

        Argument:
            - text: str
            - room_id: int
            - color: int, default is 16777215
            - fontsize: int, default is 25
            - mode: int, default is 1
            - limit: int, text length limit
            - scale: float, send text interval
        '''
        if len(text) > limit:
            flag = send.danmaku(text[:limit], room_id, color, fontsize, mode, limit, scale)
            if not flag:
                return False
            time.sleep(scale*max(limit, len(text)-limit))
            return send.danmaku(text[limit:], room_id, color, fontsize, mode, limit, scale)
        url = 'https://api.live.bilibili.com/msg/send'
        data = dict(
            msg=text, roomid=room_id,
            color=color, fontsize=fontsize, mode=mode, rnd=int(time.time()),
        )
        return cls._post(url, data).json()['code'] == 0

    @classmethod
    def gold(cls, from_uid, to_uid, room_id, gift_number=1, gift_id=20004, price=100):
        '''
        Argument:
            - from_uid: int, gift from user id
            - to_uid: int, gift to user id
            - room_id: int
            - gift_number: int
            - gift_id: int
            - price: int
        '''
        url = 'https://api.live.bilibili.com/xlive/revenue/v1/gift/sendGold'
        data = dict(
            uid=from_uid, gift_id=gift_id, ruid=to_uid, platform='pc',
            gift_num=gift_number, price=price, biz_code='Live',
            coin_type='gold', biz_id=room_id, rnd=int(time.time()),
        )
        response = cls._post(url, data).json()
        return response['code'] == 0

    @classmethod
    def bag_gift(cls, from_uid, to_uid, room_id, gift_number=1, gift_id=1):
        '''发送背包礼物（暂定辣条）

        Argument:
            - from_uid: int, gift from user id
            - to_uid: int, gift to user id
            - room_id: int
            - gift_number: int
            - gift_id: int, 1 for 辣条

        TODO:
            - 简化参数
        '''
        url = 'https://api.live.bilibili.com/gift/v2/live/bag_send'
        data = dict(
            uid=from_uid, gift_id=gift_id, ruid=to_uid, biz_id=room_id,
            rnd=int(time.time()), price=0, gift_num=None, bag_id=None,
        )
        bags = cls._bags(gift_id)
        if gift_number > sum(bags.values()):
            return False
        for bag_id, number in bags.items():
            data['bag_id'] = bag_id
            data['gift_num'] = gift_number if gift_number<=number else number
            if cls._post(url, data).json()['code'] != 0:
                return False
            if gift_number <= number:
                break
            gift_number -= number
        return True

    @classmethod
    def _bags(cls, gift_id=None):
        # {bag_id: gift_num}
        url = 'https://api.live.bilibili.com/xlive/web-room/v1/gift/bag_list'
        cookies = dict(SESSDATA=session.session.cookies['SESSDATA'])
        headers = dict(Referer='https://live.bilibili.com/')
        data = session.requests.get(url, headers=headers, cookies=cookies).json()
        return {
            item['bag_id']: item['gift_num']
            for item in sorted(data['data']['list'], key=lambda x: x['expire_at'])
            if gift_id is None or item['gift_id']==gift_id
        }

    @classmethod
    def _post(cls, url, data):
        data['csrf_token'] = data['csrf'] = session.session.cookies['bili_jct']
        cookies = dict(
            SESSDATA=session.session.cookies['SESSDATA'],
            bili_jct=session.session.cookies['bili_jct'],
        )
        headers = dict(Referer='https://live.bilibili.com/')
        response = session.requests.post(url, data=data, headers=headers, cookies=cookies)
        return response


class stream:
    @classmethod
    def start(cls, room_id, area_id=27):
        # start(12735076, 27)
        url = 'https://api.live.bilibili.com/room/v1/Room/startLive'
        data = dict(
            room_id=room_id, platform='pc', area_v2=area_id,
        )
        return send._post(url, data).json()['code'] == 0

    @classmethod
    def stop(cls, room_id):
        url = 'https://api.live.bilibili.com/room/v1/Room/stopLive'
        data = dict(
            room_id=room_id, platform='pc'
        )
        return send._post(url, data).json()['code'] == 0


class get:
    @classmethod
    def areas(cls):
        keys = (
            'id', 'name', 'parent_id', 'parent_name', 'act_id',
            'pk_status', 'hot_status', 'lock_status', 'pic'
        )
        func = lambda x: int(x) if isinstance(x, str) and x.isdigit() else x
        url = 'https://api.live.bilibili.com/room/v1/Area/getList'
        data = session.requests.get(url).json()['data']
        return tuple(
            {key: func(item[key]) for key in keys}
            for item in itertools.chain(*(d['list'] for d in data))
        )

    @classmethod
    def rooms_by_area_id(cls, area_id=27, maximum=float('inf'), pn=30, count=False):
        # https://live.bilibili.com/
        url = 'https://api.live.bilibili.com/room/v3/area/getRoomList'
        keys = ('uid', 'roomid', 'uname', 'online', 'area_name', 'title')
        params = dict(area_id=area_id, page=1, page_size=pn)
        response = session.requests.get(url, params=params)
        data = response.json()['data']
        if count:
            yield data['count']
            return
        count, rooms = min(data['count'], maximum), set()
        while count:
            if not data['list']:
                break
            for room in data['list']:
                if room['roomid'] in rooms:
                    continue
                rooms.add(room['roomid'])
                count -= 1
                yield {key: room[key] for key in keys}
            params['page'] += 1
            try:
                data = session.requests.get(url, params=params).json()['data']
            except:
                pass

    @classmethod
    def seven_rank(cls, room_id, user_id=1):
        url = 'https://api.live.bilibili.com/rankdb/v1/RoomRank/webSevenRank'
        params = dict(roomid=room_id, ruid=user_id)
        return tuple(
            {key: data[key] for key in ('uid', 'uname', 'face', 'rank', 'score')}
            for data in session.requests.get(url, params=params).json()['data']['list']
        )

    @classmethod
    def guards(cls, user_id, room_id=None):
        def f(room_id, user_id, page, pn=29):
            url = 'https://api.live.bilibili.com/xlive/app-room/v1/guardTab/topList'
            params = dict(roomid=room_id, page=page, ruid=user_id, page_size=pn)
            return session.requests.get(url, params=params).json()['data']
        keys = ('uid', 'username', 'face', 'guard_level')
        room_id = room_id or User(user_id, info=False).room['roomid']
        data = f(room_id, user_id, 1)
        for item in data['list']:
            yield {key: item[key] for key in keys}
        for page in range(data['info']['page']-1):
            for item in f(room_id, user_id, page+2)['list']:
                yield {key: item[key] for key in keys}
