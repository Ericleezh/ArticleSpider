# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """
        #获取文章列表页中的文章url并交给scrapy下载后并进行解析
        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        for post_url in post_urls:
            #若取到的url没有域名，则需要使用parse连接
            # 初始化request后交给scrapy下载
            yield Request(url=parse.urljoin(response.url,post_url),callback=self.parse_detail)

        #提取下一页并交给scrapy进行下载
        next_urls = response.css(".next.page-numbers a::href").extract_first()
        if next_urls:
            #调用twist底层，直接填函数名
            yield Request(url=parse.urljoin(response.url,post_url),callback=self.parse)

    def parse_detail(self,response):
        #提取文章的具体字段
        # title = response.xpath("// *[ @ id = 'post-113652'] / div[1] / h1/text()").extract()[0]
        # 使用css样式选择器
        title = response.css(".entry-header h1::text").extract_first()
        create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first().strip().replace("·","").strip()
        praise_nums = response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first()
        # fav_nums = response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0].replace("收藏",'').strip()
        #使用正则表达式
        fav_nums = response.css(".bookmark-btn::text").extract_first()
        match_re = re.match(".*?(\d+).*",fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract_first().replace("评论","").strip()
        if comment_nums == "":
            comment_nums = 0
        content = response.xpath("//div[@class='entry']").extract_first()
        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tag_set = list(set(tag_list))
        tags = ",".join(tag_set)

        pass
