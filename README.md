imagine-gallery
===============

Image catalog/gallery: make archives of photographs more accessible.

[![Code Health](https://landscape.io/github/aquatix/imagine-gallery/master/landscape.svg?style=flat)](https://landscape.io/github/aquatix/imagine-gallery/master)

This is a gallery, written in Python/Django, based on the older imagine
[crawler/updater](https://github.com/aquatix/imagine-crawler). This project
largely supersedes the older, more modular approach by integrating the update
mechanism, admin and gallery web view in one.


## Why an image archiver?

As a (hobby) photographer, you might have years and many gigabytes of material
on your drives which you only rarely watch back. To make it more easy to find
certain pictures or just provide a fun trip down memory lane, use imagine to
make an overview of your archives.

The goal is not to import the images into a (new) archive and manage collections
from there, but to provide an easy-to-use overview of your work. This can even
be used standalone (think on a different machine with no access to your library).


## But this is just a gallery, right?

Right :) It's one that tries to make it more easy to get an overview of your
collection, and find things back by making use of the EXIF information embedded
inside the images.

Part of the reason to create imagine was because other gallery software (zenphoto,
gallery2/3 and such) didn't suit my needs, were flaky, insecure or had other
shortcomings.
