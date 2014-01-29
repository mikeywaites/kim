#!/usr/bin/python
# -*- coding: utf-8 -*-

import pytest


@pytest.fixture(scope="module")
def foo(request):

    foo = {'foo': 'bar'}

    return foo
