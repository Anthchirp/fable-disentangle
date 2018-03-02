from __future__ import division

import os
import re
import sys

import fable.cout
import fable.simple_compilation
import pytest

file_names_disable_warnings = set([
  'add_reals.f',
  'add_real_integer.f',
  'logical_a_or_b.f',
  'add_dp_integer.f',
  'real_array_sum.f',
])

file_names_join_stdout_stderr = set([
  'stop_bare.f',
  'stop_integer.f',
  'stop_string.f',
])

top_procedures_by_file_name = {
  'const_analysis_1.f': ['prog'],
  'const_analysis_2.f': ['prog'],
}

dynamic_parameters_by_file_name = {
  "dynamic_parameters_1.f": [fable.cout.dynamic_parameter_props(
    name="root_size", ctype="int", default="3")],
  "dynamic_parameters_2.f": [fable.cout.dynamic_parameter_props(
    name="nums_size", ctype="int", default="2")],
  "dynamic_parameters_3.f": [fable.cout.dynamic_parameter_props(
    name="base_size", ctype="int", default="3")],
  "dynamic_parameters_4.f": [fable.cout.dynamic_parameter_props(
    name="base_size", ctype="int", default="3")],
  "dynamic_parameters_5.f": [fable.cout.dynamic_parameter_props(
    name="base_size", ctype="int", default="3")]}

common_equivalence_simple_by_file_name = {
  "common_equivalence_simple_1.f": ["info"],
  "common_equivalence_simple_2.f": ["info"],
  "common_equivalence_simple_3.f": ["tab"],
  "common_equivalence_simple_4.f": ["first"],
  "common_equivalence_simple_5.f": ["all"],
  "common_equivalence_simple_6.f": ["com"]}

def check_intrinsics_extra(text):
  lines = text.splitlines()
  def check():
    if (len(lines) != 6): return False
    if (re.match(r'\d\d-[A-Z][a-z][a-z]-\d\d', lines[0]) is None): return False
    if (re.match(r'\d\d:\d\d:\d\d', lines[1]) is None): return False
    if (len(lines[2]) != 70): return False
    if (len(lines[3]) != 6): return False
    if (lines[4] != "YkD"): return False
    if (lines[5] != "           0"): return False
    return True
  assert check(), "Unexpected output:\n" + text

