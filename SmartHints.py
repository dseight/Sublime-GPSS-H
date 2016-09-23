import sublime
import sublime_plugin


# Optional argumets starts with '*'
descriptions = {
    'ADVANCE': [
        '*The mean time increment',
        '*The time half-range or, if a function, the function modifier'
    ],
    'GENERATE': [
        '*Mean inter generation time',
        '*Inter generation time half-range or Function Modifier',
        '*Start delay time',
        '*Creation limit',
        '*Priority level'
    ],
    'TRANSFER': [
        '*Transfer Block mode',
        '*Block number or location',
        '*Block number or location',
        '*Block number increment for ALL Mode'
    ]
}

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
        block_descriptions = descriptions.get(blockname)
        if not block_descriptions:
            return

        # Try to get description for current argument
        try:
            arg_description = block_descriptions[arg_number]
        except IndexError:
            return

        # Check argument optionality
        if arg_description[0] == '*':
            optional = True
            arg_description = arg_description[1:]
        else:
            optional = False

        # Argument identifying letter
        letter = chr(ord('A') + arg_number)

        if optional:
            message = '<b><i>{}</i></b>: {}'.format(letter, arg_description)
        else:
            message = '<b>{}</b>: {}'.format(letter, arg_description)

        self.view.show_popup(
            message,
            flags=sublime.COOPERATE_WITH_AUTO_COMPLETE,
            max_width=512,
            location=-1)
