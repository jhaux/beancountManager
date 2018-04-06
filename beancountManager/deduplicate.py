from beancount import loader
from beancount.parser import printer
from beancount.ingest import similar
from beancount.core.data import Transaction


def find_and_delete_duplicates(l):
    for e1 in l:
        duplicates = similar.find_similar_entries([e1], l, window_days=4)

        for d in duplicates:
            if d != e1:
                printer.print_entries([d[1]])
                l.remove(d[1])


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
