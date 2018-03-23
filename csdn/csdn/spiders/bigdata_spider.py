#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Topic: sample
Desc :
"""
from csdn.items import BigdataItem
import scrapy

class HuxiuSpider(scrapy.Spider):
    name = "bigdata"
    allowed_domains = ["cnblogs.com"]
    start_urls = [
        "http://www.cnblogs.com/zlslch/"
    ]

    def parse(self, response):
        for sel in response.xpath('//div[@class="day"]/div[@class="postTitle"]') :
            item = BigdataItem()
            item['title'] = sel.xpath('a/text()')[0].extract()
            item['url'] = sel.xpath('a/@href')[0].extract()
            print(item['title'],item['url'])
            yield item
