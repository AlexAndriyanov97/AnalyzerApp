# coding: utf-8

from cx_Freeze import setup, Executable

executables = [Executable('main.py','design,py','table.py','PandasModel.py')]

setup(name='Analyzer',
      version='0.0.1',
      description='Analyzer!',
      executables=executables)
