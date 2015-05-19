import sublime, sublime_plugin, re

class Znuny4OtrsGenerateBlockHooksCommand(sublime_plugin.TextCommand):
  def run(self, edit):

    # get file name/path of current opened view
    file_path = self.view.file_name()
    # exit early if there is none
    if not file_path: return

    # try to extract the name of the template file
    template_name_match = re.search('.*[\/\\\\](.*?)\.tt$', file_path)
    # exit early if there is none
    if not template_name_match: return

    # store template name
    template_name = template_name_match.group(1)

    # start XML template stub and add template name
    config_template = """<ConfigItem Name="Frontend::Template::GenerateBlockHooks###100-Znuny4OTRSGenerateBlockHooks" Required="1" Valid="1">
    <Description Translatable="1">Generate HTML comment hooks for the specified blocks so that filters can use them.</Description>
    <Group>Znuny4OTRSGenerateBlockHooks</Group>
    <SubGroup>Core</SubGroup>
    <Setting>
        <Hash>
            <Item Key=\""""
    config_template += template_name
    config_template += """\">
                <Array>
"""

    # loop over all "RenderBlockStart" blocks via a RegExp
    # and add an <Item></Item> - entry for each of them
    pattern = re.compile(r'\[% RenderBlockStart\("([^"]+)"\) %\]')
    body    = self.view.substr(sublime.Region(0, self.view.size()))
    for (block_name) in re.findall(pattern, body):
      config_template += '                    '
      config_template += '<Item>'+ block_name +"</Item>\n"

    # close XML template stub
    config_template += '                '
    config_template += """</Array>
            </Item>
        </Hash>
    </Setting>
</ConfigItem>"""

    # open new temporary sublime view and add the XML template
    n = sublime.active_window().new_file()
    n.set_scratch(True)
    n.insert(edit, 0, config_template)