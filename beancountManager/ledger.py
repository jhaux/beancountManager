class Ledger(object):

    def __init__(self):
        self._entries = []

    def add_entry(self, entry):
        if entry not in self._entries:
            self._entries.append(entry)
        else:
            raise ValueError("Entry already in ledger:\n{}\n{}"
                             .format(entry, self._entries))

    def remove_entry(self, entry):
        self._entries.remove(entry)

    def __str__(self):
        return '\n'.join(map(str, self._entries))


class Entry(object):
    def __init__(self, date):
        self.date = date


class Open(Entry):

    def __init__(self, date, account,
                 constraintCurrencies=[], bookingMethod=None):
        super().__init__(date)
        self.account = account
        self.constraintCurrencies = constraintCurrencies
        self.bookingMethod = bookingMethod

    def __str__(self):
        d = self.date
        a = self.account
        ccs = ' '.join(self.constraintCurrencies)
        b = self.bookingMethod if self.bookingMethod else ''

        return '{} open {} {} {}'.format(d, a, ccs, b)


class Transaction(Entry):
    def __init__(self, date, postings,
                 payee=None, narration=None, meta=None):
        super().__init__(date)
        self.postings = postings
        self.payee = payee
        self.narration = narration
        self.meta = meta

    def __str__(self):
        d = self.date
        pe = '"{}" '.format(self.payee) if self.payee else ''
        n = '"{}"'.format(self.narration) if self.narration else ''

        ps = '\n'.join(map(str, self.postings))

        m = '\n  {}'.format(self.meta) if self.meta else ''

        return '{} * {}{}{}\n{}'.format(d, pe, n, m, ps)


class Posting(object):
    def __init__(self, account, amount=None, currency=None,
                 flag=None, cost=None, price=None, meta=None):

        self.account = account
        self.amount = amount
        self.currency = currency
        self.flag = flag
        self.cost = cost
        self.price = price
        self.meta = meta

    def __str__(self):
        f = '{} '.format(self.flag) if self.flag else ''
        ac = self.account
        am = self.amount if self.amount else ''
        cur = self.currency if self.amount else ''  # if no ammount => no curr
        c = ' {{{}}}'.format(self.cost) if self.cost else ''
        p = ' [{}]'.format(self.price) if self.price else ''
        m = ''
        if self.meta:
            for k, v in self.meta.items():
                m += '\n    {}: "{}"'.format(k, v)

        return '  {}{}\t{} {}{}{}{}'.format(f, ac, am, cur, c, p, m)


class Balance(Entry):
    def __init__(self, date, amount, currency=None):
        super().__init__(date)
        self.amount = amount
        self.currency = currency

    def __str__(self):
        c = self.currency if self.currency else ''
        return '{} balance {}{}'.format(self.date, self.amount, c)
