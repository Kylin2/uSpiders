# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ProductItem(scrapy.Item):
    id = scrapy.Field() # 商品id
    link = scrapy.Field()  # 商品链接
    name = scrapy.Field() # 商品名称
    commentNum = scrapy.Field() # 商品评论数
    shopName = scrapy.Field() # 店铺名称
    price = scrapy.Field() # 商品价格
    commentVersion = scrapy.Field() # 获得评论所必须的特殊字段
    score1count = scrapy.Field() # 1星数量
    score2count = scrapy.Field() # 2星数量
    score3count = scrapy.Field() # 3星数量
    score4count = scrapy.Field() # 4星数量
    score5count = scrapy.Field() # 5星数量
    brand = scrapy.Field() # 品牌
    time = scrapy.Field() # 数据获取时间

class CommentItem(scrapy.Item):
    id = scrapy.Field() # id
    pid = scrapy.Field() # 商品id
    pname = scrapy.Field() # 商品id
    nickname = scrapy.Field() # 用户名
    content = scrapy.Field() # 评论内容
    creationTime = scrapy.Field() # 评论时间
    referenceTime = scrapy.Field() # 下单时间
    days = scrapy.Field() # 下单与评论间隔时间
    socre = scrapy.Field() # 评分
    userClientShow = scrapy.Field() # 客户端类型
    userLevelName = scrapy.Field() # 会员等级
    isMobile = scrapy.Field() # 是否来自手机
    afterDays = scrapy.Field()  # 追评天数
    afterTime = scrapy.Field() # 追评时间
    afterContent = scrapy.Field() # 追评内容
    productColor = scrapy.Field() # 产品颜色
    productSize = scrapy.Field() # 产品规格
    imageCount = scrapy.Field() # 评论图片数量
    usefulVoteCount = scrapy.Field() # 点赞数
    replyCount = scrapy.Field() # 回复数
    time = scrapy.Field()  # 数据获取时间

