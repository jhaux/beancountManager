import numpy as np
import pandas as pd
import datetime

from beancount.core.data import Open, Close, Balance, Posting, Transaction
from beancount.core.amount import Amount, NULL_AMOUNT
from beancount.core.number import D
from beancountManager.referencer import Referencer


class VolksbankConverter(object):

    def __init__(self, references, userInputFn, ledger, sess_id='noid'):
        '''Sets up the Reader.

        Arguments:
            references: file containing sets of rules to determine the posting
                    directions (?!)
            userInputFn: Function, which can be called to correctly format the
                    ledger entry if no rule can be applyed.
                    Has the signature (entry) => (entry)
            sess_id: unique identifier for backups
        '''
        self.ledger = ledger
        self.referencer = Referencer(references, userInputFn, ledger, sess_id)
        self.sess_id = sess_id

    def __call__(self, csv_file, pbar=None):
        '''Reads all relevant data in one vb csv file and returns it as a
        preprocessed ledger class object.

        Arguments:
            csv_file: path to the data to be read and converted

        Returns:
            vb_ledger: ledger object containing all relevant data
        '''

        self.read_data(csv_file, pbar)

    def read_data(self, csv_file, pbar=None):
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

        if pbar:
            pbar['maximum'] = len(raw_data)
            pbar['maximum'] = 17 - 13

        for index, row in raw_data.iterrows():
            if index < 13:
                continue

            if index > 16:
                break

            fr = row['from']
            to = row['to']
            narr = row['description'].replace('\n', '')
            curr = row['currency']
            amount = float(row['amount'].replace(',', '.'))
            sign = 1 if row['HS'] == 'H' else -1
            date = row['date']
            date = datetime.date(*[int(d) for d in date.split('.')[::-1]])

            post_from = Posting(fr,  # Account
                                Amount(D(str(amount*sign)), curr),  # units
                                None,  # cost
                                None,  # price
                                None,  # flag
                                None)  # meta

            post_to = Posting(to,  # Account
                              Amount(D(str(-amount*sign)), curr),  # units
                              None,  # cost
                              None,  # price
                              None,  # flag
                              None)  # meta

            postings = [post_from, post_to]

            raw_tract = Transaction(None,  # meta (optional)
                                    date,  # date
                                    '*',  # flag
                                    None,  # payee (optional)
                                    narr,  # narration
                                    None,  # tags
                                    None,  # links
                                    postings)  # postings

            tract = self.referencer(raw_tract)

            self.ledger += tract

            if pbar:
                pbar.step()

        return self.ledger
