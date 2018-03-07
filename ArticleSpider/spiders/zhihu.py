# -*- coding: utf-8 -*-
import scrapy,time,hmac,json,requests
import execjs
import re
from hashlib import sha1
#兼容py2和py3
try:
    import  urlpare as parse
except:
    from urllib import parse

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    sessiona = requests.Session()

    phone = '+8615112580677'  # 手机号
    password = 'lizhenhao0524'  # 密码
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    headers = {
        'authorization': 'oauth ' + client_id,
        'Host': 'www.zhihu.com',
        'Origin': 'https://www.zhihu.com',
        'Referer': 'https://www.zhihu.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/63.0.3239.84 Safari/537.36'
    }
    def parse(self, response):
        """
        提取出html页面中的所有url，并且跟踪这些url
        如果提取的url中有格式为/question/xxx 就下载后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url,url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False,all_urls)#过滤无用的url
        for url in all_urls:
            print(url)
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$)",url)
            if match_obj:
                request_url = match_obj.group(1)
                question_url = match_obj.group(2)

                yield scrapy.Request(request_url,headers=self.headers,callback=self.parse_question)

    def parse_question(self,response):
        #处理question，从页面中提取出具体的question item
        pass

    # def get_captcha(data,need_cap):
    #     # 处理验证码
    #     if need_cap is False:
    #         return ""
    #     with open('captcha.gif', 'wb') as fb:
    #         fb.write(data)
    #     return input('captcha:')

    # def get_signature(self,grantType, clientId, source, timestamp):
    #     #处理签名
    #
    #     hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
    #     hm.update(str.encode(grantType))
    #     hm.update(str.encode(clientId))
    #     hm.update(str.encode(source))
    #     hm.update(str.encode(timestamp))
    #
    #     return str(hm.hexdigest())
    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',headers=self.headers,callback=self.login)]

    # def is_need_capture(self, response):
    #     yield scrapy.Request('https://www.zhihu.com/captcha.gif?r=%d&type=login' % (time.time() * 1000),
    #                         headers=self.headers, callback=self.get_captcha, meta={"resp": response})

    def login(self, response):
        captcha_info = json.loads(response.text)
        if captcha_info['show_captcha']:  # 出现验证码
            print('出现验证码')
        loginUrl = 'https://www.zhihu.com/api/v3/oauth/sign_in'
        timestamp = int(time.time() * 1000)
        fp = open('ArticleSpider/spiders/zhihu.js')
        js = fp.read()
        fp.close()
        ctx = execjs.compile(js)
        signature = ctx.call('getSignature', timestamp)
        params = {
            'client_id': self.client_id,
            'grant_type': 'password',
            'timestamp': str(timestamp),
            'source': 'com.zhihu.web',
            'signature': signature,
            'username': str(self.phone),
            'password': str(self.password),
            'captcha': '',
            'lang': 'cn',
            'ref_source': 'homepage',
            'utm_source': ''
        }
        yield scrapy.FormRequest(url=loginUrl, headers=self.headers, formdata=params, method='POST', callback=self.check_login)

    def check_login(self, response):
        # 验证服务器返回是否成功。
        HomeUrl = 'https://www.zhihu.com/'
        headers = {
            'Host': 'www.zhihu.com',
            'Referer': 'https://www.zhihu.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        }
        text_json = json.loads(response.text)

        print(response.text)
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True,headers=headers)
