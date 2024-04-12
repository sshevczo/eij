import os
import django
from dotenv import load_dotenv
from scenarios_translation import translate_to_one_lang_with_azure as translate

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import ScenarioMetaTranslated
    load_dotenv()


if __name__ == '__main__':
    azure_key = os.environ.get('AZURE_TRANSLATE_API_KEY')
    base_meta = ScenarioMetaTranslated.objects.get(language_id=2)
    from_lang = base_meta.language.code_a2
    qs = ScenarioMetaTranslated.objects.all().exclude(pk=base_meta.pk)
    for meta in qs:
        meta.categories = translate(azure_key, from_lang, meta.language.code_a2, meta.categories)
        meta.save()
