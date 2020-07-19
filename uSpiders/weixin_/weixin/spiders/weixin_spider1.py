import scrapy
from ..items import WeixinItem1
import sys
import re
import json
import requests
import time
import datetime
from bs4 import BeautifulSoup
from ..settings import COOKIE

class WeixinSpider1(scrapy.Spider):
    name = 'WeixinSpider1'
    keyword = '雷军'
    start_time = '2018-12-18'
    end_time = '2018-12-18'
    n = 3

    def start_requests(self):
        st = int(time.mktime(time.strptime(self.start_time,'%Y-%m-%d')))
        et = int(time.mktime(time.strptime(self.end_time,'%Y-%m-%d')))
        assert st <= et
        for t in range(st,et+1,86400):
            st = time.strftime('%Y-%m-%d', time.localtime(t))

            url = 'https://weixin.sogou.com/weixin?type=2&ie=utf8&query=%s&tsn=5&ft=%s&et=%s&interation=&wxid=&usip=' % (self.keyword,st,st)
            yield scrapy.Request(url,cookies=self._get_cookie(),callback=self.parse_captcha_html)

    def parse_captcha_html(self,response):
        html = str(response.body.decode(response.encoding))
        cookies = response.cookies
        s1 = '请输入验证码'
        s2 = 'antispider'
        if s1 in html:
            url = 'http://weixin.sogou.com/antispider/util/seccode.php?tc=%s' % str(int(round(time.time() * 1000)))
            yield scrapy.Request(url,meta={'html':html,'s':s1},cookies=cookies,callback=self.parse_captcha)
        elif s2 in response.url:
            url = 'http://weixin.sogou.com/antispider/util/seccode.php?tc=%s' % str(int(round(time.time() * 1000)))
            yield scrapy.Request(url, meta={'html': html, 's': s2},cookies=cookies,callback=self.parse_captcha)
        else:
            yield scrapy.Request()

    def parse_captcha(self,response):




    def parse(self,response):
        selector = scrapy.Selector(response)
        lis = selector.xpath('//div[@class="news-box"]/ul[@class="news-list"]/li')
        print(lis)
        print(selector.xpath('//div[@class="news-box"]/ul[@class="news-list"]//text()').extract())


    def _get_cookie(self,suv='',snuid=''):
        suv = COOKIE.get('SUV') if not suv else suv
        snuid = COOKIE.get('SNUID') if snuid else snuid
        return {'SUV':suv,'SNUID':snuid}

    def _set_cookie(self,suv,snuid):
        COOKIE['SUV'] = suv
        COOKIE['SNUID'] = snuid
