import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from .models import Collection, Directory, Image, ImageMeta
from fractions import Fraction


def fraction_to_float(fraction):
    """Parse string with fraction and return as float"""
    return float(sum(Fraction(s) for s in fraction.split()))


def index(request):
    site_title = settings.SITE_TITLE

    collection_list = Collection.objects.all()
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

    directory_list = Directory.objects.filter(collection=collection, parent_directory=directory)

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

    directory_list = Directory.objects.filter(collection=collection).filter(parent_directory=directory)

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


def image_detail(request, collection_slug, file_path, imagename):
    """
    Show image detail page
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

    image_title = image.filename
    try:
        image_meta = ImageMeta.objects.get(image_hash=image.image_hash)
        if image_meta.title:
            image_title = image_meta.title
    except ImageMeta.DoesNotExist:
        image_meta = ImageMeta()

    exif_highlights = image.get_exif_highlights()
    exif_highlights_pretty = []
    # TODO: translate into icons and such
    for exif_item in exif_highlights:
        if exif_item['key'] == 'EXIF FNumber':
            f_value = 'f/{}'.format(fraction_to_float(exif_item['value']))
            exif_highlights_pretty.append({'key': 'Aperture', 'value': f_value})
        elif exif_item['key'] == 'EXIF ExposureTime':
            exif_highlights_pretty.append({'key': 'Exposure', 'value': '{} sec'.format(exif_item['value'])})
        elif exif_item['key'] == 'EXIF FocalLength':
            exif_highlights_pretty.append({'key': 'Focal length', 'value': '{} mm'.format(exif_item['value'])})
        elif exif_item['key'] == 'EXIF LensModel':
            exif_highlights_pretty.append({'key': 'Lens', 'value': exif_item['value']})
        elif exif_item['key'] == 'Image Model':
            exif_highlights_pretty.append({'key': 'Camera', 'value': exif_item['value']})
        elif exif_item['key'] == 'Image Copyright':
            exif_highlights_pretty.append({'key': '&copy;', 'value': exif_item['value']})
        else:
            exif_highlights_pretty.append(exif_item)

    directory = image.directory
    images = image.directory.images(collection.sortmethod)

    navigation_items = []
    navigation_items.append({'url': reverse('collection_detail', args=[collection.slug]), 'title': collection.title})

    prev_image = None
    next_image = None
    prevpage = ''
    nextpage = ''
    find_next = False

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
            prevpage = reverse('image_detail', args=[collection.slug, directory.relative_path, prev_image.filename])
        if next_image:
            nextpage = reverse('image_detail', args=[collection.slug, directory.relative_path, next_image.filename])
        #navigation_items.append({'url': reverse('directory_detail', args=[collection.slug, directory.relative_path]), 'title': directory.relative_path})

        nav_dir = directory
        while nav_dir.parent_directory:
            navigation_items.insert(1, {'url': reverse('directory_detail', args=[collection.slug, nav_dir.relative_path]), 'title': nav_dir.dir_name})
            nav_dir = nav_dir.parent_directory

        navigation_items.append({'url': reverse('image_detail', args=[collection.slug, directory.relative_path, image.filename]), 'title': image_title})
    else:
        if prev_image:
            prevpage = reverse('rootdir_image_detail', args=[collection.slug, prev_image.filename])
        if next_image:
            nextpage = reverse('rootdir_image_detail', args=[collection.slug, next_image.filename])
        #navigation_items.append({'url': reverse('directory_detail', args=[collection.slug, directory.relative_path]), 'title': directory.relative_path})
        navigation_items.append({'url': reverse('rootdir_image_detail', args=[collection.slug, image.filename]), 'title': image_title})


    context = {
        'site_title': site_title,
        'collection': collection,
        'directory': directory,
        'image': image,
        'image_url': image_url,
        'image_meta': image_meta,
        'image_title': image_title,
        'exif_highlights': exif_highlights_pretty,
        'images': images,
        'navigation_items': navigation_items,
        'prevpage': prevpage,
        'nextpage': nextpage,
    }
    return render(request, 'image/detail.html', context)


def rootdir_image_detail(request, collection_slug, imagename):
    """
    Image from the root of a collection
    """
    return image_detail(request=request, collection_slug=collection_slug, file_path=None, imagename=imagename)


def imagehash_detail(request, imagehash):
    """
    Show image detail page based on imagehash identifier
    """
    try:
        image = Image.objects.filter(imagehash=imagehash)
    except Image.DoesNotExist:
        raise Http404('Image not found')

    site_title = settings.SITE_TITLE

    context = {
        'site_title': site_title,
        'image': image,
    }

    return render(request, 'image/detail.html', context)
