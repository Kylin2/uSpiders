# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem1(scrapy.Item):
    uid = scrapy.Field() # 用户id
    uname = scrapy.Field() # 用户昵称
    location = scrapy.Field() # 地址
    gender = scrapy.Field() # 性别
    verified = scrapy.Field() # 是否认证
    verified_reason = scrapy.Field() # 认证原因
    friends_count = scrapy.Field() # 关注数
    statuses_count = scrapy.Field() # 微博数
    followers_count = scrapy.Field() # 粉丝数
    description = scrapy.Field() # 简介
    labels = scrapy.Field() # 标签
    rank = scrapy.Field() # 等级

class WeiboItem2(scrapy.Item):
    wid = scrapy.Field() # 微博id
    uid = scrapy.Field() # 用户id
    uname = scrapy.Field() # 用户昵称
    time = scrapy.Field() # 微博发布时间
    text = scrapy.Field() # 微博内容
    share_count = scrapy.Field() # 转发数
    comments_count = scrapy.Field() # 评论数
    zan_count = scrapy.Field() # 点赞数
    source = scrapy.Field() # 来源

class WeiboItem3(scrapy.Item):
    wid = scrapy.Field() # 微博id
    cid = scrapy.Field() # 评论id
    type = scrapy.Field() # 类型(评论 or 转发)
    uid = scrapy.Field() # 用户id
    uname = scrapy.Field() # 用户昵称
    time = scrapy.Field() # 发布时间
    text = scrapy.Field() # 内容
    zan_count = scrapy.Field() # 点赞数
    share_count = scrapy.Field() # 转发数
    comments_count = scrapy.Field() # 评论数

class WeiboItem4(scrapy.Item):
    uid = scrapy.Field() # 用户id
    friends_uid = scrapy.Field() # 关注用户id
    followers_uid = scrapy.Field() # 粉丝用户id

