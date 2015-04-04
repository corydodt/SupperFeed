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
      packages=['supperfeed'],
      package_data={'supperfeed': ['templates/*.html']},
      scripts=['./appbin/spoon', './appbin/recipeschema'],
      install_requires=[
        # app:
        "gdata",
        "jinja2",
        "klein",
        "markdown",
        "microdata",
        "mongoengine",
        "nodeenv",
        "pyopenssl",
        "pyyaml",
        "service_identity",
        # testing:
        "coverage",
        "pyflakes",
        "mock",
        "fabric",
      ],
      zip_safe=False)

setup(**cfg)
