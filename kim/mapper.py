# kim/mapper.py
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


class Mapper(object):
    """Mappers are the building blocks of Kim - they define how JSON output
    should look and how input JSON should be expected to look.

    Mappers consist of Fields. Fields define the shape and nature of the data
    both when being serialised and marshaled.

    Mappers must define a __model__. This is the type that will be
    instantiated if a new object is marshaled through the mapper. __model__
    maybe be any object that supports setter and getter functionality.

    """
    pass
