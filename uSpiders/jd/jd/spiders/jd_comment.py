import scrapy
import json
import datetime
import sqlite3
import math
from scrapy.utils.project import get_project_settings
from ..items import CommentItem


class CommentSpider(scrapy.Spider):
    name = "CommentSpider"
    base_url = 'http://club.jd.com/comment/skuProductPageComments.action?callback=fetchJSON_comment98vv%s&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1'


    def start_requests(self):
        SETTINGS = get_project_settings()
        conn = sqlite3.connect(SETTINGS['SQLITE_DB_NAME'])
        cursor = conn.cursor()
        cursor.execute('''
                SELECT id,name,commentNum,commentVersion FROM product
                ''')

        for row in cursor.fetchall():
            self.pid = row[0]
            self.pname = row[1]
            self.commentNum = row[2]
            self.commentVersion = row[3]
            page_num = math.ceil(int(self.commentNum) / 10)
            page_num = page_num if page_num <= 100 else 100
            for i in range(page_num):
                url = self.base_url % (self.commentVersion,self.pid,i)
                yield scrapy.Request(url, callback=self.parse, dont_filter=True)

        cursor.close()
        conn.close()


    def parse(self, response):
        try:
            temp = str(response.body.decode(response.encoding)).strip()
            temp = temp.replace('fetchJSON_comment98vv'+self.commentVersion,'')
            js = json.loads(temp[1:-2])
            comments = js['comments']
        except:
            comments = []
        items = []
        for comment in comments:
            item = CommentItem()
            item['pid'] = self.pid
            item['pname'] = self.pname
            item['id'] = comment['id']
            item['nickname'] = comment['nickname']
            item['content'] = comment['content']
            item['creationTime'] = comment['creationTime']
            item['referenceTime'] = comment['referenceTime']
            item['days'] = comment['days']
            item['socre'] = comment['score']
            item['userClientShow'] = comment['userClientShow']
            item['userLevelName'] = comment['userLevelName']
            item['isMobile'] = comment['isMobile']
            item['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['afterDays'] = comment['afterDays']
            if int(item['afterDays']) > 0:
                item['afterTime'] = comment['afterUserComment']['created']
                item['afterContent'] = comment['afterUserComment']['hAfterUserComment']['content']
            else:
                item['afterTime'] = ''
                item['afterContent'] = ''
            item['productColor'] = comment['productColor']
            item['productSize'] = comment['productSize']
            item['imageCount'] = comment.get('imageCount','0')
            item['usefulVoteCount'] = comment['usefulVoteCount']
            item['replyCount'] = comment['replyCount']
            items.append(item)
        return items

