import os

from beancountManager.referencer import Referencer


class ConverterBase(object):

    def __init__(self,
                 userInputFn,
                 ledger,
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

        rules_file = type(self).__name__ + '.rules'
        rules_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])
        rules_path = os.path.join(rules_path, rules_file)
        self.referencer = Referencer(rules_path, userInputFn, ledger, sess_id)

        self.pbar = pbar

    def __call__(self, csv_file):
        '''Makes a pandas dataframe using read_data and iterates over it,
        generating ledger entries using step_data and the referencer'''

        df = self.read_data(csv_file)

        if pbar:
            pbar['maximum'] = len(df)

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
