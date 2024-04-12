from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ParseError
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from eij.models import Page, Language
from eij.serializers import (
    PageSerializer, LanguageSerializer, )


class DefaultPagination(PageNumberPagination):
    page_size_query_param = 'per_page'
    page_size = 10


class PageListApiView(ListAPIView):
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = Page.objects.select_related('meta').order_by('pk')
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        lang = self.request.query_params.get('lang')
        category = self.request.query_params.get('category')
        if lang:
            queryset = queryset.filter(language__code_a2=lang)
        if category:
            try:
                category_id = int(category)
            except ValueError:
                raise ParseError(detail='Invalid category value. It must be an integer.')
            queryset = queryset.filter(taxonomy_id=category_id)
        return queryset


class LanguageListApiView(ListAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = Language.objects.all().order_by('pk')
    pagination_class = None


class PageRetrieveAPIView(RetrieveAPIView):
    serializer_class = PageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = Page.objects.all()
    lookup_field = 'pk'

    def get_object(self):
        to_lang = self.request.query_params.get('to_lang', None)
        obj = super().get_object()
        if to_lang:
            switch_lang = get_object_or_404(Language, code_a2=to_lang)
            if switch_lang.code_a2 == 'en' and obj.parent:
                translated_obj = obj.parent
            elif switch_lang.code_a2 == 'en' and not obj.parent:
                return obj
            elif obj.parent:
                translated_obj = obj.parent.children.filter(language=switch_lang).first()
            else:
                translated_obj = obj.children.filter(language=switch_lang).first()
            return translated_obj
        return obj


class LanguageRetrieveAPIView(RetrieveAPIView):
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    queryset = Language.objects.all()
    lookup_field = 'pk'
