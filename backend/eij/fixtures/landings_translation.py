import os
import django
from dotenv import load_dotenv
from scenarios_translation import translate_to_one_lang_with_azure as translate

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import Language, Landing, LandingStep
    load_dotenv()


if __name__ == '__main__':
    azure_key = os.environ.get('AZURE_TRANSLATE_API_KEY')
    base_landing = Landing.objects.get(language_id=1)
    from_lang = base_landing.language.code_a2
    base_landing_steps = base_landing.steps.all()
    target_langs = Language.objects.all().exclude(id__in=[1, 2, 27, 30, 35])
    for lang in target_langs:
        landing = Landing.objects.create(
            language=lang,
            hero_title=translate(azure_key, from_lang, lang.code_a2, base_landing.hero_title),
            hero_desc=translate(azure_key, from_lang, lang.code_a2, base_landing.hero_desc),
            about_title=translate(azure_key, from_lang, lang.code_a2, base_landing.about_title),
            about_description=translate(azure_key, from_lang, lang.code_a2, base_landing.about_description),
            about_subtitle_1=translate(azure_key, from_lang, lang.code_a2, base_landing.about_subtitle_1),
            about_text_1=translate(azure_key, from_lang, lang.code_a2, base_landing.about_text_1),
            about_text_2=translate(azure_key, from_lang, lang.code_a2, base_landing.about_text_2),
            steps_title=translate(azure_key, from_lang, lang.code_a2, base_landing.steps_title),
            feat_title=translate(azure_key, from_lang, lang.code_a2, base_landing.feat_title),
            feat_cta=translate(azure_key, from_lang, lang.code_a2, base_landing.feat_cta),
            feat_find=translate(azure_key, from_lang, lang.code_a2, base_landing.feat_find),
            feat_time=translate(azure_key, from_lang, lang.code_a2, base_landing.feat_time),
            feat_law=translate(azure_key, from_lang, lang.code_a2, base_landing.feat_law),
            feat_happy=translate(azure_key, from_lang, lang.code_a2, base_landing.feat_happy),
            form=translate(azure_key, from_lang, lang.code_a2, base_landing.form),
            bot_team=translate(azure_key, from_lang, lang.code_a2, base_landing.bot_team),
            bot_qa=translate(azure_key, from_lang, lang.code_a2, base_landing.bot_qa),
            bot_chat=translate(azure_key, from_lang, lang.code_a2, base_landing.bot_chat),
            bot_att=translate(azure_key, from_lang, lang.code_a2, base_landing.bot_att),
            bot_lng=translate(azure_key, from_lang, lang.code_a2, base_landing.bot_lng),
        )
        for step in base_landing_steps:
            landing_step = LandingStep.objects.create(
                landing=landing,
                number=step.number,
                title=translate(azure_key, from_lang, lang.code_a2, step.title),
                text=translate(azure_key, from_lang, lang.code_a2, step.text),
                time=step.time,
                label=translate(azure_key, from_lang, lang.code_a2, step.label),
            )
            print('> step:', landing_step)
        print('> > done:', landing)
