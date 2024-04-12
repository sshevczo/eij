import sys
import time
import uuid
from pathlib import Path
from typing import List

import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from config.settings import MAIN_MCC_ID
from eij.models import Page, Campaign


def make_client(path: str = 'google-ads.yaml', mcc_account_id=MAIN_MCC_ID) -> GoogleAdsClient:
    # if mcc_account_id:
    with open('google-ads.yaml', 'r') as file:
        config = yaml.safe_load(file)

    config['login_customer_id'] = mcc_account_id
    google_ads_client = GoogleAdsClient.load_from_dict(config)
    # else:
    #     google_ads_client = GoogleAdsClient.load_from_storage(version="v14", path=path)

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
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED  # ToDo ENABLED
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
        ad_group_criterion.status = client.enums.AdGroupCriterionStatusEnum.ENABLED  # ToDo ENABLED
        ad_group_criterion.keyword.text = keyword_text
        ad_group_criterion.keyword.match_type = (
            client.enums.KeywordMatchTypeEnum.BROAD  # EXACT
        )

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
        client, f"{headers[0][:24]}", served_asset_enum
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
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED  # ToDo ENABLED
        ad_group_ad.ad_group = ad_group_service.ad_group_path(customer_id, ad_group_id)

        # Set responsive search ad info.
        ad_group_ad.ad.final_urls.append(target_url)

        # Set a pinning to always choose this asset for HEADLINE_1. Pinning is
        # optional; if no pinning is set, then headlines and descriptions will be
        # rotated and the ones that perform best will be used more often.

        api_headers, api_descriptions = _collect_headlines(client, headers, descriptions)
        ad_group_ad.ad.responsive_search_ad.headlines.extend(api_headers)
        ad_group_ad.ad.responsive_search_ad.descriptions.extend(api_descriptions)
        ad_group_ad.ad.responsive_search_ad.path1 = "page"
        ad_group_ad.ad.responsive_search_ad.path2 = "remote"

        # Send a request to the server to add a responsive search ad.
        ad_group_ad_response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        full_result = []
        for result in ad_group_ad_response.results:
            full_result.append(result.resource_name)
        return full_result
    except GoogleAdsException as ex:
        handle_googleads_exception(ex, sys_exit=False)


def generate_google_ads(main_campaign_id: str, pages: List[Page], ads_number=1):
    # main_customer_id = '8620481282'
    campaign = Campaign.objects.get(campaign_id=main_campaign_id)
    main_customer_id = campaign.customer_id
    keys_path = Path.cwd() / 'eij' / 'fixtures' / 'google_ads_api' / 'google-ads.yaml'
    google_api_client = make_client(path=keys_path.__str__())
    result = []
    for page in pages:
        page.ads_task_status = Page.STARTED
        page.save()

        if not page.pagegooglekeyword_set.all():
            print(f'> page {page} skipped. google kwds not found')
            page.ads_task_status = Page.FAILED
            page.ads_task_description = f'Page {page} skipped. Google kwds not found'
            page.save()
            continue
        try:
            page_url = page.url

            # step 1: add ad_group
            ad_group_id = add_ad_group(google_api_client, main_customer_id, main_campaign_id, page.title[:60])
            # step 2 add keywords to ad_group
            keywords = page.pagegooglekeyword_set.all().order_by('pk')[:25]
            skipped_kws = 0
            for keyword in keywords:
                kw = add_keyword(client=google_api_client, customer_id=main_customer_id,
                                 ad_group_id=ad_group_id, keyword_text=keyword.text)
                if not kw:
                    skipped_kws += 1
                    print(f'>>> keyword [{keyword}] skipped!')
                time.sleep(3)
            print(
                f'> kwds for [{page}] added to group: {ad_group_id} ({len(keywords) - skipped_kws} of {len(keywords)})')
            # step 3: add responsive search_ad
            headers = [h.text for h in page.pageheader_set.all()]
            descriptions = [d.text for d in page.pagedescription_set.all()]
            for i in range(ads_number):
                for count in range(3):
                    rsa = add_responsive_search_ad(client=google_api_client, customer_id=main_customer_id,
                                                   ad_group_id=ad_group_id, target_url=page_url,
                                                   headers=headers, descriptions=descriptions)
                    if rsa:
                        msg = f'>> rsa for [{page}] done (try {count + 1}/3): {rsa}'
                        result.append(msg)
                        print(msg)
                        break
                    # print(f'>>> create rsa error for [{s}]. headers: {headers}, descriptions: {descriptions}')
                    if count == 2:
                        raise Exception(f'>>> create rsa error: [3] times gone for [{page}]')

                if rsa:
                    page.ads_task_status = Page.SUCCESS
                else:
                    page.ads_task_status = Page.FAILED
                    page.ads_task_description = 'Cant create ads for page'
                page.save()

        except Exception as ex:
            with open('skipped_pages_ids.txt', 'a') as file:
                file.write(f'{page.id} -> {page}: {str(ex)}\n')
            page.ads_task_status = Page.FAILED

    return result

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
#     main_campaign_id = '20532856715'
#     google_api_client = make_client()
#     lang = Language.objects.filter(name='Italian').first()
#     vpages = Page.objects.filter(language=lang).order_by('pk')
#     for v in vpages:
#         # if v.id <= 111:
#         #     continue
#         if not v.pagegooglekeyword_set.all():
#             print(f'> page {v} skipped. google kwds not found')
#             continue
#         try:
#             page_url = f'https://eij.org/page/{v.id}/{v.language.code_a2}'
#             # step 1: add ad_group
#             ad_group_id = add_ad_group(google_api_client, main_customer_id, main_campaign_id, v.title[:60])
#             # step 2 add keywords to ad_group
#             keywords = v.pagegooglekeyword_set.all().order_by('pk')[:25]
#             skipped_kws = 0
#             for keyword in keywords:
#                 kw = add_keyword(client=google_api_client, customer_id=main_customer_id,
#                                  ad_group_id=ad_group_id, keyword_text=keyword.text)
#                 if not kw:
#                     skipped_kws += 1
#                     print(f'>>> keyword [{keyword}] skipped!')
#                 time.sleep(3)
#             print(f'> kwds for [{v}] added to group: {ad_group_id} ({len(keywords) - skipped_kws} of {len(keywords)})')
#             # step 3: add responsive search_ad
#             headers = [h.text for h in v.pageheader_set.all()]
#             descriptions = [d.text for d in v.pagedescription_set.all()]
#             for count in range(3):
#                 rsa = add_responsive_search_ad(client=google_api_client, customer_id=main_customer_id,
#                                                ad_group_id=ad_group_id, target_url=page_url,
#                                                headers=headers, descriptions=descriptions)
#                 if rsa:
#                     print(f'>> rsa for [{v}] done (try {count + 1}/3): {rsa}')
#                     break
#                 # print(f'>>> create rsa error for [{v}]. headers: {headers}, descriptions: {descriptions}')
#                 if count == 2:
#                     raise Exception(f'>>> create rsa error: [3] times gone for [{v}]')
#         except Exception as ex:
#             with open('skipped_vpages_ids.txt', 'a') as file:
#                 file.write(f'{v.id} -> {v}: {str(ex)}\n')
#     print('Done!')
