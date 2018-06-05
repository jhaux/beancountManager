from beancount.parser import printer


def store_sorted_ledger(
        ledger,
        path,
        key_dict={'Transaction': 2, 'Balance': 1, 'Open': 0, 'Other': 2},
        title='J\'s Beancount file'
        ):

        ledger = sort_by_date(ledger, key_dict)

        # print('storing {} entries.'.format(len(ledger)))
        # printer.print_entries(ledger)
        # for e in ledger:
        #     print(e)

        with open(path, 'w+') as ledgerFile:
            ledgerFile.write('option "title" "{}"\n'.format(title)
                             + 'option "operating_currency" "EUR"\n\n')
            printer.print_entries(ledger, file=ledgerFile)


def sort_by_date(
        ledger,
        key_dict={'Transaction': 2, 'Balance': 1, 'Open': 0, 'Other': 2},
        ):

        def key(entry):
            tp = type(entry).__name__

            primary = entry.date
            secondary = 0 if tp == 'Open' else 1 if tp == 'Balance' else 2

            return primary, secondary

        ledger = list(sorted(ledger,
                             key=key))

        return ledger
