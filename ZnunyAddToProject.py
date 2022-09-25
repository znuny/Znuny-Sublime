import sublime
import sublime_plugin
import os

# https://github.com/titoBouzout/Open-Include/issues/28#issuecomment-31145976


def plugin_loaded():
    global settings
    settings = sublime.load_settings('Znuny.sublime-settings')


class ZnunyAddToProject(sublime_plugin.TextCommand):

    workspace_content = []

    def run(self, edit):

        workspace_directories = settings.get('znuny_workspaces')
        self.workspace_content = []
        for workspace_directory in workspace_directories:
            self.workspace_content += [workspace_directory + name for name in os.listdir(workspace_directory) if os.path.isdir(os.path.join(workspace_directory, name))]  # noqa: E501

        sublime.active_window().show_quick_panel(self.workspace_content, self.add_folder_to_project)

    # inspired by: https://github.com/hellojinjie/OpenCurrentFolder/blob/master/OpenCurrentFolder.py
    def add_folder_to_project(self, index):

        if index == -1:
            return

        dir_name = self.workspace_content[index]

        folder = {
            'follow_symlinks': True,
            'path':            dir_name,
        }
        project_data = sublime.active_window().project_data()
        try:
            folders = project_data['folders']
            for f in folders:
                if f['path'] == dir_name:
                    return
            folders.append(folder)
        except:  # noqa: E722
            folders = [folder]
            if project_data is None:
                project_data = {}
            project_data['folders'] = folders
        sublime.active_window().set_project_data(project_data)
