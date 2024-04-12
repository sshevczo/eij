import json
from urllib.parse import urlparse

from django.contrib.auth.models import User
from django.db.models import Q
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.signalmanager import dispatcher

from config.settings import OPENAI_KEY
from crawler.crawler.spiders.seo_data import SeoDataSpider
from eij.fixtures.open_ai_handler import get_summary_prompt, make_summary_of_page, clean_ai_answer
from eij.models import Page, Language, Website

created_pages_count = 0


def get_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


def crawler_results(signal, sender, item, response, spider):
    ds = str(item['description']) if bool(item['description']) else None
    title = str(item['title']) if bool(item['title']) else None
    keywords = str(item['keywords']) if bool(item['keywords']) else None
    url = item['url']
    clean_text = item['clean_text']
    global created_pages_count

    log = f'> New page | ds: {ds}; title: {title}; kw: {keywords}; url: {url}'
    print(log)

    if title is not None:
        if ds is None:
            prompt = get_summary_prompt(spider.language, title, clean_text)
            summary = make_summary_of_page(prompt, OPENAI_KEY)

            try:
                parsed_json = json.loads(summary)
                if parsed_json:
                    ds = parsed_json.get('summary')[0]
            except Exception as ex:
                print(ex)

        if ds and not Page.objects.filter(Q(url=url) | Q(title=title), website=spider.website):
            page = Page(text=ds, title=title, language=spider.language, url=url, website=spider.website,
                        created_by_id=spider.user)
            page.save()
            created_pages_count += 1

            if keywords:
                for keyword in keywords[:15]:
                    page.pagerawkeyword_set.create(text=keyword[:40])


def crawl_website_seo_data(url: str, language: str, user: int):
    stats = []

    def crawler_stats(*args, **kwargs):
        stats.append(kwargs['sender'].stats.get_stats())

    lang_obj = Language.objects.get(name=language)
    website_obj = Website.objects.filter(base_url=url, created_by_id=user).first()
    global created_pages_count

    website_obj.crawl_task_status = Website.STARTED
    website_obj.save()

    dispatcher.connect(crawler_results, signal=signals.item_scraped)
    dispatcher.connect(crawler_stats, signal=signals.spider_closed)
    process = CrawlerProcess()
    process.crawl(SeoDataSpider,
                  start_urls=[url],
                  allowed_domains=[str(get_domain(url))],
                  language=lang_obj,
                  website=website_obj,
                  user=user)
    process.start()

    item_scraped_count = stats[0]['item_scraped_count']

    created_pages = created_pages_count
    created_pages_count = 0

    if created_pages > 0:
        website_obj.crawl_task_status = Website.SUCCESS
        website_obj.crawl_task_description = f'Created Pages: {created_pages}. Crawled pages: {item_scraped_count}.'

        website_obj.save()
    else:
        website_obj.crawl_task_status = Website.FAILED
        website_obj.crawl_task_description = f'Crawler not found any valid Pages. Crawled pages: {item_scraped_count}.'

        website_obj.save()

    return f'Executed successfully! Created Pages: {created_pages}'
