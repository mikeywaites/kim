Changelog
========================

v0.1.5
-----------------------
* fix another issue with decimal type when None

v0.1.4
-----------------------
* fix issue with decimal type when None

v0.1.3
-----------------------
* allow integers to be passed to decimal type
* fix issue where nested top level validate methods would raise
  KimError and not MappingError

v0.1.2
-----------------------
* don't call top level validate methods if errors are already present

v0.1.1
-----------------------
* add NestedForeignKeyStr

v0.1.0
-----------------------
* stable api
* support for SQLAlchemy serializers
* support for django serializers
* full test coverage
* full documentation
