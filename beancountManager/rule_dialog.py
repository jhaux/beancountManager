import copy
import json

from tkinter import Frame, BOTH, Label, Entry, Checkbutton
from tkinter import OptionMenu, StringVar, IntVar
from tkinter import SUNKEN
from tkinter import N, E, S, W, LEFT, TOP, BOTTOM, CENTER, X, Y  # noqa
from tkinter.simpledialog import Dialog
from collections import OrderedDict

from beancount.core.data import Transaction
from beancount.parser import printer
from beancountManager.referencer import StringComparison, StringModification
from beancountManager.referencer import Rule, RULES
from beancountManager.util import CustomMenubutton, validate_entry, print_dict
from beancountManager.code_dialog import CodeDialog


class RuleDialog(Dialog):

    def __init__(self,
                 parent,
                 entry=None,
                 ledger=[],
                 rule=None,
                 title='Edit Rule',
                 sess_id='noid'):
        self.entry = entry
        self.rule = rule

        self.ledger = ledger

        self.sess_id = sess_id

        self.kind = None if not entry else type(entry).__name__
        self.kind = self.kind if not rule else rule['kind']

        self.newRule = getProtoRule(self.kind, self.entry)

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
                                    text=printer.format_entry(self.entry),
                                    justify=LEFT,
                                    relief=SUNKEN,
                                    wraplength=400)
            self.entryLabel.grid(row=row_id, columnspan=5)
            row_id += 1

        self.changes = {}

        if self.entry and isinstance(self.entry, Transaction):
            kind = 'Transaction'
        elif self.rule:
            kind = self.rule['kind']

        if kind not in RULES:
            return self.promt

        elif kind == 'Transaction':
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

            self.recursiveMakeChangable(self.newRule,
                                        row_id,
                                        self.entry,
                                        self.rule)

        return self.promt

    def setToEmpty(self):
        preVals = {
                'relation': StringComparison.options[0],
                'pattern': '',
                'change': StringModification.options[0],
                'changeTo': ''
                }
        return preVals

    def recursiveMakeChangable(self, theRuleDict, startRow,
                               entry=None, rule=None):
        kind = theRuleDict['kind']
        ruleDict = theRuleDict['rule']

        row_id = startRow
        for k, r in ruleDict.items():
            if not isinstance(r, (dict, OrderedDict)) and k != 'postings':
                preVals = self.setToEmpty()
                if rule and k in ruleDict:
                    preVals['pattern'] = r[0]
                    preVals['relation'] = r[1]
                    preVals['change'] = r[2]
                    preVals['changeTo'] = r[3]
                elif entry:
                    pat = getattr(entry, k)
                    if k == 'tags' or k == 'links':
                        preVals['pattern'] = ', '.join(pat) if pat else ''
                    else:
                        preVals['pattern'] = pat if pat else ''

                # add pattern change pair
                chv, rel, pat, ch, cht = \
                    self.make_changable(k, row_id, preVals=preVals)
                ruleDict[k] = [chv, rel, pat, ch, cht]
                row_id += 1
            elif k == 'postings':
                label = Label(self.diagFrame, text=k.title())
                label.grid(row=row_id, column=0, sticky=E+W)
                row_id += 1

                for i, p in enumerate(r):
                    subDict = {'kind': kind,
                               'rule': p}
                    subEntry = None if not entry else entry.postings[i]
                    subRule = None if not rule else \
                        {'rule': rule[k],
                         'kind': kind}

                    subdDict, row_id = self.recursiveMakeChangable(subDict,
                                                                   row_id,
                                                                   subEntry,
                                                                   subRule)
            elif k == 'units':
                subDict = {'kind': kind,
                           'rule': r}
                subEntry = None if not entry else entry.units
                subRule = None if not rule else \
                    {'rule': rule[k],
                     'kind': kind}

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

        if self.entry and hasattr(self.entry, name):
            inString = getattr(self.entry, name)
        else:
            inString = ''
        chMenu = OptionMenu(self.diagFrame,
                            change,
                            *StringModification.options,
                            command=self.possibleDialog(changeTo, inString))
        chMenu.grid(row=row_id, column=3, sticky=W)

        if name == 'account':
            chVal = CustomMenubutton(self.diagFrame,
                                     self.ledger,
                                     self.entry,
                                     textvariable=changeTo,
                                     indicatoron=True)
        else:
            chVal = Entry(self.diagFrame, textvariable=changeTo)
        chVal.grid(row=row_id, column=4, sticky=W)

        settableItems = [relMenu, patEntry, chMenu, chVal]
        checkVar = IntVar()
        command = self.getCheckcommand(checkVar, settableItems)
        label = Checkbutton(self.diagFrame,
                            text=name.title(),
                            variable=checkVar,
                            onvalue=True,
                            offvalue=False,
                            command=command)
        label.grid(row=row_id, column=0, sticky=E+W)

        if not preVals:
            label.deselect()
        else:
            if not preVals['pattern']:
                label.deselect()
            else:
                label.select()
        command()

        if preVals:
            if 'relation' in preVals:
                relation.set(preVals['relation'])
            if 'pattern' in preVals:
                pattern.set(preVals['pattern'])
            if 'change' in preVals:
                change.set(preVals['change'])
            if 'changeTo' in preVals:
                changeTo.set(preVals['changeTo'])

        return checkVar, relation, pattern, change, changeTo

    def possibleDialog(self, changeToVariable, inputString):
        def command(value):
            if value == 'code':
                CD = CodeDialog(self, inputString)
                code = CD.code
                if code:
                    changeToVariable.set(code)
        return command

    def getCheckcommand(self, checkVar, settableItems):
        def onOffFn():
            isOn = checkVar.get()
            for item in settableItems:
                item['state'] = 'normal' if isOn else 'disabled'
        return onOffFn

    def recursiveGetNewRule(self, ruleDict, writeDict):
        for k, v in list(ruleDict.items()):
            if isinstance(v, (dict, OrderedDict)) \
                    or k == 'postings':
                if k == 'postings':
                    for i, p in enumerate(v):
                        p = self.recursiveGetNewRule(p, writeDict[k][i])
                        writeDict[k][i] = p
                else:
                        writeDict[k] = self.recursiveGetNewRule(v, writeDict[k])
            elif isinstance(v, list):
                if v[0].get():
                    v = [v[1].get(), v[2].get(), v[3].get(), v[4].get()]
                    writeDict[k] = v
                else:
                    del writeDict[k]
            if isinstance(v, (dict, OrderedDict)) and len(v) == 0:
                del(writeDict[k])
        return writeDict

    def getNewRule(self):
        newRule = self.recursiveGetNewRule(self.newRule,
                                           getProtoRule(self.kind, self.entry))
        return newRule

    def validate(self):
        is_valid = True

        backup_rule = None
        if self.rule:
            print('has rule')
            backup_rule = copy.deepcopy(self.rule)

        if self.entry:
            print('has entry')
            backup_entry = copy.deepcopy(self.entry)
            self.apply()
            is_valid = validate_entry(self.entry)

            self.entry = backup_entry

        if backup_rule:
            self.rule = backup_rule

        print('This rule produces a{}valid entry'
              .format(' ' if is_valid else 'n in'))
        return is_valid

    def apply(self):
        newRuleDict = self.getNewRule()
        print_dict(newRuleDict)

        self.rule = newRuleDict
        newRule = Rule(newRuleDict)
        if self.entry:
            if newRule.test(self.entry):
                self.entry = newRule.apply(self.entry)


def getProtoRule(kind, entry=None):
    kind = kind if kind else 'Transaction'
    rule = OrderedDict()

    if kind == 'Transaction':
        rule['flag'] = None
        rule['payee'] = None
        rule['narration'] = None
        rule['tags'] = None
        rule['links'] = None
        rule['postings'] = []

        if entry and isinstance(entry, Transaction):
            n_postings = len(entry.postings)
        else:
            n_postings = 2

        for i in range(n_postings):
            emptyPosting = OrderedDict()
            emptyPosting['flag'] = None
            emptyPosting['account'] = None
            emptyPosting['units'] = OrderedDict()
            emptyPosting['units']['number'] = None
            emptyPosting['units']['currency'] = None

            rule['postings'].append(emptyPosting)

    return {'kind': kind, 'rule': rule}
