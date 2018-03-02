from __future__ import absolute_import, division, print_function

import os

import munch
import pytest

tests_directory = os.path.dirname(os.path.realpath(__file__))

def pytest_addoption(parser):
  '''Add a '--runslow' option to py.test.'''
  parser.addoption("--runslow", action="store_true",
                   default=False, help="run slow tests")

def pytest_collection_modifyitems(config, items):
  '''Tests marked as slow will not be run unless slow tests are enabled with
     the '--runslow' parameter or the test is selected specifically.'''
  if not config.getoption("--runslow") and len(items) > 1:
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
      if "slow" in item.keywords:
        item.add_marker(skip_slow)

@pytest.fixture
def testsdir():
  return tests_directory

def read_expected_output_for_valid_tests():
  with open(os.path.join(tests_directory, 'valid', 'file_names_and_expected_cout'), 'r') as fh:
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

expected_output_for_valid_tests_dict = read_expected_output_for_valid_tests()

@pytest.fixture(params=[ # mark most of the tests as slow tests
    test if 'stop' in test else pytest.param(test, marks=pytest.mark.slow)
    for test in expected_output_for_valid_tests_dict
])
def valid_test_and_expected_output(request):
  return (request.param, expected_output_for_valid_tests_dict[request.param])

@pytest.fixture()
def dictionary_of_all_valid_tests_and_expected_outputs():
  return expected_output_for_valid_tests_dict.copy()
