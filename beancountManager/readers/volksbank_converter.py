import numpy as np
import pandas as pd
import datetime
import os

from beancount.core.data import Open, Close, Balance, Posting, Transaction
from beancount.core.amount import Amount, NULL_AMOUNT
from beancount.core.number import D

from beancountManager.referencer import Referencer
from beancountManager.readers.converter_base import ConverterBase


class VolksbankConverter(ConverterBase):

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

        return raw_data

    def step_data(self, index, row):
        if index > 16:
            return None

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

        return tract
