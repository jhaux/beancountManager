from setuptools import setup

setup(name='beancountManager',
      version='0.2',
      description='Merge my transactions and stuff into my beancount ledger',
      url='None yet',
      author='Johannes Haux',
      author_email='johannes.haux@gmx.de',
      license='GPLv2',
      packages=['beancountManager'],
      install_requires=[
                    'pandas',
                    'numpy'
                          ],
      zip_sage=False)
