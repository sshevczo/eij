from datetime import datetime, timedelta

from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from eij.forms import CampaignForm, ActionLanguageForm, ActionCampaignForm
from eij.models import (
    Country, Language, Page,
    PageRawKeyWord, PageGoogleKeyWord, PageHeader,
    PageDescription, Campaign, Website,
)
from eij.tasks import (
    crawl_website_seo_data_for_lang, generate_seo_data_for_selected,
    generate_google_keyword_ideas_for_selected, generate_google_ads_for_selected
)


class PageRawKeyWordInline(admin.StackedInline):
    model = PageRawKeyWord
    extra = 0
    max_num = 15


class PageGoogleKeyWordInline(admin.StackedInline):
    model = PageGoogleKeyWord
    extra = 0
    max_num = 50


class PageHeaderInline(admin.StackedInline):
    model = PageHeader
    extra = 0
    max_num = 15


class PageDescriptionInline(admin.StackedInline):
    model = PageDescription
    extra = 0
    max_num = 4


class PageAdmin(admin.ModelAdmin):
    inlines = (PageRawKeyWordInline, PageGoogleKeyWordInline, PageHeaderInline, PageDescriptionInline)
    list_filter = ('language', 'website', 'seodata_task_status', 'keywords_task_status', 'ads_task_status')
    list_display = ('id',
                    'title',
                    'language',
                    'website_link',
                    'seodata_task_status',
                    'keywords_task_status',
                    'ads_task_status')
    list_display_links = ('id', 'title',)
    search_fields = ('title', 'text',)
    readonly_fields = ('url',
                       'website_link',
                       'seodata_task_status',
                       'seodata_task_description',
                       'keywords_task_status',
                       'keywords_task_description',
                       'ads_task_status',
                       'ads_task_description')
    actions = ['generate_seo_data_action', 'generate_google_keyword_data_action', 'generate_google_ads_action']
    exclude = ('website', 'created_by',)

    def get_queryset(self, request):
        qs = super(PageAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def website_link(self, obj):
        if obj.website:
            url = reverse("admin:eij_website_change", args=[obj.website.pk])
            return format_html('<a href="{}">{}</a>', url, obj.website)
        return "-"

    website_link.short_description = 'Website'

    def generate_seo_data_action(self, request, queryset):
        generate_seo_data_for_selected.delay(list(queryset.values_list('id', flat=True)))

    generate_seo_data_action.short_description = "Generate SEO data for selected"

    def generate_google_keyword_data_action(self, request, queryset):
        request.session['selected_ids'] = list(queryset.values_list('id', flat=True))
        request.session['action_type'] = 'language_form'

        return HttpResponseRedirect('action_form')

    generate_google_keyword_data_action.short_description = "Generate Google Keywords for selected"

    def generate_google_ads_action(self, request, queryset):
        request.session['selected_ids'] = list(queryset.values_list('id', flat=True))
        request.session['action_type'] = 'campaign_form'

        return HttpResponseRedirect('action_form')

    generate_google_ads_action.short_description = "Generate Google Ads for selected"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('action_form/', self.admin_site.admin_view(self.action_form_view),
                 name='action_form'),
        ]
        return my_urls + urls

    def action_form_view(self, request):
        action_type = request.session.get('action_type')
        selected_ids = request.session.get('selected_ids')

        if action_type == 'language_form':
            form = ActionLanguageForm(request.POST or None)
        elif action_type == 'campaign_form':
            form = ActionCampaignForm(request.POST or None)
        else:
            return redirect('admin:index')

        if request.method == 'POST':
            if form.is_valid():
                if action_type == 'language_form':
                    language = form.cleaned_data['language']
                    generate_google_keyword_ideas_for_selected.delay(selected_ids, language.id)
                else:
                    main_campaign = form.cleaned_data['campaign']
                    ads_number = form.cleaned_data['ads_number']
                    generate_google_ads_for_selected.delay(selected_ids, main_campaign.campaign_id, ads_number)

                if 'selected_ids' in request.session:
                    del request.session['selected_ids']

                return HttpResponseRedirect('/admin/eij/page/')

        context = self.admin_site.each_context(request)
        context['form'] = form
        return TemplateResponse(request, "admin/action_form.html", context)


class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code_a2',)
    list_display_links = ('id', 'name',)
    list_filter = ('languages',)


class CampaignAdmin(admin.ModelAdmin):
    form = CampaignForm

    def get_queryset(self, request):
        qs = super(CampaignAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class WebsiteAdmin(admin.ModelAdmin):
    list_filter = ('language', 'crawl_task_status')
    list_display = ('name', 'base_url', 'language', 'crawl_task_status')
    list_display_links = ('name',)
    actions = ['crawl_website_action']
    exclude = ('created_by',)
    readonly_fields = ('crawl_task_status', 'crawl_task_description')

    def get_queryset(self, request):
        qs = super(WebsiteAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def crawl_website_action(self, request, queryset):
        user = request.user.id

        if len(queryset) == 1:
            crawl_website_seo_data_for_lang.delay(queryset[0].id, user)
        else:
            for c, website in enumerate(queryset):
                crawl_website_seo_data_for_lang.apply_async((website.id, user),
                                                            eta=datetime.utcnow() + timedelta(hours=c * 1))

    crawl_website_action.short_description = "Crawl selected websites"


admin.site.register(Website, WebsiteAdmin)
admin.site.register(Campaign, CampaignAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Language)
admin.site.register(Page, PageAdmin)
