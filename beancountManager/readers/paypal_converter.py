import numpy as np
import pandas as pd
import datetime
from collections import OrderedDict

from beancount.core.data import Balance, Posting, Transaction
from beancount.core.amount import Amount
from beancount.core.number import D

from beancountManager.readers.converter_base import ConverterBase
from beancountManager.util import german2usNumber, getDefaultUser
from beancountManager import data


class PaypalConverter(ConverterBase):

    def read_data(self, csv_file):
        self.meta = {data.FNAME_KEY: csv_file}

        fields = [
                'Datum',
                'Uhrzeit',
                'Zeitzone',
                'Name',
                'Typ',
                'Status',
                'Währung',
                'Brutto',
                'Gebühr',
                'Netto',
                'Absender E-Mail-Adresse',
                'Empfänger E-Mail-Adresse',
                'Transaktionscode',
                'Lieferadresse',
                'Adress-Status',
                'Artikelbezeichnung',
                'Artikelnummer',
                'Versand- und Bearbeitungsgebühr',
                'Versicherungsbetrag',
                'Umsatzsteuer',
                'Option 1 Name',
                'Option 1 Wert',
                'Option 2 Name',
                'Option 2 Wert',
                'Zugehöriger Transaktionscode',
                'Rechnungsnummer',
                'Zollnummer',
                'Anzahl',
                'Empfangsnummer',
                'Guthaben',
                'Adresszeile 1',
                'Adresszusatz',
                'Ort',
                'Bundesland',
                'PLZ',
                'Land',
                'Telefon',
                'Betreff',
                'Hinweis',
                'Ländervorwahl',
                'Auswirkung auf Guthaben'
                ]

        df = pd.read_csv(csv_file, skiprows=1, names=fields, dtype=str)
        df = df.replace(np.nan, 'EMPTY', regex=True)

        self.meta_out = dict(self.meta, **{data.LINENO_KEY: str(len(df))})
        self.date_out = df['Datum'][len(df)-1]
        self.date_out = datetime.date(*[int(d) for d
                                        in self.date_out.split('.')[::-1]])
        self.date_out += datetime.timedelta(1)  # add one day
        self.balance_out = D(german2usNumber(df['Guthaben'][len(df)-1]))

        self.meta_in = dict(self.meta, **{data.LINENO_KEY: '2'})
        self.date_in = df['Datum'][0]
        self.date_in = datetime.date(*[int(d) for d
                                       in self.date_in.split('.')[::-1]])
        self.balance_in = D(str(float(german2usNumber(df['Guthaben'][0]))
                                - float(german2usNumber(df['Netto'][0]))))

        self.old_balance = -12333415.123

        self.raw_data = df[::-1]

        self.usertag = getDefaultUser(csv_file)

        return self.raw_data

    def step_data(self, index, row):

        # Test if this entry does anything
        balance = float(german2usNumber(row['Guthaben']))
        if balance != self.old_balance:
            self.old_balance = balance
        else:
            return None

        # All data
        meta = dict(self.meta)
        meta[data.LINENO_KEY] = str(index + 2)

        date = row['Datum']
        date = datetime.date(*[int(d) for d in date.split('.')[::-1]])

        fr = row['Absender E-Mail-Adresse']
        to = row['Empfänger E-Mail-Adresse']
        other_account = fr if fr != 'johannes.haux@gmx.de' else to

        tags = [self.usertag] if self.usertag else None

        payee = row['Name'] if row['Name'] != 'EMPTY' else None
        narr = row['Typ']

        curr = row['Währung']

        # Amounts
        brutto = float(german2usNumber(row['Brutto']))

        gebuhr = row['Gebühr']
        if gebuhr != 'EMPTY' and gebuhr != '0,00':
            gebuhr = -float(german2usNumber(gebuhr))
        else:
            gebuhr = None

        netto = row['Netto']
        if netto == 'EMPTY':
            netto = brutto
        else:
            netto = float(german2usNumber(netto))

        # Generate Postings in ordered fashion
        postings_map = OrderedDict()
        postings_map['Assets:PayPal'] = netto
        postings_map['Expenses:PayPal:Gebuehren'] = gebuhr
        postings_map[other_account] = -brutto

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
        inBalance = Balance(self.meta_in,
                            self.date_in,
                            'Assets:PayPal',
                            Amount(self.balance_in, 'EUR'),
                            None,
                            None)

        return inBalance

    def get_out_balance(self):
        outBalance = Balance(self.meta_out,
                             self.date_out,
                             'Assets:PayPal',
                             Amount(self.balance_out, 'EUR'),
                             None,
                             None)

        return outBalance

    def get_balance_at_step(self, index):
        meta = dict(self.meta, **{data.LINENO_KEY: str(index)})
        date = self.raw_data['Datum'][index]
        date = datetime.date(*[int(d) for d
                               in date.split('.')[::-1]])
        date += datetime.timedelta(1)  # add one day
        balance = D(german2usNumber(self.raw_data['Guthaben'][index]))

        balance_dir = Balance(meta,
                              date,
                              'Assets:PayPal',
                              Amount(balance, 'EUR'),
                              None,
                              None)

        return balance_dir
