from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END
from tkinter import Menu, OptionMenu, StringVar, Menubutton
from tkinter import SUNKEN
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa

from tkinter.simpledialog import Dialog

from beancountManager.ledger import Transaction


class GetHelp(Dialog):

    def __init__(self, parent,
                 entry, receiveFn,
                 title='Get some Help!'):
        print('GET HELP')

        self.entry = entry
        self.receiveFn = receiveFn

        Dialog.__init__(self, parent, title)

        print('Called for Help')

    def body(self, parent):
        self.diagFrame = Frame(self)
        self.diagFrame.pack(side=TOP, fill=BOTH)

        self.promt = Label(self.diagFrame,
                           text='Could not match this entry to any rule. '
                                'Please make changes manually or add a new '
                                'rule.')
        self.promt.grid(row=0, sticky=W, columnspan=2)
                                        
        self.entryLabel = Label(self.diagFrame,
                                text=str(self.entry),
                                justify=LEFT,
                                relief=SUNKEN,
                                wraplength=400)
        self.entryLabel.grid(row=1, columnspan=2)

        changables = [c for c in dir(self.entry) if not '__' in c]
        changables = [c for c in changables if not callable(c)]

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
            content = Menubutton(self.diagFrame,
                                 textvariable=textContainer,
                                 indicatoron=True)

            main = Menu(content)
            subA = Menu(self.diagFrame, tearoff=0)
            subA.add_radiobutton(
                    label='VB',
                    variable=textContainer,
                    value='Assets:VB')
            subA.add_radiobutton(
                    label='VC',
                    variable=textContainer,
                    value='Assets:VC')
            main.add_cascade(label='Assets', menu=subA)

            subI = Menu(self.diagFrame, tearoff=0)
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
