from beancount.ingest.similar import SimilarityComparator

from beancountManager import data


class SameAmountComparator(SimilarityComparator):

    def __call__(self, e1, e2):
        if self.max_date_delta is not None:
            delta = ((e1.date - e2.date)
                     if e1.date > e2.date else
                     (e2.date - e1.date))
            if delta > self.max_date_delta:
                return False

        meta_equal = self.compare_meta(e1, e2)

        if meta_equal:
            return True

        amount_equal = self.compare_amount(e1, e2)

        if amount_equal:
            return True

        return False

    def compare_meta(self, e1, e2):
        m1 = e1.meta
        m2 = e2.meta

        same_import = True
        for field in [data.FNAME_KEY, data.LINENO_KEY]:
            if field in m1 and field in m2:
                same_import = same_import and (m1[field] == m2[field])
            else:
                same_import = False

        return same_import

    def compare_amount(self, e1, e2):
        a1 = e1.units.number
        a2 = e2.units.number

        return a1 == a2
