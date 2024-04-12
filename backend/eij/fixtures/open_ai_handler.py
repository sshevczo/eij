import json
import time
from typing import List

from openai import OpenAI

from config.settings import HELICONE_API_KEY
from eij.models import Page

if __name__ == '__main__':
    import os
    import django
    from dotenv import load_dotenv

    load_dotenv()
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()


def get_keywords_prompt(page_lang: str, page_title: str, page_description: str):
    json_format = "\"keywords\": [\n    \"{keyword}\",\n    \"{keyword}\",\n    \"{keyword}\"\n]"
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"I am using google ads to promote pages on my websites. I want you to "
                                    "generate {keywords} for my ad group in specified language based on page title "
                                    "and page description. "
                                    "I also want to include in to keywords specific info mentioned in description."
                                    "You have to respect Google Ad Grants limitations and avoid trademarks in text. "
                                    "Please provide keywords using minimal capital letters."},
        {"role": "assistant", "content": "Certainly! I can help you generate keywords for your Google Ads campaign "
                                         "in specified language based on the page title and page description."},
        {"role": "user", "content": 'Ok. Generate me 15 {keywords} for this example:\n'
                                    f'Language: {page_lang}\n'
                                    f'Page title: {page_title}\n'
                                    f'Page Description: {page_description}\n'
                                    f'I want to get answer in json format only as single array '
                                    f'in this format:\n{json_format}'}
    ]
    return prompt


def get_headers_prompt(page_lang: str, page_title: str, page_description: str):
    json_format = "\"headers\": [\n    \"{header}\",\n    \"{header}\",\n    \"{header}\"\n]"
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "I am using google ads to promote pages on my websites. I want you to "
                                    "generate {headers} in specified language based on page title and page "
                                    "description. You have to respect Google Ad Grants limitations "
                                    "and avoid trademarks in text."
                                    "Please provide headers using minimal capital letters."},
        {"role": "assistant", "content": "Certainly! I can help you generate headers for your Google Ads campaign "
                                         "in specified language based on the page title and page "
                                         "description."},
        {"role": "user", "content": 'Ok. Generate me 15 {headers} limited to 30 characters for ad group for this '
                                    'example:\n'
                                    f'Language: {page_lang}\n'
                                    f'Page title: {page_title}\n'
                                    f'Page description: {page_description}\n'
                                    f'I want to get answer in json format as single array '
                                    f'in this format:\n{json_format}'}
    ]
    return prompt


def get_descriptions_prompt(page_lang: str, page_title: str, page_description: str):
    json_format = ("\"descriptions\": [\n    \"{description}\",\n    \"{description}\",\n    \"{description}\","
                   "\n    \"{description}\"\n]")
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "I am using google ads to promote pages on my websites. I want you to "
                                    "generate {descriptions} for my ad group in specified language based on page"
                                    " title and page description. You have to respect Google Ad Grants "
                                    "limitations and avoid trademarks in text."
                                    "Please provide descriptions using minimal capital letters."},
        {"role": "assistant", "content": "Certainly! I can help you generate descriptions for your ad group in "
                                         "specified language based on the page title and page description."},
        {"role": "user", "content": 'Ok. Generate me 4 {descriptions} limited to 90 characters for ad group for '
                                    'this example:\n'
                                    f'Language: {page_lang}\n'
                                    f'Page title: {page_title}\n'
                                    f'Page description: {page_description}\n'
                                    f'I want to get answer in json format as single array '
                                    f'in this format:\n{json_format}'}
    ]
    return prompt


def get_summary_prompt(page_lang: str, page_title: str, page_content: str):
    json_format = "\"summary\": [\"{summary}\"]"
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "I am using google ads to promote pages websites. "
                                    "I want you to summarize page content and "
                                    "generate {summary} for page in specified language based on page"
                                    "content and page title. "
                                    "The summary should be concise and cover the main points"},
        {"role": "assistant", "content": "Certainly! I can help you generate summary for your page in "
                                         "specified language based on the page title and page content."},
        {"role": "user", "content": 'Ok. Generate me summary limited to 600 characters for '
                                    'this example:\n'
                                    f'Language: {page_lang}\n'
                                    f'Page title: {page_title}\n'
                                    f'Page content: {page_content}\n'
                                    f'I want to get answer in json format as single array '
                                    f'in this format:\n{json_format}'}
    ]
    return prompt


def make_summary_of_page(prompt, api_key: str) -> str | None:
    client = OpenAI(
        api_key=api_key,
        base_url="http://oai.hconeai.com/v1"
    )

    time.sleep(3)

    raw_answer = client.chat.completions.create(
        model='gpt-3.5-turbo-1106',
        response_format={"type": "json_object"},
        messages=prompt,
        extra_headers={
            "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
        },
    )

    return raw_answer.choices[0].message.content


