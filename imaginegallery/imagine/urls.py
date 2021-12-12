from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stream/<stream_slug>/', views.stream_detail, name='stream_detail'),
    # ex: /vacation/
    path('<collection_slug>/', views.collection_detail, name='collection_detail'),
    # /family/home/fun/DCIM_4242.jpg/view
    path('<collection_slug>/<file_path>/<imagename>/view/', views.image_detail, name='image_detail'),
    path('<collection_slug>/<file_path>/<imagename>/full/', views.image_full, name='image_full'),
    path('<collection_slug>/<file_path>/<imagename>/max/', views.image_max, name='image_max'),
    path('<collection_slug>/<imagename>/view/', views.rootdir_image_detail, name='rootdir_image_detail'),
    path('<collection_slug>/<imagename>/full/', views.rootdir_image_full, name='rootdir_image_full'),
    path('<collection_slug>/<imagename>/max/', views.rootdir_image_max, name='rootdir_image_max'),
    path('<collection_slug>/<directory>/', views.directory_detail, name='directory_detail'),
    path('imagedetail/<imagehash>/', views.imagehash_detail, name='imagehash_detail'),
]
