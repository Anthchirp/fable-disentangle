from __future__ import absolute_import, division, print_function

import pytest

@pytest.fixture
def testsdir(request):
  return request.fspath.dirname
