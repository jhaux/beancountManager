import numpy as np
import pandas as pd
import datetime

from beancount.core.data import Balance, Posting, Transaction
from beancount.core.amount import Amount
from beancount.core.number import D

from beancountManager.readers.converter_base import ConverterBase
from beancountManager.util import german2usNumber
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

        return df[::-1]

    def step_data(self, index, row):

        balance = float(german2usNumber(row['Guthaben']))
        if balance != self.old_balance:
            self.old_balance = balance
        else:
            return None

        meta = dict(self.meta)
        meta[data.LINENO_KEY] = str(index + 2)

        date = row['Datum']
        date = datetime.date(*[int(d) for d in date.split('.')[::-1]])

        fr = row['Absender E-Mail-Adresse']
        to_geb = 'Expenses:PayPal:Gebuehren'
        to = row['Empfänger E-Mail-Adresse']

        sign = 1 if fr == 'johannes.haux@gmx.de' else -1
        inv_sign = -1 * sign

        fr = 'Assets:PayPal' if fr == 'johannes.haux@gmx.de' else fr
        to = 'Assets:PayPal' if to == 'johannes.haux@gmx.de' else to

        payee = row['Name'] if row['Name'] != 'EMPTY' else None
        narr = row['Typ']

        curr = row['Währung']

        brutto = float(german2usNumber(row['Brutto']))
        post_from = Posting(fr,  # Account
                            Amount(D(str(sign*brutto)), curr),  # units
                            None,  # cost
                            None,  # price
                            None,  # flag
                            None)  # meta
        postings = [post_from]

        gebuhr = row['Gebühr']
        if gebuhr != 'EMPTY' and gebuhr != '0,00':
            gebuhr = float(german2usNumber(gebuhr))
            post_gebu = Posting(to_geb,  # Account
                                Amount(D(str(sign*gebuhr)), curr),  # unit
                                None,  # cost
                                None,  # price
                                None,  # flag
                                None)  # meta
            postings += [post_gebu]

        netto = row['Netto']
        if netto == 'EMPTY':
            netto = brutto
        else:
            netto = float(german2usNumber(netto))
        post_to = Posting(to,  # Account
                          Amount(D(str(inv_sign*netto)), curr),  # units
                          None,  # cost
                          None,  # price
                          None,  # flag
                          None)  # meta
        postings += [post_to]

        raw_tract = Transaction(meta,  # meta (optional)
                                date,  # date
                                '*',  # flag
                                payee,  # payee (optional)
                                narr,  # narration
                                None,  # tags
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
