import os
import csv
import time
from dotenv import load_dotenv
from target_langs import eastern_european_langs, write_data_to_json
from open_ai_handler import get_scenario_creation_prompt, generate_ai_answer


def get_target_langs(data: dict) -> list:
    concatenated_langs = []
    for lst in data.values():
        concatenated_langs.extend(lst)
    return sorted(list(set(concatenated_langs)), key=lambda x: str(x))


def get_scenario_titles(filename: str, delimiter: str = ',', skip_headers: bool = True) -> list:
    with open(filename, 'r', encoding='utf-8') as file:
        rows = csv.reader(file, delimiter=delimiter)
        if skip_headers:
            next(rows)
        return [t[1] for t in rows]


if __name__ == '__main__':
    t1_start = time.perf_counter()
    load_dotenv()
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
    titles = get_scenario_titles('source_data_files/orders_skillpage(cut).csv')
    print(titles)
    langs = get_target_langs(eastern_european_langs)
    print(langs)
    result = {}
    for title in titles:
        lang = 'English'
        lang_result = {}
        t2_start = time.perf_counter()
        prompt = get_scenario_creation_prompt(title=title, language=lang)
        scenario_ad_text = generate_ai_answer(api_key=AZURE_OPENAI_API_KEY, prompt=prompt)
        lang_result[lang] = scenario_ad_text
        t2_stop = time.perf_counter()
        print("> Title done in:", round(t2_stop - t2_start, 0), 'sec.')
        result[title] = lang_result
        if title == 'Moment.js Developers':
            break
    write_data_to_json(result, 'temp_result.json', mode='w')
    t1_stop = time.perf_counter()
    print("Done in:", round(t1_stop - t1_start, 0), 'sec.')


