# -*- coding: utf-8 -*-
import scrapy,time,hmac,json,requests
from hashlib import sha1

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'}
    sessiona = requests.Session()

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request("https://www.zhihu.com/signup",headers=self.headers,callback=self.login)]

    def get_captcha(data, need_cap):
        ''' 处理验证码 '''
        if need_cap is False:
            return
        with open('captcha.gif', 'wb') as fb:
            fb.write(data)
        return input('captcha:')

    def get_signature(grantType, clientId, source, timestamp):
        #处理签名

        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        hm.update(str.encode(grantType))
        hm.update(str.encode(clientId))
        hm.update(str.encode(source))
        hm.update(str.encode(timestamp))

        return str(hm.hexdigest())

    def login(self,response):
        #处理登录
        response_text = response.text
        resp1 = self.sessiona.get('https://www.zhihu.com/signin', headers=self.headers)  # 拿cookie:_xsrf，新版知乎不用
        resp2 = self.sessiona.get('https://www.zhihu.com/api/v3/oauth/captcha?lang=cn',
                             headers=self.headers)  # 拿cookie:capsion_ticket
        need_cap = json.loads(resp2.text)["show_captcha"]  # {"show_captcha":false} 表示不用验证码
        grantType = 'password'
        clientId = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
        source = 'com.zhihu.web'
        timestamp = str((time.time() * 1000)).split('.')[0]  # 签名只按这个时间戳变化
        captcha_content = self.sessiona.get('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
                                       headers=self.headers).content
        post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
        post_data = {
            "client_id": clientId,
            "grant_type": grantType,
            "timestamp": timestamp,
            "source": source,
            "signature": self.get_signature(grantType, clientId, source, timestamp),  # 获取签名
            "username": "15112580677",
            "password": "123456",
            "lang": "cn",
            "captcha": self.get_captcha(captcha_content, need_cap),  # 获取图片验证码
            "ref_source": "homepage",
            "utm_source": ""
        }
        return [scrapy.FormRequest(
            url=post_url,
            formdata = post_data,
            headers=self.headers,
            callback= self.check_login
        )]

    def check_login(self,response):
        #验证服务器的返回数据判断是否成功
        pass
