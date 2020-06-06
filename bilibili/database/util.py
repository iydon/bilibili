__all__ = ('timestamp_to_date_time', )



from time import localtime, time as now
from datetime import datetime, date, time
from warnings import warn

from .model import session, User, Chat, Contribution, SignIn, Popularity, Follower
from ..space.model import User as SpaceUser



def timestamp_to_date_time(timestamp=None):
    if timestamp is None: timestamp = now()
    t = localtime(timestamp)
    return (
        date(t.tm_year, t.tm_mon, t.tm_mday),
        time(t.tm_hour, t.tm_min, t.tm_sec),
    )


def date_time_to_timestamp(date, time):
    return int(
        datetime(
            date.year, date.month, date.day,
            time.hour, time.minute, time.second,
        ).timestamp()
    )


class get:
    '''数据库数据获取
    '''
    @classmethod
    def user(cls, id, name=None):
        if name is None:
            name = SpaceUser(id).info['name']
        u = cls._by(User, id=id)
        if u is None:
            u = User(id=id, name=name)
            add._all(u)
        elif u.name != name:
            u.name = name
            add._all()
        return u

    @classmethod
    def _compress(cls, data):
        return [d[0] for d in data]

    @classmethod
    def _by(cls, *models, all=False, count=False, iter=False, lock=None, **condition):
        try:
            query = session.query(*models).filter_by(**condition)
            if lock: query = query.with_lockmode(lock)
            if all: return query.all()
            if count: return query.count()
            if iter: return query
            return query.first()
        except:
            args = f'models={repr(models)}, all={all}, condition={condition}'
            warn(f'Query fails: {args}')
            session.rollback()
            return list() if all else None


class add:
    @classmethod
    def chat(cls, content, user_id, timestamp=None, is_super=False):
        date, time = timestamp_to_date_time(timestamp)
        c = Chat(content=content, date=date, time=time, is_super=is_super, user_id=user_id)
        cls._all(c)
        return c

    @classmethod
    def popularity(cls, value, timestamp=None):
        date, time = timestamp_to_date_time(timestamp)
        p = Popularity(date=date, time=time, value=value)
        cls._all(p)
        return p

    @classmethod
    def contribution(cls, gift_name, gift_number, coin_type, total_coin, user_id, timestamp=None):
        # update contribution
        today, _ = timestamp_to_date_time(timestamp)
        c = get._by(Contribution,
            date=today, gift_name=gift_name, coin_type=coin_type, user_id=user_id
        )
        if c is None:
            c = Contribution(
                date=today, gift_name=gift_name, gift_number=gift_number,
                coin_type=coin_type, total_coin=total_coin, user_id=user_id,
            )
            add._all(c)
        else:
            c.gift_number += gift_number
            c.total_coin += total_coin
            add._all()
        return c

    @classmethod
    def sign_in(cls, user_id, timestamp=None):
        today, _ = timestamp_to_date_time(timestamp)
        s = get._by(SignIn, user_id=user_id, date=today)
        if s is None:
            s = SignIn(user_id=user_id, date=today)
            cls._all(s)
        return s

    @classmethod
    def followers(cls, user_ids, names, timestamp=None):
        # 建议一次增加完全
        today, _ = timestamp_to_date_time(timestamp)
        # 判断取消关注
        for f in get._by(Follower, iter=True):
            if f.is_valid and f.user_id not in user_ids:
                f.date = today
                f.is_valid = False
                cls._all()
        # 判断新增关注
        for user_id, name in zip(user_ids, names):
            cls.new_follower(user_id, name, today=today)

    @classmethod
    def new_follower(cls, user_id, name, timestamp=None, today=None):
        if today is None:
            today, _ = timestamp_to_date_time(timestamp)
        f = get._by(Follower, user_id=user_id)
        if f is None:
            get.user(user_id, name)
            f = Follower(user_id=user_id, is_valid=True, date=today)
            cls._all(f)

    @classmethod
    def _all(cls, *instances):
        try:
            session.add_all(instances)
            session.commit()
            return True
        except Exception as e:
            print(e)
            warn(f'Add fails: instances={instances}')
            session.rollback()
            return False
