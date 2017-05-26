import os
from django.conf import settings
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from .models import Collection, Directory, Image, ImageMeta, PhotoSize, Stream
from fractions import Fraction


def fraction_to_float(fraction):
    """Parse string with fraction and return as float"""
    return float(sum(Fraction(s) for s in fraction.split()))


def index(request):
    site_title = settings.SITE_TITLE

    collection_list = Collection.objects.filter(is_public=True)
    template = loader.get_template('collection/index.html')
    context = {
        'site_title': site_title,
        'collection_list': collection_list,
    }
    return HttpResponse(template.render(context, request))


def collection_detail(request, collection_slug):
    try:
        collection = Collection.objects.get(slug=collection_slug)
    except Collection.DoesNotExist:
        raise Http404('Collection does not exist')

    if collection.needs_authentication and not request.user.is_authenticated:
        # redirect to login
        return redirect('login')

    site_title = settings.SITE_TITLE

    collection_base = collection.base_dir
    if collection_base[-1] != '/':
        collection_base = collection_base + '/'

    try:
        directory = Directory.objects.get(collection=collection, parent_directory=None)
        images = directory.images(collection.sortmethod)
    except Directory.DoesNotExist:
        directory = None
        images = None

    directory_list = Directory.objects.annotate(dirtitle=Coalesce('title', 'relative_path')).filter(collection=collection, parent_directory=directory).order_by('dirtitle')

    navigation_items = []
    navigation_items.append({'url': reverse('collection_detail', args=[collection.slug]), 'title': collection.title})

    context = {
        'site_title': site_title,
        'collection': collection,
        'directory_list': directory_list,
        'directory': directory,
        'images': images,
        'navigation_items': navigation_items,
    }
    return render(request, 'collection/detail.html', context)


def directory_detail(request, collection_slug, directory):
    try:
        collection = Collection.objects.get(slug=collection_slug)
    except Collection.DoesNotExist:
        raise Http404('Collection does not exist')

    try:
        directory = Directory.objects.get(collection=collection, relative_path=directory)
    except Directory.DoesNotExist:
        raise Http404('Directory does not exist')

    site_title = settings.SITE_TITLE

    directory_list = Directory.objects.annotate(dirtitle=Coalesce('title', 'relative_path')).filter(collection=collection, parent_directory=directory).order_by('dirtitle')

    images = directory.images(collection.sortmethod)

    navigation_items = []
    navigation_items.append({'url': reverse('collection_detail', args=[collection.slug]), 'title': collection.title})

    nav_dir = directory
    while nav_dir.parent_directory:
        navigation_items.insert(1, {'url': reverse('directory_detail', args=[collection.slug, nav_dir.relative_path]), 'title': nav_dir.dir_name})
        nav_dir = nav_dir.parent_directory

    context = {
        'site_title': site_title,
        'collection': collection,
        'directory': directory,
        'directory_list': directory_list,
        'images': images,
        'navigation_items': navigation_items,
    }
    return render(request, 'directory/detail.html', context)


