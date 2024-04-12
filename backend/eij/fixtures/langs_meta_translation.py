import os
import django
from dotenv import load_dotenv
from scenarios_translation import translate_to_one_lang_with_azure as translate

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import LanguageMeta, Language
    load_dotenv()


if __name__ == '__main__':
    azure_key = os.environ.get('AZURE_TRANSLATE_API_KEY')
    base_lang_meta = LanguageMeta.objects.filter(language__code_a2='uk').first()
    from_lang = base_lang_meta.language.code_a2
    target_langs = Language.objects.all().exclude(id__in=[27, 30, 35])
    for lang in target_langs:
        try:
            menu_vacancies = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.menu_scenarios)
            menu_for_business = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.menu_for_business)
            menu_send_cv = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.menu_send_cv)
            menu_categories = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.menu_categories)
            footer_bot = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.footer_bot)
            footer_privacy = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.footer_privacy)
            footer_cookie = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.footer_cookie)
            footer_rights = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.footer_rights)
            err_title = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.err_title)
            err_subtitle = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.err_subtitle)
            err_text = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.err_text)
            err_link = translate(azure_key, from_lang, lang.code_a2, base_lang_meta.err_link)
            meta_lang = LanguageMeta.objects.create(
                language=lang,
                menu_vacancies=menu_vacancies,
                menu_for_business=menu_for_business,
                menu_send_cv=menu_send_cv,
                menu_categories=menu_categories,
                footer_bot=footer_bot,
                footer_privacy=footer_privacy,
                footer_cookie=footer_cookie,
                footer_rights=footer_rights,
                err_title=err_title,
                err_subtitle=err_subtitle,
                err_text=err_text,
                err_link=err_link,
            )
            print('> done:', meta_lang, meta_lang.menu_scenarios)
        except Exception as ex:
            print('> translate error:', ex)
