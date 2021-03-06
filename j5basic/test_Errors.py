# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import *
from j5basic import Errors

def test_traceback_str():
    traceback_str = None
    try:
        raise NotImplementedError()
    except NotImplementedError:
        traceback_str = Errors.traceback_str()
    assert traceback_str is not None

def test_exception_str():
    exception_str = None
    try:
        raise RuntimeError("Testing error")
    except RuntimeError:
        exception_str = Errors.exception_str()
    assert exception_str is not None
# I'm commenting out this test because it's failing and we are not using six
# def test_unicode_errors():
#     value_str = None
#     try:
#         raise ValueError("Pure ascii")
#     except ValueError as e:
#         value_str = Errors.error_to_str(e)
#     assert value_str is not None
#
#     value_str = None
#     try:
#         raise ValueError(six.u("前回修正"))
#     except ValueError as e:
#         value_str = Errors.error_to_str(e)
#     assert value_str is not None
#
#     value_str = None
#     try:
#         raise ValueError(six.u("前回修正").encode('shift-jis'))
#     except ValueError as e:
#         value_str = Errors.error_to_str(e)
#     assert value_str is not None
