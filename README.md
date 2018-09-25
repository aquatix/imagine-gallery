imagine-gallery
===============

Image catalog/gallery: make archives of photographs more accessible.

[![Code Health](https://landscape.io/github/aquatix/imagine-gallery/master/landscape.svg?style=flat)](https://landscape.io/github/aquatix/imagine-gallery/master)
[![Known Vulnerabilities](https://snyk.io/test/github/aquatix/imagine-gallery/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/aquatix/imagine-gallery?targetFile=requirements.txt)

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


## Features

Collections (basically groups of subalbums), protected and hidden collections,
configurable album sort options and image sizes (automatic thumbnailing etc),
swipe support on mobile devices (and laptops with touch screen and such),
keyboard navigation, maximised and full view of images, descriptions, EXIF info, GEO locations (GPS).


## TODO and changes

See the [changelog](https://github.com/aquatix/imagine-gallery/blob/master/CHANGELOG.md).


## Third party libraries

For justifying the thumbnails so they get nicely laid out, [Justified-Gallery](https://github.com/miromannino/Justified-Gallery)
is used.

The BebasNeue (regular) font used for headings was obtained from [FontsForWeb](http://fontsforweb.com/font/show?id=1962).

Swipe library: [jQuery TouchSwipe Plugin](https://github.com/mattbryson/TouchSwipe-Jquery-Plugin).
