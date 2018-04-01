from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END, Text
from tkinter import Menu, OptionMenu, StringVar, Menubutton
from tkinter import SUNKEN
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa

from tkinter.simpledialog import Dialog

from beancountManager.referencer import StringModification


example_code = \
    '''def modify_string(string):
    \'\'\'str => str | do not change function name or signature\'\'\'

    modified_string = string

    return modified_string'''


class CodeDialog(Dialog):

    def __init__(self, parent, string):
        '''Provides the ability to amipulate a string by inputting code.

        Arguments:
            string: the string to be manipulated.
        '''

        self.string = string
        self.code = None

        Dialog.__init__(self, parent, 'Enter Code')

    def body(self, parent):

        diagFrame = Frame(self)
        diagFrame.pack(side=TOP, fill=BOTH)

        diagFrame.rowconfigure(1, weight=1)

        promt = Label(diagFrame,
                      text='Enter code to manipulate this string.',
                      relief=SUNKEN)
        promt.grid(row=0, sticky=W, padx=5, pady=5)

        codeFrame = Frame(diagFrame)
        codeFrame.grid(row=1, sticky=W+E)

        self.functionDefinition = Text(codeFrame, bg='white')
        self.functionDefinition.insert('1.0', example_code)
        self.functionDefinition.grid(row=0, sticky=W+E)

        testFrame = Frame(diagFrame)
        testFrame.grid(row=3, sticky=W+E)

        Label(testFrame, text='Input').grid(row=0, column=0)
        Label(testFrame, text='Output').grid(row=0, column=2)

        self.inVar = StringVar()
        self.inVar.set(self.string)
        instr = Label(testFrame, textvariable=self.inVar)
        instr.grid(row=1, column=0)

        testConversion = Button(testFrame, text='Test Code',
                                command=self.convert)
        testConversion.grid(row=1, column=1, sticky=W+E)

        self.outVar = StringVar()
        self.outVar.set('')
        outstr = Label(testFrame, textvariable=self.outVar)
        outstr.grid(row=1, column=2)

    def convert(self):
        code = self.functionDefinition.get('1.0', 'end')
        new_string = StringModification.code(self.string, code)

        self.outVar.set(new_string)

    def apply(self):
        self.convert()

        if self.outVar.get != 'ERROR':
            self.code = self.functionDefinition.get('1.0', 'end')

        return self.code


if __name__ == '__main__':

    root = Tk()
    D = CodeDialog(root, 'Sonja ist die beste.\nsie wirklich gut')