def _get_image_details(request, collection_slug, file_path, imagename, thumbs=False, viewtype='detail'):
    """
    Show image detail page
    viewtype: detail or max
    """
    try:
        collection = Collection.objects.get(slug=collection_slug)
    except Collection.DoesNotExist:
        raise Http404('Collection does not exist')

    if not file_path:
        # Likely an image from the root of a Collection or Directory
        file_path = '/'
    else:
        file_path = '/{}'.format(file_path)

    try:
        image = Image.objects.get(file_path=file_path, filename=imagename)
    except Image.DoesNotExist:
        raise Http404('Image does not exist')

    site_title = settings.SITE_TITLE

    image_url = os.path.join(collection.archive_uri, image.get_normal())
    image_orig_url = None
    if collection.base_uri:
        image_orig_url = image.get_original(collection.base_uri)

    image_thumb_url = os.path.join(collection.archive_uri, image.get_thumbnail())
    image_thumb_sizes = (1024, 1024)
    try:
        image_thumb_sizes = PhotoSize.objects.get(name='thumbnail')
    except PhotoSize.DoesNotExist:
        pass

    image_title = image.filename
    try:
        image_meta = ImageMeta.objects.get(image_hash=image.image_hash)
        if image_meta.title:
            image_title = image_meta.title
    except ImageMeta.DoesNotExist:
        image_meta = ImageMeta()

    exif_highlights = image.get_exif_highlights()
    exif_highlights_pretty = []
    #exif_highlights_pretty.append({'key': '<i title="Taken on" class="material-icons">today</i>', 'value': image.filter_modified.strftime(settings.DATETIME_FORMAT)})
    # TODO: translate into icons and such
    for exif_item in exif_highlights:
        if exif_item['key'] == 'Image Model':
            # Camera type
            exif_highlights_pretty.append({'key': '<i title="Camera" class="ionicons ion-camera"></i>', 'value': exif_item['value']})
        elif exif_item['key'] == 'EXIF FNumber':
            # f-number
            f_value = 'f/{}'.format(fraction_to_float(exif_item['value']))
            exif_highlights_pretty.append({'key': '<i title="Aperture" class="ionicons ion-aperture"></i>', 'value': f_value})
        elif exif_item['key'] == 'EXIF ExposureTime':
            # Exposure
            exif_highlights_pretty.append({'key': '<i title="Exposure" class="material-icons">exposure</i>', 'value': '{} sec'.format(exif_item['value'])})
        elif exif_item['key'] == 'EXIF Flash':
            # Flash fired or not, what mode
            if ' not ' in exif_item['value']:
                exif_highlights_pretty.append({'key': '<i title="Flash" class="ionicons ion-flash-off"></i>', 'value': exif_item['value']})
            else:
                exif_highlights_pretty.append({'key': '<i title="Flash" class="ionicons ion-flash"></i>', 'value': exif_item['value']})
        elif exif_item['key'] == 'EXIF FocalLength':
            exif_highlights_pretty.append({'key': '<i title="Focal length" class="material-icons">visibility</i>', 'value': '{}mm'.format(exif_item['value'])})
        elif exif_item['key'] == 'EXIF ISOSpeedRatings':
            exif_highlights_pretty.append({'key': '<i title="ISO speed" class="material-icons">iso</i>', 'value': exif_item['value']})
        elif exif_item['key'] == 'EXIF LensModel':
            exif_highlights_pretty.append({'key': '<i title="Lens" class="material-icons">lens</i>', 'value': exif_item['value']})
        elif exif_item['key'] == 'Image Copyright':
            exif_highlights_pretty.append({'key': '&copy;', 'value': exif_item['value']})
        elif exif_item['key'] == 'Image Artist':
            exif_highlights_pretty.append({'key': '<i title="Image artist" class="material-icons">person</i>', 'value': exif_item['value']})
        else:
            exif_highlights_pretty.append(exif_item)

    directory = image.directory

    navigation_items = []
    navigation_items.append({'url': reverse('collection_detail', args=[collection.slug]), 'title': collection.title})

    images = None
    prev_image = None
    next_image = None
    prevpage = ''
    nextpage = ''
    uppage = ''
    find_next = False

    images = image.directory.images(collection.sortmethod)

    for this_image in images:
        if this_image == image:
            find_next = True
        elif find_next:
            next_image = this_image
            break
        else:
            prev_image = this_image

    if directory.relative_path:
        if prev_image:
            prevpage = reverse('image_' + viewtype, args=[collection.slug, directory.relative_path, prev_image.filename])
        if next_image:
            nextpage = reverse('image_' + viewtype, args=[collection.slug, directory.relative_path, next_image.filename])
        #navigation_items.append({'url': reverse('directory_detail', args=[collection.slug, directory.relative_path]), 'title': directory.relative_path})

        uppage = reverse('directory_detail', args=[collection.slug, directory.relative_path])
        nav_dir = directory
        while nav_dir.parent_directory:
            navigation_items.insert(1, {'url': reverse('directory_detail', args=[collection.slug, nav_dir.relative_path]), 'title': nav_dir.dir_name})
            nav_dir = nav_dir.parent_directory

        image_detail_url = reverse('image_detail', args=[collection.slug, directory.relative_path, image.filename])
        image_max_url = reverse('image_max', args=[collection.slug, directory.relative_path, image.filename])
        image_full_url = reverse('image_full', args=[collection.slug, directory.relative_path, image.filename])
        navigation_items.append({'url': image_detail_url, 'title': image_title})
    else:
        uppage = navigation_items[-1]['url']
        if prev_image:
            prevpage = reverse('rootdir_image_' + viewtype, args=[collection.slug, prev_image.filename])
        if next_image:
            nextpage = reverse('rootdir_image_' + viewtype, args=[collection.slug, next_image.filename])
        #navigation_items.append({'url': reverse('directory_detail', args=[collection.slug, directory.relative_path]), 'title': directory.relative_path})
        image_detail_url = reverse('rootdir_image_detail', args=[collection.slug, image.filename])
        image_max_url = reverse('rootdir_image_max', args=[collection.slug, image.filename])
        image_full_url = reverse('rootdir_image_full', args=[collection.slug, image.filename])
        navigation_items.append({'url': image_detail_url, 'title': image_title})


    context = {
        'site_title': site_title,
        'collection': collection,
        'directory': directory,
        'image': image,
        'image_url': image_url,
        'image_orig_url': image_orig_url,
        'image_thumb_url': image_thumb_url,
        'image_thumb_sizes': image_thumb_sizes,
        'image_detail_url': image_detail_url,
        'image_max_url': image_max_url,
        'image_full_url': image_full_url,
        'image_meta': image_meta,
        'image_title': image_title,
        'image_date': image.filter_modified.strftime(settings.DATETIME_FORMAT),
        'exif_highlights': exif_highlights_pretty,
        'images': images,
        'navigation_items': navigation_items,
        'prevpage': prevpage,
        'nextpage': nextpage,
        'uppage': uppage,
    }
    return context, image


