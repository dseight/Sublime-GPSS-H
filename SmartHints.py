import sublime
import sublime_plugin
import json


# Optional argumets starts with '*'
hints = {}

resources = sublime.find_resources('gpssh_hints.json')

if resources != []:
    data = sublime.load_resource(resources[0])
    hints = json.loads(data)


class SmartHint(sublime_plugin.ViewEventListener):

    def on_selection_modified_async(self):
        if not self.view.match_selector(self.view.sel()[-1].b, 'variable.parameter.gps'):
            return

        if self.view.match_selector(self.view.sel()[-1].b, 'support.function.gps'):
            return

        selection_end = self.view.sel()[-1].b

        arg_region = self.view.extract_scope(selection_end)
        arguments = self.view.substr(arg_region).strip()

        # Offset from beginning of the arguments to cursor position
        pos = selection_end - arg_region.begin()

        # Number of argument under cursor
        arg_number = arguments.count(',', 0, pos)

        blockname_region = self.view.extract_scope(arg_region.a - 1)
        blockname = self.view.substr(blockname_region).strip()

        # Arguments description for current block
        block_hints = hints.get(blockname)
        if not block_hints:
            return

        # Try to get description for current argument
        try:
            arg_hint = block_hints[arg_number]
        except IndexError:
            return

        # Check argument optionality
        if arg_hint[0] == '*':
            optional = True
            arg_hint = arg_hint[1:]
        else:
            optional = False

        # Argument identifying letter
        letter = chr(ord('A') + arg_number)

        if optional:
            message = '<b><i>{}</i></b>: {}'.format(letter, arg_hint)
        else:
            message = '<b>{}</b>: {}'.format(letter, arg_hint)

        self.view.show_popup(
            message,
            flags=sublime.COOPERATE_WITH_AUTO_COMPLETE,
            max_width=512,
            location=-1)
