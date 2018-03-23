from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END
from tkinter import Menu, OptionMenu, StringVar, Menubutton
from tkinter import SUNKEN
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa

from tkinter.simpledialog import Dialog

from beancountManager.ledger import Transaction
from beancountManager.referencer import StringComparison, StringModification


class RuleDialog(Dialog):

    def __init__(self,
                 parent,
                 entry=None,
                 rule=None,
                 title='Edit Rule'):
        self.entry = entry
        self.rule = rule

        self.mode = 'edit' if rule is not None else 'add'

        Dialog.__init__(self, parent, title)

    def body(self, parent):
        self.diagFrame = Frame(self)
        self.diagFrame.pack(side=TOP, fill=BOTH)

        row_id = 0
        self.promt = Label(self.diagFrame,
                           text='Please specify the rule.')
        self.promt.grid(row=row_id, sticky=W, columnspan=2)
        row_id += 1

        if self.entry:
            self.entryLabel = Label(self.diagFrame,
                                    text=str(self.entry),
                                    justify=LEFT,
                                    relief=SUNKEN,
                                    wraplength=400)
            self.entryLabel.grid(row=row_id, columnspan=2)
            row_id += 1

        self.changes = {}

        if self.entry and isinstance(self.entry, Transaction):
            kind = 'transaction'
        if rule:
            kind = rule['kind']

        if kind == 'transaction':
            Label(self.diagFrame,
                  text='Transaction Attributes').grid(row=row_id,
                                                      columnspan=4)
            row_id += 1
            name = 'narration'
            self.changes[name] = self.make_changable(name, row_id)
            row_id += 1

            name = 'meta'
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

        return self.promt

    def make_changable(self, name, row_id, kind='text'):
        label = Label(self.diagFrame, text=name.title)
        label.grid(row=row_id, column=0, sticky=E)
        
        relation = StringVar()
        pattern = StringVar()
        change = StringVar()
        changeTo = StringVar()

        relMenu = OptionMenu(self.diagFrame,
                             textvariable=relation,
                             StringComparison.options)
        relMenu.grid(row=row_id, column=1, sticky=W)

        patEntry = Entry(self.diagFrame, textvariable=change)
        patEntry.grid(row=row_id, column=2, sticky=W)

        chMenu = OptionMenu(self.diagFrame,
                            textvariable=change,
                            StringModification.options)
        chMenu.grid(row=row_id, column=3, sticky=W)

        chVal = Entry(self.diagFrame, textvariable=changeTo)
        chVal.grid(rwo=row_id, column=4, sticky=W)

        ### The following is not good

        if False and self.rule:
            pat_orig = self.rule['pattern'][name]
            ch_orig = self.rule['change'][name]

            pattern.set(value)
            change.set(value)

        if kind == 'text':
            content = Entry(self.diagFrame, textvariable=textContainer)
        elif kind == 'menu':
            content = Menubutton(self.diagFrame,
                                 textvariable=textContainer,
                                 indicatoron=True)

            main = Menu(content, tearoff=False)
            subA = Menu(main, tearoff=0)
            subA.add_radiobutton(
                    label='VB',
                    variable=textContainer,
                    value='Assets:VB')
            subA.add_radiobutton(
                    label='VC',
                    variable=textContainer,
                    value='Assets:VC')
            main.add_cascade(label='Assets', menu=subA)

            subI = Menu(main, tearoff=0)
            subI.add_radiobutton(
                    label='SingenEV',
                    variable=textContainer,
                    value='Income:SingenEV')
            subI.add_radiobutton(
                    label='Uni',
                    variable=textContainer,
                    value='Income:Uni')
            main.add_cascade(label='Income', menu=subI)

            content.configure(menu=main)

        content.grid(row=row_id, column=1, sticky=W)

        return textContainer

    def apply(self):
        for attr, value in self.changes.items():
            if value == '' or value == 'None':
                value = None
            elif attr == 'postings':
                for i, p in enumerate(self.changes['postings']):
                    for p_attr, p_value in p.items():
                        if p_value == '' or p_value == 'None':
                            p_value = None
                        setattr(self.entry.postings[i], p_attr, p_value)
            setattr(self.entry, attr, value)

        self.result = self.entry
        self.receiveFn(self.entry)
