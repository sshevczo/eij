import uuid

import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from config.settings import MAIN_MCC_ID


def campaign_name_exists(customer_id, campaign_name):
    with open('google-ads.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Override the 'login_customer_id'
    config['login_customer_id'] = MAIN_MCC_ID
    google_ads_client = GoogleAdsClient.load_from_dict(config)

    ga_service = google_ads_client.get_service("GoogleAdsService")

    query = f"""
        SELECT campaign.name
        FROM campaign
        WHERE campaign.name = '{campaign_name}'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)
        for row in response:
            # If any row is returned, the campaign name exists
            return True
        return False
    except Exception as e:
        raise e


def create_campaign(customer_id, campaign_name, budget_usd):
    with open('google-ads.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Override the 'login_customer_id'
    config['login_customer_id'] = MAIN_MCC_ID
    google_ads_client = GoogleAdsClient.load_from_dict(config)

    campaign_budget_service = google_ads_client.get_service("CampaignBudgetService")
    campaign_service = google_ads_client.get_service("CampaignService")

    campaign_budget_operation = google_ads_client.get_type("CampaignBudgetOperation")
    campaign_budget = campaign_budget_operation.create
    campaign_budget.name = campaign_name + ' budget'
    campaign_budget.delivery_method = (
        google_ads_client.enums.BudgetDeliveryMethodEnum.STANDARD
    )
    campaign_budget.amount_micros = budget_usd * 1_000_000

    try:
        campaign_budget_response = (
            campaign_budget_service.mutate_campaign_budgets(
                customer_id=customer_id, operations=[campaign_budget_operation]
            )
        )
    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return

    # Create campaign.
    campaign_operation = google_ads_client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = campaign_name
    campaign.advertising_channel_type = (
        google_ads_client.enums.AdvertisingChannelTypeEnum.SEARCH
    )

    campaign.status = google_ads_client.enums.CampaignStatusEnum.ENABLED

    # Set the bidding strategy and budget.
    campaign.manual_cpc.enhanced_cpc_enabled = True
    campaign.campaign_budget = campaign_budget_response.results[0].resource_name

    # Set the campaign network options.
    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_partner_search_network = False

    # Add the campaign.
    try:
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        print(f"Created campaign {campaign_response.results[0].resource_name}.")
        return campaign_response.results[0].resource_name.split('/')[-1]

    except GoogleAdsException as ex:
        handle_googleads_exception(ex)
        return


def handle_googleads_exception(exception):
    print(
        f'Request with ID "{exception.request_id}" failed with status '
        f'"{exception.error.code().name}" and includes the following errors:'
    )
    for error in exception.failure.errors:
        print(f'\tError with message "{error.message}".')
        if error.location:
            for field_path_element in error.location.field_path_elements:
                print(f"\t\tOn field: {field_path_element.field_name}")
    return
