# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from .items import WeiboItem1,WeiboItem2,WeiboItem3,WeiboItem4


class WeiboPipeline(object):
    def open_spider(self,spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')
        spider.keyword = spider.settings.get('KEYWORD')
        spider.url = spider.settings.get('LINK')
        self.db_conn = sqlite3.connect(db_name,timeout=10)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self,spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        if isinstance(item,WeiboItem1):
            self.insert_db_weiboitem1(item)
        elif isinstance(item,WeiboItem2):
            self.insert_db_weiboitem2(item)
        elif isinstance(item,WeiboItem3):
            self.insert_db_weiboitem3(item)
        elif isinstance(item,WeiboItem4):
            self.insert_db_weiboitem4(item)
        return item

    def insert_db_weiboitem1(self,item):
        values = (
            item.get('uid',''),
            item.get('uname',''),
            item.get('location',''),
            item.get('gender',''),
            item.get('verified','-1'),
            item.get('verified_reason',''),
            item.get('friendes_count','0'),
            item.get('statuses_count','0'),
            item.get('followers_count','0'),
            item.get('description',''),
            item.get('labels',''),
            item.get('rank','0')
        )
        sql = 'INSERT INTO weibo_t1 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql,values)
        self.db_conn.commit()

    def insert_db_weiboitem2(self,item):
        values = (
            item.get('wid',''),
            item.get('uid',''),
            item.get('uname',''),
            item.get('time',''),
            item.get('text',''),
            item.get('share_count','0'),
            item.get('comments_count','0'),
            item.get('zan_count','0'),
            item.get('source',''),
        )
        sql = 'INSERT INTO weibo_t2 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql,values)
        self.db_conn.commit()

    def insert_db_weiboitem3(self,item):
        values = (
            item.get('wid',''),
            item.get('cid',''),
            item.get('type',''),
            item.get('uid',''),
            item.get('uname',''),
            item.get('time',''),
            item.get('text',''),
            item.get('zan_count','0'),
            item.get('share_count','0'),
            item.get('comments_count','0'),
        )
        sql = 'INSERT INTO weibo_t3 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql,values)
        self.db_conn.commit()

    def insert_db_weiboitem4(self,item):
        values = (
            item.get('uid',''),
            item.get('friends_uid',''),
            item.get('followers_uid',''),
        )
        sql = 'INSERT INTO weibo_t4 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql,values)
        self.db_conn.commit()