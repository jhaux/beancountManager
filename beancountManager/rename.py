import os


LPATH = os.path.abspath(os.path.dirname(__file__))
parent_path = os.path.join(LPATH, 'readers')
RULES = os.listdir(parent_path)
RULES = [os.path.join(parent_path, p) for p in RULES if p[-6:] == '.rules']


def rename(old, new, ledger='Johannes_Ledger.beancount'):
    for fname in RULES + [os.path.join(LPATH, '../../', ledger)]:
        with open(fname, 'r') as f:
            content = f.read()

        content = content.replace(old, new)

        with open(fname, 'w') as f:
            f.write(content)


if __name__ == '__main__':
    renames = {
            'Liabilities:VISA:Sonja': 'Expenses:VISA:Sonja'
        }

    print(RULES)

    for k, v in renames.items():
        rename(k, v, 'Sonjas_Ledger.beancount')
