from distutils.core import setup
import os

setup(name = 'GTDonDjango',
      version = '20090218',
      author = 'Shibukawa Yoshiki',
      author_email = 'yoshiki@shibu.jp',
      url = "http://www.shibu.jp/programs/gtd",
      packages = ['gtd_site', ''])

# python setup.py sdist
# python setup.py bdist_wininst
# python setup.py bdist_rpm
