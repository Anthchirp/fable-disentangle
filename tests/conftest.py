from __future__ import absolute_import, division, print_function

import os

import munch
import pytest

@pytest.fixture
def testsdir(request):
  return request.fspath.dirname

@pytest.fixture
def expected_output_for_valid_tests(testsdir):
  with open(os.path.join(testsdir, 'valid', "file_names_and_expected_cout"), 'r') as fh:
    text = fh.read()
  result = {}
  file_name, info = None, None
  for line in text.splitlines():
    if line.startswith("<"):
      assert file_name is not None
      assert line.endswith("<")
      info.inp_lines.append(line[1:-1])
    elif line.startswith("|"):
      assert file_name is not None
      assert line.endswith("|")
      info.out_lines.append(line[1:-1])
    else:
      info = munch.Munch(
          inp_lines=[],
          out_lines=[],
          skip_run=False,
          ifort_diff_behavior=False,
          ifort_diff_floating_point_format=False,
      )
      if line.startswith("!@"):
        file_name = line[2:]
        info.skip_run = True
      elif line.startswith("!="):
        file_name = line[2:]
        info.ifort_diff_behavior = True
      elif line.startswith("!%"):
        file_name = line[2:]
        info.ifort_diff_floating_point_format = True
      else:
        file_name = line
      result[file_name] = result.get(file_name, [])
      result[file_name].append(info)
  return result
