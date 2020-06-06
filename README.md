[![PyPI 版本](https://badge.fury.io/py/bilibili-utils.svg)](https://pypi.org/project/bilibili-utils/)

*Bilibili-utils* 集成了部分的[哔哩哔哩](https://www.bilibili.com/)接口。

# 基本使用（未完善）
## 安装
使用 `pip` 进行安装：
```shell
pip install bilibili-utils
```


## 使用样例
```python
# 数据库模块
from bilibili.database.model import User, Chat, Contribution, SignIn, Popularity, Follower
from bilibili.database.util import add, get
# 用户视频模块
from bilibili.space import User, Video, Dynamic, Comment, FavoriteList
# 直播模块
from bilibili.live import model as blivedm
from bilibili.live.util import send
# 其他工具
from bilibili.util.session import session
from bilibili.util.voice import playsound, voice_via_baidu, voice_via_google
from bilibili.util.others import av2bv, bv2av
```



# 参考
- [blivedm](https://github.com/xfgryujk/blivedm)
- [AV、BV 互相转化](https://www.zhihu.com/question/381784377/answer/1099438784)
