from __future__ import absolute_import, division, print_function

import os

import fable.utils

class file_name_and_expected_cout_info(object):
  def __init__(self):
    self.inp_lines = []
    self.out_lines = []
    self.skip_run = False
    self.ifort_diff_behavior = False
    self.ifort_diff_floating_point_format = False

def read_file_names_and_expected_cout(test_valid):
  with open(os.path.join(test_valid, "file_names_and_expected_cout"), 'r') as fh:
    text = fh.read()
  result = fable.utils.keyed_lists()
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
      if file_name is not None:
        result.get(file_name).append(info)
      info = file_name_and_expected_cout_info()
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
  if file_name is not None:
    result.get(file_name).append(info)
  return result
