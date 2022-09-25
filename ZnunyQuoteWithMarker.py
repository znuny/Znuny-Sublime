import sublime
import sublime_plugin


class ZnunyQuoteWithMarkerCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        # get quoting char
        quote_char = None
        syntax = self.view.settings().get('syntax')

        if syntax == 'Packages/JavaScript/JavaScript.tmLanguage' or syntax == 'Packages/JavaScript/JavaScript.sublime-syntax':
            quote_char = '//'
        elif syntax == 'Packages/Perl/Perl.tmLanguage' or syntax == 'Packages/Perl/Perl.sublime-syntax':
            quote_char = '#'
        elif syntax == 'Packages/HTML/HTML.tmLanguage' or syntax == 'Packages/HTML/HTML.sublime-syntax':
            quote_char = '#'

        if not quote_char:
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
{quote_char} Znuny-
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
    #        code_marker_replace.format(**replace_dict)

            # replace the selection with transformed text
            self.view.replace(edit, region, code_marker_replace)

        # clear selection regions / cursor position
        self.view.sel().clear()

        # set new regions to inserted custom marker package name
        for begin in self.view.find_all("Znuny-\n"):
            self.view.sel().add(sublime.Region(begin.a, begin.b - 1))
