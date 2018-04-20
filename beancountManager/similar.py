from beancount.core import data
from beancount.parser import printer
from beancount.core.data import Transaction
from beancount.ingest.similar import SimilarityComparator

import datetime


def filter_ledger(ledger, entry_type):
    '''Iterator, which returns all entries of a certain type.
    Arguments:
        ledger: list of entries, returned e.g. by bencounts
                importer.import_file
        entry_type: type passed to isinstance, can alo be a tuple of types

    Yields:
        A list of entries of entry_type, in the same order as they are in the
                ledger
    '''

    for entry in ledger:
        if isinstance(entry, entry_type):
            yield entry


def find_similar_entries(entries,
                         source_entries,
                         comparator=None,
                         window_days=2,
                         filter_type=Transaction):
    '''Same as beancount's similar.find_similar_entries function, but with the
    ability to filter any type of entries'''

    window_head = datetime.timedelta(days=window_days)
    window_tail = datetime.timedelta(days=window_days + 1)

    if comparator is None:
        comparator = SimilarityComparator()

    # For each of the new entries, look at entries at a nearby date.
    duplicates = []
    for entry in filter_ledger(entries, filter_type):

        p1 = entry.payee
        print('payee', p1)
        print('date', entry.date)
        print('date', type(entry.date))
        debug_cond = p1 is not None and 'Edeka' in str(p1)
        debug_cond = entry.date == datetime.date(2018, 3, 19)

        filtered_entries = list(filter_ledger(
                data.iter_entry_dates(source_entries,
                                      entry.date - window_head,
                                      entry.date + window_tail),
                filter_type))

        if debug_cond:
            print(entry.date)
            print(len(filtered_entries))

        for source_entry in filtered_entries:

            if debug_cond:
                printer.print_entries([entry, source_entry])

            if comparator(entry, source_entry):
                duplicates.append((entry, source_entry))
                break
    return duplicates
