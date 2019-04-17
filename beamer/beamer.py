"""Sphinxextension for Beamer.

Outputs a Beamer LaTeX file.
"""

from os import path
from sphinx.builders.latex import LaTeXBuilder
from sphinx.writers.latex import LaTeXTranslator
from sphinx.util.template import SphinxRenderer

import docutils
from docutils import nodes

class BeamerTranslator(LaTeXTranslator):
    """Beamer translator class.
    Overloaded to define directives and render
    the correct template.
    """

    def __init__(self, document, builder):
        LaTeXTranslator.__init__(self, document, builder)
        self.elements["maketitle"] = r"\maketitle"
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
            if path.exists(template):
                return BeamerRenderer(template_dir).render(template, variables)

        return BeamerRenderer().render(template_name, variables)

    def visit_title(self, node):
        """Prepend with begin frame."""

        self.body.append(r"\begin{frame}{")
        self.context.append("}\n" + self.hypertarget_to(node.parent))
        self.in_title = 1

    def depart_title(self, node):
        """Append with closing bracket."""

        self.body.append("}\n")
        self.in_title = 0

    def visit_close_environment_node(self, node):
        """Replace with end frame."""
        self.body.append(r"\end{frame}")

    def depart_close_environment_node(self, node):
        """Do nothing."""
        pass


class BeamerRenderer(SphinxRenderer):
    """Beamer renderer.
    Overloaded to pass along the custom
    template path.
    """

    def __init__(self, template_path=""):
        # type: () -> None
        super(BeamerRenderer, self).__init__(template_path)

        # use JSP/eRuby like tagging instead because curly bracket; the default
        # tagging of jinja2 is not good for LaTeX sources.
        self.env.variable_start_string = '<%='
        self.env.variable_end_string = '%>'
        self.env.block_start_string = '<%'
        self.env.block_end_string = '%>'

class BeamerBuilder(LaTeXBuilder):
    """Builder for LaTeX Beamer.
    Overloaded to load the custom translator.
    """

    name = "beamer"
    format = "latex"

    def init(self):
        self.default_translator_class = BeamerTranslator
        super(BeamerBuilder, self).init()

class CloseEnvironment(nodes.Admonition, nodes.Element):
    """Empty environment.
    Defined to be used with close_environments.
    Closes LaTeX frame environments.
    """

    pass


def close_environments(app, doctree, docname):
    """Function connected to doctree-resolved.
    Appens each section with a CloseEnvironment
    node, which later is replaced with end frame.
    """

    for section in doctree.traverse(docutils.nodes.section):
        node = CloseEnvironment()
        section.append(node)

def setup(app):
    """Setup the Sphinx extension."""
    # Register builder.
    app.add_builder(BeamerBuilder)
    # Register close_environments node.
    app.add_node(CloseEnvironment,
                 beamer=(BeamerTranslator.visit_close_environment_node,
                         BeamerTranslator.depart_close_environment_node))
    # Connect close_environments.
    app.connect("doctree-resolved", close_environments)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

"""
    TODO
        * Replace subsections with bold, or something
          subsection-looking in beamer. Not with a new frame.
        * Use the NIRA Beamer template.

       (* Solve the highlightning warning?)
       (* Solve the PyLint warnings?)
"""
