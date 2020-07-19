import requests
import time
import urllib.parse
import scrapy
import types
import re
from PIL import Image
from .settings import COOKIES
from .items import WeixinItem1
from .pipelines import WeixinPipeline



class WeixinSpider(object):
    def __init__(self):
        self.captcha_try_times = 3

    def _get_headers(self,suv='',snuid='',referer=''):
        suv = COOKIES.get('SUV') if not suv else suv
        snuid = COOKIES.get('SNUID') if not snuid else snuid
        headers = {'Cookie':'SUV=%s;SNUID=%s' % (suv,snuid)}
        if referer:
            headers['Referer'] = referer
        return headers

    def _set_cookie(self,suv,snuid):
        COOKIES['SUV'] = suv
        COOKIES['SNUID'] = snuid


    def _get(self,url,session,headers={}):
        response = session.get(url,headers=headers)
        if not response.ok:
            raise Exception('get error')
        return response

    def _get_sogou_captcha(self,url,session):
        response_captcha = session.get('http://weixin.sogou.com/antispider/util/seccode.php?tc=%s' % str(int(round(time.time() * 1000))))
        if not response_captcha.ok:
            raise Exception('get sogou captcha error')

        captcha = self._identify_captcha(response_captcha.content)
        print(captcha)
        response_callback = self._sogou_callback(url,session,captcha)
        print(response_callback)

        if response_callback['code'] != 0:
            raise Exception('error'+' ' + str(response_callback.get('code')) +' ' + response_callback('msg'))
        else:
            print(session.cookies.get('SUID'),response_callback.get('id'))
            self._set_cookie(session.cookies.get('SUID'),response_callback.get('id'))

    def _identify_captcha(self,captcha_content):
        print('captcha')
        print(captcha_content)
        with open('./weixin/temp/captcha.jpeg','wb') as f:
            print(captcha_content)
            f.write(captcha_content)
        img = Image.open('./weixin/temp/captcha.jpeg')
        img.show()
        return input('please input captcha:')

    def _sogou_callback(self,url,session,captcha):
        ref = url.split('weixin.sogou.com/')[-1]
        print(url)
        data = {
            'c': captcha,
            'r': '%2F' + ref,
            'v': 5
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://weixin.sogou.com/antispider/?from=%2f' + ref
        }
        response = session.post('http://weixin.sogou.com/antispider/thank.php',data,headers=headers)
        if not response.ok:
            raise Exception('error' + ' ' + str(response.status_code) + ' ' + (response.text))

        return response.json()

    def search_article(self,keyword,ft,et):
        self.keyword = keyword
        ft = int(time.mktime(time.strptime(ft,'%Y-%m-%d')))
        et = int(time.mktime(time.strptime(et,'%Y-%m-%d')))
        assert ft <= et
        for t in range(ft,et+1,86400):
            st = time.strftime('%Y-%m-%d', time.localtime(t))
            params = {
                'type':2,
                'ie':'utf-8',
                'tsn':5,
                'query':keyword,
                'ft':st,
                'et':st,
                'interation':'',

            }
            url = 'https://weixin.sogou.com/weixin?type=2&ie=utf8&query=%s&tsn=5&ft=%s&et=%s&interation=&wxid=&usip=' % (urllib.parse.quote(self.keyword),st,st)
            session = self._get_session_by_login()
            referer = 'https://weixin.sogou.com/weixin?type=2&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_=' % urllib.parse.quote(self.keyword)
            article_generator = list(self._parse_article(session,self._parse_article_html(url,session,referer=referer)))
            saver = WeixinPipeline()
            self._save_article(article_generator,saver)
            time.sleep(1)

    def _parse_article_html(self,url,session,referer):
        response = self._get(url,session,headers=self._get_headers(referer=referer))
        if 'antispider' in response.url or '请输入验证码' in response.text:
            print('aa')
            for i in range(self.captcha_try_times):
                print(i)
                try:
                    self._get_sogou_captcha(url,session)
                    break
                except Exception as e:
                    print(str(e))
            if '请输入验证码' in response.text:
                response = session.get(url)
            else:
                response = self._get(url,session,headers=self._get_headers(referer=referer))
            print(self._response_decode(response))
        return response

    def _parse_article(self,session,response):
        html = self._response_decode(response)
        selector = scrapy.Selector(text=html)
        lis = selector.xpath('//div[@class="news-box"]/ul[@class="news-list"]/li')
        for li in lis:
            try:
                item = WeixinItem1()
                item['wid'] = self.keyword + '_' + li.attrib.get('d')
                txt_box = li.xpath('./div[@class="txt-box"]')[0]
                item['url'] = txt_box.xpath('./h3/a')[0].attrib.get('href')
                item['title'] = ''.join(txt_box.xpath('./h3/a//text()').extract())
                div = txt_box.xpath('./div[@class="s-p"]')
                item['source'] = ''.join(div.xpath('./a//text()').extract())
                item['time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(div.attrib.get('t'))))
                article_html = self._response_decode(requests.get(item['url']))
                article_selector = scrapy.Selector(text=article_html)
                item['text'] = '\n'.join(article_selector.xpath('//div[@id="page-content"]//div[@id="img-content"]/div[@id="js_content"]//text()').extract()).strip()
                if not item['text']:
                    original_url = article_selector.xpath('//div[@class="original_panel"]/div[@class="original_panel_tool"]/a[@id="js_share_source"]').attrib.get('href')
                    print('original',original_url)
                    if original_url:
                        article_html = self._response_decode(requests.get(original_url))
                        article_selector = scrapy.Selector(text=article_html)
                        item['text'] = '\n'.join(article_selector.xpath('//div[@id="page-content"]//div[@id="img-content"]/div[@id="js_content"]//text()').extract()).strip()
                    if not item['text']:
                        continue
                yield item
            except:
                continue

        next_url = selector.xpath('//div[@id="pagebar_container"]/a[@id="sogou_next"]')
        print(next_url)
        if next_url:
            next_url = 'https://weixin.sogou.com/weixin' + next_url[0].attrib.get('href')
            print(response.url)
            print(next_url)
            yield self._parse_article(session,self._parse_article_html(next_url,session,referer=response.url))


    def _response_decode(self,response):
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

    def _save_article(self,article_generator,saver):
        for x in article_generator:
            if isinstance(x,types.GeneratorType):
                self._save_article(list(x),saver)
            elif isinstance(x,WeixinItem1):
                saver.process_item(x)


    def _get_session_by_login(self):
        session = requests.session()
        url1 = 'https://account.sogou.com/connect/login?provider=weixin&client_id=2017&ru=https://weixin.sogou.com&third_appid=wx6634d697e8cc0a29&href=https://dlweb.sogoucdn.com/weixin/css/weixin_join.min.css?v=20170315'
        res1 = session.get(url1)
        url2 = res1.url
        state = re.findall(r'state=(.*)&',url2)
        url3 = 'https://pb.sogou.com/cl.gif?uigs_t=%s&uigs_productid=vs_web&terminal=web&vstype=weixin&pagetype=index&channel=index_pc&type=weixin_search_pc&wuid=00F83DEFAFA78A1A5C1BAF0649830928&snuid=&uigs_uuid=%s&login=0&uigs_cl=home_login_top&href=javascript:void(0);&uigs_refer=https://weixin.sogou.com/' % (str(int(round(time.time() * 1000))),str(int(round(time.time() * 1000000))))
        session.get(url3)
        res2 = session.get(url2)
        res2_html = self._response_decode(res2)
        selector = scrapy.Selector(text=res2_html)
        uuid = selector.xpath('//div[@class="wrp_code"]/img').attrib.get('src').split('/')[-1]
        url4 = 'https://open.weixin.qq.com/connect/qrcode/' + uuid
        res4 = session.get(url4,headers={'Referer':url2})
        with open('./weixin/temp/qrcode.png','wb') as f:
            f.write(res4.content)
        img = Image.open('./weixin/temp/qrcode.png')
        img.show()
        time.sleep(10)
        ck = ''
        while ck != '405':
            url5 = 'https://long.open.weixin.qq.com/connect/l/qrconnect?uuid=%s&_=%s' % (uuid,str(int(round(time.time() * 1000))))
            res5 = session.get(url5)
            fre = re.findall(r"window.wx_errcode=(\d{3});window.wx_code='(.*)'",res5.text)[0]
            ck = fre[0]
            code = fre[1]
        img.close()
        url5 = 'https://account.sogou.com/connect/callback/weixin?code=%s&state=%s' % (code,state)
        session.get(url5)
        print('logined')
        return session