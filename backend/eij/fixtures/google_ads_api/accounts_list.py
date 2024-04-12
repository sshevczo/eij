import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from config.settings import MAIN_MCC_ID


def get_management_accounts():
    with open('google-ads.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Override the 'login_customer_id'
    config['login_customer_id'] = MAIN_MCC_ID
    google_ads_client = GoogleAdsClient.load_from_dict(config)
    google_ads_service = google_ads_client.get_service("GoogleAdsService")

    query = ("""
        SELECT customer_client.client_customer, customer_client.resource_name, 
        customer_client.level, customer_client.manager, 
        customer_client.hidden, customer_client.descriptive_name
        FROM customer_client
        WHERE customer_client.level = 1
    """)

    accounts = []

    try:
        response = google_ads_service.search_stream(customer_id=MAIN_MCC_ID, query=query)

        for batch in response:
            for row in batch.results:
                client_customer = row.customer_client.client_customer
                resource_name = row.customer_client.resource_name
                level = row.customer_client.level
                manager = row.customer_client.manager
                hidden = row.customer_client.hidden
                descriptive_name = row.customer_client.descriptive_name

                print(f"Client Customer ID: {client_customer}, Resource Name: {resource_name}, "
                      f"Level: {level}, Manager: {manager}, Hidden: {hidden}, "
                      f"Descriptive Name: {descriptive_name}")

                accounts.append({'client_customer': client_customer.split('/')[-1], 'name': descriptive_name})

        return accounts

    except GoogleAdsException as ex:
        print(f"Request with ID '{ex.request_id}' failed with status "
              f"'{ex.error.code().name}' and includes the following errors:")
        for error in ex.failure.errors:
            print(f"\tError with message '{error.message}'.")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")

        return
