from __future__ import absolute_import, division, print_function

import io
import os
import re
import sys

from setuptools import find_packages, setup, Extension

# cf.
# https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
def read(*names, **kwargs):
  with io.open(
    os.path.join(os.path.dirname(__file__), *names),
    encoding=kwargs.get("encoding", "utf8")
  ) as fp:
    return fp.read()

def find_version(*file_paths):
  version_file = read(*file_paths)
  version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                            version_file, re.M)
  if version_match:
    return version_match.group(1)
  raise RuntimeError("Unable to find version string.")

if sys.version_info < (2,7):
  sys.exit('Sorry, Python < 2.7 is not supported')

fable_ext = Extension(
    'fable_ext',
    sources=[os.path.join('fable', 'ext.cpp')],
    include_dirs=['fable'],
    libraries=['boost_python'],
    extra_compile_args=[
        '-g0', # disable debug symbols
        '-Wno-sign-compare',
    ],
)

setup(name='fable',
      description='An experiment',
      url='https://github.com/Anthchirp/fable-disentangle',
      author='Markus Gerstel',
      author_email='scientificsoftware@diamond.ac.uk',
      download_url="https://github.com/Anthchirp/fable-disentangle",
      version=find_version('fable', '__init__.py'),
      install_requires=[
        'munch',
      ],
      packages=find_packages(),
      include_package_data=True,
      ext_modules=[ fable_ext ],
      license='BSD',
      entry_points={
        'console_scripts': [
          'fable.cout = fable.command_line.cout:main',
          'fable.read = fable.command_line.read:main',
          'fable.split = fable.command_line.split:main',
        ],
      },
      setup_requires=[
        'pytest-runner',
      ],
      tests_require=['pytest'],
      classifiers = [
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        ]
     )
