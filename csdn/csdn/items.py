# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CsdnItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class BigdataItem(scrapy.Item):
    url = scrapy.Field()    #文章链接
    title = scrapy.Field()  #文章标题
