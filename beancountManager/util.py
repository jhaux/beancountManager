from tkinter import Tk, Frame
from tkinter import Menu, Menubutton, StringVar, Label
from tkinter import W, E, S, N, X, Y
from tkinter import simpledialog


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


class CustomMenubutton(Menubutton):
    def __init__(self, parent, menuDict, **kwargs):
        self.menuDict = menuDict
        self.tv = kwargs['textvariable']
        Menubutton.__init__(self, parent, **kwargs)

        self.refresh()

    def refresh(self):
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
                self.addEntry(ret, fallbackString)
                ret = ':'.join([fallbackString, ret])
            else:
                ret = fallbackString
            self.tv.set(ret)
        return askForString

    def addEntry(self, entry, fallbackString):
        keys = fallbackString.split(':')
        d = self.menuDict
        for key in keys:
            d = d[key]
        d[entry] = {}

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
