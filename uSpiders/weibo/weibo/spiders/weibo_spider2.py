import scrapy
from ..items import WeiboItem2
from ..settings import CHROME_DRIVER_PATH
import re
import json
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import quote


class WeiboSpider1(scrapy.Spider):
    name = 'WeiboSpider2'
    #keyword = '雷军'

    def start_requests(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('user-agent="Mozilla/5.0 (compatible;Baiduspider+(+http://www.baidu.com/search/spider.htm)"')
        executable_path = CHROME_DRIVER_PATH
        driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
        for i in range(1,10):
            url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103%s&page_type=searchall&page=%s' % (quote('type=1&q='+self.keyword),str(i))
            yield scrapy.Request(url,meta={'driver':driver},callback=self.parse,dont_filter=True)


    def parse(self, response):
        driver = response.meta['driver']
        data = json.loads(str(response.body.decode(response.encoding)))
        if data.get('ok') == 1:
            cards = data.get('data').get('cards')
            for card in cards:
                card_group = card.get('card_group',[])
                for c in card_group:
                    if c.get('card_type') == 9:
                        item = WeiboItem2()
                        mblog = c.get('mblog')
                        item['uid'] = str(mblog.get('user').get('id', ''))
                        item['uname'] = mblog.get('user').get('screen_name','')
                        item['wid'] = str(mblog.get('id', ''))
                        if mblog.get('isLongText') == True:
                            if mblog.get('longText'):
                                text = mblog.get('longText').get('longTextContent')
                            else:
                                html = requests.get(c.get('scheme')).text
                                rd = re.findall(r'var \$render_data = \[\{([\s\S]*)\}\]', html)
                                if rd:
                                    text = json.loads('{'+rd[0]+'}').get('status').get('text')
                                else:
                                    text = ''
                        else:
                            text = mblog.get('text')
                        soup = BeautifulSoup(text,'lxml')
                        spans = soup.find_all('span', class_='url-icon')
                        for span in spans:
                            try:
                                new_tag = soup.new_tag('newtag')
                                new_tag.string = span.img.get('alt')
                                span.replace_with(new_tag)
                            except:
                                continue
                        item['text'] = soup.get_text().strip()
                        item['share_count'] = str(mblog.get('reposts_count', '0'))
                        item['comments_count'] = str(mblog.get('comments_count', '0'))
                        item['zan_count'] = str(mblog.get('attitudes_count', '0'))
                        item['source'] = mblog.get('source', '')
                        driver.get('https://weibo.com/%s/%s' % (item['uid'], mblog.get('bid', '')))
                        html = driver.page_source
                        selector = scrapy.Selector(text=html)
                        time = selector.xpath('//a[@name="' + item['wid'] + '"]/@title').extract_first()
                        if time:
                            item['time'] = time
                        else:
                            item['time'] = mblog.get('created_at', '')
                        yield item
