from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END
from tkinter import OptionMenu, StringVar, Grid
from tkinter.ttk import Separator
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

        self.label = Label(self.bottomFrame,
                           text='Beancount Import Manager - Version {}'
                                .format(beancountManager.__version__))
        self.label.pack()

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
        backup_file_by_sessio_start(self.ledgerPath, self.session_start)

        with open(self.ledgerPath, 'w+') as ledgerFile:
            printer.print_entries(self.ledger, file=ledgerFile)

    def addFile(self):

        filename = askopenfilename()
        if filename:
            self.openFiles += 1
            ff = FileFrame(self.bodyFrame,
                           filename,
                           self.openFiles,
                           receive=self.sendDestroy,
                           ledger=self.ledger)
            ff.grid(row=self.openFiles - 1, sticky=W+E)
            self.fileFrames.append(ff)

            self.sep.grid(row=self.openFiles)
            self.addFileButton.grid(row=self.openFiles + 1)

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


class FileFrame(Frame):

    def __init__(self, parent, fname, index, receive, ledger, sess_id='noid'):
        Frame.__init__(self, parent)
        self.parent = parent
        self.sess_id = sess_id

        self.ledger = ledger

        self.fname = fname
        self.index = index
        self.receive = receive

        self.initUI()

    def initUI(self):
        self.FilePathEntry = Entry(self)
        self.FilePathEntry.delete(0, END)
        self.FilePathEntry.insert(0, self.fname)
        self.FilePathEntry.pack(side=LEFT, padx=5, fill=X, expand=1)

        self.csvType = StringVar()
        options = readers.options
        self.typeSelection = OptionMenu(self, self.csvType, *options)
        self.typeSelection.pack(side=LEFT, padx=5)

        self.scanButton = Button(self, text='Import', command=self.importFile)
        self.scanButton.pack(side=LEFT)

        self.removeButton = Button(self, text='Remove', command=self.remove)
        self.removeButton.pack(side=LEFT, padx=5)

    def importFile(self):
        name = self.csvType.get()
        if name != '':
            converter = getattr(readers, name)(name+'.rules', self.getHelp)

            self.ledger += converter(self.fname)

            backup_file_by_sessio_start(self.fname, self.sess_id)
            printer.print_entries(self.ledger)

    def getHelp(self, entry):
        helpDialog = GetHelp(self, entry, self.ledger)
        entry = helpDialog.result
        rule = helpDialog.rule

        return entry, rule

    def remove(self):
        self.receive(self)
        self.destroy()


def main():
    root = Tk()
    mainWindow = Beanee(root)
    root.geometry("800x500+300+300")
    root.mainloop()


if __name__ == '__main__':
    main()
