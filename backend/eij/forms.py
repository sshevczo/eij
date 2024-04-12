from django import forms

from .fixtures.google_ads_api.accounts_list import get_management_accounts
from .fixtures.google_ads_api.create_campaign import create_campaign, campaign_name_exists
from .models import Campaign, Language


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['customer_id', 'name', 'budget_usd', 'language']

    customer_id = forms.ChoiceField(
        choices=(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(CampaignForm, self).__init__(*args, **kwargs)
        customer_ids = get_management_accounts()
        customer_id_choices = [(customer.get('client_customer'), customer.get('name')) for customer in customer_ids]
        self.fields['customer_id'].choices = customer_id_choices

    def clean_name(self):
        name = self.cleaned_data['name']
        customer_id = self.cleaned_data['customer_id']

        if campaign_name_exists(customer_id, name):
            error_message = f"Campaign with this name ({name}) already exists."

            print(error_message)
            self.add_error('name', 'A campaign with this name already exists.')

        return name

    def save(self, commit=True):
        if not self.instance.pk:
            try:
                campaign_id = create_campaign(customer_id=self.cleaned_data['customer_id'],
                                              campaign_name=self.cleaned_data['name'],
                                              budget_usd=self.cleaned_data['budget_usd'])
                self.instance.campaign_id = campaign_id
            except Exception as e:
                print('Campaign not created!')
                self.add_error(None, 'An unexpected error occurred: {}'.format(e))
                raise e

        # return super(CampaignForm, self).save(commit=commit)

        if not self.errors:
            return super(CampaignForm, self).save(commit=commit)


class ActionLanguageForm(forms.Form):
    language = forms.ModelChoiceField(queryset=Language.objects.all(),
                                      required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}))


class ActionCampaignForm(forms.Form):
    campaign = forms.ModelChoiceField(queryset=Campaign.objects.all(),
                                      required=True,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    ads_number = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )
