# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SeoDataItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    keywords = scrapy.Field()
    clean_text = scrapy.Field()
