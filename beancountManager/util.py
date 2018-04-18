from tkinter import Tk, Frame
from tkinter import Menu, Menubutton, StringVar, Label
from tkinter import W, E, S, N, X, Y
from tkinter import simpledialog

import os
from shutil import copyfile

from beancount.core.realization import realize
from beancount.core.data import Open, Transaction, sanity_check_types

from beancountManager import data


VALID_CHARS = 'abcdefghijklmnopqrstuvwxyz:ABCDEFGHIJKLMNOPQRSTUVWXYZ'
VALID_CHARS += '1234567890'


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


def identifyImportType(filename):
    if 'Umsaetze_DE0227092555' in filename:
        return data.filetypes.VOLKSBANK
    elif 'Umsaetze_Paypal' in filename:
        return data.filetypes.PAYPAL
    elif '-umsatz.CSV' in filename:
        return data.filetypes.SPARKASSE
    else:
        return None


def getDefaultUser(filename):
    for identifier, user in data.USERS.items():
        if identifier in filename:
            return user
    return None


def german2usNumber(string_num):
    return string_num.replace('.', '').replace(',', '.')


def is_valid_account(account):
    is_valid = True

    if account == '':
        return is_valid

    # Test for not allowed chracters
    for c in account:
        if c not in VALID_CHARS:
            print('Unallowed character \'{}\' in account {}'
                  .format(c, account))
            is_valid = False

    # Test that all branches are starting with a capital letter
    for name in account.split(':'):
        if not name[0].isupper():
            print('Must start uppercase: {}'.format(name))
            is_valid = False

    return is_valid


def validate_entry(entry):
    is_valid = True

    # Use builtin data type checks
    try:
        sanity_check_types(entry, allow_none_for_tags_and_links=True)
    except AssertionError as e:
        if str(e) == 'Missing filename in metadata':
            pass
        elif str(e) == 'Missing lineno in metadata':
            pass
        else:
            print(e)
            is_valid = False

    if isinstance(entry, Transaction):
        # Test account names for correctness
        for p in entry.postings:
            is_valid = is_valid and is_valid_account(p.account)

    return is_valid


def backup_file_by_sessio_start(filepath, session_start):
    '''Backs up a file once per Session, if there are changes made to it.

    Arguments:
        filepath: path to the file to be stored.
        session_start: unique identifier for the current session.
    '''

    names = filepath.split('/')
    name = '.' + names[-1]
    names[-1] = name
    newpath = '/'.join(names)

    backup_name = '{}.bak.{}'.format(newpath, session_start)
    if not os.path.isfile(backup_name) and os.path.isfile(filepath):
        copyfile(filepath, backup_name)


def str2dict(string):

    string = string.strip('{')
    string = string.strip('}')

    entries = string.split(', ')

    d = {}
    for e in entries:
        k, v = e.split(': ')
        d[k.strip('\'')] = v.strip('\'')

    return d


def print_dict(le_dict, sort_keys=True, indent=4):
    def do_stuff(item, indentation=''):
        if isinstance(item, dict):
            rec_d(item, indentation)
        elif isinstance(item, list):
            rec_l(item, indentation)
        else:
            print(indentation + str(item))

    def rec_l(sub_list, indentation=''):
        new_indent = indentation + ' '*indent
        for i in sub_list:
            do_stuff(i, new_indent)

    def rec_d(subDict, indentation=''):
        new_indent = indentation + ' '*indent

        keys = list(subDict.keys())
        if sort_keys:
            keys = sorted(keys)
        for k in keys:
            v = subDict[k]
            print(indentation + str(k) + ':')
            do_stuff(v, new_indent)

    do_stuff(le_dict)


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
            key_val_pairs = sorted(list(indict.items()), key=lambda kv: kv[0])
            for k, v in key_val_pairs:
                subMenu = Menu(menu, tearoff=0)
                js = joint.join([jointString, k]) if jointString else k
                self.dictGenerator(v,
                                   jointString=js,
                                   menu=subMenu)
                menu.add_cascade(label=k, menu=subMenu)
            menu.add_radiobutton(label='select',
                                 variable=self.tv,
                                 value=jointString)
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
            # If ret is None, cancle has been pressed
            while ret and not is_valid_account(ret):
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

        date = data.EXP_OPEN_DATE
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
