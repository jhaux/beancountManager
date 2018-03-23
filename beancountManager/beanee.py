from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END
from tkinter import OptionMenu, StringVar
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa
from tkinter.filedialog import askopenfilename

from beancountManager import readers


class Beanee(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.openFiles = 0
        self.fileFrames = []

        self.initUI()

    def initUI(self):

        self.parent.title("Beanee - Convert your banking files")
        self.pack(fill=BOTH, expand=1)

        self.headerFrame = Frame(self, bg='orange')
        self.headerFrame.pack(fill=X, padx=10, pady=10)
        self.bodyFrame = Frame(self)
        self.bodyFrame.pack(fill=X, expand=1)
        self.bottomFrame = Frame(self, bg='red')
        self.bottomFrame.pack(side=BOTTOM, fill=X, padx=10, pady=10)

        self.label = Label(self.headerFrame, text='Hello')
        self.label.pack()

        self.addFileButton = Button(self.bodyFrame,
                                    text='Add File',
                                    command=self.addFile)
        self.addFileButton.grid(row=0, sticky=N+E+S+W)

        self.toggleIntroText()

    def toggleIntroText(self):
        if self.openFiles == 0:
            self.introText = Label(self, text='')
            self.introText.pack(fill=BOTH, expand=1)
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

    def addFile(self):

        filename = askopenfilename()
        if filename:
            self.openFiles += 1
            ff = FileFrame(self.bodyFrame, filename, self.openFiles,
                           receive=self.sendDestroy)
            ff.grid(row=self.openFiles - 1)
            self.fileFrames.append(ff)

            self.addFileButton.grid(row=self.openFiles)

        self.toggleIntroText()

    def sortFileDialogue(self):
        for i, frame in enumerate(self.fileFrames):
            idx = frame.index
            if idx != i+1:
                frame.index = i + 1
                frame.grid(row=i)
        self.openFiles = len(self.fileFrames)

        self.addFileButton.grid(row=self.openFiles)

    def sendDestroy(self, element):
        self.fileFrames.remove(element)
        self.sortFileDialogue()


class FileFrame(Frame):

    def __init__(self, parent, fname, index, receive):
        Frame.__init__(self, parent)
        self.parent = parent

        self.fname = fname
        self.index = index
        self.receive = receive

        self.initUI()

    def initUI(self):
        self.FilePathEntry = Entry(self)

        self.FilePathEntry.delete(0, END)
        self.FilePathEntry.insert(0, self.fname)
        self.FilePathEntry.pack(side=LEFT, padx=5)

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

            self.ledger = converter(self.fname)

    def getHelp(self, entry):
        return entry

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
