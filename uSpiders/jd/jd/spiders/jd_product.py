import scrapy
from scrapy_splash import SplashRequest
from ..items import ProductItem
import re
import json
import datetime

lua_script = '''
function main(splash)
    assert(splash:go(splash.args.url))
    assert(splash:wait(15))
    splash:runjs("document.getElementsByClassName('page')[0].scrollIntoView(true)")
    assert(splash:wait(5))
    return splash:html()
end
'''

class ProductSpider(scrapy.Spider):
    name = "ProductSpider"
    #allowed_domains = ["search.jd.com"]
    #keyword = "小米手机"
    #base_url = "https://search.jd.com/Search?keyword=%s&enc=utf-8&wq=%s" % (keyword,keyword)


    def start_requests(self):
        self.base_url = "https://search.jd.com/Search?keyword=%s&enc=utf-8&wq=%s" % (self.keyword, self.keyword)
        yield scrapy.Request(self.base_url,callback=self.parse_urls,dont_filter=True)

    '''
    def parse_urls(self,response):
        for i in range(1):
            url = "%s&page=%s" % (self.base_url, 2 * i + 1)
            yield scrapy.Request(url)
    '''
    def parse_urls(self,response):
        page_sum = int(response.css('span.fp-text i::text').extract_first())
        for i in range(10):
            url = "%s&page=%s" %(self.base_url,2*i+1)
            yield SplashRequest(url,
                                endpoint='execute',
                                args={'lua_source':lua_script},
                                cache_args=['lua_source'])

    def parse_price(self,response):
        item = response.meta['item']
        js = json.loads(str(response.body.decode(response.encoding))[1:-2])
        item['price'] = js['op']

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


    def parse_detail(self,response):
        item = response.meta['item']
        selector = scrapy.Selector(response)
        item['commentVersion'] = re.search(r"commentVersion:\'(\d+)\'", str(response.body.decode(response.encoding))).group(1)

        url = 'http://club.jd.com/clubservice.aspx?method=GetCommentsCount&referenceIds=' + item['id']
        yield scrapy.Request(url,meta={'item':item},callback=self.parse_comment_num)

    def parse(self, response):
        selector = scrapy.Selector(response)
        products = selector.xpath('//li[@class="gl-item"]')
        for product in products:
            item = ProductItem()
            item['id'] = product.xpath('.//div[@class="p-img"]/a/@onclick').extract_first().split(',')[1]
            item['link'] = 'http://item.jd.com/%s.html' % item['id']
            item['name'] = ''.join(product.xpath('.//div[contains(@class,"p-name")]/a/em//text()').extract())
            item['shopName'] = product.xpath('.//div[@class="p-shop"]/span/a/text()').extract_first()
            if not item['shopName']:
                item['shopName'] = ''.join(product.xpath('.//div[@class="p-shopnum"]//text()').extract()).strip()
            #item['price'] = product.xpath('.//div[@class="p-price"]/i/text()').extract_first()
            item['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            url = item['link']
            yield scrapy.Request(url,meta={'item':item},callback=self.parse_detail)

