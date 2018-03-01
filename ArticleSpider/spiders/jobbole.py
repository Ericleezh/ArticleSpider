# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader

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
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            #若取到的url没有域名，则需要使用parse连接
            # 初始化request后交给scrapy下载
            yield Request(url=parse.urljoin(response.url,post_url),meta={"front_image_url":image_url},callback=self.parse_detail)

        #提取下一页并交给scrapy进行下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first()
        if next_urls:
            #调用twist底层，直接填函数名
            yield Request(url=parse.urljoin(response.url,post_url),callback=self.parse)

    def parse_detail(self,response):

        article_item = JobBoleArticleItem()

        #提取文章的具体字段
        # title = response.xpath("// *[ @ id = 'post-113652'] / div[1] / h1/text()").extract()[0]
        # 使用css样式选择器
        # front_image_url = response.meta.get("front_image_url","")#文章封面图
        # title = response.css(".entry-header h1::text").extract_first()
        # create_date = response.xpath("//p[@class='entry-meta-hide-on-mobile']/text()").extract_first().strip().replace("·","").strip()
        # #praise_nums = response.xpath("//span[contains(@class,'vote-post-up')]/h10/text()").extract_first()
        # praise_nums = response.css(".vote-post-up h10::text").extract_first()
        # # fav_nums = response.xpath("//span[contains(@class,'bookmark-btn')]/text()").extract()[0].replace("收藏",'').strip()
        # #使用正则表达式
        # fav_nums = response.css(".bookmark-btn::text").extract_first()
        # match_re = re.match(".*?(\d+).*",fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        #
        # # comment_nums = response.xpath("//a[@href='#article-comment']/span/text()").extract_first().replace("评论","").strip()
        # comment_nums = response.css("a[href='#article-comment'] span::text").extract_first()
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # content = response.xpath("//div[@class='entry']").extract_first()
        # tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = list(set(tag_list))
        #
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["title"] = title
        # try:
        #     create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["url"] = response.url
        # article_item["front_image_url"] = [front_image_url]
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content

        #通过Item loader 加载Item（利于后期维护）
        # 1.默认都是生成list
        # 2.增加处理函数
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(),response=response)
        item_loader.add_css("title",".entry-header h1::text")
        item_loader.add_value("url",response.url)
        item_loader.add_value("url_object_id",get_md5(response.url))
        item_loader.add_xpath("create_date","//p[@class='entry-meta-hide-on-mobile']/text()")
        item_loader.add_value("front_image_url",[front_image_url])
        item_loader.add_css("praise_nums",".vote-post-up h10::text")
        item_loader.add_css("comment_nums","a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums",".bookmark-btn::text")
        item_loader.add_xpath("tags","//p[@class='entry-meta-hide-on-mobile']/a/text()")
        item_loader.add_xpath("content","//div[@class='entry']")

        article_item = item_loader.load_item()


        yield article_item
