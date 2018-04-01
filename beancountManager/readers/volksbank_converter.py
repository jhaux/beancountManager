import numpy as np
import pandas as pd
import datetime

from beancount.core.data import Open, Balance, Posting, Transaction
from beancount.core.amount import Amount, NULL_AMOUNT
from beancount.core.number import D

from beancountManager.readers.converter_base import ConverterBase


class VolksbankConverter(ConverterBase):

    def read_data(self, csv_file):
        self.csv_file = csv_file

        self.meta = {'file': self.csv_file}
        self.kto = csv_file.split('_')[1]

        raw_data = pd.read_csv(csv_file,
                               skiprows=13,
                               encoding='latin3',
                               quotechar='"',
                               delimiter=';',
                               names=['date', 'valuata', 'from', 'to', 'KTO',
                                      'IBAN', 'BLZ', 'BIC', 'description',
                                      'ref', 'currency', 'amount', 'HS'])

        raw_data = raw_data.replace(np.nan, 'EMPTY', regex=True)

        self.date_out = raw_data['date'][len(raw_data)-1]
        self.date_out = datetime.date(*[int(d) for d
                                        in self.date_out.split('.')[::-1]])
        self.date_out += datetime.timedelta(1)  # add one day
        self.balance_out = raw_data['amount'][len(raw_data)-1]
        self.balance_out = self.balance_out.replace('.', '')
        self.balance_out = float(self.balance_out.replace(',', '.'))
        self.balance_out *= 1 if raw_data['HS'][len(raw_data)-1] == 'H' else -1
        self.balance_out = D(str(self.balance_out))

        self.date_in = raw_data['date'][len(raw_data)-2]
        self.date_in = datetime.date(*[int(d) for d
                                       in self.date_in.split('.')[::-1]])
        self.balance_in = raw_data['amount'][len(raw_data)-2]
        self.balance_in = self.balance_in.replace('.', '')
        self.balance_in = float(self.balance_in.replace(',', '.'))
        self.balance_in *= 1 if raw_data['HS'][len(raw_data)-2] == 'H' else -1
        self.balance_in = D(str(self.balance_in))

        raw_data = raw_data.drop(raw_data.tail(2).index)

        return raw_data

    def step_data(self, index, row):
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

        raw_tract = Transaction(self.meta,  # meta (optional)
                                date,  # date
                                '*',  # flag
                                None,  # payee (optional)
                                narr,  # narration
                                None,  # tags
                                None,  # links
                                postings)  # postings

        return raw_tract

    def get_in_balance(self):
        inBalance = Balance(self.meta,
                            self.date_in,
                            'Assets:VB:Giro',
                            Amount(self.balance_in, 'EUR'),
                            None,
                            None)

        return inBalance

    def get_out_balance(self):
        outBalance = Balance(self.meta,
                             self.date_out,
                             'Assets:VB:Giro',
                             Amount(self.balance_out, 'EUR'),
                             None,
                             None)
        return outBalance
