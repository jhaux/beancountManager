import os
import pandas as pd

from beancountManager.referencer import Referencer
from beancountManager.deduplicate import DeduplicateIngester


class ConverterBase(object):

    def __init__(self,
                 userInputFn,
                 ledger,
                 saveFn,
                 sess_id='noid',
                 pbar=None):
        '''Sets up the Reader.

        Arguments:
            userInputFn: Function, which can be called to correctly format the
                    ledger entry if no rule can be applyed.
                    Has the signature (entry) => (entry)
            ledger: the list of entries to be updated
            sess_id: unique identifier for backups
            pbar: ttk Progressbar instance or None
        '''
        self.ledger = ledger
        self.saveFn = saveFn

        rules_file = type(self).__name__ + '.rules'
        rules_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        rules_path = os.path.join(rules_path, rules_file)
        self.referencer = Referencer(rules_path, userInputFn, ledger, sess_id)
        self.ingester = DeduplicateIngester(ledger)

        self.pbar = pbar

    def __call__(self, csv_file):
        '''Makes a pandas dataframe using read_data and iterates over it,
        generating ledger entries using step_data and the referencer'''

        df = self.read_data(csv_file)
        assert isinstance(df, pd.DataFrame), \
            'Data must be read in as pandas.DataFrame but is ' + type(df)

        if self.pbar:
            self.pbar['maximum'] = len(df)

        in_balance = self.get_in_balance()
        if in_balance:
            self.ledger += [in_balance]

        for index, row in df[::-1].iterrows():

            entry = self.step_data(index, row)

            if entry is not None and self.ingester.is_no_duplicate(entry):
                entry, opens = self.referencer(entry)
                self.ledger = self.ingester.ingest(entry)
                self.ledger += opens

            if self.pbar:
                self.pbar.step()

        out_balance = self.get_out_balance()
        if out_balance:
            self.ledger += [out_balance]

        return self.ledger

    def read_data(self, csv_file):
        '''Generate one pandas frame containing all data and return it'''
        raise NotImplementedError('This needs to be overwritten')

    def step_data(self, index, row):
        '''Converts data to a not yet valid beancount core.data entry and
        return it'''
        raise NotImplementedError('This needs to be overwritten')

    def get_in_balance(self):
        '''Optional method: get an entry, which places a balance statement.'''

        return None

    def get_out_balance(self):
        '''Optional method: get an entry, which places a balance statement.'''

        return None
