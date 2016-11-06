from django.shortcuts import render
from django.http import HttpResponse
from .models import Collection

def index(request):
    collections = Collection.objects.all()
    output = ', '.join([c.title for c in collections])
    return HttpResponse(output)


def collection_detail(request, collection_slug):
    return HttpResponse('collection detail')
