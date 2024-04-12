import os
import uuid
import django
import requests
from dotenv import load_dotenv

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import Language, Scenario
    load_dotenv()


def translate_to_several_langs_with_azure(api_key: str, from_lang: str, to_langs: list, text: str):
    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    params = {'api-version': '3.0', 'from': from_lang.lower(), 'to': to_langs}
    headers = {
        'Ocp-Apim-Subscription-Key': api_key,
        'Ocp-Apim-Subscription-Region': "eastus",
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    body = [{'text': text}]
    request = requests.post(url=endpoint, params=params, headers=headers, json=body)
    response = request.json()
    result = response[0].get('translations')
    # print(result)
    return result if result else ''


if __name__ == '__main__':
    azure_translate_api_key = os.environ.get('AZURE_TRANSLATE_API_KEY')
    lang_set = ['ro', 'sl', 'es', 'tr']  # set langs to partial db update
    target_langs = Language.objects.filter(code_a2__in=lang_set).order_by('pk').exclude(id__in=[2, 27, 30, 35])
    target_langs_codes = [lang.code_a2.lower() for lang in target_langs]
    source_scenarios = Scenario.objects.filter(parent__isnull=True).order_by('pk')
    for scenario in source_scenarios:
        print('>>> scenario Done:', scenario)
        text_html_translated_raw = translate_to_several_langs_with_azure(
            api_key=azure_translate_api_key,
            from_lang='en',
            to_langs=target_langs_codes,
            text=scenario.text_html,
        )
        text_html_translated = {lang.get('to'): lang.get('text') for lang in text_html_translated_raw}
        for v_children in scenario.children.filter(language__code_a2__in=lang_set):
            lang_code = v_children.language.code_a2.lower()
            v_children.text_html = text_html_translated[lang_code]
            v_children.save()
