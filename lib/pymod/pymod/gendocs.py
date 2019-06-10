import inspect
import textwrap
from argparse import ArgumentParser

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
    return '\n'.join(filled)


class Callback:
    def __init__(self, name):
        self.name = name
        self.obj = pymod.callback.get_callback(name)
        self.raw_doc = inspect.getdoc(self.obj)
        self.doc = self._remove_module_mode_params(self.raw_doc)
        self.sig = inspect.signature(self.obj)
        self._doc_sections = {}

    def _remove_module_mode_params(self, doc):
        doc = doc.split('\n')
        in_params = 0
        for (i, line) in enumerate(doc):
            if line.startswith('-----'):
                preceding = doc[i-1]
                if preceding.lower().startswith('parameters'):
                    in_params = 1
                    continue
            elif in_params:
                if in_params in (1, 2, 3, 4):
                    # skip module and mode parameter descriptions
                    in_params += 1
                    doc[i] = None
                else:
                    continue
        doc = '\n'.join(x for x in doc if x is not None)
        return doc

    def get_doc_section(self, name):
        if name.lower() in self._doc_sections:
            return self._doc_sections[name.lower()]

        doc = self.doc.split('\n')
        section = []
        in_section = 0
        for (i, line) in enumerate(doc):
            if line.startswith('-----'):
                if in_section:
                    section = section[:-1]
                this_section_name = doc[i-1].lower()
                in_section = this_section_name == name.lower()
                continue
            if in_section:
                section.append(line)
        section = '\n'.join(section)
        self._doc_sections[name.lower()] = section
        return section

    @property
    def description(self):
        doc = self.doc.split('\n')
        description = []
        for (i, line) in enumerate(doc):
            if line.startswith('-----'):
                description = description[:-1]
                break
            description.append(line)
        description = '\n'.join(description)
        return description

    def long_description(self, indent='    '):
        notes = self.get_doc_section('notes')
        long_description = indent + self.description
        if notes.split():
            notes = fill_with_paragraphs(notes, indent=indent)
            long_description += '\n' + notes
        return long_description.rstrip()

    @property
    def parameters(self):
        return ['{0}'.format(x) for x in list(self.sig.parameters.values())[2:]]

    @property
    def signature(self):
        s = '{0}({1})'.format(self.name, ', '.join(self.parameters))
        return s

    def info(self, indent='    '):
        params = ', '.join(x.replace('*', '\*') for x in self.parameters)
        s = ['**{0}**\ *({1})*'.format(self.name, params)]
        s.append(self.long_description(indent=indent))
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
            print(cb.info())
            print('\n')


def main():
    p = ArgumentParser()
    p.add_argument('what', choices=('callbacks',))
    args = p.parse_args()

    if args.what == 'callbacks':
        gen_callback_docs()
