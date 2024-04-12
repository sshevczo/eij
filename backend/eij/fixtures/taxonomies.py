import os
from ads_text_generator.open_ai_handler import get_taxonomy_creation_prompt, generate_ai_answer


if __name__ == '__main__':
    import django
    os.environ["DJANGO_SETTINGS_MODULE"] = 'config.settings'
    django.setup()
    from eij.models import FirstLevelTaxonomy, SecondLevelTaxonomy, TechnologyItem
    tax_qs = FirstLevelTaxonomy.objects.all()
    for tax in tax_qs:
        print(tax.role)
        if not tax.secondleveltaxonomy_set.all():
            prompt = get_taxonomy_creation_prompt(tax.role)
            tax_lvl2 = generate_ai_answer(prompt, '',
                                          expected_data_type='json', print_raw_answer=True)
            if len(tax_lvl2) > 1 and tax_lvl2[0].get('category') and tax_lvl2[0].get('items'):
                for tax2 in tax_lvl2:
                    items = []
                    items_raw = tax2.get('items')
                    for item in items_raw:
                        i, created = TechnologyItem.objects.get_or_create(name=item)
                        items.append(i)
                    category = tax2.get('category')
                    obj = SecondLevelTaxonomy.objects.create(taxonomy=tax, category=category)
                    for i in items:
                        obj.items.add(i)
                    obj.save()

