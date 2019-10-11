import sublime, sublime_plugin, os, re
from os import walk

class Znuny4OtrsGenerateFilelist(sublime_plugin.TextCommand):

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

    sublime.status_message('Getting content.')

    view_content = self.view.substr(sublime.Region(0, self.view.size()))
    sublime.status_message('Got content.')

    m = re.search(r'<Framework[^>]*>([^<]+)', view_content)
    sublime.status_message('Getting Framework version.')
    if not m:
      return
    sublime.status_message('Got Framework version.')

    otrs_version = m.group(1)

    exec_permission    = '755'
    regular_permission = '644'

    if otrs_version == '6.0.x':
      exec_permission    = '770'
      regular_permission = '660'

    files = []
    for (dirpath, dirnames, filenames) in walk(folder):

      sub_dir = dirpath
      if (sub_dir != folder):
        sub_dir = sub_dir.replace(folder + os.path.sep, '')
      else:
        sub_dir = ''


      if re.search(r'^\.git', sub_dir):
        continue

      if re.search(r'^doc', sub_dir):
        continue

      if re.search(r'^misc', sub_dir):
        continue

      for filename in filenames:

        if re.search(r'^\.', filename):
          continue

        if re.search(r'^README\.md$', filename):
          continue

        if re.search(r'\.sopm$', filename):
          continue

        files.append(os.path.join(sub_dir, filename))

    file_entry_template = '        <File Permission="{permission}" Location="{location}"/>'
    filelist = []
    for file_location in sorted(files, key=str.lower):
      file_entry = file_entry_template

      permission = regular_permission
      if re.search(r'^bin/', file_location):
        permission = exec_permission

      if re.search(r'\.sh$', file_location):
        permission = exec_permission

      if os.path.sep != '/':
        file_location = file_location.replace(os.path.sep, '/')

      file_entry = file_entry.replace('{permission}', permission)
      file_entry = file_entry.replace('{location}', file_location)

      filelist.append(file_entry)

    filelist_result = "\n".join(filelist)

    self.view.run_command("znuny4_otrs_insert_filelist", {"args":{'filelist':filelist_result}})

class Znuny4OtrsInsertFilelist(sublime_plugin.TextCommand):
  def run(self, edit, args):
    self.view.insert(edit, self.view.sel()[0].begin(), args['filelist'])
