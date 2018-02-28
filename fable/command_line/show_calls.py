from __future__ import absolute_import, division
import optparse

def run(args):
  if not args: args = ["--help"]
  parser = optparse.OptionParser(usage="fable.show_calls [options] fortran_file ...")
  parser.add_option("-?", action="help", help=optparse.SUPPRESS_HELP)
  parser.add_option("--top_procedure", action="append", type="str")
  parser.add_option("--top-procedure", action="append", type="str", help=optparse.SUPPRESS_HELP)
  parser.add_option("--write_graphviz_dot", action="store", type="str")
  parser.add_option("--write-graphviz-dot", action="store", type="str", help=optparse.SUPPRESS_HELP)
  option, files = parser.parse_args(args)
  from fable.read import process
  all_fprocs = process(file_names=files)
  topological_fprocs = all_fprocs.build_bottom_up_fproc_list_following_calls(
    top_procedures=option.top_procedure)
  dep_cycles = topological_fprocs.dependency_cycles
  if len(dep_cycles) != 0:
    print "Dependency cycles:", len(dep_cycles)
    for cycle in dep_cycles:
      print " ", " ".join(cycle)
    print
  print "Top-down procedure list:"
  print
  digraph_lhs_rhs = []
  for fproc in reversed(topological_fprocs.bottom_up_list):
    if (fproc.name is None):
      lhs = fproc.fproc_type
      print lhs
    else:
      lhs = fproc.name.value
      print fproc.fproc_type, fproc.name.value
    fwds = set(
      topological_fprocs.forward_uses_by_identifier.get(
        fproc.name.value, []))
    for identifier in sorted(fproc.fdecl_by_identifier.keys()):
      fdecl = fproc.fdecl_by_identifier[identifier]
      if fdecl.is_fproc_name(): continue
      if not fdecl.is_user_defined_callable():
        continue
      called_name = fdecl.id_tok.value
      passed = fproc.externals_passed_by_arg_identifier.get(called_name)
      if passed is None:
        digraph_lhs_rhs.append((lhs, called_name))
      else:
        called_name += "->" + ",".join(sorted(passed))
        for indirectly_called_name in passed:
          digraph_lhs_rhs.append((lhs, indirectly_called_name))
      if fdecl.is_function():
        sz = ""
        if fdecl.size_tokens:
          if (len(fdecl.size_tokens) == 1
                and fdecl.size_tokens[0].is_integer()):
            sz = "*%s" % fdecl.size_tokens[0].value
          else:
            sz = "*(*)"
        s = "%s (%s%s)" % (called_name, fdecl.data_type.value, sz)
      else:
        s = called_name
      if called_name in fwds:
        s += " (dependency cycle)"
      print "  %s" % s
  print
  if option.write_graphviz_dot:
    with open(option.write_graphviz_dot, "w") as f:
      print >> f, "digraph G {"
      for lhs_rhs in digraph_lhs_rhs:
        print >> f, "  %s -> %s;" % lhs_rhs
      print >> f, "}"

if __name__ == "__main__":
  import sys
  run(args=sys.argv[1:])
