from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stream/(?P<stream_slug>[-\w]+)/$', views.stream_detail, name='stream_detail'),
    # ex: /vacation/
    url(r'^(?P<collection_slug>[-\w]+)/$', views.collection_detail, name='collection_detail'),
    # /family/home/fun/DCIM_4242.jpg/view
    url(r'^(?P<collection_slug>[-\w]+)/(?P<file_path>.+)/(?P<imagename>.+)/view/$', views.image_detail, name='image_detail'),
    url(r'^(?P<collection_slug>[-\w]+)/(?P<file_path>.+)/(?P<imagename>.+)/full/$', views.image_full, name='image_full'),
    url(r'^(?P<collection_slug>[-\w]+)/(?P<file_path>.+)/(?P<imagename>.+)/max/$', views.image_max, name='image_max'),
    url(r'^(?P<collection_slug>[-\w]+)/(?P<imagename>.+)/view/$', views.rootdir_image_detail, name='rootdir_image_detail'),
    url(r'^(?P<collection_slug>[-\w]+)/(?P<imagename>.+)/full/$', views.rootdir_image_full, name='rootdir_image_full'),
    url(r'^(?P<collection_slug>[-\w]+)/(?P<imagename>.+)/max/$', views.rootdir_image_max, name='rootdir_image_max'),
    url(r'^(?P<collection_slug>[-\w]+)/(?P<directory>.+)/$', views.directory_detail, name='directory_detail'),
    url(r'^imagedetail/(?P<imagehash>\w+)/$', views.imagehash_detail, name='imagehash_detail'),
]
