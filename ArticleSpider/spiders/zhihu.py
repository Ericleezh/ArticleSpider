# -*- coding: utf-8 -*-
import scrapy,time,hmac,json,requests
import execjs
import re
import datetime
from hashlib import sha1
from scrapy.loader import ItemLoader
from ArticleSpider.items import ZhihuQuestionItem,ZhihuAnswerItem

#兼容py2和py3
try:
    import  urlpare as parse
except:
    from urllib import parse

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    #question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}&sort_by=default"

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
                #如果提取到question的页面，则交给提取函数进行处理
                request_url = match_obj.group(1)
                #深度优先遍历的入口
                yield scrapy.Request(request_url,headers=self.headers,callback=self.parse_question)
            else:
                #若不是则进一步跟踪
                yield scrapy.Request(url,headers=self.headers,callback=self.parse)

    def parse_question(self,response):
        #处理question，从页面中提取出具体的question item
        match_obj  = re.match("(.*zhihu.com/question/(\d+))(/|$)",response.url)
        if match_obj:
            question_id = int(match_obj.group(2))

        item_loader = ItemLoader(item=ZhihuQuestionItem(),response=response)
        item_loader.add_css("title",".QuestionHeader .QuestionHeader-content .QuestionHeader-main h1.QuestionHeader-title::text")
        item_loader.add_css("content","div.QuestionHeader-detail")
        item_loader.add_value("url",response.url)
        item_loader.add_value("zhihu_id",question_id)
        item_loader.add_css("answer_num","h4.List-headerText span::text")
        item_loader.add_css("comments_num",".QuestionHeader-Comment button::text")
        item_loader.add_css("watch_user_num",".NumberBoard-itemValue::text")
        item_loader.add_css("topics",".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()

        # 路由到下载器
        yield scrapy.Request(self.start_answer_url.format(question_id,5,0),headers=self.headers,callback=self.parse_answer)
        yield question_item #路由到pipeline中

    def parse_answer(self,response):
        #处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        #提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item
        if not is_end:
            yield  scrapy.Request(next_url,headers=self.headers,callback=self.parse_answer)




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
