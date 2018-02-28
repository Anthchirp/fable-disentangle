from __future__ import absoute_import, division
import sys

def run(args):
  if (args not in [["--with-quotes"], ["--no-quotes"]]):
    import libtbx.load_env
    sys.exit("%s --with-quotes|--no-quotes" % libtbx.env.dispatcher_name)
  from fable import simple_compilation
  comp_env = simple_compilation.environment()
  print comp_env.assemble_include_search_paths(
    no_quotes=(args[0]=="--no-quotes"))

if __name__ == "__main__":
  run(args=sys.argv[1:])
