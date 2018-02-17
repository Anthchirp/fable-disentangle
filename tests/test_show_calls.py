from __future__ import absolute_import, division, print_function

import os

def test_that_show_calls_does_not_crash():
  import fable.command_line.show_calls
  t_dir = os.path.join(fable.__path__[0], 'test', 'valid')
  files = [f for f in os.listdir(t_dir) if f.endswith('.f') and f != 'blockdata_unnamed.f']
  assert files
  for filename in files:
    fable.command_line.show_calls.run(args=[os.path.join(t_dir, filename)])
