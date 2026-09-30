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
import socket
import threading
import traceback


# Stall timeout for each blocking socket op. Prevents a hung GitHub
# connection from freezing the worker indefinitely.
REQUEST_TIMEOUT = 30


# taken from: https://github.com/twolfson/sublime-request/blob/master/request.py#L5
# Attempt to load urllib.request/error and fallback to urllib2 (Python 2/3 compat)
try:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError, URLError
except ImportError:
    from urllib2 import urlopen, Request, HTTPError, URLError

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

        # An empty window has no target for the downloaded file.
        # Stop here, before any GitHub request.
        if not self.project_folders():
            return

        sublime.active_window().show_quick_panel(self.repository_names, self.repository_selected)

    def repository_selected(self, index):

        if index == -1:
            return

        self.selected_repository = self.repository_names[index]

        sublime.status_message('Fetching branches for "%s".' % self.selected_repository)

        def task():
            branches = self.branches()

            names = []
            for branch in branches:
                names.append(branch['name'])

            # reverse branches
            names.reverse()
            return names

        def on_success(names):
            self.branch_names = names
            sublime.status_message('Showing branch selection.')
            sublime.active_window().show_quick_panel(self.branch_names, self.branch_selected)

        self.run_async(task, on_success)

    def branches(self):
        url = 'https://api.github.com/repos/znuny/%s/branches' % self.selected_repository
        sublime.status_message('fetching branches from "%s".' % url)

        return self.url_json(url)

    def branch_selected(self, index):

        if index == -1:
            return

        self.selected_branch = self.branch_names[index]

        sublime.status_message('Fetching files for branch "%s".' % self.selected_branch)

        def task():
            return self.fetch_branch_files()

        def on_success(files):
            self.branch_files = files
            sublime.status_message('Showing file selection for branch "%s".' % self.selected_branch)
            sublime.active_window().show_quick_panel(self.branch_files, self.file_selected)

        self.run_async(task, on_success)

    def fetch_branch_files(self):

        url = "https://api.github.com/repos/znuny/%s/git/trees/%s?recursive=1" % (self.selected_repository, self.selected_branch)

        sublime.status_message('Fetching files for branch "%s" from "%s".' % (self.selected_branch, url))

        tree = self.url_json(url)

        sublime.status_message('Files fetched for branch "%s". Building file list.' % self.selected_branch)

        files = []

        for file in tree['tree']:

            # skip folder names
            if file['type'] == 'tree':
                continue

            files.append(file['path'])

        return files

    def file_selected(self, index):

        if index == -1:
            return

        file_path = self.branch_files[index]

        sublime.status_message('Fetching file "%s" from branch "%s".' % (file_path, self.selected_branch))

        def task():
            url = 'https://api.github.com/repos/znuny/%s/contents/%s?ref=%s' % (self.selected_repository, file_path, self.selected_branch)

            sublime.status_message('Fetching file information for file "%s" from branch "%s" from "%s".' % (file_path, self.selected_branch, url))

            file_information = self.url_json(url)

            url = "https://api.github.com/repos/znuny/%s/commits?path=%s&sha=%s" % (self.selected_repository, file_path, self.selected_branch)

            sublime.status_message('Fetching commits for file "%s" from branch "%s" from "%s".' % (file_path, self.selected_branch, url))

            commits = self.url_json(url)

            file_content = base64.b64decode(file_information['content'].encode('utf-8')).decode('utf-8')

            sublime.status_message('Decoded file "%s" from branch "%s". Adding custom header.' % (file_path, self.selected_branch))
            file_content = self.custom_header(file_content, file_path, commits[0]['sha'])

            target_path = file_path

            if file_path.endswith('.pm') or file_path.endswith('.dtl') or file_path.endswith('.tt'):
                sublime.status_message('Adding file "%s" to Custom/ folder.' % file_path)
                target_path = "Custom/%s" % file_path

            # fix windows line endings
            file_content = file_content.replace('\r\n', '\n')
            file_content = file_content.replace('\r', '\n')

            return {
                'path': target_path,
                'content': file_content,
            }

        def on_success(file_data):
            self.file = file_data

            sublime.status_message('Determing possible target folders for file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
            folders = self.project_folders()

            if not folders:
                return

            if len(folders) > 1:
                sublime.status_message('Showing folder selection for file "%s" from branch "%s".' % (self.file['path'], self.selected_branch))
                sublime.active_window().show_quick_panel(folders, self.folder_selected)
            else:
                self.file['folder'] = folders[0]
                self.write_and_open_file()

        self.run_async(task, on_success)

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

    def project_folders(self):

        folders = self.window.folders()

        if folders:
            return folders

        sublime.error_message('Add a project folder before using Znuny Customizer.')
        return []

    def folder_selected(self, index):

        if index == -1:
            return

        folders = self.project_folders()

        if not folders:
            return

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

    def run_async(self, task, on_success):

        # Drop stale results when a newer selection started another request.
        self._async_token = getattr(self, '_async_token', 0) + 1
        token = self._async_token

        def worker():
            try:
                result = task()
            except Exception as err:
                # URLError.reason is the message built in url_request.
                # Other failures still get a console traceback.
                if isinstance(err, URLError) and isinstance(getattr(err, 'reason', None), str):
                    message = err.reason
                    print('ZnunyCustomizers: %s' % message)
                else:
                    message = 'Error fetching from GitHub: %s' % err
                    print('ZnunyCustomizers: %s' % message)
                    traceback.print_exc()

                def on_error():
                    if token != self._async_token:
                        return
                    sublime.error_message(message)

                sublime.set_timeout(on_error, 0)
                return

            def on_done():
                if token != self._async_token:
                    return
                on_success(result)

            sublime.set_timeout(on_done, 0)

        # Quick-panel callbacks run on the UI thread. Network must not.
        if hasattr(sublime, 'set_timeout_async'):
            sublime.set_timeout_async(worker, 0)
            return

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()

    def url_json(self, url):

        json_result = self.url_content(url)

        sublime.status_message('Successfully read from "%s"' % url)

        return json.loads(json_result)

    def url_content(self, url):

        req = self.url_request(url)

        try:
            charset = req.headers.get_content_charset() or 'utf-8'
            return req.read().decode(charset)
        finally:
            req.close()

    def url_request(self, url):

        request = Request(url)

        github_username = settings.get("znuny_github_username")
        github_token = settings.get("znuny_github_token")

        if github_username and github_token and len(github_username) > 0 and len(github_token) > 0:

            credentials = '%s:%s' % (github_username, github_token)

            credentials_base64 = base64.b64encode(credentials.encode('utf-8'))

            request.add_header("Authorization", "Basic %s" % credentials_base64.decode('utf-8'))

        try:
            req = urlopen(request, timeout=REQUEST_TIMEOUT)
        except HTTPError as err:
            # HTTPError is a URLError. status_message() returns None, so callers
            # must get a raised error instead of a response they would .read().
            message = 'HTTP %s connecting to "%s"' % (err.code, url)
            if err.code == 403 or err.code == 429:
                message += '. GitHub rate limit may be exhausted. Set znuny_github_username and znuny_github_token.'
            err.close()
            raise URLError(message)
        except TypeError as err:
            raise URLError(str(err))
        except socket.timeout:
            raise URLError('Timeout connecting to "%s"' % url)
        except URLError as err:
            raise URLError('Error connecting to "%s" (%s)' % (url, err.reason))

        return req
