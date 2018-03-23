import numpy as np
import pandas as pd

from beancountManager.ledger import Ledger, Transaction, Open, Posting
from beancountManager.referencer import Referencer


class VolksbankConverter(object):

    def __init__(self, references, userInputFn):
        '''Sets up the Reader.

        Arguments:
            references: file containing sets of rules to determine the posting
                    directions (?!)
            userInputFn: Function, which can be called to correctly format the
                    ledger entry if no rule can be applyed.
                    Has the signature (entry) => (entry)
        '''
        self.ledger = Ledger()
        self.referencer = Referencer(references, userInputFn)

    def __call__(self, csv_file):
        '''Reads all relevant data in one vb csv file and returns it as a
        preprocessed ledger class object.

        Arguments:
            csv_file: path to the data to be read and converted

        Returns:
            vb_ledger: ledger object containing all relevant data
        '''

        data = self.read_data(csv_file)

        return data

    def read_data(self, csv_file):
        raw_data = pd.read_csv(csv_file,
                               skiprows=13,
                               skipfooter=3,
                               encoding='latin3',
                               quotechar='"',
                               delimiter=';',
                               names=['date', 'valuata', 'from', 'to', 'KTO',
                                      'IBAN', 'BLZ', 'BIC', 'description',
                                      'ref', 'currency', 'amount', 'HS'])

        raw_data = raw_data.replace(np.nan, 'EMPTY', regex=True)
        # balance_in = raw_data['amount'][-1]
        # balance_out = raw_data['amount'][-2]

        for index, row in raw_data.iterrows():
            if index < 13:
                continue

            fr = row['from']
            to = row['to']
            narr = row['description'].replace('\n', '')
            curr = row['currency']
            amount = float(row['amount'].replace(',', '.'))
            sign = 1 if row['HS'] == 'H' else -1
            date = row['date']

            post_from = Posting(fr, amount*sign, curr)
            post_to = Posting(to)

            raw_tract = Transaction(date, [post_from, post_to], narration=narr)

            tract = self.referencer(raw_tract)

            self.ledger.add_entry(tract)

        return self.ledger
