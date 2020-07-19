import requests
import scrapy
import re
import types
import time
from PIL import Image
from .items import DoubanBookInfoItem, DoubanBookCommentsItem, DoubanBookReviewsItem
from .pipelines import DoubanPipeline
from bs4 import BeautifulSoup


class DoubanBookSpider(object):
    def __init__(self):
        self.session = self._get_session_by_login()

    def _get_session_by_login(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
        session = requests.session(headers=headers)
        url = 'https://accounts.douban.com/login'
        res = session.get(url)
        res_html = self._response_decode(res)
        selector = scrapy.Selector(text=res_html)
        img_captcha = selector.xpath('//img[@id="captcha_image"]')
        captcha_id = ''
        captcha_solution = ''
        if img_captcha:
            img_captcha_url = img_captcha[0].attrib.get('src')
            captcha_id = re.findall(r'id=(.*:en)', img_captcha_url)[0]
            res_captcha = session.get(img_captcha_url)
            captcha_solution = self._identify_captcha(res_captcha.content)
        form_email, form_password = self._input_user_info()
        data = {
            'source': 'movie',
            'redir': 'https://movie.douban.com/',
            'form_email': form_email,
            'form_password': form_password,
            'captcha-solution': captcha_solution,
            'captcha-id': captcha_id,
            'login': '登录',
        }
        res = session.post(url, data)
        if res.url != 'https://movie.douban.com/':
            print('login failed')
            return None
        print('logined')
        return session

    def _response_decode(self, response):
        if response.encoding != 'ISO-8859-1':
            html = response.text
        else:
            html = response.content
            if 'charset' not in response.headers.get('content-type'):
                encodings = requests.utils.get_encodings_from_content(response.text)
                if len(encodings) > 0:
                    response.encoding = encodings[0]
                    html = response.text
        return html or ''

    def _identify_captcha(self, captcha_content):
        with open('./douban/temp/captcha.png', 'wb') as f:
            f.write(captcha_content)
        img = Image.open('./douban/temp/captcha.png')
        img.show()
        return input('please input captcha:')

    def _input_user_info(self):
        return input('please input email:'), input('please input passsword:')

    def _save(self, items_generator, saver):
        for x in items_generator:
            if isinstance(x, types.GeneratorType):
                self._save(list(x), saver)
            else:
                try:
                    saver.process_item(x)
                except:
                    continue

    def parse_book(self, bids, isinfo=True, iscomments=False, isreviews=False):
        if isinfo:
            self._parse_book_info(bids)
        if iscomments:
            self._parse_book_comments(bids)
        if isreviews:
            self._parse_book_reviews(bids)

    def _parse_book_info(self, bids):
        saver = DoubanPipeline()
        for bid in bids:
            try:
                item = self._parse_book_info_item(bid)
                if item:
                    self._save([item], saver)
            except:
                print(bid + ' info error')
                continue

    def _parse_book_info_item(self, bid):
        url = 'https://book.douban.com/subject/%s/' % bid
        item = DoubanBookInfoItem()
        item['bid'] = bid
        item['link'] = url
        res = self.session.get(url, allow_redirects=False)
        html = self._response_decode(res)
        if not res.ok or html.find('页面不存在') != -1 or len(html) < 500:
            print('no content')
            return None
        selector = scrapy.Selector(text=html)
        item['name'] = ''.join(selector.xpath('.//div[@id="wrapper"]/h1/span[@property="v:itemreviewed"]/text()').extract()).strip()
        content = selector.xpath('.//div[@id="content"]')
        if not content:
            print('a')
            return None
        content = content[0]
        article = content.xpath('.//div[@class="article"]')
        if not article:
            print('b')
            return None
        article = article[0]
        article_subject = article.xpath('./div[contains(@class,"indent")]/div[contains(@class,"subjectwrap")]/div[contains(@class,"subject")]')[0]
        item['cover'] = article_subject.xpath('./div[@id="mainpic"]//img').attrib.get('src')
        article_subject_info = article_subject.xpath('./div[@id="info"]')[0]
        item['authors'] = ','.join([s.strip() for s in article_subject_info.xpath('./span/span[contains(text(),"作者")]/following-sibling::a/text()').extract()])
        publisher = article_subject_info.xpath('./span[contains(text(),"出版社")]/following-sibling::text()[following-sibling::br]').extract()
        if publisher:
            item['publisher'] = publisher[0].strip()
        alias = article_subject_info.xpath('./span[contains(text(),"原作名")]/following-sibling::text()[following-sibling::br]').extract()
        if alias:
            item['alias'] = alias[0].strip()
        subname = article_subject_info.xpath('./span[contains(text(),"副标题")]/following-sibling::text()[following-sibling::br]').extract()
        if subname:
            item['subname'] = subname[0].strip()
        item['translator'] = ','.join([s.strip() for s in article_subject_info.xpath('./span/span[contains(text(),"译者")]/following-sibling::a/text()').extract()])
        date = article_subject_info.xpath('./span[contains(text(),"出版年")]/following-sibling::text()[following-sibling::br]').extract()
        if date:
            item['date'] = date[0].strip()
        pages = article_subject_info.xpath('./span[contains(text(),"页数")]/following-sibling::text()[following-sibling::br]').extract()
        if pages:
            item['pages'] = pages[0].strip()
        price = article_subject_info.xpath('./span[contains(text(),"定价")]/following-sibling::text()[following-sibling::br]').extract()
        if price:
            item['price'] = price[0].strip()
        binding = article_subject_info.xpath('./span[contains(text(),"装帧")]/following-sibling::text()[following-sibling::br]').extract()
        if binding:
            item['binding'] = binding[0].strip()
        isbn = article_subject_info.xpath('./span[contains(text(),"ISBN")]/following-sibling::text()[following-sibling::br]').extract()
        if isbn:
            item['isbn'] = isbn[0].strip()
        producer = article_subject_info.xpath('./span[contains(text(),"出品方")]/following-sibling::a[following-sibling::br]').extract()
        if producer:
            item['producer'] = producer[0].strip()
        series = article_subject_info.xpath('./span[contains(text(),"丛书")]/following-sibling::a[following-sibling::br]').extract()
        if series:
            item['series'] = series[0].strip()
        article_interest = article.xpath('./div[contains(@class,"indent")]/div[contains(@class,"subjectwrap")]/div[@id="interest_sectl"]')[0]
        score = article_interest.xpath('.//strong[@property="v:average"]/text()').extract_first()
        item['score'] = score.strip() if score else ''
        votes = article_interest.xpath('.//span[@property="v:votes"]/text()').extract_first()
        item['votes'] = votes.strip() if votes else ''
        stars = article_interest.xpath('.//div[contains(@class,"rating_wrap")]//span[@class="rating_per"]/text()').extract()
        item['star5'], item['star4'], item['star3'], item['star2'], item['star1'] = stars if stars else ['']*5
        related_info = article.xpath('./div[@class="related_info"]')[0]
        summary = ''.join([s.strip() for s in related_info.xpath('./div[@id="link-report"]/span[contains(@class,"all")]//div[@class="intro"]//text()').extract()])
        if not summary:
            summary = ''.join([s.strip() for s in related_info.xpath('./div[@id="link-report"]//div[@class="intro"]//text()').extract()])
        item['summary'] = summary
        authorintro = ''.join([s.strip() for s in related_info.xpath('./h2[child::span[contains(text(),"作者简介")]]/following-sibling::div[@class="indent "]/span[contains(@class,"all")]//div[@class="intro"]//text()').extract()])
        if not authorintro:
            authorintro = ''.join([s.strip() for s in related_info.xpath('./h2[child::span[contains(text(),"作者简介")]]/following-sibling::div[@class="indent "]//div[@class="intro"]//text()').extract()])
        item['authorintro'] = authorintro
        item['tags'] = ','.join([s.strip() for s in related_info.xpath('./div[@id="db-tags-section"]//a[contains(@class,"tag")]/text()').extract()])
        comments = ''.join([s.strip() for s in related_info.xpath('./div[@class="mod-hd"]/h2/span[contains(text(),"短评")]/following-sibling::span/a/text()').extract()])
        comments = re.findall(r'全部 (\d+) 条', comments)
        item['comments'] = comments[0] if comments else '0'
        reviews = ''.join([s.strip() for s in related_info.xpath('./section[contains(@class,"reviews")]/header/h2/span/a/text()').extract()])
        reviews = re.findall(r'全部 (\d+) 条', reviews)
        item['reviews'] = reviews[0] if reviews else '0'
        return item

    def _parse_book_comments(self, bids):
        saver = DoubanPipeline()
        for bid in bids:
            url = 'https://book.douban.com/subject/%s/comments/hot' % bid
            comments_generator = list(self._parse_book_comments_item(url, bid))
            self._save(comments_generator, saver)
            time.sleep(1)

    def _parse_book_comments_item(self, url, bid):
        response = self.session.get(url)
        html = self._response_decode(response)
        selector = scrapy.Selector(text=html)
        divs = selector.xpath('.//div[@id="comments"]//li[@class="comment-item"][@data-cid]')
        for div in divs:
            try:
                cid = div.attrib.get('data-cid')
                if not cid:
                    continue
                item = DoubanBookCommentsItem()
                item['bid'] = bid
                item['cid'] = cid
                item['uname'] = div.xpath('./div[@class="avatar"]/a').attrib.get('title')
                comment = div.xpath('./div[@class="comment"]')
                item['votes'] = ''.join(comment.xpath('./h3/span[@class="comment-vote"]/span[@class="vote-count"]/text()').extract()).strip()
                if not item['uname']:
                    item['uname'] = ''.join(comment.xpath('./h3/span[@class="comment-info"]/a/text()').extract()).strip()
                item['time'] = ''.join(comment.xpath('./h3/span[@class="comment-info"]/span[not(@class)]/text()').extract()).strip()
                score = str(comment.xpath('./h3/span[@class="comment-info"]/span[contains(@class,"rating")]').attrib.get('class'))
                score = re.findall(r'allstar(\d{1})0 rating', score)
                item['score'] = score[0] if score else ''
                item['text'] = ''.join([s.strip() for s in comment.xpath('./p/span[@class="short"]//text()').extract()]).strip()
                yield item
            except:
                print(bid + ' comments error')
                continue

        time.sleep(0.5)
        next_url = selector.xpath('.//div[@class="paginator-wrapper"]/ul[@class="comment-paginator"]//a[@class="page-btn" and text()="后一页"]').attrib.get('href')
        if next_url:
            next_url = 'https://book.douban.com/subject/%s/comments/' % bid + next_url
            yield self._parse_book_comments_item(next_url, bid)



    def _parse_book_reviews(self, bids):
        saver = DoubanPipeline()
        for bid in bids:
            url = 'https://book.douban.com/subject/%s/reviews' % bid
            reviews_generator = list(self._parse_book_reviews_item(url, bid))
            self._save(reviews_generator, saver)
            time.sleep(1)



    def _parse_book_reviews_item(self, url, bid):
        response = self.session.get(url)
        html = self._response_decode(response)
        selector = scrapy.Selector(text=html)
        divs = selector.xpath('.//div[@id="content"]//div[@class="article"]/div[contains(@class,"review-list")]//div[@data-cid]')
        for div in divs:
            try:
                item = DoubanBookReviewsItem()
                item['bid'] = bid
                item['rid'] = div.attrib.get('data-cid')
                item['uname'] = ''.join(div.xpath('.//header[@class="main-hd"]/a[@class="name"]/text()').extract()).strip()
                score = str(div.xpath('.//header[@class="main-hd"]/span[contains(@class,"main-title-rating")]').attrib.get('class'))
                print(bid, score)
                score = re.findall(r'allstar(\d{1})0 main-title-rating', score)
                item['score'] = score[0] if score else ''
                item['time'] = ''.join(div.xpath('.//header[@class="main-hd"]/span[@class="main-meta"]/text()').extract()).strip()
                item['title'] = ''.join(div.xpath('.//div[@class="main-bd"]/h2/a/text()').extract()).strip()
                numreply = ''.join(div.xpath('.//div[@class="main-bd"]//a[@class="reply"]/text()').extract()).strip()
                numreply = re.findall(r'(\d+)回应', numreply)
                item['numreply'] = numreply[0] if numreply else '0'
                try:
                    js = self.session.get('https://book.douban.com/j/review/%s/full' % item['rid']).json()
                    if js:
                        item['text'] = BeautifulSoup(js.get('html', ''), 'lxml').get_text()
                        item['numuseful'] = js.get('votes').get('useful_count') or '0'
                        item['numuseless'] = js.get('votes').get('useless_count') or '0'
                except:
                    item['text'] = ''.join([s.strip() for s in div.xpath('.//div[@class="main-bd"]//div[@class="short-content"]//text()').extract()])
                    item['numuseful'] = ''.join([s.strip() for s in div.xpath('.//div[@class="main-bd"]//a[@class="action-btn up"]//text()').extract()]) or '0'
                    item['numuseless'] = ''.join([s.strip() for s in div.xpath('.//div[@class="main-bd"]//a[@class="action-btn down"]//text()').extract()]) or '0'
                yield item
            except:
                print(bid+' reviews error')
                continue

        time.sleep(0.5)
        next_url = selector.xpath('.//div[@id="content"]//div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a').attrib.get('href')
        if next_url:
            next_url = 'https://book.douban.com/subject/%s/reviews' % bid + next_url
            yield self._parse_book_reviews_item(next_url, bid)