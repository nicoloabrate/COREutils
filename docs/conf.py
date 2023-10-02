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
# print(sys.path)
sys.path.insert(0, os.path.abspath('..'))
# print(sys.path)

# -- readthedocs -------------------------------------------------------------
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'


# -- Project information -----------------------------------------------------

project = 'coreutils'
copyright = "2020, Nicolò Abrate"
author = "Nicolò Abrate"

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------
master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    # 'sphinxcontrib.bibtex',
    # 'sphinxcontrib.rsvgconverter',
    'sphinx_copybutton',
    'sphinx.ext.imgmath',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'matplotlib.sphinxext.plot_directive',
    'nbsphinx'
    # 'jupyter_sphinx.execute'
]

intersphinx_mapping = {'python': ('https://docs.python.org/3', None),
                       'numpy': ('https://docs.scipy.org/doc/numpy/', None),
                       'scipy': ('https://docs.scipy.org/doc/scipy/reference/', None),
                       'matplotlib': ('https://matplotlib.org/', None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
imgmath_use_preview = True
imgmath_image_format = 'svg'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

htmlhelp_basename = 'COREUTILSdoc'

# -- Options for nbsphinx
nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
    "--InlineBackend.rc={'figure.dpi': 150}"]

# import os
# os.environ['COREUTILS_PATH'] = os.path.abspath('../')
# print(os.environ['COREUTILS_PATH'])
# import coreutils