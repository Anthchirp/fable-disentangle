from __future__ import absolute_import, division
from __future__ import print_function

import os
import subprocess
import sys

def _show_lines(lines, out, prefix):
  if (out is None): out = sys.stdout
  for line in lines:
    print(prefix+line, file=out)

class fully_buffered_base(object):

  def format_errors_if_any(self):
    assert not self.join_stdout_stderr
    if (len(self.stderr_lines) != 0):
      msg = ["child process stderr output:"]
      msg.append("  command: " + repr(self.command))
      for line in self.stderr_lines:
        msg.append("  " + line)
      return "\n".join(msg)
    if (self.return_code != 0):
      return "non-zero return code: %s"%(self.return_code)
    return None

  def raise_if_errors(self, Error=RuntimeError):
    assert not self.join_stdout_stderr
    msg = self.format_errors_if_any()
    if (msg is not None):
      raise Error(msg)
    return self

  def raise_if_output(self, show_output_threshold=10, Error=RuntimeError):
    def start_msg():
      result = ["unexpected child process output:"]
      result.append("  command: " + repr(self.command))
      return result
    if (self.stdout_buffer is not None):
      if (len(self.stdout_buffer) != 0):
        msg = start_msg()
        msg.append("  length of output: %d bytes" % len(self.stdout_buffer))
        raise Error("\n".join(msg))
    elif (len(self.stdout_lines) != 0):
      msg = start_msg()
      for line in self.stdout_lines[:show_output_threshold]:
        msg.append("  " + line)
      n = len(self.stdout_lines)
      if (n > show_output_threshold):
        if (n <= show_output_threshold+2):
          for line in self.stdout_lines[show_output_threshold:n]:
            msg.append("  " + line)
        else:
          msg.append("  ...")
          msg.append("  remaining %d lines omitted."
            % (n-show_output_threshold))
      raise Error("\n".join(msg))
    return self

  def raise_if_errors_or_output(self, Error=RuntimeError):
    self.raise_if_errors(Error=Error)
    self.raise_if_output(Error=Error)
    return self

  def show_stderr(self, out=None, prefix=""):
    _show_lines(lines=self.stderr_lines, out=out, prefix=prefix)

  def show_stdout(self, out=None, prefix=""):
    assert self.stdout_lines is not None
    _show_lines(lines=self.stdout_lines, out=out, prefix=prefix)

class fully_buffered_simple(fully_buffered_base):
  """\
Executes command, sends stdin_lines (str or sequence), then reads
stdout_lines first, stderr_lines second (if join_stdout_stderr
is False).

The constructor may deadlock if the I/O buffers are too small to allow
the blocking write and reads in the given sequence. Specifically,
stdin_lines may be too big, or there may be too many stderr_lines,
but there can be any number of stdout_lines. The tests below are
known to work under Mac OS X, Windows XP, IRIX, and Tru64 Unix with
stdin_lines up to 1000000, stderr_lines up to 500. I.e. this simple
implementation should cover most practical situations.
  """

  def __init__(self,
        command,
        stdin_lines=None,
        join_stdout_stderr=False,
        stdout_splitlines=True,
        bufsize=-1):
    self.command = command
    self.join_stdout_stderr = join_stdout_stderr
    if (join_stdout_stderr):
      child_stdin, child_stdout = os.popen4(command, "t", bufsize)
      child_stderr = None
    else:
      child_stdin, child_stdout, child_stderr = os.popen3(command,"t",bufsize)
    if (stdin_lines is not None):
      if (not isinstance(stdin_lines, str)):
        stdin_lines = os.linesep.join(stdin_lines)
        if (len(stdin_lines) != 0):
          stdin_lines += os.linesep
      child_stdin.write(stdin_lines)
    child_stdin.close()
    if (stdout_splitlines):
      self.stdout_buffer = None
      self.stdout_lines = child_stdout.read().splitlines()
    else:
      self.stdout_buffer = child_stdout.read()
      self.stdout_lines = None
    if (child_stderr is not None):
      self.stderr_lines = child_stderr.read().splitlines()
    else:
      self.stderr_lines = []
    child_stdout.close()
    if (child_stderr is not None):
      child_stderr.close()
    self.return_code = None

class fully_buffered_subprocess(fully_buffered_base):
  "This implementation is supposed to never block."

  def __init__(self,
        command,
        stdin_lines=None,
        join_stdout_stderr=False,
        stdout_splitlines=True,
        bufsize=-1):
    self.command = command
    self.join_stdout_stderr = join_stdout_stderr
    if (not isinstance(command, str)):
      command = subprocess.list2cmdline(command)
    if (sys.platform == 'darwin'):   # bypass SIP on OS X 10.11
      command = ("DYLD_LIBRARY_PATH=%s exec "%\
                 os.environ.get("DYLD_LIBRARY_PATH","")) + command
    if (stdin_lines is not None):
      if (not isinstance(stdin_lines, str)):
        stdin_lines = os.linesep.join(stdin_lines)
        if (len(stdin_lines) != 0):
          stdin_lines += os.linesep
    if (join_stdout_stderr):
      stderr = subprocess.STDOUT
    else:
      stderr = subprocess.PIPE
    p = subprocess.Popen(
      args=command,
      shell=True,
      bufsize=bufsize,
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=stderr,
      universal_newlines=True,
      close_fds=not subprocess.mswindows)
    o, e = p.communicate(input=stdin_lines)
    if (stdout_splitlines):
      self.stdout_buffer = None
      self.stdout_lines = o.splitlines()
    else:
      self.stdout_buffer = o
      self.stdout_lines = None
    if (join_stdout_stderr):
      self.stderr_lines = []
    else:
      self.stderr_lines = e.splitlines()
    self.return_code = p.returncode

fully_buffered = fully_buffered_subprocess

def go(command, stdin_lines=None,join_stdout_stderr=True):
  return fully_buffered(
    command=command,
    stdin_lines=stdin_lines,
    join_stdout_stderr=join_stdout_stderr)

def call(command):
  """
  Wraps subprocess.call to run a command.

  Parameters
  ----------
  command : str

  Returns
  -------
  int
      Exit code of subprocess.

  Examples
  --------
  >>> from libtbx.easy_run import call
  >>> ret = call("echo 1")
  1
  >>> print ret
  0
  """
  for s in [sys.stdout, sys.stderr]:
    flush = getattr(s, "flush", None)
    if (flush is not None): flush()
  if (sys.platform == 'darwin'):   # bypass SIP on OS X 10.11
    command = ("DYLD_LIBRARY_PATH=%s exec "%\
               os.environ.get("DYLD_LIBRARY_PATH","")) + command
  return subprocess.call(args=command, shell=True)
