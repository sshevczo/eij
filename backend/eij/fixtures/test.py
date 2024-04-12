import openai
import time


def get_keywords_prompt(page_lang: str, page_title: str, page_description: str):
    json_format = "[\n    \"{keyword}\",\n    \"{keyword}\",\n    \"{keyword}\"\n]"
    prompt = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": f"I am using google ads to promote scenarios on my job list site. I want you to "
                                    "generate {keywords} for my ad group in specified language based on scenario title "
                                    "and scenario description. "
                                    "I also want to include in to keywords specific skills or technologies mentioned "
                                    "in the job description. You have to respect Google Ad Grants limitations "
                                    "and avoid trademarks in text."},
        {"role": "assistant", "content": "Certainly! I can help you generate keywords for your Google Ads campaign "
                                         "in specified language based on the scenario title and scenario description."},
        {"role": "user", "content": 'Ok. Generate me 15 {keywords} for this example:\n'
                                    f'Language: {page_lang}\n'
                                    f'Scenario title: {page_title}\n'
                                    f'Scenario Description: {page_description}\n'
                                    f'I want to get answer in json format only as single array '
                                    f'in this format:\n{json_format}'}
    ]
    return prompt


def generate_ads_data(prompt, api_key="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",
                      target_element_len: int = None):
    # openai.api_type = "azure"
    # 'https://chat-gpt-4-usa.openai.azure.com/'
    openai.api_base = "https://oai.hconeai.com/v1"
    # openai.api_version = "2023-03-15-preview"  # 2023-05-15
    # openai.api_version = "2023-05-15"
    openai.api_key = api_key

    raw_answer = openai.ChatCompletion.create(
        model='gpt-3.5-turbo', messages=prompt, headers={
            "Helicone-Auth": f"Bearer sk-helicone-tcrwswq-vuuukny-rzve7vy-pfiw3oi",
            # "Helicone-OpenAI-Api-Base": 'https://bablo.openai.azure.com/',
        })  # "gpt-4-32k"

    print(raw_answer)


generate_ads_data([{"role": "system", "content": "You are a helpful assistant."}])