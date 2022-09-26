import sublime
import sublime_plugin
import re


def plugin_loaded():
    global settings
    settings = sublime.load_settings('Znuny.sublime-settings')


class ZnunyQuoteWithMarkerCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # get quoting char
        quote_char = None
        syntax = self.view.settings().get('syntax')
        znuny_code_marker = settings.get('znuny_code_marker') or "Znuny"

        if re.search("JavaScript", syntax):
            quote_char = '//'
        elif re.search("Perl", syntax):
            quote_char = '#'
        elif re.search("HTML", syntax):
            quote_char = '#'

        if not quote_char or not znuny_code_marker:
            return

        # loop over all selections
        for region in self.view.sel():

            # skip empty selections
            if region.empty():
                next

            # Get the selected text
            selection = self.view.substr(region)

            # start custom maker
            code_marker_replace = """{quote_char} ---
{quote_char} {znuny_code_marker}-
{quote_char} ---
"""

            # loop over each selected line
            for line in selection.split('\n'):

                # add perl quote
                code_marker_replace += '{quote_char}'

                # insert leading space for non empty lines
                if len(line) >= 1:
                    code_marker_replace += ' '

                # add old line and an linebreak
                code_marker_replace += line + "\n"

            # add old selection and trailing code marker
            code_marker_replace += selection
            code_marker_replace += "\n\n{quote_char} ---"

            code_marker_replace = code_marker_replace.replace('{quote_char}', quote_char)
            code_marker_replace = code_marker_replace.replace('{znuny_code_marker}', znuny_code_marker)
    #        code_marker_replace.format(**replace_dict)

            # replace the selection with transformed text
            self.view.replace(edit, region, code_marker_replace)

        # clear selection regions / cursor position
        self.view.sel().clear()

        # set new regions to inserted custom marker package name
        for begin in self.view.find_all("Znuny-\n"):
            self.view.sel().add(sublime.Region(begin.a, begin.b - 1))
