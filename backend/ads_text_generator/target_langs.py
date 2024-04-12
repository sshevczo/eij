import os
import json
from dotenv import load_dotenv

eastern_european_countries = [
    {
        "code": "ua",
        "name": "Ukraine"
    },
    {
        "code": "gb",
        "name": "United Kingdom"
    },
    {
        "code": "fr",
        "name": "France"
    },
    {
        "code": "it",
        "name": "Italy"
    },
    {
        "code": "al",
        "name": "Albania"
    },
    {
        "code": "ad",
        "name": "Andorra"
    },
    {
        "code": "am",
        "name": "Armenia"
    },
    {
        "code": "at",
        "name": "Austria"
    },
    {
        "code": "az",
        "name": "Azerbaijan"
    },
    {
        "code": "be",
        "name": "Belgium"
    },
    {
        "code": "ba",
        "name": "Bosnia and Herzegovina"
    },
    {
        "code": "bg",
        "name": "Bulgaria"
    },
    {
        "code": "cz",
        "name": "Czech Republic"
    },
    {
        "code": "dk",
        "name": "Denmark"
    },
    {
        "code": "ee",
        "name": "Estonia"
    },
    {
        "code": "fi",
        "name": "Finland"
    },
    {
        "code": "ge",
        "name": "Georgia"
    },
    {
        "code": "de",
        "name": "Germany"
    },
    {
        "code": "gr",
        "name": "Greece"
    },
    {
        "code": "hu",
        "name": "Hungary"
    },
    {
        "code": "is",
        "name": "Iceland"
    },
    {
        "code": "ie",
        "name": "Ireland"
    },
    {
        "code": "lv",
        "name": "Latvia"
    },
    {
        "code": "li",
        "name": "Liechtenstein"
    },
    {
        "code": "lt",
        "name": "Lithuania"
    },
    {
        "code": "lu",
        "name": "Luxembourg"
    },
    {
        "code": "mt",
        "name": "Malta"
    },
    {
        "code": "md",
        "name": "Moldova"
    },
    {
        "code": "mc",
        "name": "Monaco"
    },
    {
        "code": "me",
        "name": "Montenegro"
    },
    {
        "code": "nl",
        "name": "Netherlands"
    },
    {
        "code": "no",
        "name": "Norway"
    },
    {
        "code": "ro",
        "name": "Romania"
    },
    {
        "code": "sm",
        "name": "San Marino"
    },
    {
        "code": "rs",
        "name": "Serbia"
    },
    {
        "code": "si",
        "name": "Slovenia"
    },
    {
        "code": "es",
        "name": "Spain"
    },
    {
        "code": "se",
        "name": "Sweden"
    },
    {
        "code": "ch",
        "name": "Switzerland"
    },
    {
        "code": "tr",
        "name": "Turkey"
    }
]

eastern_european_langs = {
    "Ukraine": ["Ukrainian"],
    "United Kingdom": ["English"],
    "France": ["French"],
    "Italy": ["Italian"],
    "Albania": ["Albanian"],
    "Andorra": ["Catalan"],
    "Armenia": ["Armenian"],
    "Austria": ["German"],
    "Azerbaijan": ["Azerbaijani"],
    "Belgium": ["Dutch", "French", "German"],
    "Bosnia and Herzegovina": ["Bosnian", "Croatian", "Serbian"],
    "Bulgaria": ["Bulgarian"],
    "Czech Republic": ["Czech"],
    "Denmark": ["Danish"],
    "Estonia": ["Estonian"],
    "Finland": ["Finnish", "Swedish"],
    "Georgia": ["Georgian"],
    "Germany": ["German"],
    "Greece": ["Greek"],
    "Hungary": ["Hungarian"],
    "Iceland": ["Icelandic"],
    "Ireland": ["English", "Irish"],
    "Latvia": ["Latvian"],
    "Liechtenstein": ["German"],
    "Lithuania": ["Lithuanian"],
    "Luxembourg": ["Luxembourgish", "French", "German"],
    "Malta": ["Maltese", "English"],
    "Moldova": ["Moldovan (Romanian)"],
    "Monaco": ["French"],
    "Montenegro": ["Montenegrin"],
    "Netherlands": ["Dutch"],
    "Norway": ["Norwegian"],
    "Romania": ["Romanian"],
    "San Marino": ["Italian"],
    "Serbia": ["Serbian"],
    "Slovenia": ["Slovenian"],
    "Spain": ["Spanish"],
    "Sweden": ["Swedish"],
    "Switzerland": ["German", "French", "Italian", "Romansh"],
    "Turkey": ["Turkish"]
}


def write_data_to_json(data: (list, dict), filename: str, mode: str = 'w'):
    json_obj = json.dumps(data, indent=4)
    with open(filename, mode) as outfile:
        outfile.write(json_obj)
        print(f'{len(data)} elements wrote to {filename}')


def get_countries_list(countries_raw_list: list) -> list:
    country_codes = [c.get('name') for c in countries_raw_list if c.get('name')]
    return country_codes


# if __name__ == '__main__':
#     split_langs = {}
#     for key, value in eastern_european_langs.items():
#         split_langs[key] = [lang.strip() for lang in value.split(',')]
#     write_data_to_json(split_langs, 'eastern_european_langs.json')


