import requests
import scrapy
import re
import types
import time
from PIL import Image
from .items import DoubanMovieInfoItem, DoubanMovieCommentsItem, DoubanMovieReviewsItem
from .pipelines import DoubanPipeline
from bs4 import BeautifulSoup


class DoubanMovieSpider(object):
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

    def parse_movie(self, mids, isinfo=True, iscomments=False, isreviews=False):
        if isinfo:
            self._parse_movie_info(mids)
        if iscomments:
            self._parse_movie_comments(mids)
        if isreviews:
            self._parse_movie_reviews(mids)

    def _parse_movie_info(self, mids):
        saver = DoubanPipeline()
        for mid in mids:
            try:
                item = self._parse_movie_info_item(mid)
                if item:
                    self._save([item], saver)
            except:
                print(mid + ' info error')
                continue

    def _parse_movie_info_item(self, mid):
        url = 'https://movie.douban.com/subject/%s/' % mid
        item = DoubanMovieInfoItem()
        item['mid'] = mid
        item['link'] = url
        item['num'] = '1'
        res = self.session.get(url, allow_redirects=False)
        html = self._response_decode(res)
        if not res.ok or html.find('页面不存在') != -1 or len(html) < 500:
            print('no content')
            return None
        selector = scrapy.Selector(text=html)
        content = selector.xpath('.//div[@id="content"]')
        if not content:
            print('a')
            return None
        content = content[0]
        item['name'] = ''.join([s.strip() for s in content.xpath('./h1//text()').extract()])
        article = content.xpath('.//div[@class="article"]')
        if not article:
            print('b')
            return None
        article = article[0]
        article_subject = article.xpath('./div[contains(@class,"indent")]/div[contains(@class,"subjectwrap")]/div[contains(@class,"subject")]')[0]
        item['poster'] = article_subject.xpath('./div[@id="mainpic"]//img').attrib.get('src')
        article_subject_info = article_subject.xpath('./div[@id="info"]')[0]
        item['directors'] = ','.join([s.strip() for s in article_subject_info.xpath('.//a[@rel="v:directedBy"]//text()').extract()])
        item['actors'] = ','.join([s.strip() for s in article_subject_info.xpath('.//a[@rel="v:starring"]//text()').extract()])
        item['types'] = ','.join([s.strip() for s in article_subject_info.xpath('.//span[@property="v:genre"]//text()').extract()])
        item['dates'] = ','.join([s.strip() for s in article_subject_info.xpath('.//span[@property="v:initialReleaseDate"]//text()').extract()])
        item['duration'] = ','.join([s.strip() for s in article_subject_info.xpath('.//span[@property="v:runtime"]//text()').extract()])
        item['scriptwriters'] = ','.join([s.strip() for s in article_subject_info.xpath('./span/span[text()="编剧"]/following-sibling::span[@class="attrs"]//text()').extract() if s.strip() != '/'])
        soup = BeautifulSoup(html, 'lxml')
        info = soup.find('div', id='info').contents
        for i in range(len(info)):
            if len(str(info[i])) < 10:
                continue
            if str(info[i]).find('制片国家/地区:') != -1:
                item['regions'] = ','.join([s.strip() for s in str(info[i + 1]).split('/')])
            if str(info[i]).find('语言:') != -1:
                item['languages'] = ','.join([s.strip() for s in str(info[i + 1]).split('/')])
            if str(info[i]).find('又名:') != -1:
                item['alias'] = ','.join([s.strip() for s in str(info[i + 1]).split('/')])
            if str(info[i]).find('集数:') != -1:
                item['num'] = ','.join([s.strip() for s in str(info[i + 1]).split('/')])
            if str(info[i]).find('单集片长:') != -1:
                item['duration'] = ','.join([s.strip() for s in str(info[i + 1]).split('/')])
        article_interest = article.xpath('./div[contains(@class,"indent")]/div[contains(@class,"subjectwrap")]/div[@id="interest_sectl"]')[0]
        score = article_interest.xpath('.//strong[@property="v:average"]/text()').extract_first()
        item['score'] = score.strip() if score else ''
        votes = article_interest.xpath('.//span[@property="v:votes"]/text()').extract_first()
        item['votes'] = votes.strip() if votes else ''
        stars = article_interest.xpath('.//div[@class="ratings-on-weight"]//span[@class="rating_per"]/text()').extract()
        item['star5'], item['star4'], item['star3'], item['star2'], item['star1'] = stars if stars else ['']*5
        item['description'] = ''.join([s.strip() for s in content.xpath('.//span[@property="v:summary"]/text()').extract()])
        item['tags'] = ','.join([s.strip() for s in content.xpath('.//div[@class="tags-body"]/a/text()').extract()])
        comments = ''.join([s.strip() for s in content.xpath('.//div[@id="comments-section"]/div[@class="mod-hd"]/h2/span/a/text()').extract()])
        comments = re.findall(r'全部 (\d+) 条', comments)
        item['comments'] = comments[0] if comments else '0'
        reviews = ''.join([s.strip() for s in content.xpath('.//section[contains(@class,"reviews")]/header/h2/span/a/text()').extract()])
        reviews = re.findall(r'全部 (\d+) 条', reviews)
        item['reviews'] = reviews[0] if reviews else '0'
        return item

    def _parse_movie_comments(self, mids):
        saver = DoubanPipeline()
        for mid in mids:
            start_urls = [
                'https://movie.douban.com/subject/%s/comments?start=0&limit=20&sort=new_score&status=P&percent_type=h' % mid,
                'https://movie.douban.com/subject/%s/comments?start=0&limit=20&sort=new_score&status=P&percent_type=m' % mid,
                'https://movie.douban.com/subject/%s/comments?start=0&limit=20&sort=new_score&status=P&percent_type=l' % mid,
                'https://movie.douban.com/subject/%s/comments?start=0&limit=20&sort=time&status=P' % mid,
            ]
            for url in start_urls:
                comments_generator = list(self._parse_movie_comments_item(url, mid))
                self._save(comments_generator, saver)
                time.sleep(1)

    def _parse_movie_comments_item(self, url, mid):
        response = self.session.get(url)
        html = self._response_decode(response)
        selector = scrapy.Selector(text=html)
        divs = selector.xpath('.//div[@id="comments"]/div[@class="comment-item"][@data-cid]')
        for div in divs:
            try:
                cid = div.attrib.get('data-cid')
                if not cid:
                    continue
                item = DoubanMovieCommentsItem()
                item['mid'] = mid
                item['cid'] = cid
                item['uname'] = div.xpath('./div[@class="avatar"]/a').attrib.get('title')
                comment = div.xpath('./div[@class="comment"]')
                item['votes'] = ''.join(comment.xpath('./h3/span[@class="comment-vote"]/span[@class="votes"]/text()').extract()).strip()
                if not item['uname']:
                    item['uname'] = ''.join(comment.xpath('./h3/span[@class="comment-info"]/a/text()').extract()).strip()
                item['time'] = comment.xpath('./h3/span[@class="comment-info"]/span[contains(@class,"comment-time")]').attrib.get('title')
                score = str(comment.xpath('./h3/span[@class="comment-info"]/span[contains(@class,"rating")]').attrib.get('class'))
                score = re.findall(r'allstar(\d{1})0 rating', score)
                item['score'] = score[0] if score else ''
                item['text'] = ''.join([s.strip() for s in comment.xpath('./p/span[@class="short"]//text()').extract()]).strip()
                yield item
            except:
                print(mid + ' comments error')
                continue

        next_url = selector.xpath('.//div[@id="paginator"]/a[@class="next" or text()="后页 >"]').attrib.get('href')
        if next_url:
            next_url = 'https://movie.douban.com/subject/%s/comments' % mid + next_url
            yield self._parse_movie_comments_item(next_url, mid)



    def _parse_movie_reviews(self, mids):
        saver = DoubanPipeline()
        for mid in mids:
            url = 'https://movie.douban.com/subject/%s/reviews' % mid
            reviews_generator = list(self._parse_movie_reviews_item(url, mid))
            self._save(reviews_generator, saver)
            time.sleep(1)



    def _parse_movie_reviews_item(self, url, mid):
        response = self.session.get(url)
        html = self._response_decode(response)
        selector = scrapy.Selector(text=html)
        divs = selector.xpath('.//div[@id="content"]//div[@class="article"]/div[contains(@class,"review-list")]//div[@data-cid]')
        for div in divs:
            try:
                item = DoubanMovieReviewsItem()
                item['mid'] = mid
                item['rid'] = div.attrib.get('data-cid')
                item['uname'] = ''.join(div.xpath('.//header[@class="main-hd"]/a[@class="name"]/text()').extract()).strip()
                score = str(div.xpath('.//header[@class="main-hd"]/span[contains(@class,"main-title-rating")]').attrib.get('class'))
                print(mid, score)
                score = re.findall(r'allstar(\d{1})0 main-title-rating', score)
                item['score'] = score[0] if score else ''
                item['time'] = ''.join(div.xpath('.//header[@class="main-hd"]/span[@class="main-meta"]/text()').extract()).strip()
                item['title'] = ''.join(div.xpath('.//div[@class="main-bd"]/h2/a/text()').extract()).strip()
                numreply = ''.join(div.xpath('.//div[@class="main-bd"]//a[@class="reply"]/text()').extract()).strip()
                numreply = re.findall(r'(\d+)回应', numreply)
                item['numreply'] = numreply[0] if numreply else '0'
                try:
                    js = self.session.get('https://movie.douban.com/j/review/%s/full' % item['rid']).json()
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
                print(mid+' reviews error')
                continue

        next_url = selector.xpath('.//div[@id="content"]//div[@class="article"]/div[@class="paginator"]/span[@class="next"]/a').attrib.get('href')
        if next_url:
            next_url = 'https://movie.douban.com/subject/%s/reviews' % mid + next_url
            yield self._parse_movie_reviews_item(next_url, mid)