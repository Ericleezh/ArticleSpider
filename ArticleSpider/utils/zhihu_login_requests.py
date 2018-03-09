# -*- coding: utf-8 -*-
__author__ = 'leeho'
import requests
import time
import execjs
import hmac
from hashlib import sha1

session = requests.session()
agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
header = {
    "HOST":"www.zhihu.com",
    "Referer": "https://www.zhizhu.com",
    'User-Agent': agent,
    'Authorization':'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
}


def get_signature(grantType, clientId, source, timestamp):
    # 处理签名

    hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
    hm.update(str.encode(grantType))
    hm.update(str.encode(clientId))
    hm.update(str.encode(source))
    hm.update(str.encode(timestamp))

    return str(hm.hexdigest())

def get_captcha():
    import time
    t = str(int(time.time()*1000))
    print(t)
    #请求的url在新版本中找不到
    captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
    t = session.get(captcha_url,headers = header)
    with open("captcha.jpg","wb") as f:
        f.write(t.content)
        f.close()

    from PIL import Image
    try:
        im = Image.open('captcha.jpg')
        im.show()
        im.close()
    except:
        pass

    captcha = input("请输入验证码\n")
    return captcha

def is_login():
    #通过个人中心页面返回状态码来判断是否为登录状态
    inbox_url = "https://www.zhihu.com/question/56250357/answer/148534773"
    response = session.get(inbox_url, headers=header, allow_redirects=False)
    if response.status_code  != 200:
        return False
    else:
        return True

def zhihu_login(account, password):
    #知乎登录
    loginUrl = 'https://www.zhihu.com/api/v3/oauth/sign_in'
    timestamp = int(time.time() * 1000)
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    # fp = open('ArticleSpider/utils/zhihu.js')
    # js = fp.read()
    # fp.close()
    # ctx = execjs.compile(js)
    # signature = ctx.call('getSignature', timestamp)

    print("登录知乎-------------")
    params = {
        'client_id': client_id,
        'grant_type': 'password',
        'timestamp': str(timestamp),
        'source': 'com.zhihu.web',
        'signature': get_signature("password",client_id,"com.zhihu.web",str(timestamp)),
        'username': account,
        'password': password,
        'captcha': get_captcha(),
        'lang': 'cn',
        'ref_source': 'homepage',
        'utm_source': '',
    }

    response_text = session.post(loginUrl, data=params, headers=header)
    session.cookies.save()

zhihu_login("15112580677","lizhenhao0524")
is_login()
# get_captcha()