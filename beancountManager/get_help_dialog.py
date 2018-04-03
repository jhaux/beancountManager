import copy

from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END
from tkinter import Menu, OptionMenu, StringVar, Menubutton
from tkinter import SUNKEN
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa

from tkinter.simpledialog import Dialog

from beancount.core.data import Transaction
from beancount.parser import printer
from beancount.core.realization import realize

from beancountManager.rule_dialog import RuleDialog
from beancountManager.util import CustomMenubutton, str2dict, validate_entry


class GetHelp(Dialog):

    def __init__(self,
                 parent,
                 entry,
                 ledger,
                 title='Get some Help!',
                 sess_id='noid'):
        self.entry = entry
        self.ledger = ledger

        self.sess_id = sess_id

        self.rule = None

        Dialog.__init__(self, parent, title)

    def body(self, parent):
        self.diagFrame = Frame(self)
        self.diagFrame.pack(side=TOP, fill=BOTH)

        self.promt = Label(self.diagFrame,
                           text='Could not match this entry to any rule. '
                                'Please make changes manually or add a new '
                                'rule.')
        self.promt.grid(row=0, sticky=W, columnspan=2)

        self.entryLabel = Label(self.diagFrame,
                                text=printer.format_entry(self.entry),
                                justify=LEFT,
                                relief=SUNKEN,
                                wraplength=400)
        self.entryLabel.grid(row=1, columnspan=2)

        self.changes = {}

        row_id = 2
        if isinstance(self.entry, Transaction):
            Label(self.diagFrame,
                  text='Transaction Attributes').grid(row=row_id,
                                                      columnspan=2)
            row_id += 1
            name = 'narration'
            self.changes[name] = \
                self.make_changable(name.title(),
                                    getattr(self.entry, name),
                                    row_id)
            row_id += 1

            name = 'meta'
            self.changes[name] = \
                self.make_changable(name.title(),
                                    getattr(self.entry, name),
                                    row_id)
            row_id += 1

            name = 'tags'
            self.changes[name] = \
                self.make_changable(name.title(),
                                    getattr(self.entry, name),
                                    row_id)
            row_id += 1

            name = 'links'
            self.changes[name] = \
                self.make_changable(name.title(),
                                    getattr(self.entry, name),
                                    row_id)
            row_id += 1

            Label(self.diagFrame, text='Postings').grid(row=row_id,
                                                        columnspan=2)
            row_id += 1

            self.changes['postings'] = []
            for idx, p in enumerate(self.entry.postings):
                p_changes = {}
                name = 'flag'
                p_changes[name] = \
                    self.make_changable(name.title(),
                                        getattr(p, name),
                                        row_id)
                row_id += 1

                name = 'account'
                p_changes[name] = \
                    self.make_changable(name.title(),
                                        getattr(p, name),
                                        row_id,
                                        'menu')
                row_id += 1

                self.changes['postings'].append(p_changes)

        addRule = Button(self.diagFrame,
                         text='Add Rule',
                         command=self.addRule)
        addRule.grid(row=row_id, column=0, sticky=N+E+S+W, columnspan=2)

        return self.promt

    def refresh(self):
        if self.changes:
            for name, var in self.changes.items():
                value = getattr(self.entry, name)
                if not name == 'postings':
                    if value is not None:
                        var.set(value)
                    else:
                        var.set('')
                else:
                    for idx, p in enumerate(var):
                        for p_name, p_var in p.items():
                            p_value = getattr(value[idx], p_name)
                            if p_value is not None:
                                p_var.set(p_value)
                            else:
                                p_var.set('')

    def addRule(self):
        rd = RuleDialog(self.diagFrame,
                        self.entry,
                        self.ledger,
                        sess_id=self.sess_id)
        self.entry = rd.entry
        self.rule = rd.rule
        self.refresh()

    def make_changable(self, name, value, row_id, kind='text'):
        label = Label(self.diagFrame, text=name)
        label.grid(row=row_id, column=0, sticky=E)

        textContainer = StringVar()
        if value is None:
            value = ''
        textContainer.set(value)

        if kind == 'text':
            content = Entry(self.diagFrame, textvariable=textContainer)
        elif kind == 'menu':
            content = CustomMenubutton(self.diagFrame,
                                       self.ledger,
                                       self.entry,
                                       textvariable=textContainer,
                                       indicatoron=True)

        content.grid(row=row_id, column=1, sticky=W)
        row_id += 1

        return textContainer

    def validate(self):
        backup_entry = copy.deepcopy(self.entry)
        self.apply()

        is_valid = validate_entry(self.entry)

        self.entry = backup_entry

        return is_valid

    def apply(self):
        for attr, value in self.changes.items():
            if attr == 'tags' or attr == 'links':
                value = value.get()
                if ', ' in value:
                    values = value.split(', ')
                elif ',' in value:
                    values = value.split(',')
                elif ' ' in value:
                    values = value.split(' ')
                elif value == '':
                    values = None
                else:
                    values = [value]
                self.entry = self.entry._replace(**{attr: values})
            elif attr == 'meta' and value != '':
                value = str2dict(value.get())
                self.entry = self.entry._replace(**{attr: value})
            elif attr == 'postings':
                for i, p in enumerate(self.changes['postings']):
                    for p_attr, p_value in p.items():
                        p_value = p_value.get()
                        if p_value == '' or p_value == 'None':
                            p_value = None
                        self.entry.postings[i]\
                            = self.entry.postings[i]\
                            ._replace(**{p_attr: p_value})
            else:
                value = value.get()
                if value == '' or value == 'None':
                    value = None
                self.entry = self.entry._replace(**{attr: value})
