from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /vacation/
    url(r'^(?P<collection_slug>)/$', views.collection_detail, name='collection_detail'),
]
