# -*- coding ascii -*-

import os
from distutils.core import setup
from distutils.command.install_data import install_data

class smart_install_data(install_data):
    def run(self):
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)


def search_packages(path, result=[]):
    if os.path.exists(os.path.join(path, "__init__.py")):
        result.append(path)
    for filename in os.listdir(path):
        child_path = os.path.join(path, filename)
        if os.path.isdir(child_path):
            search_packages(child_path, result)
    return result


def find_data_files(path, result=[], prefix=None, ok_exts=[], ng_exts=[]):
    files = []
    for filename in os.listdir(path):
        if filename == ".svn":
            continue
        child_path = os.path.join(path, filename)
        is_ok = False
        if os.path.isdir(child_path):
            find_data_files(child_path, result, prefix, ok_exts, ng_exts)
        elif os.path.isfile(child_path):
            is_ng = False
            for extfilter in ng_exts:
                if child_path.endswith(extfilter):
                    is_ng = True
                    break
            if is_ng:
                break
            if not ok_exts:
                is_ok = True
            for extfilter in ok_exts:
                if child_path.endswith(extfilter):
                    is_ok = True
                    break
        if is_ok:
            files.append(child_path)
    if files:
        if prefix is not None:
            result.append((os.path.join(prefix, path), files))
        else:
            result.append((path, files))
    return result


data_files = []
find_data_files('static', data_files,
                prefix='gtdd', ok_exts=['.gif', '.css', '.js', '.jpg', '.png'])


setup(name = 'gtd_on_django',
      version = "20080218",
      url = 'http://www.shibu.jp/programs/django/',
      author = 'Shibukawa Yoshiki',
      author_email = ('yoshiki at shibu.jp'),
      packages = search_packages("gtdd"),
      cmdclass = {'install_data': smart_install_data},
      data_files=data_files
)

# python setup.py sdist -f
# python setup.py bdist_wininst --install-script=pyspec_postinstall.py
# python setup.py bdist_rpm
