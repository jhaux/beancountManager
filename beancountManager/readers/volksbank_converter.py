import numpy as np
import pandas as pd
import datetime

from beancount.core.data import Open, Close, Balance, Posting, Transaction
from beancount.core.amount import Amount, NULL_AMOUNT
from beancount.core.number import D
from beancountManager.referencer import Referencer


class ConverterBase(object):

    def __init__(self,
                 parent_name,
                 userInputFn,
                 ledger,
                 sess_id='noid',
                 pbar=None):
        '''Sets up the Reader.

        Arguments:
            paranet_name: used to find the file containing sets of rules to
                    determine the posting directions (?!)
            userInputFn: Function, which can be called to correctly format the
                    ledger entry if no rule can be applyed.
                    Has the signature (entry) => (entry)
            ledger: the list of entries to be updated
            sess_id: unique identifier for backups
            pbar: ttk Progressbar instance or None
        '''
        self.ledger = ledger

        rules_file = parent_name + '.rules'
        self.referencer = Referencer(rules_file, userInputFn, ledger, sess_id)

        self.pbar = pbar

    def __call__(self, csv_file):
        '''Makes a pandas dataframe using read_data and iterates over it,
        generating ledger entries using step_data and the referencer'''

        df = self.read_data(csv_file)

        for index, row in df.iterrows():
            entry = self.step_data(index, row)
            entry = self.referencer(entry)

            self.ledger += entry

            if self.pbar:
                pbar.step()

        return self.ledger

    def read_data(self, csv_file):
        '''Generate one pandas frame containing all data and return it'''
        raise NotImplementedError('This needs to be overwritten')

    def step_data(self, index, row):
        '''Converts data to a not yet valid beancount core.data entry and
        return it'''
        raise NotImplementedError('This needs to be overwritten')



class VolksbankConverter(ConverterBase):

    def __init__(self,
                 references,
                 userInputFn,
                 ledger,
                 sess_id='noid',
                 pbar=None):

        ConverterBase.__init__(self,
                               self.__name__,
                               userInputFn,
                               ledger,
                               sess_id,
                               pbar)

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

        for index, row in raw_data.iterrows():

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
