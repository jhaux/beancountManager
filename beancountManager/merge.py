from beancount import loader
from beancount.parser import printer
from beancount.core.data import Transaction
from beancountManager.deduplicate import DeduplicateIngester
from beancountManager.io import store_sorted_ledger


def merge_ledgers(ledgers):
    merged_ledger = ledgers[0]
    ingester = DeduplicateIngester(merged_ledger)

    old_len = len(merged_ledger)
    for ledger in ledgers[1:]:
        for entry in ledger:
            print('\n')
            if ingester.is_no_duplicate(entry):
                merged_ledger = ingester.ingest(entry)

            old_len = len(merged_ledger)

    return merged_ledger


def merge_and_store(*legerpaths, storePath=None, title='Merged'):
    if storePath is None:
        storePath = legerpaths[0]

    ledgers = [loader.load_file(p)[0] for p in legerpaths]

    merged_ledger = merge_ledgers(ledgers)

    store_sorted_ledger(merged_ledger, storePath, title=title)


if __name__ == '__main__':
    merge_and_store('Sonjas_Ledger.beancount',
                    'MergedLedger.beancount',
                    storePath='MergedLedger2.beancount', title='Merged2')