def image_detail(request, collection_slug, file_path, imagename, thumbs=False):
    context, image = _get_image_details(request, collection_slug, file_path, imagename, True)
    if image.is_photosphere:
        return render(request, 'image/detail_photosphere.html', context)
    else:
        return render(request, 'image/detail.html', context)


def rootdir_image_detail(request, collection_slug, imagename):
    """
    Image from the root of a collection
    """
    return image_detail(request=request, collection_slug=collection_slug, file_path=None, imagename=imagename)


def image_full(request, collection_slug, file_path, imagename):
    """
    Show image full view page (unzoomed, no album thumbnails)
    """
    context, image = _get_image_details(request, collection_slug, file_path, imagename, False)
    return render(request, 'image/full.html', context)


def image_max(request, collection_slug, file_path, imagename):
    """
    Show image fullscreen page (zoomed to fit screen, no album thumbnails and details)
    """
    context, image = _get_image_details(request, collection_slug, file_path, imagename, False, viewtype='max')
    return render(request, 'image/max.html', context)


def rootdir_image_full(request, collection_slug, imagename):
    """
    Image from the root of a collection, large size
    """
    return image_full(request=request, collection_slug=collection_slug, file_path=None, imagename=imagename)


def rootdir_image_max(request, collection_slug, imagename):
    """
    Image from the root of a collection, fullscreen
    """
    return image_max(request=request, collection_slug=collection_slug, file_path=None, imagename=imagename)


def imagehash_detail(request, imagehash):
    """
    Show image detail page based on imagehash identifier
    """
    try:
        image = Image.objects.filter(image_hash=imagehash)
    except Image.DoesNotExist:
        raise Http404('Image not found')

    site_title = settings.SITE_TITLE

    context = {
        'site_title': site_title,
        'image': image,
    }

    return render(request, 'image/detail.html', context)


def stream_overview(request):
    """
    Show a choise of streams
    """
    pass


def stream_detail(request, stream_slug):
    """
    Show a stream of images:
    - selection from a set of Collection
    - delimited by start_datetime and end_datetime, both not mandatory
    """
    try:
        stream = Stream.objects.get(slug=stream_slug)
    except Stream.DoesNotExist:
        raise Http404('Stream does not exist')

    print(stream.collections.all())

    # Get all images that are in the selected Collections of this Stream
    images = Image.objects.filter(collection__in=stream.collections.all()).distinct()

    if stream.start_datetime:
        images.filter(filter_modified__gte=stream.start_datetime)
    if stream.end_datetime:
        images.filter(filter_modified__lte=stream.end_datetime)

    images.filter(is_visible=True)

    if stream.sortmethod == Collection.SORT_NAME_DESC:
        images.order_by('-filename')
    elif stream.sortmethod == Collection.SORT_NAME_ASC:
        images.order_by('filename')
    elif stream.sortmethod == Collection.SORT_DATE_DESC:
        images.order_by('-filter_modified')
    elif stream.sortmethod == Collection.SORT_DATE_ASC:
        images.order_by('filter_modified')
    print images

    site_title = settings.SITE_TITLE
    context = {
        'site_title': site_title,
        'stream': stream,
        'images': images,
    }

    return render(request, 'stream/detail.html', context)
