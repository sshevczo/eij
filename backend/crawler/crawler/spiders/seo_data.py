from urllib.parse import urlparse

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import SeoDataItem


class SeoDataSpider(CrawlSpider):
    name = "seo_spider"

    def __init__(self, start_urls=None, allowed_domains=None, language=None, website=None, user=None, *args, **kwargs):
        super(SeoDataSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.allowed_domains = allowed_domains
        self.language = language
        self.website = website
        self.user = user

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = SeoDataItem()
        item["title"] = response.css('title::text').get()
        item["description"] = response.css("meta[property*='description']::attr(content)").get()
        item["keywords"] = response.css("meta[name='keywords']::attr(content)").get()
        item["url"] = response.url

        text_elements = response.xpath('//body//text()[not(ancestor::script|ancestor::style|ancestor::head)]').getall()
        item["clean_text"] = ' '.join([text.strip() for text in text_elements])

        return item
