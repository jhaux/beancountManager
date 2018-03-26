from tkinter import Frame, Tk, BOTH, Label, Button, Entry, END, Checkbutton
from tkinter import Menu, OptionMenu, StringVar, Menubutton, IntVar
from tkinter import SUNKEN
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa
from tkinter.simpledialog import Dialog
from collections import OrderedDict

from beancountManager.ledger import Transaction
from beancountManager.referencer import StringComparison, StringModification
from beancountManager.referencer import Rule


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
        self.promt.grid(row=row_id, sticky=W+E, columnspan=5)
        row_id += 1

        if self.entry:
            self.entryLabel = Label(self.diagFrame,
                                    text=str(self.entry),
                                    justify=LEFT,
                                    relief=SUNKEN,
                                    wraplength=400)
            self.entryLabel.grid(row=row_id, columnspan=5)
            row_id += 1

        self.changes = {}

        if self.entry and isinstance(self.entry, Transaction):
            kind = 'transaction'
        elif rule:
            kind = rule['kind']

        if kind == 'transaction':
            Label(self.diagFrame,
                  text='Transaction Attributes').grid(row=row_id,
                                                      columnspan=5,
                                                      sticky=E+W)
            row_id += 1

            for col, n in enumerate(['Field',
                                     'Relation',
                                     'Pattern',
                                     'Ch. Method',
                                     'New Value']):
                Label(self.diagFrame, text=n).grid(row=row_id,
                                                   column=col,
                                                   sticky=E+W)
            row_id += 1
            
            self.newRule = getProtoRule()

            self.recursiveMakeChangable(self.newRule,
                                        row_id,
                                        self.entry,
                                        self.rule)

        return self.promt

    def recursiveMakeChangable(self, ruleDict, startRow,
                               entry=None, rule=None):
        kind = ruleDict['kind']
        patterns = ruleDict['pattern']
        changes = ruleDict['changes']

        row_id = startRow
        for k in patterns.keys():
            vp = patterns[k]
            vc = changes[k]
            if not vp:
                preVals = {}
                if entry:
                    pat =  getattr(entry, k)
                    preVals['pattern'] = pat if pat else ''
                if rule:
                    preVals['pattern'] = list(rule['pattern'][k].values())[0]
                    preVals['relation'] = list(rule['pattern'][k].keys())[0]
                    preVals['change'] = list(rule['changes'][k].values())[0]
                    preVals['changeTo'] = list(rule['changes'][k].keys())[0]

                # add pattern change pair
                rel, pat, ch, cht = \
                    self.make_changable(k, row_id, preVals=preVals)
                patterns[k] = [rel, pat]
                changes[k] = [ch, cht]
                row_id += 1
            else:
                label = Label(self.diagFrame, text=k.title())
                label.grid(row=row_id, column=0, sticky=E+W)
                row_id += 1

                subDict = {'kind': kind,
                           'pattern': vp,
                           'changes': vc}
                if not k.isdigit():
                    subEntry = None if not entry else getattr(entry, k)
                else:
                    subEntry = None if not entry else entry[int(k)-1]
                subRule = None if not rule else \
                        {'pattern': rule['pattern'][k],
                         'changes': rule['changes'][k]}

                subdDict, row_id = self.recursiveMakeChangable(subDict,
                                                               row_id,
                                                               subEntry,
                                                               subRule)
        return ruleDict, row_id
            

    def make_changable(self, name, row_id,
                       kind='text', preVals=None):
        
        relation = StringVar()
        pattern = StringVar()
        change = StringVar()
        changeTo = StringVar()

        relMenu = OptionMenu(self.diagFrame,
                             relation,
                             *StringComparison.options)
        relMenu.grid(row=row_id, column=1, sticky=W)

        patEntry = Entry(self.diagFrame, textvariable=pattern)
        patEntry.grid(row=row_id, column=2, sticky=W)

        chMenu = OptionMenu(self.diagFrame,
                            change,
                            *StringModification.options)
        chMenu.grid(row=row_id, column=3, sticky=W)

        chVal = Entry(self.diagFrame, textvariable=changeTo)
        chVal.grid(row=row_id, column=4, sticky=W)

        settableItems = [relMenu, patEntry, chMenu, chVal]
        checkVar = IntVar()
        label = Checkbutton(self.diagFrame,
                            text=name.title(),
                            variable=checkVar,
                            onvalue=1,
                            offvalue=0,
                            command=self.getCheckcommand(checkVar,
                                                         settableItems))
        label.select()
        label.grid(row=row_id, column=0, sticky=E)


        if preVals:
            if 'relation' in preVals:
                relation.set(preVals['relation'])
            if 'pattern' in preVals:
                pattern.set(preVals['pattern'])
            if 'change' in preVals:
                change.set(preVals['change'])
            if 'changeTo' in preVals:
                changeTo.set(preVals['changeTo'])

        return relation, pattern, change, changeTo

    def getCheckcommand(self, checkVar, settableItems):
        def onOffFn():
            isOn = checkVar.get() == 1
            for item in settableItems:
                item['state'] = 'normal' if isOn else 'disabled'
        return onOffFn

    def recursiveGetNewRule(self, ruleDict):
        for k, v in ruleDict.items():
            if isinstance(v, dict):
                v = self.recursiveGetNewRule(v)
            elif isinstance(v, list):
                v = {v[0].get(): v[1].get()}
            ruleDict[k] = v
        return ruleDict

    def getNewRule(self):
        self.newRule = newRule = self.recursiveGetNewRule(self.newRule)
        return newRule

    def apply(self):
        newRuleDict = self.getNewRule()
        newRule = Rule(newRuleDict)
        if self.entry:
            if newRule.test(self.entry):
                newRule.apply(self.entry)


def getProtoRule():
    return OrderedDict({
            "kind": None,
            "pattern":
            OrderedDict({
                    "date": None,
                    "narration": None,
                    "postings":
                    OrderedDict({
                            "1":
                            {
                            "flag": None,
                            "account": None,
                            "amount": None,
                            "currency": None
                            },
                            "2":
                            {
                            "flag": None,
                            "account": None,
                            "amount": None,
                            "currency": None
                            }
                    })
            }),
            "changes":
            OrderedDict({
                    "date": None,
                    "narration": None,
                    "postings": 
                    OrderedDict({
                            "1":
                            {
                            "flag": None,
                            "account": None,
                            "amount": None,
                            "currency": None
                            },
                            "2":
                            {
                            "flag": None,
                            "account": None,
                            "amount": None,
                            "currency": None
                            }
                    })
            })
    })
