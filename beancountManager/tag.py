from beancount import loader
from beancount.core.data import Transaction
from beancount.parser import printer


def tag(entry):
    if isinstance(entry, Transaction):
        if 'import_file' in entry.meta:
            if 'Umsaetze_DE0227092555' in entry.meta['import_file']:
                entry = entry._replace(**{'tags': ['Johannes']})
            elif '_Paypal_' in entry.meta['import_file']:
                entry = entry._replace(**{'tags': ['Johannes']})
        for p in entry.postings:
            if p.account == 'Assets:Sparkasse:Gemeinschaftskonto':
                entry = entry._replace(**{'tags': ['Gemeinsam']})

    return entry


if __name__ == '__main__':
    l, _, _ = loader.load_file('Johannes_Ledger.beancount')

    l_new = []
    for entry in l:
        l_new.append(tag(entry))

    with open('Johannes_Ledger.beancount', 'r') as f:
        c = f.readlines()[:3]

    with open('Johannes_Ledger.beancount', 'w') as f:
        f.writelines(c)
        printer.print_entries(l_new, file=f)
