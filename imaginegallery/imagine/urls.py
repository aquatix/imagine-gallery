from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # ex: /vacation/
    url(r'^(?P<collection_slug>.+)/$', views.collection_detail, name='collection_detail'),
    # /family/home/fun/DCIM_4242.jpg/view
    url(r'^(?P<collection_slug>.+)/(?P<directory>)/(?P<imagename>)/view$', views.image_detail, name='image_detail'),
]
