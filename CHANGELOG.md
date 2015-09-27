# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).


## [Unreleased][unreleased]
### Fixed
- Version links in changelog


## [1.2.0] - 2015-09-27
### Added
- Added changelog and version tags.

### Fixed
- Name collision in when two calls started/received to same number in same minutes #1


## [1.1.1] - 2015-07-13
### Added
- Added version number to script (can check it with ``--version``)

### Changed
- Made more understandable command line help


## [1.1.0] - 2015-05-31
### Added
- Substitutes phone number by name from ``contacts.ini`` (user manage the content)


## 1.0.0 - 2014-12-13
### Added
- Parse filename and convert it's parts as datetime and phone number object.
- User can skip the parse errors (process will not be aborted on error)


[unreleased]: https://github.com/andras-tim/callrecord-renamer/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/andras-tim/callrecord-renamer/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/andras-tim/callrecord-renamer/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/andras-tim/callrecord-renamer/compare/v1.0.0...v1.1.0
