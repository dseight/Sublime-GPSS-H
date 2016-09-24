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

    @classmethod
    def is_applicable(cls, settings):
        if 'GPSSH.sublime-syntax' in settings.get('syntax'):
            return True
        else:
            return False

    def __init__(self, view):
        self.selection_end = 0
        super().__init__(view)

    def on_selection_modified_async(self):
        selection_end = self.view.sel()[-1].b
        
        if self.selection_end != selection_end:
            self.selection_end = selection_end
        else:
            return

        if not self.view.match_selector(selection_end, 'variable.parameter.gps'):
            return

        if self.view.match_selector(selection_end, 'support.function.gps'):
            return

        arg_region = self.view.extract_scope(selection_end)
        arguments = self.view.substr(arg_region)

        # Offset from beginning of the arguments to cursor position
        pos = selection_end - arg_region.begin()

        # Number of argument under cursor
        arg_number = arguments.count(',', 0, pos)

        blockname_region = self.view.extract_scope(arg_region.a - 1)

        # Properly recognize name for block with two zones of aruments (such as TEST)
        if not self.view.match_selector(blockname_region.a, 'support.function.gps'):
            blockname_region = self.view.extract_scope(blockname_region.a - 1)

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
        # TODO: if there are any functions, ignore commas in their args
        letter = chr(ord('A') + arg_number)

        if optional:
            message = '<b><i>{}</i></b>: {}'.format(letter, arg_hint)
        else:
            message = '<b>{}</b>: {}'.format(letter, arg_hint)

        self.view.show_popup(
            message,
            flags=sublime.COOPERATE_WITH_AUTO_COMPLETE,
            max_width=512)
