"""
SupperFeed, the recipe server
"""
import os

from setuptools import setup, find_packages

cfg = dict(name='SupperFeed',
      version='0.0',
      description='Pull Google Sheets containing recipe data and render as web pages',
      url='http://github.com/corydodt/SupperFeed',
      author='Cory Dodt',
      author_email='corydodt@gmail.com',
      license='MIT',
      packages=[], # not installing any source code, we only care about deps
      install_requires=[
        # app:
        "mongoengine",
        "klein",
        "jinja2",
        "pyyaml",
        "markdown",
        "nodeenv",
        # testing:
        "coverage",
        "pyflakes",
        "mock",
        "fabric",
      ],
      zip_safe=False)

setup(**cfg)
