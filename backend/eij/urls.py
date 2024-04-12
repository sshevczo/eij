from django.urls import path

from eij.views import (PageListApiView, LanguageListApiView,
                       PageRetrieveAPIView, LanguageRetrieveAPIView)

urlpatterns = [
    path('page/list/', PageListApiView.as_view(), name='page_list'),
    path('page/<int:pk>/', PageRetrieveAPIView.as_view(), name='page'),

    path('language/list/', LanguageListApiView.as_view(), name='language_list'),
    path('language/<int:pk>/', LanguageRetrieveAPIView.as_view(), name='language'),
]
