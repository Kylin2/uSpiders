# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem1(scrapy.Item):
    nid = scrapy.Field() # news id
    title = scrapy.Field() # 标题
    text = scrapy.Field() # 正文
    time = scrapy.Field() # 时间
    source = scrapy.Field() # 来源
    search = scrapy.Field() # 搜索词
    url = scrapy.Field() # 链接
