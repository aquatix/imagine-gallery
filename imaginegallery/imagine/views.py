from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import Http404
from .models import Collection

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
    return render(request, 'collection/detail.html', {'collection': collection})
