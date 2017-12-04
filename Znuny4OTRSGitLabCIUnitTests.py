import sublime, sublime_plugin, os, re
from os import walk

class Znuny4OtrsGitLabCiUnitTests(sublime_plugin.TextCommand):

  def run(self, edit):

    folders = self.view.window().folders()

    if len(folders) > 1:
      sublime.status_message('Showing folder selection.')
      sublime.active_window().show_quick_panel(folders, self.folder_selected)
    else:
      self.generate_filelist(folders[0])

  def folder_selected(self, index):

    folders = self.view.window().folders()

    self.generate_filelist(folders[ index ])

  def generate_filelist(self, folder):

    files = []
    for (dirpath, dirnames, filenames) in walk(folder):

      sub_dir = dirpath
      if (sub_dir != folder):
        sub_dir = sub_dir.replace(folder + os.path.sep, '')
      else:
        sub_dir = ''

      if not re.search(r"^scripts"+ re.escape(os.path.sep) + r"test", sub_dir):
        continue

      for filename in filenames:

        if not re.search(r'\.t$', filename):
          continue

        files.append(os.path.join(sub_dir, filename))

    file_entry_template = None
    view_content = self.view.substr(sublime.Region(0, self.view.size()))


    if re.search(r'otrs4', view_content):
      file_entry_template = '    - su -c "perl /opt/otrs/bin/otrs.UnitTest.pl -n {location}" -s /bin/bash otrs'

    # elif re.search(r'image: otrs5', view_content):
    else:
      file_entry_template = '    - su -c "perl /opt/otrs/bin/otrs.Console.pl Dev::UnitTest::Run --verbose --test {location}" -s /bin/bash otrs'

    filelist = []
    for file_location in sorted(files, key=str.lower):
      file_entry = file_entry_template

      if os.path.sep != '/':
        file_location = file_location.replace(os.path.sep, '/')

      file_location = re.sub(r'\.t$', '', file_location)
      file_location = file_location.replace('scripts/test/', '')
      file_entry    = file_entry.replace('{location}', file_location)

      filelist.append(file_entry)

    filelist_result = "\n".join(filelist)

    self.view.run_command("znuny4_otrs_insert_git_lab_ci_unit_tests", {"args":{'filelist':filelist_result}})

class Znuny4OtrsInsertGitLabCiUnitTests(sublime_plugin.TextCommand):
  def run(self, edit, args):
    self.view.insert(edit, self.view.sel()[0].begin(), args['filelist'])
