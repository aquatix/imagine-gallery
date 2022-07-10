"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='imagine-gallery', # pip install imagine-gallery
    description='Image archive, core (models) and frontend',
    #long_description=open('README.md', 'rt').read(),
    long_description=long_description,

    # version
    # third part for minor release
    # second when api changes
    # first when it becomes stable someday
    version='0.1.0',
    author='Michiel Scholten',
    author_email='michiel@diginaut.net',

    url='https://github.com/aquatix/imagine-gallery',
    license='Apache',

    # as a practice no need to hard code version unless you know program wont
    # work unless the specific versions are used
    install_requires=['django'],

    py_modules=['imagine-core'],

    zip_safe=True,
)
