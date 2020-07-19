import scrapy
from ..items import NewsItem1
import sys
import re
import time
import datetime
from bs4 import BeautifulSoup
sys.path.append('/home/kylin/Documents/code/python/pycharm/BSAPI')
from extractors.v2.content import Article as Extractor1
from extractors.v1.extractor2 import Article as Extractor2


class NewsSpider1(scrapy.Spider):
    name = 'NewsSpider1'
    #keyword = '小米'

    def start_requests(self):
        #year = 2018
        #bt = int(time.mktime(time.strptime(str(year) + '-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")))
        #et = int(time.mktime(time.strptime(str(year) + '-12-31 00:00:00', "%Y-%m-%d %H:%M:%S")))
        #url = 'http://news.baidu.com/ns?rn=50&ie=utf-8&cl=2&ct=0&tn=newstitle&word=%s&bt=%s&et=%s' % (self.keyword, bt, et)
        #yield scrapy.Request(url,meta={'year':str(year)},callback=self.parse)

        for year in range(2008, 2019):
            bt = int(time.mktime(time.strptime(str(year)+'-01-01 00:00:00', "%Y-%m-%d %H:%M:%S")))
            et = int(time.mktime(time.strptime(str(year)+'-12-31 00:00:00', "%Y-%m-%d %H:%M:%S")))
            url = 'http://news.baidu.com/ns?rn=50&ie=utf-8&cl=2&ct=0&tn=newstitle&word=%s&bt=%s&et=%s' % (self.keyword,bt,et)
            yield scrapy.Request(url,meta={'year':str(year)},callback=self.parse)

    def parse(self, response):
        year = response.meta.get('year')
        selector = scrapy.Selector(response)
        divs = selector.xpath('//div[contains(@class,"result title")]')
        for div in divs:
            item = NewsItem1()
            item['search'] = self.keyword
            item['nid'] = self.keyword + '_' + year + '_' + div.attrib.get('id',str(int(time.time())))
            tag_a = div.xpath('h3/a')[0]
            item['url'] = tag_a.attrib.get('href','')
            item['title'] = ''.join(tag_a.xpath('.//text()').extract()).strip().replace('\n','')
            tag_div_text = div.xpath('div')[0].xpath('.//text()').extract()[0]
            st = [x.strip() for x in tag_div_text.split('\xa0') if x.strip()]
            #print(st)
            if len(st) == 0:
                item['source'] = ''
                time_tuple = -1,''
            elif len(st) == 1:
                temp = self._findTimeText(st)
                item['source'] = '' if temp[0] != -1 else st[0]
                time_tuple = temp
            else:
                item['source'] = st[0]
                time_tuple = self._findTimeText(st)
            try:
                extractor = Extractor1(item['url'],fetch_images=False)
                extractor.extract()
                item['text'] = extractor.text
                if not extractor.text:
                    try:
                        extractor = Extractor2(item['url'])
                        extractor.extract()
                        item['text'] = extractor.text
                    except:
                        continue
            except:
                try:
                    extractor = Extractor2(item['url'])
                    extractor.extract()
                    item['text'] = extractor.text
                except:
                    continue

            if time_tuple[0] == -1:
                item['time'] = ''
            elif time_tuple[0] == 3:
                item['time'] = time_tuple[1]
            else:
                soup = BeautifulSoup(extractor.html,'lxml')
                _ = [s.extract() for s in soup("script")]
                html_text_list = [x.strip() for x in soup.text.split('\n') if len(x.strip())>5]
                try:
                    istart = html_text_list.index(item['title'])
                except:
                    istart = 0
                len_list = [len(x) for x in html_text_list]
                iend = len_list.index(max(len_list)) + 1
                time_list = []
                for i,s in enumerate(html_text_list):
                    s2t = self._str2time(s)
                    if s2t:
                        time_list.append((i,s2t))

                time_list = self._findTime(time_list,time_tuple)
                if not time_list:
                    item['time'] = self._getTime(time_tuple)
                elif len(time_list) == 1:
                    item['time'] = time_list[0][1]
                else:
                    fl = [x for x in time_list if x[0] in range(istart,iend)]
                    if not fl:
                        item['time'] = time_list[0][1]
                    else:
                        item['time'] = fl[0][1]

            yield item

        next_url = selector.xpath('//p[@id="page"]/a[text()="下一页>"]').attrib.get('href')
        print(next_url)
        if next_url:
            next_url = 'http://news.baidu.com' + next_url
            yield scrapy.Request(url=next_url,meta={'year':year},callback=self.parse)



    def _findTimeText(self,slist):
        for s in slist:
            if s.find('秒前') != -1:
                return 0,s
            elif s.find('分钟前') != -1:
                return 1,s
            elif s.find('小时前') != -1:
                return 2,s
            else:
                try:
                    t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日 %H:%M'))
                    return 3,t
                except:
                    continue
            return -1,''

    def _findTime(self,time_list,time_tuple):
        return_list = []
        for t in time_list:
            t1 = datetime.datetime.now()
            t2 = datetime.datetime.strptime(t[1],'%Y-%m-%d %H:%M')
            dt = t1 - t2
            if time_tuple[0] == 0 or time_tuple[0] == 1:
                dtm = dt.seconds // 60
                dtm_ft = int(re.findall(r'\d+', time_tuple[1])[0])
                if dtm in range(dtm_ft - 5, dtm_ft + 6):
                    return_list.append(t)
            elif time_tuple[0] == 2:
                dth = dt.seconds // 3600
                dth_ft = int(re.findall(r'\d+', time_tuple[1])[0])
                if dth == dth_ft:
                    return_list.append(t)
        return return_list

    def _getTime(self,time_tuple):
        print(time_tuple)
        if time_tuple[0] == 0:
            t = datetime.datetime.now() - datetime.timedelta(seconds=int(re.findall(r'\d+', time_tuple[1])[0]))
            t = datetime.datetime.strftime(t,'%Y-%m-%d %H:%M')
            return t
        elif time_tuple[0] == 1:
            t = datetime.datetime.now() - datetime.timedelta(minutes=int(re.findall(r'\d+', time_tuple[1])[0]))
            t = datetime.datetime.strftime(t, '%Y-%m-%d %H:%M')
            return t
        elif time_tuple[0] == 2:
            t = datetime.datetime.now() - datetime.timedelta(hours=int(re.findall(r'\d+', time_tuple[1])[0]))
            t = datetime.datetime.strftime(t, '%Y-%m-%d %H:%M')
            return t


    def _str2time(self,s):
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日 %H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日 %H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日%H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日%H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y-%m-%d %H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y-%m-%d %H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime())+' %H:%M',time.strptime(s,'今天 %H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime())+' %H:%M',time.strptime(s,'今天%H:%M'))
            return t
        except:
            pass

        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime())+' %H:%M',time.strptime(s,'今天 %H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime())+' %H:%M',time.strptime(s,'今天%H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime(time.mktime(time.localtime()) - 86400))+' %H:%M',time.strptime(s,'昨天 %H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime(time.mktime(time.localtime()) - 86400))+' %H:%M',time.strptime(s,'昨天%H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime(time.mktime(time.localtime()) - 86400))+' %H:%M',time.strptime(s,'昨天 %H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y-%m-%d',time.localtime(time.mktime(time.localtime()) - 86400))+' %H:%M',time.strptime(s,'昨天%H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y',time.localtime())+'-%m-%d %H:%M',time.strptime(s,'%m-%d %H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y',time.localtime())+'-%m-%d %H:%M',time.strptime(s,'%m-%d %H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y',time.localtime())+'-%m-%d %H:%M',time.strptime(s,'%m月%d日 %H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y',time.localtime())+'-%m-%d %H:%M',time.strptime(s,'%m月%d日 %H:%M:%S'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y',time.localtime())+'-%m-%d %H:%M',time.strptime(s,'%m月%d日%H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime(time.strftime('%Y',time.localtime())+'-%m-%d %H:%M',time.strptime(s,'%m月%d日%H:%M:S'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日%H:%M'))
            return t
        except:
            pass
        try:
            t = time.strftime('%Y-%m-%d %H:%M',time.strptime(s,'%Y年%m月%d日%H:%M:%S'))
            return t
        except:
            return ''
