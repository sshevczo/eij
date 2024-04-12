import sys
import time
import uuid
from pathlib import Path
from typing import List
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from eij.models import Page, Language

_DATE_FORMAT = "%Y%m%d"


# https://developers.google.com/oauthplayground/#step1&scopes=https%3A//www.googleapis.com/auth/adwords&url=https%3A//&
# content_type=application/json&http_method=GET&useDefaultOauthCred=checked&oauthEndpointSelect=Google&oauthAuthEndpoin
# tValue=https%3A//accounts.google.com/o/oauth2/v2/auth&oauthTokenEndpointValue=https%3A//oauth2.googleapis.com/token&
# includeCredentials=unchecked&accessTokenType=bearer&autoRefreshToken=unchecked&accessType=offline&forceAprovalPrompt=
# checked&response_type=code
def make_client(path: str = 'google-ads.yaml') -> GoogleAdsClient:
    google_ads_client = GoogleAdsClient.load_from_storage(version="v14", path=path)
    return google_ads_client


def handle_googleads_exception(exception, sys_exit: bool = True):
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")
    if sys_exit:
        sys.exit(1)


def get_campaigns(client, customer_id):
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
          campaign.id,
          campaign.name
        FROM campaign
        ORDER BY campaign.id"""
    try:
        stream = ga_service.search_stream(customer_id=customer_id, query=query)
        campaigns = []
        for batch in stream:
            for row in batch.results:
                campaigns.append([row.campaign.id, row.campaign.name])
        return campaigns
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)


def add_ad_group(client, customer_id, campaign_id, group_name) -> str:
    ad_group_service = client.get_service("AdGroupService")
    campaign_service = client.get_service("CampaignService")

    # Create ad group.
    try:
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = f"{group_name} {uuid.uuid4()}"
        ad_group.status = client.enums.AdGroupStatusEnum.PAUSED  # ToDo ENABLED
        ad_group.campaign = campaign_service.campaign_path(customer_id, campaign_id)
        ad_group.type_ = client.enums.AdGroupTypeEnum.SEARCH_STANDARD
        ad_group.cpc_bid_micros = 1000000
        # Add the ad group.
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        created_ad_group_id = ad_group_response.results[0].resource_name.split('/')[-1]
        return created_ad_group_id
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)


def add_keyword(client, customer_id, ad_group_id, keyword_text):
    try:
        ad_group_service = client.get_service("AdGroupService")
        ad_group_criterion_service = client.get_service("AdGroupCriterionService")

        # Create keyword.
        ad_group_criterion_operation = client.get_type("AdGroupCriterionOperation")
        ad_group_criterion = ad_group_criterion_operation.create
        ad_group_criterion.ad_group = ad_group_service.ad_group_path(
            customer_id, ad_group_id
        )
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.PAUSED  # ToDo ENABLED
        ad_group_criterion.keyword.text = keyword_text
        ad_group_criterion.keyword.match_type = (
            client.enums.KeywordMatchTypeEnum.BROAD  # EXACT
        )
        # Optional field
        # All fields can be referenced from the protos directly.
        # The protos are located in subdirectories under:
        # https://github.com/googleapis/googleapis/tree/master/google/ads/googleads
        # ad_group_criterion.negative = True

        # Optional repeated field
        # ad_group_criterion.final_urls.append('https://www.example.com')

        # Add keyword
        ad_group_criterion_response = ad_group_criterion_service.mutate_ad_group_criteria(
            customer_id=customer_id, operations=[ad_group_criterion_operation],
        )
        # print('> > >', ad_group_criterion_response.results[0])
        return [ad_group_criterion_response.results[0].resource_name]
    except GoogleAdsException as ex:
        handle_googleads_exception(ex, sys_exit=False)


def create_ad_text_asset(client, text, pinned_field=None):
    """Create an AdTextAsset."""
    ad_text_asset = client.get_type("AdTextAsset")
    ad_text_asset.text = text
    if pinned_field:
        ad_text_asset.pinned_field = pinned_field
    return ad_text_asset


def _collect_headlines(client, headers: list, descriptions: list) -> tuple:
    served_asset_enum = client.enums.ServedAssetFieldTypeEnum.HEADLINE_1
    pinned_headline = create_ad_text_asset(
        client, f"{headers[0][:24]} #{str(uuid.uuid4())[:4]}", served_asset_enum
    )
    api_headers = [create_ad_text_asset(client, header[:30]) for header in headers[1:]]
    api_headers.insert(0, pinned_headline)
    api_descriptions = [create_ad_text_asset(client, description[:90]) for description in descriptions]
    return api_headers, api_descriptions


def add_responsive_search_ad(client, customer_id, ad_group_id, target_url: str, headers: list, descriptions: list):
    try:
        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_service = client.get_service("AdGroupService")

        # Create the ad group ad.
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.PAUSED  # ToDo ENABLED
        ad_group_ad.ad_group = ad_group_service.ad_group_path(customer_id, ad_group_id)

        # Set responsive search ad info.
        ad_group_ad.ad.final_urls.append(target_url)

        # Set a pinning to always choose this asset for HEADLINE_1. Pinning is
        # optional; if no pinning is set, then headlines and descriptions will be
        # rotated and the ones that perform best will be used more often.

        api_headers, api_descriptions = _collect_headlines(client, headers, descriptions)
        ad_group_ad.ad.responsive_search_ad.headlines.extend(api_headers)
        ad_group_ad.ad.responsive_search_ad.descriptions.extend(api_descriptions)
        ad_group_ad.ad.responsive_search_ad.path1 = "pages"
        ad_group_ad.ad.responsive_search_ad.path2 = "remote"

        # Send a request to the server to add a responsive search ad.
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        full_result = []
        print('> > >', ad_group_ad_response.results)
        for result in ad_group_ad_response.results:
            full_result.append(result.resource_name)
        return full_result
    except GoogleAdsException as ex:
        handle_googleads_exception(ex, sys_exit=False)


def generate_keyword_ideas(
        client, customer_id, keyword_texts: list, page_url=None, location_ids=None, language_id='1000'
) -> list:
    try:
        if location_ids is None:
            location_ids = ["2804", "2036", "2250"]
        keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")
        keyword_plan_network = (
            client.enums.KeywordPlanNetworkEnum.GOOGLE_SEARCH_AND_PARTNERS
        )
        build_resource_name = client.get_service("GeoTargetConstantService").geo_target_constant_path
        location_rns = [build_resource_name(location_id) for location_id in location_ids]
        language_rn = client.get_service("GoogleAdsService").language_constant_path(language_id)
        if not (keyword_texts or page_url):
            raise ValueError("At least one of keywords or page URL is required, but neither was specified.")
        request = client.get_type("GenerateKeywordIdeasRequest")
        request.customer_id = customer_id
        request.language = language_rn
        request.geo_target_constants.extend(location_rns)
        request.include_adult_keywords = False
        request.keyword_plan_network = keyword_plan_network
        if not keyword_texts and page_url:
            request.url_seed.url = page_url
        if keyword_texts and not page_url:
            request.keyword_seed.keywords.extend(keyword_texts)
        if keyword_texts and page_url:
            request.keyword_and_url_seed.url = page_url
            request.keyword_and_url_seed.keywords.extend(keyword_texts)
        keyword_ideas_raw = keyword_plan_idea_service.generate_keyword_ideas(request=request)
        keyword_ideas = [[idea.text,
                          idea.keyword_idea_metrics.avg_monthly_searches,
                          idea.keyword_idea_metrics.competition] for idea in keyword_ideas_raw]
        return sorted(keyword_ideas, key=lambda x: int(x[1]), reverse=True)
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)


def generate_google_keywords_for_pages(client, customer_id, pages, location_ids, language_id):
    result = []
    for count, page in enumerate(pages):
        page.keywords_task_status = Page.STARTED
        page.save()

        raw_keywords = [kw.text for kw in page.pagerawkeyword_set.all().order_by('pk')[:20]]
        # print('<<<<< raw_kwds:', raw_keywords[:8])
        if not raw_keywords:
            page.keywords_task_status = Page.FAILED
            page.keywords_task_description = 'No rawkeywords for page'
            page.save()
            continue
        if page.pagegooglekeyword_set.all():
            page.pagegooglekeyword_set.all().delete()
            page.keywords_task_description = 'Deleted previous and regenerating Google Keywords'
            page.save()

        google_keywords = generate_keyword_ideas(client=client, customer_id=customer_id, keyword_texts=raw_keywords,
                                                 location_ids=location_ids, language_id=language_id)
        # print('<<<<< google_kwds:', google_keywords[:8])
        time.sleep(4)
        for kw in google_keywords[:30]:
            if len(kw[0]) <= 70:
                page.pagegooglekeyword_set.create(text=kw[0])
            else:
                print('> keyword skipped:', kw)
        log = f'>> {count + 1}/{pages.count()} done. Added {len(google_keywords)} google kwds --> {page}'
        print(log)

        if google_keywords:
            page.keywords_task_status = Page.SUCCESS
            page.keywords_task_description = f'Added {len(google_keywords)} google kwds for page'
        else:
            page.keywords_task_status = Page.FAILED
            page.keywords_task_description = 'Cant get keywords for page'
        page.save()

        result.append(log)

    return result


def generate_google_keyword_ideas(language: Language, pages: List[Page]):
    customer_id = '8620481282'  # ASSOCIATION OF ASSISTANCE TO THE...
    keys_path = Path.cwd() / 'eij' / 'fixtures' / 'google_ads_api' / 'google-ads.yaml'
    google_client = make_client(path=keys_path.__str__())
    google_loc_ids = [i.google_location_id for i in language.country_set.all() if i.google_location_id]
    res = generate_google_keywords_for_pages(client=google_client, customer_id=customer_id, pages=pages,
                                             location_ids=google_loc_ids, language_id=language.google_lang_id)
    return res

# if __name__ == '__main__':
#     import os
#     import django
#     from dotenv import load_dotenv
#     load_dotenv()
#     AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
#     os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
#     django.setup()
#     from eij.models import Page, Language
#     main_customer_id = '8620481282'
#     client = make_client()
#     lang = Language.objects.filter(name='Italian').first()
#     pages = Page.objects.filter(language=lang).order_by('pk')
#     loc_ids = [i.google_location_id for i in lang.country_set.all() if i.google_location_id]
#     generate_google_keywords_for_pages(client=client, customer_id=main_customer_id, pages=pages,
#                                            location_ids=loc_ids, language_id=lang.google_lang_id)
