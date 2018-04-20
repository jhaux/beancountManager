from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END, TclError
from tkinter import OptionMenu, StringVar, Grid
from tkinter.ttk import Separator, Progressbar
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa
from tkinter.filedialog import askopenfilename

from beancount import loader
from beancount.parser import printer
import time
import datetime

import beancountManager
from beancountManager import readers
from beancountManager.get_help_dialog import GetHelp
from beancountManager.util import backup_file_by_sessio_start
from beancountManager.util import identifyImportType
from beancountManager.io import store_sorted_ledger


class Beanee(Frame):

    def __init__(self, parent):
        t = time.time()
        t = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H:%M:%S')
        self.session_start = t

        Frame.__init__(self, parent)

        self.parent = parent
        self.ledger = []

        self.openFiles = 0
        self.fileFrames = []

        self.initUI()

    def initUI(self):

        self.parent.title("Beanee - Convert your banking files")
        self.pack(fill=BOTH, expand=1)

        self.headerFrame = Frame(self)
        self.headerFrame.pack(fill=X, padx=10, pady=10)
        Separator(self, orient='horizontal').pack(fill=X)
        self.bodyFrame = Frame(self)
        self.bodyFrame.pack(fill=BOTH, expand=1)
        Separator(self, orient='horizontal').pack(fill=X)
        self.bottomFrame = Frame(self)
        self.bottomFrame.pack(side=BOTTOM, fill=X, padx=10, pady=10)

        Grid.columnconfigure(self.bodyFrame, 0, weight=1)
        Grid.columnconfigure(self.bottomFrame, 0, weight=1)
        Grid.rowconfigure(self.bottomFrame, 0, weight=1)

        self.sep = Separator(self.bodyFrame, orient='horizontal')
        self.sep.grid(row=0, sticky=W+E)

        self.addFileButton = Button(self.bodyFrame,
                                    text='Add File',
                                    command=self.addFile)
        self.addFileButton.grid(row=1, sticky=E+W)

        self.addLedgerDialog(self.headerFrame)

        self.storeLedgerButton = Button(self.bottomFrame,
                                        text='Store Ledger',
                                        command=self.storeLedger)
        self.storeLedgerButton.grid(column=0, row=0, sticky=E+W)

        Separator(self.bottomFrame, orient='horizontal').grid(row=1,
                                                              sticky=E+W)
        Label(self.bottomFrame,
              text='Beancount Import Manager - Version {}'
                   .format(beancountManager.__version__)).grid(row=2)

        self.toggleIntroText()

    def toggleIntroText(self):
        if self.openFiles == 0:
            if hasattr(self, 'introText'):
                self.introText.destroy()
            Grid.rowconfigure(self.bodyFrame, 2, weight=1)
            self.introText = Label(self.bodyFrame, text='')
            self.introText.grid(sticky=W+E+S+N)
            self.introText['text'] = 'Add banking files via the ' \
                                     '\'Add File\' Button\nand import ' \
                                     'them via the upcoming Dialoge.\n' \
                                     'Importing the files is automated ' \
                                     'using rules,\n which can be added ' \
                                     'via the menu (Edit->Rules) or while' \
                                     ' importing.\n Unknown entries not ' \
                                     'matching any rule have to be edited' \
                                     ' by hand.'
        else:
            self.introText.destroy()
            Grid.rowconfigure(self.bodyFrame, 2, weight=0)

    def addLedgerDialog(self,
                        parent,
                        defaultPath='/home/johannes/Documents/Finanzen/'
                        'test_ledger.beancount'):
        self.ledgerVar = StringVar()
        self.ledgerEntry = le = Entry(parent, textvariable=self.ledgerVar)
        le.delete(0, END)
        le.insert(0, defaultPath)
        le.pack(side=LEFT, padx=5, fill=X, expand=1)

        self.changeL = Button(parent,
                              text='Choose Ledger',
                              command=self.changeLedger)
        self.changeL.pack()

        self.ledgerPath = self.ledgerVar.get()
        self.ledger, _, _ = loader.load_file(self.ledgerPath)

        backup_file_by_sessio_start(self.ledgerVar.get(), self.session_start)

        with open(self.ledgerVar.get(), 'w+') as ledgerFile:
            printer.print_entries(self.ledger, file=ledgerFile)

    def changeLedger(self):
        filename = askopenfilename()
        if filename:
            self.ledgerVar.set(filename)
            self.ledger, _, _ = loader.load_file(self.ledgerVar.get())
            printer.print_entries(self.ledger)
            print('')

    def storeLedger(self):
        self.ledgerPath = self.ledgerVar.get()
        backup_file_by_sessio_start(self.ledgerPath, self.session_start)

        store_sorted_ledger(self.ledger, self.ledgerPath)

    def deduplicate(self, ledger):
        return ledger

    def addFile(self):

        filename = askopenfilename()
        if filename:
            self.openFiles += 1
            ff = FileFrame(self.bodyFrame,
                           filename,
                           self.openFiles,
                           receive=self.sendDestroy,
                           update_ledger=self.update_ledger,
                           ledger=self.ledger,
                           saveFn=self.storeLedger,
                           sess_id=self.session_start)
            ff.grid(row=self.openFiles - 1, sticky=W+E)
            self.fileFrames.append(ff)

            self.sep.grid(row=self.openFiles)
            self.addFileButton.grid(row=self.openFiles + 1)

            self.ledger = ff.ledger

        self.toggleIntroText()

    def sortFileDialogue(self):
        for i, frame in enumerate(self.fileFrames):
            idx = frame.index
            if idx != i+1:
                frame.index = i + 1
                frame.grid(row=i, sticky=W+E)
        self.openFiles = len(self.fileFrames)

        self.sep.grid(row=self.openFiles)
        self.addFileButton.grid(row=self.openFiles + 1)

    def sendDestroy(self, element):
        self.fileFrames.remove(element)
        self.sortFileDialogue()
        self.toggleIntroText()

    def update_ledger(self, ledger):
        self.ledger = ledger


