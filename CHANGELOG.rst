Changelog
========================

v1.1.1
-----------------------
Fix version of iso8601 dependency which was broken by the latest release of that project

v1.1.0
-----------------------

This release focussed solely on improving the peformance of Kim during serialization cycles.  Overall Kim
is now around 75% faster.

* Deprecated `Pipe` class.  This was causing a huge amount of overhead in `Pipelines`
* Reduced the foot print of `Pipeline` and `Session` with usage of __slots__
* removed marshal_extra_X and serialize_extra_X.  Additional pipes are now added to the Pipeline at compile time.
* Avoid duplicate calls to the _MapperRegistry
* optimised the number of time get_mapper_session is called especially in field.Collection runs.
* Added benchmark suite to repo which is run during circle.ci builds

v1.0.3
-----------------------

Removal of Try/Except block from update_output_to_name.  This yielded ~10% performance increase.

v1.0.2
-----------------------

Version bump to fix issues with documentation.

v1.0.1
-----------------------

Version bump to fix issues with documentation.

v1.0.0
-----------------------

Official release of Kim April 2017.
