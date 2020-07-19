# -*- coding: utf-8 -*-
import sqlite3
from .items import DoubanMovieInfoItem, DoubanMovieCommentsItem, DoubanMovieReviewsItem, DoubanBookInfoItem, DoubanBookCommentsItem, DoubanBookReviewsItem
from .settings import SQLITE_DB_NAME


class DoubanPipeline(object):
    def __init__(self):
        self.db_conn = sqlite3.connect(SQLITE_DB_NAME, timeout=10)
        self.db_cur = self.db_conn.cursor()

    def close(self):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item):
        if isinstance(item, DoubanMovieInfoItem):
            self.insert_db_douban_movie_info_item(item)
        elif isinstance(item, DoubanMovieCommentsItem):
            self.insert_db_douban_movie_comments_item(item)
        elif isinstance(item, DoubanMovieReviewsItem):
            self.insert_db_douban_movie_reviews_item(item)
        elif isinstance(item, DoubanBookInfoItem):
            self.insert_db_douban_book_info_item(item)
        elif isinstance(item, DoubanBookCommentsItem):
            self.insert_db_douban_book_comments_item(item)
        elif isinstance(item, DoubanBookReviewsItem):
            self.insert_db_douban_book_reviews_item(item)
        return item

    def insert_db_douban_movie_info_item(self, item):
        values = (
            item.get('mid', ''),
            item.get('name', ''),
            item.get('alias', ''),
            item.get('directors', ''),
            item.get('scriptwriters', ''),
            item.get('actors', ''),
            item.get('types', ''),
            item.get('regions', ''),
            item.get('dates', ''),
            item.get('languages', ''),
            item.get('duration', ''),
            item.get('score', ''),
            item.get('description', ''),
            item.get('tags', ''),
            item.get('link', ''),
            item.get('poster', ''),
            item.get('star1', ''),
            item.get('star2', ''),
            item.get('star3', ''),
            item.get('star4', ''),
            item.get('star5', ''),
            item.get('votes', ''),
            item.get('comments', ''),
            item.get('reviews', ''),
            item.get('num', ''),
        )
        sql = 'INSERT INTO douban_movie_t1 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()

    def insert_db_douban_movie_comments_item(self, item):
        values = (
            item.get('mid', ''),
            item.get('cid', ''),
            item.get('uname', ''),
            item.get('text', ''),
            item.get('time', ''),
            item.get('score', ''),
            item.get('votes', ''),
        )
        sql = 'INSERT INTO douban_movie_t2 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()

    def insert_db_douban_movie_reviews_item(self, item):
        values = (
            item.get('mid', ''),
            item.get('rid', ''),
            item.get('uname', ''),
            item.get('title', ''),
            item.get('text', ''),
            item.get('time', ''),
            item.get('score', ''),
            item.get('numuseful', ''),
            item.get('numuseless', ''),
            item.get('numreply', ''),
        )
        sql = 'INSERT INTO douban_movie_t3 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()

    def insert_db_douban_book_info_item(self, item):
        values = (
            item.get('bid', ''),
            item.get('name', ''),
            item.get('alias', ''),
            item.get('subname', ''),
            item.get('authors', ''),
            item.get('authorintro', ''),
            item.get('translator', ''),
            item.get('producer', ''),
            item.get('series', ''),
            item.get('publisher', ''),
            item.get('date', ''),
            item.get('pages', ''),
            item.get('price', ''),
            item.get('binding', ''),
            item.get('isbn', ''),
            item.get('cover', ''),
            item.get('link', ''),
            item.get('tags', ''),
            item.get('summary', ''),
            item.get('score', ''),
            item.get('star1', ''),
            item.get('star2', ''),
            item.get('star3', ''),
            item.get('star4', ''),
            item.get('star5', ''),
            item.get('votes', ''),
            item.get('comments', ''),
            item.get('reviews', ''),
        )
        sql = 'INSERT INTO douban_book_t1 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()

    def insert_db_douban_book_comments_item(self, item):
        values = (
            item.get('bid', ''),
            item.get('cid', ''),
            item.get('uname', ''),
            item.get('text', ''),
            item.get('time', ''),
            item.get('score', ''),
            item.get('votes', ''),
        )
        sql = 'INSERT INTO douban_book_t2 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()

    def insert_db_douban_book_reviews_item(self, item):
        values = (
            item.get('bid', ''),
            item.get('rid', ''),
            item.get('uname', ''),
            item.get('title', ''),
            item.get('text', ''),
            item.get('time', ''),
            item.get('score', ''),
            item.get('numuseful', ''),
            item.get('numuseless', ''),
            item.get('numreply', ''),
        )
        sql = 'INSERT INTO douban_book_t3 VALUES(%s)' % ','.join(['?'] * len(values))
        self.db_cur.execute(sql, values)
        self.db_conn.commit()