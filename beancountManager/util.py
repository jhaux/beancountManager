from tkinter import Tk, Frame
from tkinter import Menu, Menubutton, StringVar, Label
from tkinter import W, E, S, N, X, Y
from tkinter import simpledialog

import os
from shutil import copyfile

from beancount.core.realization import realize
from beancount.core.data import Open


class LeTestApp(Frame):
    def __init__(self, parent, leDict):
        Frame.__init__(self, parent)

        self.parent = parent
        self.menuDict = leDict

        self.tv = StringVar()
        self.tv.set('Not yet set')

        Label(text='Test').pack()

        self.mb = CustomMenubutton(self.parent,
                                   self.menuDict,
                                   textvariable=self.tv,
                                   indicatoron=True)
        self.mb.pack()

        self.mb.refresh()


def backup_file_by_sessio_start(filepath, session_start):
    '''Backs up a file once per Session, if there are changes made to it.

    Arguments:
        filepath: path to the file to be stored.
        session_start: unique identifier for the current session.
    '''

    backup_name = filepath + '.bak.{}'.format(session_start)
    if not os.path.isfile(backup_name):
        copyfile(filepath, backup_name)


class CustomMenubutton(Menubutton):
    def __init__(self, parent, ledger, entry, **kwargs):
        self.entry = entry  # Current entry for which this menu is created
        self.ledger = ledger
        self.tv = kwargs['textvariable']
        Menubutton.__init__(self, parent, **kwargs)

        self.refresh()

    def refresh(self):
        self.menuDict = realize(self.ledger)
        self.mainMenu = Menu(self, tearoff=False)
        self.dictGenerator(self.menuDict,
                           menu=self.mainMenu)
        self.configure(menu=self.mainMenu)

    def dictGenerator(self,
                      indict,
                      joint=':',
                      jointString=None,
                      menu=None):
        if len(indict) != 0:
            for k, v in indict.items():
                subMenu = Menu(menu, tearoff=0)
                js = joint.join([jointString, k]) if jointString else k
                self.dictGenerator(v,
                                   jointString=js,
                                   menu=subMenu)
                menu.add_cascade(label=k, menu=subMenu)
            self.add_add(menu, jointString)
        else:
            menu.add_radiobutton(label='select',
                                 variable=self.tv,
                                 value=jointString)
            self.add_add(menu, jointString)

    def add_add(self, menu, fallbackString):
        menu.add_radiobutton(label='Add',
                             variable=self.tv,
                             command=self.getString(fallbackString))

    def getString(self, fallbackString):
        def askForString():
            ret = simpledialog.askstring('Enter the new Field',
                                         'I said ENTEEER')
            if ret:
                ret = ':'.join([fallbackString, ret]) if fallbackString \
                                                      else ret
                self.addEntry(ret, self.entry)
            else:
                ret = fallbackString
            self.tv.set(ret)
        return askForString

    def addEntry(self, account, entry):

        date = entry.date
        opendir = Open(None, date, account, None, None)

        self.ledger += [opendir]

        self.refresh()


if __name__ == '__main__':
    leDict = {
            'Assets':
            {
                'VB':
                    {
                        'Giro': {},
                        'Flex': {}
                    },
                'Paypal': {}
            },
            'Expenses':
            {
                'Schwachsinn':
                {
                    'Euromillions': {}
                },
                'Essen':
                {
                    'Mensa': {}
                }
            },
            'Income':
            {
                'jomotion': {},
                'SingenEV': {},
                'Uni': {}
            }
        }

    root = Tk()
    mainWindow = LeTestApp(root, leDict)
    root.geometry("800x500+300+300")
    root.mainloop()
