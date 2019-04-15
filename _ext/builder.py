"""Beamer builder extension for Sphinx.
"""

import os

from sphinx.builders.latex import LaTeXBuilder
from sphinx.util import logging


class BeamerBuilder(LaTeXBuilder):
    """Builder for LaTeX Beamer.
    """
    name = "beamer"
    format = "latex"

    def init(self):
        super(BeamerBuilder, self).init()
