from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from eij.fixtures.google_ads_api.create_campaign import create_campaign


def get_default_user():
    User = get_user_model()
    return User.objects.filter(is_superuser=True).first().id


class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code_a2 = models.CharField(max_length=2, unique=True)
    google_location_id = models.SmallIntegerField(blank=True, null=True)
    languages = models.ManyToManyField('Language', blank=True)

    def __str__(self):
        return f'[{self.code_a2}] {self.name}'

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class Language(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code_a2 = models.CharField(max_length=2, blank=True)
    google_lang_id = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'


class Page(models.Model):
    NO_ACTION = '0'
    STARTED = '1'
    SUCCESS = '2'
    FAILED = '3'

    TASK_STATUS_CHOICES = [
        (NO_ACTION, '-'),
        (STARTED, 'Started'),
        (SUCCESS, 'Successfully Completed'),
        (FAILED, 'Failed'),
    ]

    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    url = models.CharField(max_length=300)
    title = models.CharField(max_length=300)
    text = models.TextField(blank=True)
    website = models.ForeignKey('Website', on_delete=models.SET_NULL, null=True, blank=True)

    seodata_task_status = models.CharField(max_length=1,
                                           choices=TASK_STATUS_CHOICES,
                                           default=NO_ACTION,
                                           verbose_name='SEO data')
    seodata_task_description = models.TextField(blank=True)

    keywords_task_status = models.CharField(max_length=1,
                                            choices=TASK_STATUS_CHOICES,
                                            default=NO_ACTION,
                                            verbose_name='Google Keywords')
    keywords_task_description = models.TextField(blank=True)

    ads_task_status = models.CharField(max_length=1,
                                       choices=TASK_STATUS_CHOICES,
                                       default=NO_ACTION,
                                       verbose_name='ADs')
    ads_task_description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_pages',
        null=True
    )

    class Meta:
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'

    def __str__(self):
        return f'id: {self.pk}, {self.title} [{self.url}]'


class PageRawKeyWord(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Page Raw KeyWord"
        verbose_name_plural = "Page Raw KeyWords"

    def __str__(self):
        return f'v.id: {self.page.id}, text (raw): {self.text}'


class PageGoogleKeyWord(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=70)

    class Meta:
        verbose_name = 'Page Google KeyWord'
        verbose_name_plural = 'Page Google KeyWords'

    def __str__(self):
        return f'v.id: {self.page.id}, text: {self.text}'


class PageHeader(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=30)

    class Meta:
        verbose_name = 'Page Header'
        verbose_name_plural = 'Page Headers'

    def __str__(self):
        return f'v.id: {self.page.id}, text: {self.text}'


class PageDescription(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, null=True)
    text = models.CharField(max_length=90)

    class Meta:
        verbose_name = 'Page Description'
        verbose_name_plural = 'Page Descriptions'

    def __str__(self):
        return f'v.id: {self.page.id}, text: {self.text}'


class Campaign(models.Model):
    campaign_id = models.CharField(blank=True, null=True, max_length=20)
    customer_id = models.CharField(blank=True, max_length=20)
    name = models.CharField(max_length=200, blank=False)
    budget_usd = models.IntegerField(default=333, blank=False)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_campaigns',
        null=True
    )

    class Meta:
        verbose_name = 'Google ADs Campaign'
        verbose_name_plural = 'Google ADs Campaigns'

    def __str__(self):
        return f'Campaign id: {self.campaign_id}, name: {self.name}'


class Website(models.Model):
    NO_ACTION = '0'
    STARTED = '1'
    SUCCESS = '2'
    FAILED = '3'

    TASK_STATUS_CHOICES = [
        (NO_ACTION, '-'),
        (STARTED, 'Started'),
        (SUCCESS, 'Successfully Completed'),
        (FAILED, 'Failed'),
    ]

    base_url = models.CharField(max_length=200, blank=False)
    name = models.CharField(max_length=200, blank=False)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    crawl_task_status = models.CharField(max_length=1,
                                         choices=TASK_STATUS_CHOICES,
                                         default=NO_ACTION,
                                         verbose_name='Crawl status')
    crawl_task_description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_websites',
        null=True
    )

    class Meta:
        verbose_name = 'Website'
        verbose_name_plural = 'Websites'

    def __str__(self):
        return f'{self.name}'
