import os
import django
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from ads_text_generator.open_ai_handler import get_scenario_creation_with_taxonomy_prompt, generate_ai_answer

if __name__ == '__main__':
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import FirstLevelTaxonomy, Language, Scenario
    load_dotenv()


def create_scenarios(api_key: str, qnt_limit: int):
    main_language = Language.objects.filter(name='English').first()
    categories = FirstLevelTaxonomy.objects.all()
    for count, tax in enumerate(categories):
        if tax.scenario_set.count() >= qnt_limit:
            print(f'! scenario creation for [{tax}] passed!')
            continue
        taxonomies = tax.secondleveltaxonomy_set.all().order_by('?')[:7]
        taxonomies_prompt = [t.get_category_items_prompt() for t in taxonomies]
        prompt = get_scenario_creation_with_taxonomy_prompt(taxonomy1=tax.role, taxonomies2=str(taxonomies_prompt))
        ai_scenario_text_html = generate_ai_answer(prompt, api_key, expected_data_type='html', print_raw_answer=False)
        soup = BeautifulSoup(ai_scenario_text_html, 'lxml')
        ai_scenario_text = soup.text
        Scenario.objects.create(
            language=main_language,
            taxonomy=tax,
            title=tax.role,
            text=ai_scenario_text,
            text_html=ai_scenario_text_html,
        )
        print(f'> {count+1}/{len(categories)} done > [{tax}]')


if __name__ == '__main__':
    azure_api_key = os.environ.get('AZURE_OPENAI_API_KEY')
    create_scenarios(azure_api_key, qnt_limit=10)
    print('Done!')
