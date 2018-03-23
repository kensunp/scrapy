#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: 登录爬虫
Desc : 模拟登录http://www.iteye.com后将自己的私信全部爬出来
tips：使用chrome调试post表单的时候勾选Preserve log和Disable cache
"""
import logging
import re
import sys
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest, HtmlResponse

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[logging.StreamHandler(sys.stdout)])


class IteyeSpider(CrawlSpider):
    name = "iteye"
    allowed_domains = ["iteye.com"]
    start_urls = [
        'http://my.iteye.com/messages',
        'http://my.iteye.com/messages/store',
    ]
    rules = (
        # 消息列表
        Rule(LinkExtractor(allow=('/messages/\d+',),
                           restrict_xpaths='//table[@class="admin"]/tbody/tr/td[2]'),
             callback='parse_page'),
        # 下一页, If callback is None follow defaults to True, otherwise it defaults to False
        Rule(LinkExtractor(restrict_xpaths='//a[@class="next_page"]')),
    )
    request_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Referer": "http://www.iteye.com/login",
    }

    post_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36",
        "Referer": "http://www.iteye.com/",
    }

    # 重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    def start_requests(self):
        return [Request("http://www.iteye.com/login",
                        meta={'cookiejar': 1}, callback=self.post_login)]

    # FormRequeset
    def post_login(self, response):
        # 先去拿隐藏的表单参数authenticity_token
        authenticity_token = response.xpath(
            '//input[@name="authenticity_token"]/@value').extract_first()
        logging.info('authenticity_token=' + authenticity_token)
        # FormRequeset.from_response是Scrapy提供的一个函数, 用于post表单
        # 登陆成功后, 会调用after_login回调函数，如果url跟Request页面的一样就省略掉
        return [FormRequest.from_response(response,
                                          url='http://www.iteye.com/login',
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.post_headers,  # 注意此处的headers
                                          formdata={
                                              'name': 'yidao620c',
                                              'password': '******',
                                              'authenticity_token': authenticity_token
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self, response):
        # logging.info(response.body.encode('utf-8'))
        # 登录之后，开始进入我要爬取的私信页面
        # 对于登录成功后的页面我不感兴趣，所以这里response没啥用
        for url in self.start_urls:
            logging.info('letter url=' + url)
            # 因为我们上面定义了Rule，所以只需要简单的生成初始爬取Request即可
            yield Request(url, meta={'cookiejar': response.meta['cookiejar']})
            # 如果是普通的Spider，而不是CrawlerSpider，没有定义Rule规则，
            # 那么就需要像下面这样定义每个Request的callback
            # yield Request(url, dont_filter=True,
            #               callback=self.parse_page, )

    def parse_page(self, response):
        """这个是使用LinkExtractor自动处理链接以及`下一页`"""
        logging.info(u'--------------消息分割线-----------------')
        logging.info(response.url)
        logging.info(response.xpath('//a[@href="/messages/new"]/text()').extract_first())
        # msg_time = response.xpath(
        #     '//div[@id="main"]/table[1]/tbody/tr[1]/td[1]/text()').extract_first()
        # logging.info(msg_time)
        # msg_title = response.xpath(
        #     '//div[@id="main"]/table[1]/tbody/tr[2]/th[2]/span/text()').extract_first()
        # logging.info(msg_title)

        # def parse_page(self, response):
        #     """这个是不使用LinkExtractor我自己手动处理链接以及下一页"""
        #     logging.info(response.url)
        #     for each_msg in response.xpath('//ul[@class="Msgs"]/li'):
        #         logging.info('--------------消息分割线-----------------')
        #         logging.info(''.join(each_msg.xpath('.//div[@class="msg"]//*/text()').extract()))
        #     next_page = response.xpath('//li[@class="page next"]/a')
        #     if next_page:
        #         logging.info(u'继续处理下一页')
        #         yield Request(response.url + next_page.xpath('@href').extract())
        #     else:
        #         logging.info(u"已经处理完成，没有下一页了")

    def _requests_to_follow(self, response):
        """重写加入cookiejar的更新"""
        if not isinstance(response, HtmlResponse):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = Request(url=link.url, callback=self._response_downloaded)
                # 下面这句是我重写的
                r.meta.update(rule=n, link_text=link.text, cookiejar=response.meta['cookiejar'])
                yield rule.process_request(r)
