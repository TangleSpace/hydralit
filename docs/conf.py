# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------

project = 'Hydralit'
copyright = '2021, Jackson Storm'
author = 'Jackson Storm'
release = '1.0.8'

extensions = [
    'matplotlib.sphinxext.plot_directive',
    'IPython.sphinxext.ipython_directive',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary', 
    'sphinx.ext.coverage', 
    'sphinx.ext.mathjax',
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram',
    'sphinx.ext.napoleon',
    'matplotlib.sphinxext.plot_directive',    
    'numpydoc',  # handle NumPy documentation formatted docstrings]
    'nbsphinx',
]

#napoleon_numpy_docstring = True

source_suffix = ['.rst', '.ipynb']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store',
    'examples/.ipynb_checkpoints',
    'articles/.ipynb_checkpoints',
    'examples/Index.ipynb'
]

nbsphinx_input_prompt = '%s'
nbsphinx_output_prompt = '%s'

napoleon_numpy_docstring = True
napoleon_google_docstring = False
#napoleon_use_param = False
#napoleon_use_ivar = True

#autosummary_generate = True
master_doc = 'index'

suppress_warnings = [
    "nbsphinx.ipykernel",
]

# matplotlib plot directive
plot_include_source = True
plot_formats = [("png", 90)]
plot_html_show_formats = False
plot_html_show_source_link = False

# plot_pre_code = """
# import numpy as np
# import pandas as pd
# import hotstepper as hs
# from hotstepper import Step, Steps
# import matplotlib.pyplot as plt
# """

## Generate autodoc stubs with summaries from code
autosummary_generate = True
autoclass_content = 'class'
# -- Options for HTML output -------------------------------------------------
html_title = 'Hydralit'
html_theme = 'sphinx_material'

html_theme_options = {

    # Set the name of the project to appear in the navigation.
    'nav_title': 'Hydralit',

    # Set the color and the accent color
    'color_primary': 'indigo',
    'color_accent': 'deep-purple',


    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 1,
    # If False, expand all TOC entries
    'globaltoc_collapse': False,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,
}

html_logo = 'images/hydra.png'


html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}