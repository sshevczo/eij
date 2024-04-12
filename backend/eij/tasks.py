from celery import shared_task

from config.settings import OPENAI_KEY
from crawler.crawler_start import crawl_website_seo_data
from eij.fixtures.google_ads_api.create_ads import generate_google_ads
from eij.fixtures.google_ads_api.create_kw_ideas import generate_google_keyword_ideas
from eij.fixtures.open_ai_handler import generate_page_seo_data
from eij.models import Page, Language, Website



@shared_task
def generate_page_seo_data_for_lang(language_name: str, start_from_page_pk: int = None) -> [list, str]:
    try:
        if not start_from_page_pk:
            pages = Page.objects.filter(language__name=language_name).order_by('pk')
        else:
            pages = Page.objects.filter(
                id__gte=start_from_page_pk, language__name=language_name
            ).order_by('pk')
        result = generate_page_seo_data(open_ai_api_key=OPENAI_KEY, pages=pages)
        return result
    except Exception as ex:
        msg = f'> generate_page_seo_data task Exception: {ex}'
        print(msg)
        return msg


@shared_task
def generate_page_google_keyword_ideas(language_name: str, start_from_page_pk: int = None) -> [list, str]:
    try:
        lang = Language.objects.filter(name=language_name).first()
        if not start_from_page_pk:
            pages = Page.objects.filter(language=lang).order_by('pk')
        else:
            pages = Page.objects.filter(id__gte=start_from_page_pk, language=lang).order_by('pk')
        from pathlib import Path
        result = generate_google_keyword_ideas(language=lang, pages=pages)
        return result
    except Exception as ex:
        msg = f'> generate_page_google_keyword_ideas task Exception: {ex}'
        print(msg)
        return msg


@shared_task
def generate_page_google_ads(
        main_campaign_id: str, language_name: str, start_from_page_pk: int = None
) -> [list, str]:
    try:
        lang = Language.objects.filter(name=language_name).first()
        if not start_from_page_pk:
            pages = Page.objects.filter(language=lang).order_by('pk')
        else:
            pages = Page.objects.filter(id__gte=start_from_page_pk, language=lang).order_by('pk')
        result = generate_google_ads(main_campaign_id=main_campaign_id, pages=pages)
        return result
    except Exception as ex:
        msg = f'> generate_page_google_ads task Exception: {ex}'
        print(msg)
        return msg


@shared_task
def crawl_website_seo_data_for_lang(website_id, user) -> str:
    website = Website.objects.filter(id=website_id).first()

    try:
        result = crawl_website_seo_data(url=website.base_url, language=website.language.name, user=user)
        print(result)
        return result
    except Exception as ex:
        msg = f'> crawl_website_seo_data_for_lang task for website {website.name} Exception: {ex}'
        print(msg)
        return msg


@shared_task
def generate_seo_data_for_selected(websites_ids) -> [list, str]:
    websites_queryset = Page.objects.filter(id__in=websites_ids).order_by('pk')

    try:
        result = generate_page_seo_data(open_ai_api_key=OPENAI_KEY, pages=websites_queryset)
        return result
    except Exception as ex:
        msg = f'> generate_seo_data_for_selected task Exception: {ex}'
        print(msg)
        return msg


@shared_task
def generate_google_keyword_ideas_for_selected(object_ids, language_id):
    try:
        lang = Language.objects.filter(id=language_id).first()
        queryset = Page.objects.filter(id__in=object_ids).order_by('pk')

        from pathlib import Path
        result = generate_google_keyword_ideas(language=lang, pages=queryset)
        return result
    except Exception as ex:
        msg = f'> generate_google_keyword_ideas_for_selected task Exception: {ex}'
        print(msg)
        return msg


@shared_task
def generate_google_ads_for_selected(object_ids, main_campaign_id, ads_number):
    try:
        queryset = Page.objects.filter(id__in=object_ids).order_by('pk')

        result = generate_google_ads(main_campaign_id=main_campaign_id, pages=queryset, ads_number=ads_number)
        return result
    except Exception as ex:
        msg = f'> generate_page_google_ads task Exception: {ex}'
        print(msg)
        return msg
