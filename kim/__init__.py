# kim
# Copyright (C) 2014-2015 the Kim authors and contributors
# <see AUTHORS file>
#
# This module is part of Kim and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


__version__ = '1.0.0'


from .mapper import Mapper, PolymorphicMapper
from .exception import (
    MapperError, MappingInvalid, RoleError, FieldOptsError, FieldError,
    FieldInvalid, StopPipelineExecution)
from .role import blacklist, whitelist
from .pipelines import pipe
from .field import (
    Field, String, Integer, Decimal, Boolean, Nested, Collection, Static,
    DateTime, Date)


__all__ = [
    Mapper, PolymorphicMapper, MapperError, MappingInvalid, RoleError,
    FieldOptsError, FieldError, FieldInvalid, StopPipelineExecution, blacklist,
    whitelist, pipe, Field, String, Integer, Decimal, Boolean, Nested,
    Collection, Static, DateTime, Date]
