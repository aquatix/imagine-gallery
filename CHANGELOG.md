# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## TODO

- Sort EXIF tags in a logical, fixed order (at least the important ones)
- Protect Collection by only allowing specific users (instead of the current 'needs to be logged in')
- Show GEO info for images with GPS tags
- Video (clip) support


## [Unreleased]
### Added
- Timeline (show latest images from select Collections)
- Django analytics module, supporting Matomo (Piwik) settings for now. Optional.

### Changed
- Some internal housekeeping
- Latest jQuery (3.3.1)
- Latest justifiedGallery (3.7.0)
- Latest Python dependencies
- Moved to the binary distribution of psycopg2, saves some compilation
- Use the [Ionicons icon set](https://ionicons.com/) for EXIF info

### Removed

### Fixed
- Python 3 compatibility
- Redirect to correct page after logging in
