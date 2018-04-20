from beancount import loader
from beancount.parser import printer
from beancount.core.data import Transaction

import argparse

from beancountManager.deduplicate import DeduplicateIngester
from beancountManager.io import store_sorted_ledger


def merge_ledgers(ledgers):
    merged_ledger = ledgers[0]
    ingester = DeduplicateIngester(merged_ledger)

    old_len = len(merged_ledger)
    for ledger in ledgers[1:]:
        for entry in ledger:
            if ingester.is_no_duplicate(entry):
                merged_ledger = ingester.ingest(entry, merged_ledger)

            old_len = len(merged_ledger)

    return merged_ledger


def merge_and_store(*legerpaths, storePath=None, title='Merged'):
    if storePath is None:
        storePath = legerpaths[0]

    ledgers = [loader.load_file(p)[0] for p in legerpaths]

    merged_ledger = merge_ledgers(ledgers)

    store_sorted_ledger(merged_ledger, storePath, title=title)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ledgers', nargs='+', type=str, help='list of ledgers')
    parser.add_argument('--store', type=str, help='store path', default=None)
    parser.add_argument('--title', type=str, help='title string', default=None)

    args = parser.parse_args()

    merge_and_store(*args.ledgers,
                    storePath=args.store,
                    title=args.title)
