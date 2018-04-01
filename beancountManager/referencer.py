import json
import os

from beancount.core.data import Transaction, Open

from beancountManager.util import backup_file_by_sessio_start


class Referencer(object):
    '''Contains rules, by which the incoming ledger entries are formatted.'''

    def __init__(self, rules_file, userInputFn, ledger, session_start='noid'):
        '''Arguments:
            rules_file: path to the file containing the rules
        '''

        self.ledger = ledger

        self.rules_file = rules_file
        self.userInputFn = userInputFn
        self.rules = []
        self.rule_dicts = []
        self.session_start = session_start

        if os.path.isfile(self.rules_file):
            with open(rules_file, 'r') as the_file:
                self.rule_dicts = json.load(the_file)
                for rule in self.rule_dicts:
                    self.rules.append(Rule(rule))

    def __call__(self, entry):
        if isinstance(entry, Transaction):
            matchedSomeRule = False
            for rule in self.rules:
                if rule.test(entry):
                    entry = rule.apply(entry)
                    matchedSomeRule = True
            if not matchedSomeRule:
                entry, rule = self.userInputFn(entry)
                if rule:
                    self.add_rule(rule)
        ret_list = [entry]

        for p in entry.postings:
            if self.is_not_open(p.account):
                ret_list = [Open(None, entry.date, p.account, None, None)] \
                    + ret_list
        return ret_list

    def add_rule(self, rule):
        if rule not in self.rule_dicts:
            self.rule_dicts.append(rule)
            self.rules.append(Rule(rule))
            self.store_rules()

    def store_rules(self):
        backup_file_by_sessio_start(self.rules_file, self.session_start)

        with open(self.rules_file, 'w+') as the_file:
            the_file.write(json.dumps(self.rule_dicts,
                                      indent=4,
                                      sort_keys=True))

    def is_not_open(self, account):
        isOpen = False
        for e in self.ledger:
            if isinstance(e, Open):
                isOpen = isOpen or e.account == account
        return not isOpen


class Rule(object):

    def __init__(self, rule_dict):
        self.kind = rule_dict['kind']
        self.rd = rule_dict['rule']

    def test(self, entry):
        if type(entry).__name__ != self.kind:
            return False
        elif self.kind == 'Transaction':
            result = True
            for k, v in self.rd.items():
                if k != 'postings' and k != 'units':
                    method, test, _, _ = v
                    success = self.atomic_test(getattr(entry, k),
                                               method,
                                               test)
                    result = result and success
                else:
                    postings = entry.postings
                    for idx, p in enumerate(v):
                        for pk, pv in p.items():
                            if pk == 'units':
                                for uk, uv in pv.items():
                                    method, test, _, _ = uv
                                    s = getattr(postings[idx].units, uk)
                                    success = self.atomic_test(
                                            s,
                                            method,
                                            test)
                                    result = result and success
                            else:
                                method, test, _, _ = pv
                                s = getattr(postings[idx], pk)
                                success = self.atomic_test(
                                        s,
                                        method,
                                        test)
                                result = result and success
            return result
        else:
            return False

    def atomic_test(self, string, method, test):
        string = str(string)
        test_method = getattr(StringComparison, method)
        success = test_method(string, test)
        # print('Compare: {} {} {}? => {}'.format(string,
        #                                         method,
        #                                         test,
        #                                         success))

        return success

    def apply(self, entry):
        assert type(entry).__name__ == self.kind, 'Cannot apply rule'
        if self.kind == 'Transaction':
            for k, v in self.rd.items():
                if k != 'postings' and k != 'units':
                    _, _, method, change = v
                    new_str = self.atomic_modofocation(
                            getattr(entry, k),
                            method,
                            change)
                    entry = entry._replace(**{k: new_str})
                else:
                    postings = entry.postings
                    for idx, p in enumerate(v):
                        for pk, pv in v[idx].items():
                            if pk == 'units':
                                units = postings[idx].units
                                for uk, uv in pv.items():
                                    _, _, method, change = uv
                                    s = getattr(units, uk)
                                    new_str = self.atomic_modofocation(
                                            s,
                                            method,
                                            change)
                                    units = units._replace(**{uk: new_str})
                            else:
                                _, _, method, change = pv
                                new_str = self.atomic_modofocation(
                                        getattr(postings[idx], pk),
                                        method,
                                        change)
                                postings[idx] = postings[idx]._replace(
                                        **{pk: new_str}
                                        )
        return entry

    def atomic_modofocation(self, orig, method, change):
        change_method = getattr(StringModification, method)
        new_str = change_method(orig, change)
        # print('Change: {} {} {} => {}'.format(orig,
        #                                       method,
        #                                       change,
        #                                       new_str))
        return new_str


class StringComparison(object):
    options = ['contains', 'equal', 'any']

    @classmethod
    def any(cls, s, test):
        return True

    @classmethod
    def contains(cls, s, test):
        '''Arguments:
            s: string to be tested
            test: string to be conatined in s
        '''

        return test in s

    @classmethod
    def equal(cls, s, test):
        '''Arguments:
            s: string to be tested
            test: string to be conatined in s
        '''

        return test == s


class StringModification(object):
    options = ['exchange', 'leave']

    @classmethod
    def exchange(cls, orig, new):
        return new

    @classmethod
    def leave(cls, orig, new):
        return orig


RULES = ['Transaction']
