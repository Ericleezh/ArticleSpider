# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader
from ArticleSpider.utils.common import extract_num
from ArticleSpider.settings import SQL_DATE_FORMAT,SQL_DATETIME_FORMAT
from w3lib.html import remove_tags

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date

def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

def remove_comment_tags(value):
    # tags = list(set(value))
    if "评论" in value:
        return ""
    else:
        return value

def return_value(value):
    return value

class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


#定义结构
class JobBoleArticleItem(scrapy.Item) :
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        #覆盖default_output_processor
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags =scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
           insert into jobbole_article(title, url, url_object_id, create_date, fav_nums, comment_nums, praise_nums, tags)
           VALUE (%s,%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE title=VALUES(title),fav_nums=VALUES(fav_nums),
           comment_nums=VALUES(comment_nums),praise_nums=VALUES(praise_nums)
           """

        params = (self["title"], self["url"], self["url_object_id"], self["create_date"], self["fav_nums"], self["comment_nums"],
                   self["praise_nums"], self["tags"])

        return insert_sql,params

class ZhihuQuestionItem(scrapy.Item):
    #知乎问题的Item
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question数据
        insert_sql = """
           insert into zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time)
           VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE title=VALUES(title),content=VALUES(content),answer_num=VALUES(answer_num),
           comments_num=VALUES(comments_num),watch_user_num=VALUES(watch_user_num),
           click_num=VALUES(click_num)
           """

        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = self["title"][0]
        content = "".join(self["content"])
        answer_num = extract_num(self["answer_num"])
        comments_num = extract_num(self["comments_num"][0])

        if len(self["watch_user_num"]) == 2:
            watch_user_num = int(self["watch_user_num"][0].replace(",",""))
            click_num = int(self["watch_user_num"][1].replace(",",""))
        else:
            watch_user_num = int(self["watch_user_num"][0].replace(",",""))
            click_num = 0
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (zhihu_id, topics, url, title, content, answer_num, comments_num,
                  watch_user_num, click_num, crawl_time)

        return insert_sql,params

class ZhihuAnswerItem(scrapy.Item):
    #知乎的问题回答Item
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question数据
        #防止主键冲突，再次爬取时遇到相同则更新
        insert_sql = """
           insert into zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time,update_time,crawl_time)
           VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE content=VALUES(content),comments_num=VALUES(comments_num),praise_num=VALUES(praise_num),update_time=VALUES(update_time)
           """
        create_time = datetime.datetime.fromtimestamp(self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(self["update_time"]).strftime(SQL_DATETIME_FORMAT)

        params = (
            self["zhihu_id"],self["url"],self["question_id"],
            self["author_id"],self["content"],self["praise_num"],
            self["comments_num"],create_time,update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return  insert_sql,params


def remove_splash(value):
    return value.replace("/","")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [ item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)

class LagouItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()

class LagouJobItem(scrapy.Item):
    #拉勾网职位信息
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr)
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr)
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        #插入知乎question数据
        #防止主键冲突，再次爬取时遇到相同则更新
        insert_sql = """
           insert into lagou_job(url,url_object_id, title, salary, job_city, work_years, degree_need,
              job_type,publish_time,tags,job_advantage,job_desc,job_addr,company_url,company_name,crawl_time)
           VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE url=VALUES(url),url_object_id=VALUES(url_object_id),title=VALUES(title),salary=VALUES(salary)
           ,job_city=VALUES(job_city),work_years=VALUES(work_years),degree_need=VALUES(degree_need),job_type=VALUES(job_type)
           ,job_advantage=VALUES(job_advantage),job_addr=VALUES(job_addr)
           """

        params = (
            self["url"],self["url_object_id"],self["title"],
            self["salary"],self["job_city"],self["work_years"],
            self["degree_need"], self["job_type"], self["publish_time"],
            self["tags"], self["job_advantage"], self["job_desc"],
            self["job_addr"], self["company_url"], self["company_name"],
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
        )

        return  insert_sql,params
