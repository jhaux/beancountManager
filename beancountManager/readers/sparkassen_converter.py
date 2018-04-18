import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict

from beancount.core.data import Balance, Posting, Transaction
from beancount.core.amount import Amount
from beancount.core.number import D

from beancountManager.readers.converter_base import ConverterBase
from beancountManager.readers.default_assets import defAsset
from beancountManager.util import german2usNumber, getDefaultUser
from beancountManager import data


class SparkassenConverter(ConverterBase):

    def read_data(self, csv_file):
        self.meta = {data.FNAME_KEY: csv_file}

        fields = [
                'Auftragskonto',
                'Buchungstag',
                'Valutadatum',
                'Buchungstext',
                'Verwendungszweck',
                'Glaeubiger ID',
                'Mandatsreferenz',
                'Kundenreferenz',
                'Sammlerreferenz',
                'Lastschrift Ursprungsbetrag',
                'Auslagenersatz Ruecklastschrift',
                'Beguenstigter/Zahlungspflichtiger',
                'IBAN',
                'BIC',
                'Betrag',
                'Waehrung',
                'Info'
                ]

        df = pd.read_csv(csv_file,
                         skiprows=1,
                         names=fields,
                         dtype=str,
                         delimiter=';')
        df = df.replace(np.nan, 'EMPTY', regex=True)

        self.raw_data = df

        self.usertag = getDefaultUser(csv_file)

        return self.raw_data

    def step_data(self, index, row):

        # Test if this entry does anything and quit if not
        gebucht = row['Info'] == 'Umsatz gebucht'
        if not gebucht:
            print(row['Info'])
            return None

        # All data
        meta = dict(self.meta)
        meta[data.LINENO_KEY] = str(index + 2)

        date = row['Buchungstag']
        y, m, d = [int(d) for d in date.split('.')[::-1]]
        y += 2000
        date = datetime.date(y, m, d)

        fr = row['Auftragskonto']
        to = row['Beguenstigter/Zahlungspflichtiger']

        payee = row['IBAN'] if row['IBAN'] != 'EMPTY' else None
        narr = row['Verwendungszweck']

        curr = row['Waehrung']

        tags = [self.usertag] if self.usertag else None

        # Amounts
        brutto = float(german2usNumber(row['Betrag']))

        # Generate Postings in ordered fashion
        postings_map = OrderedDict()
        postings_map[defAsset(fr)] = brutto
        postings_map[defAsset(to)] = -brutto

        postings = []
        for account, number in postings_map.items():
            if number is not None:
                p = Posting(account,
                            Amount(D(str(number)), curr),
                            None,
                            None,
                            None,
                            None)
                postings.append(p)

        raw_tract = Transaction(meta,  # meta (optional)
                                date,  # date
                                '*',  # flag
                                payee,  # payee (optional)
                                narr,  # narration
                                tags,  # tags
                                None,  # links
                                postings)  # postings

        return raw_tract

    def get_in_balance(self):
        pass
        # inBalance = Balance(self.meta_in,
        #                     self.date_in,
        #                     'Assets:PayPal',
        #                     Amount(self.balance_in, 'EUR'),
        #                     None,
        #                     None)

        # return inBalance

    def get_out_balance(self):
        pass
        # outBalance = Balance(self.meta_out,
        #                      self.date_out,
        #                      'Assets:PayPal',
        #                      Amount(self.balance_out, 'EUR'),
        #                      None,
        #                      None)

        # return outBalance

    def get_balance_at_step(self, index):
        pass
        # meta = dict(self.meta, **{data.LINENO_KEY: str(index)})
        # date = self.raw_data['Datum'][index]
        # date = datetime.date(*[int(d) for d
        #                        in date.split('.')[::-1]])
        # date += datetime.timedelta(1)  # add one day
        # balance = D(german2usNumber(self.raw_data['Guthaben'][index]))

        # balance_dir = Balance(meta,
        #                       date,
        #                       'Assets:PayPal',
        #                       Amount(balance, 'EUR'),
        #                       None,
        #                       None)

        # return balance_dir
