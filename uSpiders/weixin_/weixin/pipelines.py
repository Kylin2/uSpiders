# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
from .items import WeixinItem1


class WeixinPipeline(object):
    def open_spider(self,spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')
        #spider.keyword = spider.settings.get('KEYWORD')
        self.db_conn = sqlite3.connect(db_name,timeout=10)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self,spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        if isinstance(item,WeixinItem1):
            self.insert_db_weixinitem1(item)
        return item

    def insert_db_weixinitem1(self,item):
        values = (
            item.get('wid',''),
            item.get('title',''),
            item.get('text',''),
            item.get('time',''),
            item.get('source',''),
            item.get('search',''),
            item.get('url',''),
        )
        sql = 'INSERT INTO weixin_t1 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql,values)
        self.db_conn.commit()
