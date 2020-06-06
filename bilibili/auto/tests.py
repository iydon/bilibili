from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from bilibili.space import Video, User


class Auto:
    _HOME = 'https://www.bilibili.com'
    _SPACE = 'https://space.bilibili.com'


    def __init__(self, login=True, web_driver='Chrome'):
        # set browser
        if isinstance(web_driver, str):
            self._browser = getattr(webdriver, web_driver)()
        elif isinstance(web_driver, webdriver.Remote):
            self._browser = web_driver
        else:
            raise TypeError('Argument `web_driver` has wrong type.')
        # login
        self._goto(self._HOME)
        if login:
            self.login()


    def __repr__(self):
        return f'<Auto @ {hash(self):#x}>'


    def login(self):
        '''Since I am lazy to write this function, you may login your
        Bilibili account manually.
        '''
        while self._browser.find_elements_by_class_name('logout-face'):
            input('(Off-line) Please log in >>> ')
        print('(On-line) You are now logged in.')


    def like_videos_from_user_in_video_comments(self, video_id):
        '''从视频评论区获得用户，点赞其投稿视频
        '''
        users = set()
        v = Video(video_id)
        for comment in v.comments:
            if comment.user_id not in users:
                users.add(comment.user_id)
                self.like_videos_from_user(comment.user_id)


    def like_videos_from_user(self, user_id):
        for video in User(user_id).videos:
            self._goto(self._video_url_from_id(video.id))
            # self._wait(element_to_be_clickable=(By.CLASS_NAME, class_like))
            self.like_this_video()


    def like_this_video(self):
        class_like = 'van-icon-videodetails_like'
        class_flag = 'like.on'
        self._browser.implicitly_wait(10)
        if not self._browser.find_elements_by_class_name(class_flag):
            element = self._browser.find_element_by_class_name(class_like)
            element.click()


    def _goto(self, url):
        self._browser.get(url)


    def _wait(self, timeout=5, poll_frequency=0.5, **kwargs):
        '''Web driver wait.

        Argument:
            - timeout: [int, float]
            - poll_frequency: [int, float]

        Example:
            >>> self._wait(element_to_be_clickable=(By.ID, '...'))
        '''
        wait =  WebDriverWait(self._browser, timeout, poll_frequency)
        for key, val in kwargs.items():
            wait.until(getattr(expected_conditions, key)(val))


    def _user_url_from_id(self, id):
        return self._SPACE + f'/{id}'


    def _video_url_from_id(self, id):
        return self._HOME + f'/av{id}'
