import sublime, sublime_plugin, re

class Znuny4OtrsObjectDependencies(sublime_plugin.TextCommand):
  def run(self, edit):

    # get file name/path of current opened view
    file_path = self.view.file_name()
    # exit early if there is none
    if not file_path: return

    # try to extract the name of the perl module file
    perl_module_check = re.search('.*[\/\\\\](.*?)\.pm$', file_path)
    # exit early if it is none
    if not perl_module_check: return

    # store template name
    perl_module_name = perl_module_check.group(1)

    # get the file content
    body = self.view.substr(sublime.Region(0, self.view.size()))

    # try to extract the packe name of the perl module file
    package_name_check = re.search('package (.+'+ perl_module_name +');', body)

    # store if we found one
    package_name = None
    if package_name_check:
        # store template name
        package_name = package_name_check.group(1)

    # @ObjectDependencies template
    object_dependencies_template = "our @ObjectDependencies = (\n"

    # loop over all "$Kernel::OM->Get('...')"s via a RegExp
    # and extract the used object
    object_dependencies = []
    pattern             = re.compile(r'\$Kernel::OM\->(?:Get|Create)\(\s*(?:\'|\")([^\'\"]+)(?:\'|\")')
    for (dependency) in re.findall(pattern, body):

      if package_name and dependency == package_name: continue
      if dependency.find('$') != -1: continue
      if dependency in object_dependencies: continue
      object_dependencies.append( dependency )

    for (dependency) in sorted(object_dependencies):
      object_dependencies_template += "    \'"
      object_dependencies_template += dependency +"',\n"

    object_dependencies_template += ");"

    self.view.insert(edit, self.view.sel()[0].begin(), object_dependencies_template)
