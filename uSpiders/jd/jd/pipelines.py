# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
from twisted.enterprise import adbapi
from .items import ProductItem,CommentItem


class JdSpiderPipeline(object):
    def process_item(self, item, spider):
        return item

class PCPipeline(object):
    def open_spider(self,spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')
        spider.keyword = spider.settings.get('KEYWORD')
        spider.lprice = spider.settings.get('LPRICE')
        spider.hprice = spider.settings.get('HPRICE')
        self.db_conn = sqlite3.connect(db_name,timeout=10)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self,spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self,item,spider):
        if isinstance(item,ProductItem):
            self.insert_db_product(item)
        else:
            self.insert_db_comment(item)
        return item

    def insert_db_product(self,item):
        values = (
            item['id'],
            item['link'],
            item['name'],
            item['commentNum'],
            item['shopName'],
            item['price'],
            item['commentVersion'],
            item['score1count'],
            item['score2count'],
            item['score3count'],
            item['score4count'],
            item['score5count'],
            item['brand'],
            item['time'],
        )

        sql = 'INSERT INTO product VALUES(%s)' % ','.join(['?']*len(values))
        self.db_cur.execute(sql,values)
        self.db_conn.commit()

    def insert_db_comment(self,item):
        values = (
            item['id'],
            item['pid'],
            item['pname'],
            item['nickname'],
            item['content'],
            item['creationTime'],
            item['referenceTime'],
            item['days'],
            item['socre'],
            item['userClientShow'],
            item['userLevelName'],
            item['isMobile'],
            item['afterDays'],
            item['afterTime'],
            item['afterContent'],
            item['productColor'],
            item['productSize'],
            item['imageCount'],
            item['usefulVoteCount'],
            item['replyCount'],
            item['time'],
        )

        sql = 'INSERT INTO comment VALUES(%s)' % ','.join(['?']*len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()

'''
class PCPipeline(object):
    def open_spider(self,spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')
        spider.keyword = spider.settings.get('KEYWORD')
        spider.lprice = spider.settings.get('LPRICE')
        spider.hprice = spider.settings.get('HPRICE')
        self.dbpool = adbapi.ConnectionPool('sqlite3',db_name,check_same_thread=True)

    def close_spider(self,spider):
        self.dbpool.close()

    def process_item(self,item,spider):
        if isinstance(item,ProductItem):
            self.dbpool.runInteraction(self.insert_db_product,item)
        else:
            self.dbpool.runInteraction(self.insert_db_comment,item)
        return item

    def insert_db_product(self,tx,item):
        values = (
            item['id'],
            item['link'],
            item['name'],
            item['commentNum'],
            item['shopName'],
            item['price'],
            item['commentVersion'],
            item['score1count'],
            item['score2count'],
            item['score3count'],
            item['score4count'],
            item['score5count'],
            item['time'],
        )

        sql = 'INSERT INTO product VALUES(%s)' % ','.join(['?']*len(values))
        tx.execute(sql,values)

    def insert_db_comment(self,tx,item):
        values = (
            item['id'],
            item['pid'],
            item['pname'],
            item['nickname'],
            item['content'],
            item['creationTime'],
            item['referenceTime'],
            item['days'],
            item['socre'],
            item['userClientShow'],
            item['userLevelName'],
            item['isMobile'],
            item['afterDays'],
            item['afterTime'],
            item['afterContent'],
            item['productColor'],
            item['productSize'],
            item['imageCount'],
            item['usefulVoteCount'],
            item['replyCount'],
            item['time'],
        )

        sql = 'INSERT INTO comment VALUES(%s)' % ','.join(['?']*len(values))
        tx.execute(sql,values)
'''

class ProductPipeline(object):
    def open_spider(self,spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')
        spider.keyword = spider.settings.get('KEYWORD')
        spider.lprice = spider.settings.get('LPRICE')
        spider.hprice = spider.settings.get('HPRICE')
        self.dbpool = adbapi.ConnectionPool('sqlite3',db_name,check_same_thread=False)

    def close_spider(self,spider):
        self.dbpool.close()

    def process_item(self,item,spider):
        self.dbpool.runInteraction(self.insert_db,item)
        return item

    def insert_db(self,tx,item):
        values = (
            item['id'],
            item['link'],
            item['name'],
            item['commentNum'],
            item['shopName'],
            item['price'],
            item['commentVersion'],
            item['score1count'],
            item['score2count'],
            item['score3count'],
            item['score4count'],
            item['score5count'],
            item['time'],
        )

        sql = 'INSERT INTO product VALUES(%s)' % ','.join(['?']*len(values))
        tx.execute(sql,values)

class CommentPipeline(object):

    def open_spider(self,spider):
        db_name = spider.settings.get('SQLITE_DB_NAME')
        self.dbpool = adbapi.ConnectionPool('sqlite3',db_name,check_same_thread=False)

    def close_spider(self,spider):
        self.dbpool.close()

    def process_item(self,item,spider):
        self.dbpool.runInteraction(self.insert_db,item)
        return item

    def insert_db(self,tx,item):
        values = (
            item['id'],
            item['pid'],
            item['pname'],
            item['nickname'],
            item['content'],
            item['creationTime'],
            item['referenceTime'],
            item['days'],
            item['socre'],
            item['userClientShow'],
            item['userLevelName'],
            item['isMobile'],
            item['afterDays'],
            item['afterTime'],
            item['afterContent'],
            item['productColor'],
            item['productSize'],
            item['imageCount'],
            item['usefulVoteCount'],
            item['replyCount'],
            item['time'],
        )

        sql = 'INSERT INTO comment VALUES(%s)' % ','.join(['?']*len(values))
        tx.execute(sql,values)
