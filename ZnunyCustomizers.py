# http://docs.sublimetext.info/en/latest/extensibility/plugins.html
# window.run_command('znuny_customizers')
# view.run_command('znuny_customizers')
# sublime.run_command('znuny_customizers')

import sublime
import sublime_plugin
import os
import json
import re
import base64
import codecs


# taken from: https://github.com/twolfson/sublime-request/blob/master/request.py#L5
# Attempt to load urllib.request/error and fallback to urllib2 (Python 2/3 compat)
try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError
except ImportError:
    from urllib2 import urlopen, URLError

# https://github.com/titoBouzout/Open-Include/issues/28#issuecomment-31145976


def plugin_loaded():
    global settings
    settings = sublime.load_settings('Znuny.sublime-settings')


class ZnunyCustomizers(sublime_plugin.WindowCommand):

    repository_names = ['Znuny', 'ITSMIncidentProblemManagement', 'ITSMConfigurationManagement', 'ITSMChangeManagement', 'ITSMCore', 'GeneralCatalog', 'ITSMServiceLevelManagement', 'ImportExport', 'OTRSMasterSlave', 'TimeAccounting', 'Survey', 'FAQ']  # noqa: E501
    selected_repository = ''
    branch_names = []
    branch_files = []
    selected_branch = ''

    file = {}

    def run(self):

        sublime.active_window().show_quick_panel(self.repository_names, self.repository_selected)

    def repository_selected(self, index):

        if index == -1:
            return

        self.selected_repository = self.repository_names[index]

        branches = self.branches()

        self.branch_names = []
        for branch in branches:
            self.branch_names.append(branch['name'])

        # reverse branches
        self.branch_names = self.branch_names[::-1]

        sublime.status_message('Showing branch selection.')

        sublime.active_window().show_quick_panel(self.branch_names, self.branch_selected)

    def branches(self):
        url = 'https://api.github.com/repos/znuny/%s/branches' % self.selected_repository
        sublime.status_message('fetching branches from "%s".' % url)

        return self.url_json(url)

    def branch_selected(self, index):

        if index == -1:
            return

        self.selected_branch = self.branch_names[index]

        sublime.status_message('Branch "%s" selected.' % self.selected_branch)

        self.fetch_branch_files()

        sublime.status_message('Showing file selection for branch "%s".' % self.selected_branch)
        sublime.active_window().show_quick_panel(self.branch_files, self.file_selected)

    def fetch_branch_files(self):

        url = "https://api.github.com/repos/znuny/%s/git/trees/%s?recursive=1" % (self.selected_repository, self.selected_branch)

        sublime.status_message('Fetching files for branch "%s" from "%s".' % (self.selected_branch, url))

        self.branch_files = []

        tree = self.url_json(url)

        sublime.status_message('Files fetched for branch "%s". Building file list.' % self.selected_branch)

        for file in tree['tree']:

            # skip folder names
            if file['type'] == 'tree':
                continue

            self.branch_files.append(file['path'])

    def file_selected(self, index):

        if index == -1:
            return

        file_path = self.branch_files[index]

        sublime.status_message('Selected file "%s" from branch "%s".' % (file_path, self.selected_branch))

        url = 'https://api.github.com/repos/znuny/%s/contents/%s?ref=%s' % (self.selected_repository, file_path, self.selected_branch)

        sublime.status_message('Fetching file information for file "%s" from branch "%s" from "%s".' % (file_path, self.selected_branch, url))

        file_information = self.url_json(url)

        url = "https://api.github.com/repos/znuny/%s/commits?path=%s;sha=%s" % (self.selected_repository, file_path, self.selected_branch)

        sublime.status_message('Fetching commits for file "%s" from branch "%s" from "%s".' % (file_path, self.selected_branch, url))

        commits = self.url_json(url)

        file_content = base64.decodestring(file_information['content'].encode('utf-8')).decode('utf-8')

        sublime.status_message('Decoded file "%s" from branch "%s". Adding custom header.' % (file_path, self.selected_branch))
        file_content = self.custom_header(file_content, file_path, commits[0]['sha'])

        if file_path.endswith('.pm') or file_path.endswith('.dtl') or file_path.endswith('.tt'):
            sublime.status_message('Adding file "%s" to Custom/ folder.')
            file_path = "Custom/%s" % file_path

        # fix windows line endings
        file_content = file_content.replace('\r\n', '\n')
        file_content = file_content.replace('\r', '\n')

        self.file['path'] = file_path
        self.file['content'] = file_content

        sublime.status_message('Determing possible target folders for file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
        folders = self.window.folders()

        if len(folders) > 1:
            sublime.status_message('Showing folder selection for file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
            sublime.active_window().show_quick_panel(folders, self.folder_selected)
        else:
            self.file['folder'] = folders[0]
            self.write_and_open_file()

    def custom_header(self, content, path, sha):

        copyright = " Copyright (C) 2012 Znuny GmbH, https://znuny.com/"
        comment_prefix = '#'
        comment_prefix_regex = '\%s' % comment_prefix  # noqa: W605

        if path.endswith('.js'):
            comment_prefix = '//'
            comment_prefix_regex = comment_prefix

        # prepare origin block
        origin_block = "%s --\n" % comment_prefix
        origin_block += "%s $origin: %s - %s - %s" % (comment_prefix, self.selected_repository, sha, path)

        # prepare customization header with copyright and origin
        customization_block = "\n%s%s\n%s" % (comment_prefix, copyright, origin_block)

        search_regex = '(^%s\s+Copyright\s[^\n]+\sOTRS\sAG[^\n]+\n)' % comment_prefix_regex  # noqa: W605
        insert_regex = '\\1%s' % customization_block

        search = re.compile(search_regex, re.VERBOSE | re.DOTALL | re.MULTILINE | re.IGNORECASE)
        return search.sub(insert_regex, content)

    def folder_selected(self, index):

        folders = self.window.folders()
        self.file['folder'] = folders[index]

        self.write_and_open_file()

    def write_and_open_file(self):

        sublime.status_message('Adding file "%s" from branch "%s" to folder "%s".' % (self.file['path'], self.selected_branch, self.file['folder']))
        self.file['absolut_path'] = '%s/%s' % (self.file['folder'], self.file['path'])

        self.write_to_file()

        sublime.status_message('Opening file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
        sublime.active_window().open_file(self.file['absolut_path'])

        self.refresh_folders()

        sublime.status_message('Activating view for file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
        sublime.active_window().focus_view(sublime.active_window().active_view())

        self.file = {}

    def refresh_folders(self):
        sublime.status_message('Refreshing folders.')
        data = sublime.active_window().project_data()
        sublime.active_window().set_project_data({})
        sublime.active_window().set_project_data(data)

    def write_to_file(self):

        directory = os.path.dirname(self.file['absolut_path'])
        if not os.path.exists(directory):
            sublime.status_message('Creating folder structure "%s" for file "%s" from branch "%s".' % (directory, self.file['path'], self.selected_branch))  # noqa: E501
            os.makedirs(directory)

        sublime.status_message('Writing content to file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
        file_handle = codecs.open(self.file['absolut_path'], 'w', 'utf-8')
        file_handle.write(self.file['content'])
        file_handle.close()

        return

    def url_json(self, url):

        json_result = self.url_content(url)

        sublime.status_message('Successfully read from "%s"' % url)
        sublime.status_message('json_result "%s"' % json_result)

        return json.loads(json_result)

    def url_content(self, url):

        req = self.url_request(url)

        return req.read().decode(req.headers.get_content_charset())

    def url_request(self, url):

        request = Request(url)

        github_username = settings.get("znuny_github_username")
        github_token = settings.get("znuny_github_token")

        if github_username and github_token and len(github_username) > 0 and len(github_token) > 0:

            credentials = '%s:%s' % (github_username, github_token)

            credentials_base64 = base64.b64encode(credentials.encode('utf-8'))

            request.add_header("Authorization", "Basic %s" % credentials_base64.decode('utf-8'))

        # Attempt to open the url
        try:
            # Make our open request
            req = urlopen(request)
        except TypeError as err:
            # If the arguments are malformed, display the error
            return sublime.status_message(str(err))
        except URLError:
            # Otherwise, if there was a connection error, let it be known
            return sublime.status_message('Error connecting to "%s"' % url)

        return req
