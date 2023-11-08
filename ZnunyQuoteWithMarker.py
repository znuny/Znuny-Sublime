from datetime import date

import sublime
import sublime_plugin


def plugin_loaded():
    global settings
    settings = sublime.load_settings("Znuny.sublime-settings")


class ZnunyQuoteWithMarkerCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        quote_char_start = ""
        quote_char_end = ""
        code_marker_replace = ""

        code_marker = settings.get("znuny_code_marker") or "Znuny"
        current_time = date.today()
        day = current_time.strftime("%d")
        month = current_time.strftime("%m")
        year = current_time.strftime("%Y")
        code_marker = code_marker.replace("${year}", year)
        code_marker = code_marker.replace("${month}", month)
        code_marker = code_marker.replace("${day}", day)

        meta = self.view.meta_info("shellVariables", 0)
        for var in meta:
            if var["name"] == "TM_COMMENT_START":
                quote_char_start = var["value"]

            if var["name"] == "TM_COMMENT_END":
                quote_char_end = " " + var["value"]

        print(meta)

        # Loop over all selections.
        for region in self.view.sel():

            # Skip empty selections.
            if region.empty():
                next

            # Get the selected text.
            selection = self.view.substr(region)

            # Start custom maker.
            code_marker_replace = """{quote_char_start}---{quote_char_end}
{quote_char_start}{code_marker}{quote_char_end}
{quote_char_start}---{quote_char_end}
"""
            # Add QuoteCharStart to every single line.
            for line in selection.split("\n"):

                if len(line) == 0:
                    continue

                # Add quote.
                code_marker_replace += "{quote_char_start}"

                # Add old line and an linebreak.
                code_marker_replace += line + "{quote_char_end}\n"

            # Add old selection and trailing code marker.
            code_marker_replace += selection
            code_marker_replace += "\n\n{quote_char_start}---{quote_char_end}\n"

            code_marker_replace = code_marker_replace.replace(
                "{quote_char_start}", quote_char_start
            )
            code_marker_replace = code_marker_replace.replace(
                "{quote_char_end}", quote_char_end
            )
            code_marker_replace = code_marker_replace.replace(
                "{code_marker}", code_marker
            )

            # Replace the selection with transformed text
            self.view.replace(edit, region, code_marker_replace)

        # Clear selection regions / cursor position.
        self.view.sel().clear()

        # Set new regions to inserted custom marker package name.
        for begin in self.view.find_all(code_marker + "\n"):
            self.view.sel().add(sublime.Region(begin.a, begin.b - 1))
