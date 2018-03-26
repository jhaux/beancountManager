import json

from beancount.core.data import Transaction
from beancount.parser import printer


class Referencer(object):
    '''Contains rules, by which the incoming ledger entries are formatted.'''

    def __init__(self, rules_file, userInputFn):
        '''Arguments:
            rules_file: path to the file containing the rules
        '''

        self.rules_file = rules_file
        self.userInputFn = userInputFn
        self.rules = []

        with open(rules_file, 'r') as the_file:
            rule_dicts = json.load(the_file)
            for rule in rule_dicts:
                self.rules.append(Rule(rule))

    def __call__(self, entry):
        if isinstance(entry, Transaction):
            matchedSomeRule = False
            for rule in self.rules:
                if rule.test(entry):
                    entry = rule.apply(entry)
                    matchedSomeRule = True
            if not matchedSomeRule:
                entry = self.userInputFn(entry)
            # Do something
            return entry
        else:
            # Ask for help
            return entry

    def add_rule(self, rule):
        if rule not in self.rules:
            self.rules.append(rule)
            self.store_rules

    def store_rules(self):
        with open(self.rules_file, 'w+') as the_file:
            the_file.write(json.dumps(self.rules, indent=4, sort_keys=True))


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
                elif k == 'units':
                    for pk, pv in v.items():
                        method, test, _, _ = pv
                        s = getattr(entry.units, pk)
                        success = self.atomic_test(
                                s,
                                method,
                                test)
                        result = result and success
                else:
                    postings = entry.postings
                    for idx, p in enumerate(v):
                        for pk, pv in p.items():
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
        test_method = getattr(StringComparison, method)
        success = test_method(string, test)
        print('Compare: {} {} {}? => {}'.format(string, method, test, success))

        return success

    def apply(self, entry):
        print('APPLY')
        assert type(entry).__name__ == self.kind, 'Cannot apply rule'
        printer.print_entry(entry)
        if self.kind == 'Transaction':
            for k, v in self.rd.items():
                if k != 'postings' and k != 'units':
                    _, _, method, change = v
                    new_str = self.atomic_modofocation(
                            getattr(entry, k),
                            method,
                            change)
                    entry = entry._replace(**{k: new_str})
                elif k == 'units':
                    for pk, pv in v.items():
                        _, _, method, change = pv
                        s = getattr(entry.units, pk)
                        new_str = self.atomic_modofocation(
                                s,
                                method,
                                change)
                        entry.units = pv._replace(**{pk: new_str})
                else:
                    postings = entry.postings
                    for idx, p in enumerate(v):
                        for pk, pv in v[idx].items():
                            _, _, method, change = pv
                            new_str = self.atomic_modofocation(
                                    getattr(postings[idx], pk),
                                    method,
                                    change)
                            postings[idx] = postings[idx]._replace(**{pk: new_str})
            printer.print_entry(entry)
            print(entry)
        return entry

    def atomic_modofocation(self, orig, method, change):
        change_method = getattr(StringModification, method)
        new_str = change_method(orig, change)
        print('Change: {} {} {} => {}'.format(orig, method, change, new_str))
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
    options = ['exchange']

    @classmethod
    def exchange(cls, orig, new):
        return new


RULES = ['Transaction']
