# -*- coding: utf-8 -*-
import scrapy
import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ArticleSpider.items import LagouItemLoader,LagouJobItem
from ArticleSpider.utils.common import get_md5



class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']


    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 1,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'user_trace_token=20180309121039-d3c5e37a-234f-11e8-b169-5254005c3644; LGUID=20180309121039-d3c5e650-234f-11e8-b169-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; LGSID=20180309151800-fffbb7c7-2369-11e8-b172-5254005c3644; hideSliderBanner20180305WithTopBannerC=1; SEARCH_ID=f70549a528724cf7b9250c15646234a1; TG-TRACK-CODE=gongsi_banner; X_MIDDLE_TOKEN=27d1450d6d8872d5d61333d023394edd; X_HTTP_TOKEN=6f91da2bc455be0852db28c86405ce0e; _gat=1; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1520583072; LGRID=20180309161120-734359e0-2371-11e8-b174-5254005c3644',
            'Host': 'www.lagou.com',
            'Origin': 'https://www.lagou.com',
            'Referer': 'https://www.lagou.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        }
    }

    rules = (
        # Rule(LinkExtractor(allow=("zhaopin/.*",)),follow=True),
        # Rule(LinkExtractor(allow=("gongsi/\d+.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    # def parse_start_url(self, response):
    #     return []
    #
    # def process_results(self, response, results):
    #     return results

    def parse_job(self, response):
        item_loader = LagouItemLoader(item=LagouJobItem(),response=response)
        item_loader.add_css("title",".job-name::attr(title)")
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_css("salary",".job_request p .salary::text")
        item_loader.add_xpath("job_city","//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")
        item_loader.add_css("tags",".position-label li::text")
        item_loader.add_css("publish_time",".publish_time::text")
        item_loader.add_css("job_advantage",".job-advantage p::text")
        item_loader.add_css("job_desc",".job_bt div")
        item_loader.add_css("job_addr",".work_addr")
        item_loader.add_css("company_url",".c_feature li a::text ")
        item_loader.add_css("company_name","img.b2::attr(alt)")
        item_loader.add_value("crawl_time",datetime.datetime.now())


        lagoujob_item = item_loader.load_item()
        yield lagoujob_item