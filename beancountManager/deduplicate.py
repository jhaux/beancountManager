from beancount import loader
from beancount.parser import printer
from beancount.ingest import similar
from beancount.core.data import Transaction

import datetime
from collections import OrderedDict


def find_and_delete_duplicates(l):
    for e1 in l:
        duplicates = similar.find_similar_entries([e1], l, window_days=4)

        for s, d in duplicates:
            if d != e1:
                l.remove(d)

    for e1 in l:
        U = UmbuchungsComparator(datetime.timedelta(6))
        duplicates_umbuchung = similar.find_similar_entries([e1],
                                                            l,
                                                            comparator=U,
                                                            window_days=4)
        for s, d in duplicates_umbuchung:
            print(id(d))
            printer.print_entries([d])
            print(id(e1))
            printer.print_entries([e1])
            print('\n' + '='*20)

            l.remove(d)


class UmbuchungsComparator(object):
    def __init__(self, max_date_delta=None):
        self.max_date_delta = max_date_delta

    def __call__(self, entry1, entry2):
        if self.max_date_delta:
            delta = ((entry1.date - entry2.date)
                     if entry1.date > entry2.date else
                     (entry2.date - entry1.date))
        if delta > self.max_date_delta:
            return False

        try:
            if entry1.meta['import_file'] != entry2.meta['import_file'] \
                    and len(entry1.postings) == len(entry2.postings):
                d1 = account_map(entry1)
                d2 = account_map(entry2)
                a1 = set(d1)
                a2 = set(d2)

                # Are all keys the same?
                if len(a1 & a2) != len(entry1.postings):
                    return False

                # Are all postings to or from Assets?
                for a in a1 | a2:
                    if 'Assets:' not in a:
                        return False

                    if not d1[a] == d2[a]:
                        return False

                print(a1 | a2)

                return True
            return False

        except Exception:
            return False


class DuplicateComparator(object):
    def __init__(self, max_date_delta=None):
        self.max_date_delta = max_date_delta

    def __call__(self, entry1, entry2):
        e1 = entry1
        e2 = entry2
        if self.max_date_delta is not None:
            delta = ((entry1.date - entry2.date)
                     if entry1.date > entry2.date else
                     (entry2.date - entry1.date))

            if delta > self.max_date_delta:
                print(e1.date, e2.date)
                return False

        try:
            # Same File and same line: If that aint no dupe sth's fucky
            if e1.meta['import_file'] == e2.meta['import_file'] \
                    and e1.meta['import_lineno'] == e2.meta['import_lineno']:
                return True
        except Exception as e:
            print(e)

        if len(entry1.postings) == len(entry2.postings):
            d1 = account_map(entry1)
            d2 = account_map(entry2)
            u1 = [p[0] for p in list(d1.values())]
            u2 = [p[0] for p in list(d2.values())]

            # Are all postings of the same size?
            if not u1 == u2:
                return False

            return True
        return False


def account_map(e):
    d = OrderedDict()
    for p in e.postings:
        d[p.account] = (p.units.number, p.units.currency)
    return d


class DeduplicateIngester(object):

    def __init__(self, ledger):
        self.ledger = ledger
        self.U = UmbuchungsComparator(datetime.timedelta(6))
        self.D = DuplicateComparator(datetime.timedelta(1))

    def ingest(self, entry):
        if not self.entry_is_in_ledger(entry):
            self.ledger += [entry]
        else:
            print('Dropping Entry')
            printer.print_entries([entry])
            print('')

        return self.ledger

    def entry_is_in_ledger(self, entry):
        '''Used to determine if entry is in ledger AFTER the entry has been
        processed.'''
        duplicates_um = similar.find_similar_entries([entry],
                                                     self.ledger,
                                                     comparator=self.U,
                                                     window_days=4)

        if len(duplicates_um) == 0:
            return False

        try:
            print('Found Duplicates')
            printer.print_entries([entry])
            print('Umbuchung')
            printer.print_entries(list(duplicates_um[0]))
            print('')
        except Exception as e:
            print(e)

        return True

    def is_no_duplicate(self, entry):
        '''Used to determine if entry is in ledger BEFORE the entry has been
        processed.'''
        duplicates = similar.find_similar_entries([entry],
                                                  self.ledger,
                                                  comparator=self.D,
                                                  window_days=0)

        if len(duplicates) != 0:
            # print('Dropping Entry - it already exists')
            # printer.print_entries([entry])
            # print('')
            return False
        else:
            return True


def n_um(l):
    n1 = 0
    n2 = 0
    for e in l:
        if isinstance(e, Transaction):
            if 'Umbuch auf P' in e.narration:
                n1 += 1
            if 'Umbuchung V' in e.narration:
                n2 += 1
    print('VB PP SS HH')
    print(n1, n2, n1+n2, (n1+n2) / 2.)


if __name__ == '__main__':
    l, _, _ = loader.load_file('~/Documents/Finanzen/test_ledger.beancount')

    print(len(l))
    n_um(l)
    find_and_delete_duplicates(l)
    print(len(l))
    n_um(l)

    with open('/home/johannes/Documents/Finanzen/test_ledger2.beancount',
              'w+') as f:
        printer.print_entries(l, file=f)
