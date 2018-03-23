import json

from beancountManager.ledger import Transaction, Open, Balance


class Referencer(object):
    '''Contains rules, by which the incoming ledger entries are formatted.'''

    def __init__(self, rules_file, userInputFn):
        '''Arguments:
            rules_file: path to the file containing the rules
        '''

        self.userInputFn = userInputFn
        self.rules = []

        with open(rules_file, 'r') as the_file:
            rule_dicts = json.load(the_file)
            for rule in rule_dicts:
                self.rules.append(Rule(rule))

    def __call__(self, entry):
        if isinstance(entry, Transaction):
            for rule in self.rules:
                if rule.test(entry):
                    entry = rule.apply(entry)
                    print(entry)
            # Do something
            return entry
        else:
            # Ask for help
            entry = self.userInputFn(entry)
            return entry


class Rule(object):

    def __init__(self, rule_dict):
        for k, v in rule_dict.items():
            setattr(self, k, v)

    def test(self, entry):
        result = True
        if self.kind == 'transaction':
            for k, v in self.pattern.items():
                if v is not None:
                    if k != 'postings':
                        for method, test in v.items():
                            success = self.atomic_test(getattr(entry, k),
                                                       method,
                                                       test)
                            result = result and success
                    else:
                        idx = 1
                        postings = entry.postings
                        while str(idx) in v and len(postings) >= idx:
                            for pk, pv in v[str(idx)].items():
                                if pv is not None:
                                    for method, test in pv.items():
                                        s = getattr(postings[idx - 1], pk)
                                        success = self.atomic_test(
                                                s,
                                                method,
                                                test)
                                        result = result and success

                            idx += 1
        return result

    def atomic_test(self, string, method, test):
        test_method = getattr(StringComparison, method)
        success = test_method(string, test)

        return success

    def apply(self, entry):
        if self.kind == 'transaction':
            for k, v in self.changes.items():
                if v is not None:
                    if k != 'postings':
                        for method, change in v.items():
                            new_str = self.atomic_modofocation(
                                    getattr(entry, k),
                                    method,
                                    change)
                            setattr(entry, k, new_str)
                    else:
                        idx = 1
                        postings = entry.postings
                        while str(idx) in v and len(postings) >= idx:
                            for pk, pv in v[str(idx)].items():
                                if pv is not None:
                                    for method, change in pv.items():
                                        new_str = self.atomic_modofocation(
                                                getattr(postings[idx-1], pk),
                                                method,
                                                change)
                                        setattr(postings[idx-1], pk, new_str)

                            idx += 1
        return entry

    def atomic_modofocation(self, orig, method, change):
        change_method = getattr(StringModification, method)
        return change_method(orig, change)


class StringComparison(object):
    def __init__(self):
        pass

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
    def __init__(self):
        pass

    @classmethod
    def exchange(cls, orig, new):
        return new
