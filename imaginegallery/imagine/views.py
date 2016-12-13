from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Collection, Directory, Image

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
    print directory_list

    images = directory_list[0].images(collection.sortmethod)

    context = {
        'collection': collection,
        'directory_list': directory_list,
        'images': images,
    }
    return render(request, 'collection/detail.html', context)


def directory_detail(request, collection_slug, directory):
    try:
        collection = Collection.objects.get(slug=collection_slug)
    except Collection.DoesNotExist:
        raise Http404('Collection does not exist')

    directory = Directory.objects.get(collection=collection, directory=directory)
    print(directory)

    images = directory.images(collection.sortmethod)

    context = {
        'collection': collection,
        'directory': directory,
        'images': images,
    }

def image_detail(request, collection_slug, directory_slug, imagename):
    """
    Show image detail page
    """
    try:
        collection = Collection.objects.get(slug=collection_slug)
    except Collection.DoesNotExist:
        raise Http404('Collection does not exist')

    try:
        directory = Directory.objects.get(slug=directory_slug)
    except Directory.DoesNotExist:
        raise Http404('Directory does not exist')

    try:
        image = Image.objects.get(directory=directory, filename=filename)
    except Image.DoesNotExist:
        raise Http404('Image does not exist')

    context = {
        'collection': collection,
        'directory': directory,
        'image': image,
    }

    return render(request, 'image/detail.html', context)


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