def clean_ai_answer(raw_data: str, target_element_len: int = None) -> list:
    try:
        parsed_json = json.loads(raw_data)
    except Exception as ex:
        print(ex)
        parsed_json = None

    if not parsed_json:
        start_index = raw_data.find('{')
        if start_index != -1:
            end_index = raw_data.rfind('}') + 1
            json_data = raw_data[start_index:end_index]
            # print('>>> clean_ai_answer {}', json_data)
        else:
            start_index = raw_data.find('[')
            end_index = raw_data.rfind(']') + 1
            json_data = raw_data[start_index:end_index]
            # print('>>> clean_ai_answer []', json_data)
        try:
            parsed_json = json.loads(json_data)
        except Exception as ex:
            # print('>> clean_ai_answer error (raw_data):', raw_data)
            # print('>> clean_ai_answer error (json_data):', json_data)
            print('>> clean_ai_answer error:', str(ex))
            return []

    if 'keywords' in parsed_json:
        answer = parsed_json.get('keywords')
    elif 'headers' in parsed_json:
        answer = parsed_json.get('headers')
    elif 'descriptions' in parsed_json:
        answer = parsed_json.get('descriptions')
    else:
        answer = parsed_json

    if type(answer) == dict:
        answer = [value for value in answer.values()]
    if type(answer) != list or len(answer) <= 2 or type(answer) == list and type(answer[0]) != str:
        # print(f'>> clean_ai_answer error: Type: {type(answer)}; Data: {answer}')
        return []

    if target_element_len:
        len_filtered_answer = [element for element in answer if len(element) <= target_element_len]

        return len_filtered_answer if len(len_filtered_answer) > 2 else []

    return answer


def generate_ads_data(page, prompt, api_key: str, target_element_len: int = None) -> list:
    client = OpenAI(
        api_key=api_key,
        base_url="http://oai.hconeai.com/v1"
    )

    time.sleep(3)

    for i in range(20):
        try:
            raw_answer = client.chat.completions.create(
                model='gpt-3.5-turbo-1106',
                response_format={"type": "json_object"},
                messages=prompt,
                extra_headers={
                    "Helicone-Auth": f"Bearer {HELICONE_API_KEY}",
                },
            )

            if i > 1:
                print(f'> try #{i} waiting delay')
                time.sleep(20)
            answer = clean_ai_answer(
                raw_answer.choices[0].message.content, target_element_len)
            if answer:
                return answer
        except Exception as ex:
            print(f'>>> generate_ads_data error: {str(ex)}')
            continue

    page.seodata_task_description = f'> Cant generate data for case: {prompt}'
    page.seodata_task_status = Page.FAILED
    page.save()
    raise Exception(f'> Cant generate data for case: {prompt}')


def limit_phrase(phrase, limit):
    words = phrase.split()
    result = []
    current_length = 0
    for word in words:
        if current_length + len(word) + len(result) <= limit:
            result.append(word)
            current_length += len(word)
        else:
            break
    return ' '.join(result)


def generate_page_seo_data(open_ai_api_key: str, pages: List[Page]):
    result = []

    for count, page in enumerate(pages):
        page.seodata_task_status = Page.STARTED
        page.save()

        keywords_prompt = get_keywords_prompt(
            page.language.name, page.title, page.text)
        keywords = generate_ads_data(
            page=page, prompt=keywords_prompt, api_key=open_ai_api_key, target_element_len=40)
        page.pagerawkeyword_set.all().delete()
        for keyword in keywords[:15]:
            page.pagerawkeyword_set.create(text=keyword[:40])
        page.save()

        headers_prompt = get_headers_prompt(
            page.language.name, page.title, page.text)
        headers = generate_ads_data(
            page=page, prompt=headers_prompt, api_key=open_ai_api_key, target_element_len=30)
        page.pageheader_set.all().delete()
        for header in headers[:15]:
            page.pageheader_set.create(text=header[:30])
        page.save()

        descriptions_prompt = get_descriptions_prompt(
            page.language.name, page.title, page.text)
        descriptions = generate_ads_data(
            page=page, prompt=descriptions_prompt, api_key=open_ai_api_key, target_element_len=90)
        page.pagedescription_set.all().delete()
        for desc in descriptions[:4]:
            page.pagedescription_set.create(text=desc[:90])
        page.save()

        log = f'> {count + 1}/{pages.count()} done | kw: [{page.pagerawkeyword_set.count()}]; hd: ' \
              f'[{page.pageheader_set.count()}]; ds: [{page.pagedescription_set.count()}] --> {page}'
        print(log)

        if keywords and headers and descriptions:
            page.seodata_task_status = Page.SUCCESS
            page.seodata_task_description = (f"Generated kw: [{page.pagerawkeyword_set.count()}]; "
                                             f"hd: [{page.pageheader_set.count()}]; "
                                             f"ds: [{page.pagedescription_set.count()}] for page.")
        else:
            page.seodata_task_status = Page.FAILED
        page.save()

        result.append(log)
    return result
