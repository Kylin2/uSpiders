import scrapy
from ..items import WeiboItem1,WeiboItem2
from ..settings import CHROME_DRIVER_PATH
import re
import json
import math
import requests
from selenium import webdriver
from bs4 import BeautifulSoup

class WeiboSpider1(scrapy.Spider):
    name = 'WeiboSpider1'
    #url = 'https://weibo.com/leijun'

    def start_requests(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('user-agent="Mozilla/5.0 (compatible;Baiduspider+(+http://www.baidu.com/search/spider.htm)"')
        executable_path = CHROME_DRIVER_PATH
        driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        driver.get(self.url)
        html = driver.page_source
        #print(html)
        driver.close()

        id = re.findall(r"\$CONFIG\['oid'\]='(\d+)'",html)[0]
        print(id)
        if id:
            item = WeiboItem1()
            item['uid'] = id
            selector = scrapy.Selector(text=html)
            li = selector.xpath('//li[@class="item S_line2 clearfix"]')
            if li.xpath('.//em[text()="2"]').extract():
                item['location'] = li.xpath('.//em[text()="2"]/parent::span/parent::li/span[2]/text()').extract()[0].strip()
            if li.xpath('.//em[text()="T"]').extract():
                item['labels'] = ' '.join(li.xpath('.//em[text()="T"]/parent::span/parent::li/span[2]//a/text()').extract())

            url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value='+id
            yield scrapy.Request(url,meta={'item':item},callback=self.parse_info,dont_filter=True)

    def parse_info(self,response):
        item = response.meta['item']
        data = json.loads(str(response.body.decode(response.encoding)))
        if data.get('ok') == 1:
            userInfo = data.get('data').get('userInfo')
            item['uname'] = userInfo.get('screen_name','')
            item['gender'] = userInfo.get('gender','')
            item['verified'] = str(userInfo.get('verified_type','-1'))
            item['verified_reason'] = userInfo.get('verified_reason','')
            item['friends_count'] = str(userInfo.get('follow_count','0'))
            item['followers_count'] = str(userInfo.get('folowers_count','0'))
            item['statuses_count'] = str(userInfo.get('statuses_count','0'))
            item['description'] = userInfo.get('description','')
            item['rank'] = str(userInfo.get('urank','0'))
            yield item

            tabs = data.get('data').get('tabsInfo').get('tabs')
            containerid = [x['containerid'] for x in tabs if x['tab_type'] == 'weibo'][0]

            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('user-agent="Mozilla/5.0 (compatible;Baiduspider+(+http://www.baidu.com/search/spider.htm)"')
            executable_path = CHROME_DRIVER_PATH
            driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)

            for i in range(1,math.ceil((int(item['statuses_count'])+110)/10)):
                url = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=%s&containerid=%s&page=%s' % (item['uid'],containerid,str(i))
                uid = item['uid']
                uname = item['uname']
                yield scrapy.Request(url,meta={'uid':uid,'uname':uname,'driver':driver},callback=self.parse)
            #driver.close()


    def parse(self, response):
        data = json.loads(str(response.body.decode(response.encoding)))
        if data.get('ok') == 1:
            cards = data.get('data').get('cards')
            if cards:
                for card in cards:
                    if card.get('card_type') == 9:
                        item = WeiboItem2()
                        item['uid'] = response.meta['uid']
                        item['uname'] = response.meta['uname']
                        driver = response.meta['driver']
                        mblog = card.get('mblog')
                        item['wid'] = str(mblog.get('id',''))
                        if mblog.get('isLongText') == True:
                            if mblog.get('longText'):
                                text = mblog.get('longText').get('longTextContent')
                            else:
                                html = requests.get(card.get('scheme')).text
                                rd = re.findall(r'var \$render_data = \[\{([\s\S]*)\}\]', html)
                                if rd:
                                    text = json.loads('{'+rd[0]+'}').get('status').get('text')
                                else:
                                    text = ''
                        else:
                            text = mblog.get('text')
                        soup = BeautifulSoup(text,'lxml')
                        spans = soup.find_all('span',class_='url-icon')
                        for span in spans:
                            try:
                                new_tag = soup.new_tag('newtag')
                                new_tag.string = span.img.get('alt')
                                span.replace_with(new_tag)
                            except:
                                continue
                        item['text'] = soup.get_text().strip()
                        item['share_count'] = str(mblog.get('reposts_count','0'))
                        item['comments_count'] = str(mblog.get('comments_count','0'))
                        item['zan_count'] = str(mblog.get('attitudes_count','0'))
                        item['source'] = mblog.get('source','')
                        driver.get('https://weibo.com/%s/%s' % (item['uid'],mblog.get('bid','')))
                        html = driver.page_source
                        selector = scrapy.Selector(text=html)
                        time = selector.xpath('//a[@name="' + item['wid'] + '"]/@title').extract_first()
                        if time:
                            item['time'] = time
                        else:
                            item['time'] = mblog.get('created_at','')
                        yield item



