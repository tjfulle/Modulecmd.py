import re
import inspect
import textwrap
from argparse import ArgumentParser
from ordereddict_backport import OrderedDict

import pymod.callback

category_descriptions = {
    'path': 'Functions for modifying path-like variables',
    'environment': 'Functions for modifying the environment',
    'modulepath': 'Functions for interacting with the MODULEPATH',
    'utility': 'General purpose utilities',
    'interaction': 'Functions for interacting with other modules',
    'module': 'General module functions',
    'family': 'Functions for interacting with module families',
    'info': 'Functions for relaying information',
    'alias': 'Functions for defining shell aliases and functions',
}

def fill_with_paragraphs(string, indent=''):
    filled = []
    lines = []
    for line in string.split('\n'):
        if line.split():
            lines.append(line)
        elif lines:
            filled.append(
                textwrap.fill('\n'.join(lines),
                              width=80,
                              initial_indent=indent,
                              subsequent_indent=indent)
                + '\n'
            )
            lines = []
    if lines:
        filled.append(
            textwrap.fill('\n'.join(lines),
                          width=80,
                          initial_indent=indent,
                          subsequent_indent=indent)
            + '\n'
        )
    return '\n'.join(filled)


class Callback:
    section_re = re.compile('(?i)^(argument|keyword argument|return|note|example)[s]:')
    def __init__(self, name):
        self.name = name
        self.obj = pymod.callback.get_callback(name)
        self.raw_doc = inspect.getdoc(self.obj)
        self._description = None

        self.parse_docstring()

    def parse_docstring(self):
        self._description = self._parse_description()
        self._param_names = self._parse_signature()
        self._args = self._parse_args_description()
        self._kwargs = self._parse_kwargs_description()
        self._returns = self._parse_returns_description()
        self._notes = self._get_section('note')
        self._examples = self._get_section('example')

    def _parse_description(self):
        description = ''
        for line in self.raw_doc.split('\n'):
            if self.section_re.search(line):
                break
            description += line
        if description.split():
            return ' '.join(description.split())

    def _parse_signature(self):
        param_names = []
        sig = inspect.signature(self.obj)
        for (i, param) in enumerate(sig.parameters.values()):
            param_name = str(param)
            if i == 0:
                if param_name != 'module':
                    raise ValueError(
                        "Expected first parameter of {0} to be 'module', "
                        "got {1}".format(self.name, param))
            elif i == 1:
                if param_name != 'mode':
                    raise ValueError(
                        "Expected first parameter of {0} to be 'mode', "
                        "got {1}".format(self.name, param))
            else:
                param_names.append(param_name)
        return param_names

    def _parse_args_description(self):
        args = []
        in_section = 0
        regex = re.compile('(\w+)\s+\(([a-zA-Z0-9-_ ]+)\)')
        for line in self.raw_doc.split('\n'):
            if not line.split():
                continue
            if self.section_re.search(line):
                if line.lower().startswith('argument'):
                    in_section = 1
                    continue
                in_section = 0
                continue
            if in_section:
                name_and_type, _, description = line.partition(':')
                result = regex.search(name_and_type)
                if result is None:
                    raise ValueError('Expected parameter {0} to be of form '
                                     '<name (type)>'.format(name_and_type))
                name, type = result.groups()
                if name in ('module', 'mode'):
                    continue
                if (name not in self._param_names and
                    '*'+name not in self._param_names):
                    raise ValueError('Parameter {0} not in {1}'
                                     .format(name, self._param_names))
                args.append((name, type, ' '.join(description.split())))
        if args:
            return args

    def _parse_kwargs_description(self):
        kwargs = []
        in_section = 0
        regex = re.compile('(\w+)\s+\(([a-zA-Z0-9-_ ]+)\)')
        for line in self.raw_doc.split('\n'):
            if not line.split():
                continue
            if self.section_re.search(line):
                if line.lower().startswith('keyword argument'):
                    in_section = 1
                    continue
                in_section = 0
                continue
            if in_section:
                name_and_type, _, description = line.partition(':')
                result = regex.search(name_and_type)
                if result is None:
                    raise ValueError('Expected parameter {0} to be of form '
                                     '<name (type)>'.format(name_and_type))
                name, type = result.groups()
                kwargs.append((name, type, ' '.join(description.split())))
        if kwargs:
            return kwargs

    def _parse_returns_description(self):
        returns = []
        in_section = 0
        regex = re.compile('(\w+)\s+\(([a-zA-Z0-9-_ ]+)\)')
        for line in self.raw_doc.split('\n'):
            if not line.split():
                continue
            if self.section_re.search(line):
                if line.lower().startswith('return'):
                    in_section = 1
                    continue
                in_section = 0
                continue
            if in_section:
                name_and_type, _, description = line.partition(':')
                result = regex.search(name_and_type)
                if result is None:
                    raise ValueError('Expected parameter {0} to be of form '
                                     '<name (type)>'.format(name_and_type))
                name, type = result.groups()
                returns.append((name, type, ' '.join(description.split())))
        if returns:
            return returns

    def _get_section(self, section):
        content = []
        in_section = 0
        regex = re.compile('(\w+)\s+\(([a-zA-Z0-9-_ ]+)\)')
        for line in self.raw_doc.split('\n'):
            if self.section_re.search(line):
                if line.lower().startswith(section):
                    in_section = 1
                    continue
                in_section = 0
                continue
            if in_section:
                content.append(line)
        if content:
            return '\n'.join(content)

    def documentation(self, indent='    '):
        params = ', '.join(x.replace('*', '\*') for x in self._param_names)
        s = ['**{0}**\ *({1})*'.format(self.name, params)]

        s.append('\n{0}{1}'.format(indent, self._description))

        if self._args:
            s.append('\n{0}**Arguments**\n'.format(indent))
            for (name, type, description) in self._args:
                s.append('{0}*{1}* ({2}): {3}'.format(indent, name, type, description))

        if self._kwargs:
            s.append('\n{0}**Keyword arguments**\n'.format(indent))
            for (name, type, description) in self._kwargs:
                s.append('{0}*{1}* ({2}): {3}'.format(indent, name, type, description))

        if self._returns:
            s.append('\n{0}**Returns**\n'.format(indent))
            for (name, type, description) in self._returns:
                s.append('{0}*{1}* ({2}): {3}'.format(indent, name, type, description))

        if self._notes:
            s.append('\n{0}**Notes**\n'.format(indent))
            s.append('\n'.join('{0}{1}'.format(indent, x) for x in self._notes.split('\n')))

        if self._examples:
            s.append('\n{0}**Examples**\n'.format(indent))
            s.append('\n'.join('{0}{1}'.format(indent, x) for x in self._examples.split('\n')))

        return '\n'.join(s)




def gen_callback_docs():

    callbacks = {}
    for name in pymod.callback.all_callbacks():
        m = pymod.callback.get_module(name)
        cb = Callback(name)
        callbacks.setdefault(m.category, []).append(cb)

    for (category, items) in callbacks.items():
        description = category_descriptions[category]
        print('^' * len(description))
        print(description)
        print('^' * len(description) + '\n')

        for cb in items:
            print(cb.documentation(indent='    '))
            print('\n')
            exit()


def main():
    p = ArgumentParser()
    p.add_argument('what', choices=('callbacks',))
    args = p.parse_args()

    if args.what == 'callbacks':
        gen_callback_docs()