def process_file_info(ifort, comp_env, test_valid, file_info):
    from fable.libtbx import easy_run
    from cStringIO import StringIO
    file_name, io_infos = file_info
    print file_name
    file_path = os.path.join(test_valid, file_name)
    top_procedures = top_procedures_by_file_name.get(file_name)
    common_equivalence_simple_list = [set(
      common_equivalence_simple_by_file_name.get(file_name, []))]
    if (len(common_equivalence_simple_list[0]) != 0):
      common_equivalence_simple_list.append([])
    for i_ces,common_equivalence_simple in \
          enumerate(common_equivalence_simple_list):
      common_report_stringio = StringIO()
      lines = fable.cout.process(
          file_names=[file_path],
          top_procedures=top_procedures,
          dynamic_parameters=dynamic_parameters_by_file_name.get(file_name),
          common_equivalence_simple=common_equivalence_simple,
          common_report_stringio=common_report_stringio)
      have_simple_equivalence = (
        "\n".join(lines).find(" // SIMPLE EQUIVALENCE") >= 0)
      if (len(common_equivalence_simple) != 0):
        assert have_simple_equivalence
      else:
        assert not have_simple_equivalence
      assert file_name.endswith(".f")
      base_name = file_name[:-2]
      if (len(common_equivalence_simple_list) != 1):
        base_name += "_alt%d" % i_ces
      fem_cpp = base_name + "_fem.cpp"
      fem_exe_name = fem_cpp[:-4] + comp_env.exe_suffix
      print >> open(fem_cpp, "w"), "\n".join(lines)
      if ifort:
        ifort_exe_name = base_name + "_ifort"
        ifort_cmd = 'ifort -diag-disable 7000 -o %s "%s"' % (
          ifort_exe_name, file_path)
      else:
        ifort_exe_name = None
        ifort_cmd = None
      #
      class BuildError(RuntimeError): pass
      comp_env.build(
          link=True,
          file_name_cpp=fem_cpp,
          exe_name=fem_exe_name,
          disable_warnings=(file_name in file_names_disable_warnings),
          show_command=True,
          Error=BuildError)
      #
      if (ifort_cmd is not None):
        print ifort_cmd
        buffers = easy_run.fully_buffered(command=ifort_cmd)
        buffers.raise_if_errors_or_output(Error=BuildError)
      #
      for info in io_infos:
        if info.skip_run:
          print "Skipping run:", file_name
          continue
        if len(info.inp_lines) != 0:
          print "  number of input lines:", len(info.inp_lines)
        for exe_name in [fem_exe_name, ifort_exe_name]:
          if (exe_name is None): continue
          cmd = cmd0 = os.path.join(".", exe_name)
          print cmd
          join_stdout_stderr = (
               (file_name in file_names_join_stdout_stderr))
          buffers = easy_run.fully_buffered(
            command=cmd,
            stdin_lines=info.inp_lines,
            join_stdout_stderr=join_stdout_stderr)
          if (not join_stdout_stderr):
            class ExeError(RuntimeError): pass
            buffers.raise_if_errors(Error=ExeError)
          if (buffers is not None):
            text = "\n".join(buffers.stdout_lines)
            if file_name == "intrinsics_extra.f":
              check_intrinsics_extra(text)
              return
            if file_name == "sf.f":
              text = text.replace(" -0.620088", " -0.620087")
            elif file_name == "unformatted_experiments.f":
              if sys.byteorder == "big":
                text = text \
                  .replace(
                    "        1234        5678",
                    "        5678        1234") \
                  .replace(
                    "        18558553691448",
                    "        23330262356193")
            assert text == "\n".join(info.out_lines)
          def run_with_args(args):
            cmda = cmd0 + " " + args
            print cmda
            result = easy_run.fully_buffered(
              command=cmda, join_stdout_stderr=True)
            return result
          if (file_name == "read_lines.f"):
            exercise_end_of_line(exe_name=exe_name)
          elif (file_name == "dynamic_parameters_1.f"):
            buffers = run_with_args("--fem-dynamic-parameters=5")
            assert buffers.stdout_lines == [
                '          14          15          16          17          18          19',
                '          20          21          22          23'
            ]
            buffers = run_with_args("--fem-dynamic-parameters=5,6")
            assert buffers.stdout_lines[0].endswith(
              "Too many --fem-dynamic-parameters fields"
              " (given: 2, max. expected: 1)")
            buffers = run_with_args("--fem-dynamic-parameters=x")
            assert buffers.stdout_lines[0].endswith(
              'Invalid --fem-dynamic-parameters field (field 1): "x"')
          elif file_name == "intrinsics_iargc_getarg.f":
            buffers = run_with_args("D rP uWq")
            assert buffers.stdout_lines == [
              "A", "D   ", "rP  ", "uWq ",
              "B", "uWq ", "rP  ", "D   ",
              "C", "rP  ", "uWq ", "D   "]

def exercise_end_of_line(exe_name):
  lines = """\
a
bc
def
ghij
klmno
""".splitlines()
  open("unix.txt", "wb").write("\n".join(lines)+"\n")
  open("dos.txt", "wb").write("\r\n".join(lines)+"\r\n")
  open("dos2.txt", "wb").write("\r\r\n".join(lines)+"\r\n")
  open("mac.txt", "wb").write("\r".join(lines)+"\r")
  from fable.libtbx import easy_run
  from libtbx.utils import remove_files
  expected_outputs = [
    "a   \nbc  \ndef \nghij\nklmn\n",
    "a   \nbc  \ndef \nghij\nklmn\n",
    "a\r  \nbc\r \ndef\r\nghij\nklmn\n",
    "a\rbc\n"]
  for vers,expected in zip(["unix", "dos", "dos2", "mac"], expected_outputs):
    remove_files(paths=["read_lines_out"])
    cmd = "%s < %s.txt > read_lines_out" % (os.path.join(".", exe_name), vers)
    print cmd
    easy_run.fully_buffered(command=cmd).raise_if_errors_or_output()
    assert os.path.isfile("read_lines_out")
    result = open("read_lines_out", "rb").read()
    assert result == expected.replace("\n", os.linesep)

def test_compile_valid(tmpdir, testsdir, valid_test_and_expected_output):
  ifort=False
  pch=False
  pattern=''
  pattern='stop'

  test_name, expected_output = valid_test_and_expected_output
  if pattern not in test_name:
    pytest.skip('Skipped due to filter rule')

  comp_env = fable.simple_compilation.environment()
  if (comp_env.compiler_path is None):
    print "Skipping exercise_compile_valid(): %s not available." % \
      comp_env.compiler
    return

  tmpdir.chdir()

  if pch:
    comp_env.build(
      link=False,
      file_name_cpp=os.path.join(fable.__path__[0], "fem.hpp"),
      pch_name="fem.hpp",
      show_command=True)
    comp_env.set_have_pch()

  test_valid = os.path.join(testsdir, "valid")
  process_file_info(ifort, comp_env, test_valid, valid_test_and_expected_output)
