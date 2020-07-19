import scrapy
from ..items import ProductItem
import re
import json
import datetime

class ProductSpider(scrapy.Spider):
    name = "SProductSpider"


    def start_requests(self):
        ids = [('小米',['7652141','7437762','7437764','7652143']),('荣耀',['7348365','7134340','7134314','7348389','8521274']),('华为',['8026728','8240587','8026730','8026710','8026726']),('OPPO',['100000435251','100000400128','100001332646']),('VIVO',['6708229','6494554']),('魅族',['8441386','8654291','100000504504'])]
        for x in ids:
            brand = x[0]
            for y in x[1]:
                item = ProductItem()
                item['id'] = y
                item['brand'] = brand
                item['link'] = 'https://item.jd.com/%s.html' % y
                yield scrapy.Request(item['link'],meta={'item':item},callback=self.parse)


    def parse_price(self,response):
        item = response.meta['item']
        js = json.loads(str(response.body.decode(response.encoding))[1:-2])
        item['price'] = js['p']
        item['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return item

    def parse_comment_num(self,response):
        item = response.meta['item']
        js = json.loads(str(response.body.decode(response.encoding)))
        item['score1count'] = js['CommentsCount'][0]['Score1Count']
        item['score2count'] = js['CommentsCount'][0]['Score2Count']
        item['score3count'] = js['CommentsCount'][0]['Score3Count']
        item['score4count'] = js['CommentsCount'][0]['Score4Count']
        item['score5count'] = js['CommentsCount'][0]['Score5Count']
        item['commentNum'] = js['CommentsCount'][0]['CommentCount']

        url = 'http://p.3.cn/prices/mgets?skuIds=J_%s' % str(item['id'])
        yield scrapy.Request(url,meta={'item':item},callback=self.parse_price)


    def parse(self, response):
        item = response.meta['item']
        selector = scrapy.Selector(response)
        item['shopName'] = selector.xpath('//div[@class="item"]/div[@class="name"]/a//text()').extract_first().strip()
        item['name'] = ''.join(selector.xpath('//div[@class="itemInfo-wrap"]/div[@class="sku-name"]/text()').extract()).strip()
        item['commentVersion'] = re.search(r"commentVersion:\'(\d+)\'",str(response.body.decode(response.encoding))).group(1)
        url = 'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=' + item['id']
        yield scrapy.Request(url, meta={'item': item}, callback=self.parse_comment_num)