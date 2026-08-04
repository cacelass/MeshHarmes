import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

project = 'MeshHarmes'
copyright = '2026, cacelass'
author = 'cacelass'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

language = 'es'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
