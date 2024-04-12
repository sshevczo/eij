import os
from ads_text_generator.target_langs import eastern_european_countries, eastern_european_langs
import pycountry


def write_data_to_db():
    for country in eastern_european_countries:
        Country.objects.create(name=country['name'], code_a2=country['code'])

    for name, langs in eastern_european_langs.items():
        print(name, langs)
        country_obj = Country.objects.get(name=name)
        langs_obj = []
        for lang in langs:
            obj = Language.objects.get(name=lang)
            langs_obj.append(obj)
        for lang in langs_obj:
            country_obj.languages.add(lang)
        country_obj.save()


def write_a2_country_codes():
    lang = pycountry.languages.get(name='Turkish')
    print(lang.alpha_2)
    langs = Language.objects.all()
    for lang in langs:
        if not lang.code_a2:
            pycountry_lang = pycountry.languages.get(name=lang.name)
            lang.code_a2 = pycountry_lang.alpha_2
            lang.save()
            print(pycountry_lang.alpha_2, '> added to >', lang.name)
        else:
            print(lang.name, 'skipped!')


if __name__ == '__main__':
    import django
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import Country, Language
    # write_data_to_db()
    # write_a2_country_codes()




