# -*- coding: utf-8 -*-
import sqlite3
from .items import WeixinItem1
from .settings import SQLITE_DB_NAME


class WeixinPipeline(object):
    def __init__(self):
        self.db_conn = sqlite3.connect(SQLITE_DB_NAME,timeout=10)
        self.db_cur = self.db_conn.cursor()

    def close(self):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self,item):
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
