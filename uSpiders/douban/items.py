# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanMovieInfoItem(scrapy.Item):
    mid = scrapy.Field()  # 电影id
    name = scrapy.Field()  # 名称
    alias = scrapy.Field()  # 别名
    directors = scrapy.Field()  # 导演
    scriptwriters = scrapy.Field()  # 编剧
    actors = scrapy.Field()  # 主演
    types = scrapy.Field()  # 类型
    regions = scrapy.Field()  # 上映地区
    dates = scrapy.Field()  # 上映日期
    languages = scrapy.Field()  # 语言
    duration = scrapy.Field()  # 片长或单集片长
    score = scrapy.Field()  # 评分
    description = scrapy.Field()  # 简介
    tags = scrapy.Field()  # 标签
    link = scrapy.Field()  # 豆瓣链接
    poster = scrapy.Field()  # 海报
    star1 = scrapy.Field()  # 1星
    star2 = scrapy.Field()  # 2星
    star3 = scrapy.Field()  # 3星
    star4 = scrapy.Field()  # 4星
    star5 = scrapy.Field()  # 5星
    votes = scrapy.Field()  # 评价人数
    comments = scrapy.Field()  # 短评数
    reviews = scrapy.Field()  # 影评数
    num = scrapy.Field()  # 电视剧集数


class DoubanMovieCommentsItem(scrapy.Item):
    mid = scrapy.Field()  # 电影id
    cid = scrapy.Field()  # 影评id
    uname = scrapy.Field()  # 用户昵称
    text = scrapy.Field()  # 评论内容
    time = scrapy.Field()  # 评论时间
    score = scrapy.Field()  # 评分
    votes = scrapy.Field()  # 有用数


class DoubanMovieReviewsItem(scrapy.Item):
    mid = scrapy.Field()  # 电影id
    rid = scrapy.Field()  # 影评id
    uname = scrapy.Field()  # 用户昵称
    title = scrapy.Field()  # 影评标题
    text = scrapy.Field()  # 影评内容
    time = scrapy.Field()  # 影评时间
    score = scrapy.Field()  # 评分
    numuseful = scrapy.Field()  # 有用数
    numuseless = scrapy.Field()  # 无用数
    numreply = scrapy.Field()  # 回应数


class DoubanBookInfoItem(scrapy.Item):
    bid = scrapy.Field()  # book id
    name = scrapy.Field()  # 书名
    alias = scrapy.Field()  # 原作名
    subname = scrapy.Field()  # 副标题
    authors = scrapy.Field()  # 作者
    authorintro = scrapy.Field()  # 作者简介
    translator = scrapy.Field()  # 译者
    producer = scrapy.Field()  # 出品方
    series = scrapy.Field()  # 丛书
    publisher = scrapy.Field()  # 出版社
    date = scrapy.Field()  # 出版日期
    pages = scrapy.Field()  # 页数
    price = scrapy.Field()  # 定价
    binding = scrapy.Field()  # 装帧
    isbn = scrapy.Field()  # ISBN
    cover = scrapy.Field()  # 封面
    link = scrapy.Field()  # 链接
    tags = scrapy.Field()  # 标签
    summary = scrapy.Field()  # 内容摘要
    score = scrapy.Field()  # 评分
    star1 = scrapy.Field()  # 1星
    star2 = scrapy.Field()  # 2星
    star3 = scrapy.Field()  # 3星
    star4 = scrapy.Field()  # 4星
    star5 = scrapy.Field()  # 5星
    votes = scrapy.Field()  # 评价人数
    comments = scrapy.Field()  # 短评数
    reviews = scrapy.Field()  # 书评数


class DoubanBookCommentsItem(scrapy.Item):
    bid = scrapy.Field()  # book id
    cid = scrapy.Field()  # 书评id
    uname = scrapy.Field()  # 用户昵称
    text = scrapy.Field()  # 评论内容
    time = scrapy.Field()  # 评论时间
    score = scrapy.Field()  # 评分
    votes = scrapy.Field()  # 有用数


class DoubanBookReviewsItem(scrapy.Item):
    bid = scrapy.Field()  # book id
    rid = scrapy.Field()  # 书评id
    uname = scrapy.Field()  # 用户昵称
    title = scrapy.Field()  # 书评标题
    text = scrapy.Field()  # 书评内容
    time = scrapy.Field()  # 书评时间
    score = scrapy.Field()  # 评分
    numuseful = scrapy.Field()  # 有用数
    numuseless = scrapy.Field()  # 无用数
    numreply = scrapy.Field()  # 回应数