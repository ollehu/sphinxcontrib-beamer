import os
from os import path
from sphinx.locale import _,__
from sphinx import package_dir, addnodes, highlighting
from sphinx.util import logging
from sphinx.builders.latex import LaTeXBuilder
from sphinx.writers.latex import LaTeXTranslator
from sphinx.util import logging
from docutils.parsers.rst import Directive
from docutils.frontend import OptionParser
from sphinx.util.docutils import SphinxFileOutput
from sphinx.util.template import SphinxRenderer

logger = logging.getLogger(__name__)

template_path = ""

class BeamerTranslator(LaTeXTranslator):

    def __init__(self, document, builder):
        LaTeXTranslator.__init__(self, document, builder)
        self.elements["maketitle"] = "\maketitle"
        self.elements["makeindex"] = ""
        self.elements["printindex"] = ""
        self.elements["tableofcontents"] = ""
        self.elements["wrapperclass"] = "beamer"

    def astext(self):
        # type: () -> unicode
        self.elements.update({
            'body': u''.join(self.body),
            'indices': self.generate_indices()
        })
        return self.render('beamer.tex_t', self.elements)

    def render(self, template_name, variables):
        # type: (unicode, Dict) -> unicode

        for template_dir in self.builder.config.templates_path:
            template = path.join(self.builder.confdir, template_dir,
                                 template_name)
            template_path = template_dir

            if path.exists(template):
                return BeamerRenderer(template_dir).render(template, variables)

        return BeamerRenderer().render(template_name, variables)

    def visit_title(self, node):
        self.body.append(r"\begin{frame}{")
        self.context.append("}\n" + self.hypertarget_to(node.parent))
        self.in_title = 1

    def depart_title(self, node):
        self.body.append("}\n")
        self.in_title = 0


class BeamerRenderer(SphinxRenderer):
    def __init__(self, template_path=""):
        # type: () -> None
        #template_path = os.path.join(self.builder.config.templates_path)
        super(BeamerRenderer, self).__init__(template_path)

        # use JSP/eRuby like tagging instead because curly bracket; the default
        # tagging of jinja2 is not good for LaTeX sources.
        self.env.variable_start_string = '<%='
        self.env.variable_end_string = '%>'
        self.env.block_start_string = '<%'
        self.env.block_end_string = '%>'


class BeamerDirective(Directive):
    pass


class BeamerBuilder(LaTeXBuilder):
    """Builder for LaTeX Beamer.
    """
    name = "beamer"
    format = "latex"

    def init(self):
        self.default_translator_class = BeamerTranslator
        super(BeamerBuilder, self).init()


def setup(app):
    # Initialize logger.
    logger.info("Initializing Beamer Builder")

    # Register builder.
    app.add_builder(BeamerBuilder)
    # Register directive.
    app.add_directive("beamer", BeamerDirective)

    # Add fake option to test functionality.
    app.add_config_value("option_1", True, "env")

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

""" This needs to be done for 'make beamer' to compile:
        * Insert
            \newcommand{\paragraph}{}
            \newcommand{\subparagraph}{}
          in the pre-ample. For titlesec compability.
        * Replace sphinxmaketitle with maketitle for footnote
          compability.
        * Replace the documentclass to beamer.
        * Replace \chapter{#1} with
            \begin{frame}{#1}
                ...
            \end{frame}
        * Remove 'Indices and tables' all together.
        * Don't print indices.
        * Don't print table of contents.
        * Don't print \pagestyle{normal}.
"""
