import os
import uuid
import django
import requests
from time import sleep
from dotenv import load_dotenv

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import Language, Scenario, ScenarioMetaTranslated
    load_dotenv()


def translate_to_one_lang_with_azure(api_key: str, from_lang: str, to_lang: str, text: str) -> str:
    endpoint = "https://api.cognitive.microsofttranslator.com/translate"
    params = {'api-version': '3.0', 'from': from_lang.lower(), 'to': [to_lang.lower(), ]}
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
    if result:
        return result[0].get('text')
    return ''


if __name__ == '__main__':
    azure_translate_api_key = os.environ.get('AZURE_TRANSLATE_API_KEY')
    langs = Language.objects.filter(id__gt=13).exclude(id__in=[27, 30, 35])
    for lang in langs:
        print('>>> lang:', lang)
        try:
            scenarios = Scenario.objects.filter(parent__isnull=True).order_by('pk')  # [207:]
            for count, v in enumerate(scenarios):
                title_translated = translate_to_one_lang_with_azure(
                    api_key=azure_translate_api_key,
                    from_lang=v.language.code_a2,
                    to_lang=lang.code_a2,
                    text=v.title,
                )
                sleep(0.3)
                text_translated = translate_to_one_lang_with_azure(
                    api_key=azure_translate_api_key,
                    from_lang=v.language.code_a2,
                    to_lang=lang.code_a2,
                    text=v.text,
                )
                translated_v_meta, created = ScenarioMetaTranslated.objects.get_or_create(language=lang)
                translated_v = Scenario.objects.create(
                    language=lang,
                    taxonomy=v.taxonomy,
                    meta=translated_v_meta,
                    title=title_translated,
                    text=text_translated,
                    parent=v,
                )
                print(f'> {count+1}/{len(scenarios)} done! ({translated_v}).')
        except Exception as ex:
            print('> translate error:', ex)

# if __name__ == '__main__':
#     azure_translate_api_key = os.environ.get('AZURE_TRANSLATE_API_KEY')
#     result = translate_to_one_lang_with_azure(
#         api_key=azure_translate_api_key,
#         from_lang='uk',
#         to_lang='en',
#         text='Привіт!',
#     )
#     print(result)
