def get_gcc_version(command_name="gcc"):
  from fable.libtbx import easy_run
  buffer = easy_run.fully_buffered(
    command="%s -dumpversion" % command_name)
  if (len(buffer.stderr_lines) != 0):
    return None
  if (len(buffer.stdout_lines) != 1):
    return None
  major_minor_patchlevel = buffer.stdout_lines[0].split(".")
  if (len(major_minor_patchlevel) not in [2,3]):
    return None
  num = []
  for fld in major_minor_patchlevel:
    try: i = int(fld)
    except ValueError:
      return None
    num.append(i)
  if (len(num) == 2): num.append(0) # substitute missing patchlevel
  return ((num[0]*100)+num[1])*100+num[2]
