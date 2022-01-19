from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stream/<stream_slug>/', views.stream_detail, name='stream_detail'),
    # ex: /vacation/
    path('<collection_slug>/', views.collection_detail, name='collection_detail'),
    # /family/home/fun/DCIM_4242.jpg/view
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<file_path>.+)/(?P<imagename>.+)/view/$', views.image_detail, name='image_detail'),
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<file_path>.+)/(?P<imagename>.+)/full/$', views.image_full, name='image_full'),
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<file_path>.+)/(?P<imagename>.+)/max/$', views.image_max, name='image_max'),
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<imagename>.+)/view/$', views.rootdir_image_detail, name='rootdir_image_detail'),
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<imagename>.+)/full/$', views.rootdir_image_full, name='rootdir_image_full'),
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<imagename>.+)/max/$', views.rootdir_image_max, name='rootdir_image_max'),
    re_path(r'^(?P<collection_slug>[-\w]+)/(?P<directory>.+)/$', views.directory_detail, name='directory_detail'),
    re_path(r'^imagedetail/(?P<imagehash>\w+)/$', views.imagehash_detail, name='imagehash_detail'),
]