class FileFrame(Frame):

    def __init__(self,
                 parent,
                 fname,
                 index,
                 receive,
                 update_ledger,
                 ledger,
                 saveFn,
                 sess_id='noid'):
        Frame.__init__(self, parent)
        self.parent = parent
        self.sess_id = sess_id

        self.ledger = ledger
        self.saveFn = saveFn

        self.fname = fname
        self.index = index
        self.receive = receive
        self.update_ledger = update_ledger

        self.initUI()

    def initUI(self):
        Grid.columnconfigure(self, 0, weight=1)

        self.FilePathEntry = Entry(self)
        self.FilePathEntry.delete(0, END)
        self.FilePathEntry.insert(0, self.fname)
        self.FilePathEntry.grid(row=0, column=0, padx=5, sticky=E+W)

        options = readers.options
        self.csvType = StringVar()

        ftype = identifyImportType(self.fname)
        print(ftype)
        if ftype is not None:
            if ftype in options:
                self.csvType.set(ftype)

        self.typeSelection = OptionMenu(self, self.csvType, *options)
        self.typeSelection.grid(row=0, column=1, padx=5)

        self.scanButton = Button(self, text='Import', command=self.importFile)
        self.scanButton.grid(row=0, column=2, padx=5)

        self.removeButton = Button(self, text='Remove', command=self.remove)
        self.removeButton.grid(row=0, column=3, padx=5)

        self.pbar = Progressbar(self, orient='horizontal', mode='determinate')
        self.pbar.grid(row=1, columnspan=4, sticky=E+W)

    def importFile(self):
        name = self.csvType.get()
        if name != '':
            converter = getattr(readers, name)(self.getHelp,
                                               self.ledger,
                                               self.saveFn,
                                               self.sess_id,
                                               self.pbar,
                                               3 if identifyImportType(self.fname) == 'Paypal' else None)

            self.fname = self.FilePathEntry.get()
            backup_file_by_sessio_start(self.fname, self.sess_id)
            self.ledger = converter(self.fname)
            print('Ledger len at end of import:', len(self.ledger))
            self.update_ledger(self.ledger)

    def getHelp(self, entry, possible_duplicate=None):
        helpDialog = GetHelp(self, entry, self.ledger, possible_duplicate)
        entry = helpDialog.entry
        rule = helpDialog.rule

        return entry, rule

    def remove(self):
        self.receive(self)
        self.destroy()


def main():
    root = Tk()
    mainWindow = Beanee(root)
    root.geometry("800x500+300+300")

    # Stuff done to hide hidden files in the askopen filename dialog
    # Found at
    # https://mail.python.org/pipermail/tkinter-discuss/2015-August/003762.html
    try:
        # call a dummy dialog with an impossible option to initialize the file
        # dialog without really getting a dialog window; this will throw a
        # TclError, so we need a try...except :
        try:
            root.tk.call('tk_getOpenFile', '-foobarbaz')
        except TclError:
            pass
        # now set the magic variables accordingly
        root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
        root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
    except:
        pass

    root.mainloop()


if __name__ == '__main__':
    main()
