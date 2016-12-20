import os
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from .models import Collection, Directory, Image, ImageMeta

def index(request):
    collection_list = Collection.objects.all()
    template = loader.get_template('collection/index.html')
    context = {
        'collection_list': collection_list,
    }
    return HttpResponse(template.render(context, request))


def collection_detail(request, collection_slug):
    try:
        collection = Collection.objects.get(slug=collection_slug)
    except Collection.DoesNotExist:
        raise Http404('Collection does not exist')

    directory_list = Directory.objects.filter(collection=collection)

    if directory_list:
        images = directory_list[0].images(collection.sortmethod)
        directory = directory_list[0]
    else:
        images = None
        directory = None

    context = {
        'collection': collection,
        'directory_list': directory_list,
        'directory': directory,
        'images': images,
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

    images = directory.images(collection.sortmethod)

    context = {
        'collection': collection,
        'directory': directory,
        'images': images,
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

    image_url = os.path.join(collection.archive_uri, image.get_normal())

    image_title = image.filename
    try:
        image_meta = ImageMeta.objects.get(image_hash=image.image_hash)
        image_title = image_meta.title
    except ImageMeta.DoesNotExist:
        image_meta = ImageMeta()

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
        navigation_items.append({'url': reverse('directory_detail', args=[collection.slug, directory.relative_path]), 'title': directory.dir_path})
    else:
        if prev_image:
            prevpage = reverse('rootdir_image_detail', args=[collection.slug, prev_image.filename])
        if next_image:
            nextpage = reverse('rootdir_image_detail', args=[collection.slug, next_image.filename])
        #navigation_items.append({'url': reverse('directory_detail', args=[collection.slug, directory.relative_path]), 'title': directory.dir_path})

    context = {
        'collection': collection,
        'directory': directory,
        'image': image,
        'image_url': image_url,
        'image_meta': image_meta,
        'image_title': image_title,
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

    context = {
        'image': image,
    }

    return render(request, 'image/detail.html', context)
