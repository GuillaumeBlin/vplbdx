import os
import re
import glob
from setuptools import setup

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

try:
    readme = read('README.md')
except IOError as e:
    readme = ''

templates = glob.glob('templates/*')

setup(name='tmper',
      license='MIT License',
      author='Matt Bierbaum',
      url='https://github.com/mattbierbaum/tmper',
      version='0.5.6',

      install_requires=[
          "tornado>=4.3",
          "parsedatetime>=2.1",
          "bcrypt>=3.1",
          "requests>=2.0",
          "requests_toolbelt>=0.7"
        ],
      packages=['tmper'],
      entry_points={
        'console_scripts': [
            'tmper = tmper.web:main'
        ]
      },
      package_data={
        'tmper': ['../README.md', '../templates/*']
      },

      platforms='osx, posix, linux, windows',
      description='Temporary file sharing using simple two digit codes.',
      long_description=readme,
      zip_safe=False,
)
