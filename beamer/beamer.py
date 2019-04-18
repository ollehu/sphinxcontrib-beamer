"""Sphinxextension for Beamer.

Outputs a Beamer LaTeX file.
"""

from os import path
from sphinx import addnodes
from sphinx.builders.latex import LaTeXBuilder
from sphinx.writers.latex import LaTeXTranslator
from sphinx.util.template import SphinxRenderer

import docutils
from docutils import nodes

import pudb

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
        self.elements["beamer_theme"] = builder.config_options["beamer_theme"]
        self.section_levels = [
            r"\begin{frame}",
            r"\subsection",
            r"\subsubsection",
        ]
        self.elements["allowframebreaks"] = \
            builder.config_options["allowframebreaks"]
        self.in_open_frame = 0

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

        # Get saturated node depth and append section level.
        node_depth = min(node["depth"], len(self.section_levels) - 1)
        self.body.append(self.section_levels[node_depth])

        # Set up options.
        options = []
        if self.elements["allowframebreaks"]:
            options.append("allowframebreaks")
        if node["verbatim"]:
            options.append("fragile")

        # If frame environment, add options.
        if node_depth == 0:
            self.in_open_frame = 1
            if options:
                self.body.append("[" + ", ".join(options) + "]")

        # Close environments.
        self.body.append(r"{")
        self.context.append(r"}\n")
        self.in_title = 1

    def depart_title(self, node):
        """Append with closing bracket."""

        self.body.append("}\n")
        self.in_title = 0

    def visit_close_environment_node(self, node):
        """Replace with end frame."""
        if self.in_open_frame:
            self.body.append(r"\end{frame}")
            self.in_open_frame = 0

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
    config_options = {}

    def init(self):
        self.default_translator_class = BeamerTranslator
        super(BeamerBuilder, self).init()
        self.config_options["allowframebreaks"] = \
            self.config.beamer_allowframebreaks
        self.config_options["beamer_theme"] = \
            self.config.beamer_theme

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

        close_node = CloseEnvironment()

        section_handled = False
        for node in section.traverse(docutils.nodes.compound):
            for node_class in node["classes"]:
                if node_class == "toctree-wrapper" and \
                    not isinstance(node[0], CloseEnvironment):
                    section_handled = True
                    node.insert(0, close_node)
                    break

        if section["depth"] == 0 and not section_handled:
            section.append(close_node)

def adjust_titles(app, doctree, docname):
    """Function which adjust titles. Chapters
    are kept as titles where CONTINUE..."""

    def traverse_parent(depth, node):
        """Recursively find depth of section node.
        This will always terminate as the top node
        is a document instance.
        """
        if not isinstance(node, docutils.nodes.section):
            return depth - 1
        return traverse_parent(depth + 1, node.parent)

    for section in doctree.traverse(docutils.nodes.section):
        # Calculate depth.
        depth = traverse_parent(0, section)
        section["depth"] = depth

        # Look for verbatim in root nodes.
        has_verbatim = False
        for node in section.traverse():
            if isinstance(node, docutils.nodes.literal_block) and depth == 0:
                has_verbatim = True
                break

        for title in section.traverse(docutils.nodes.title):
            title["depth"] = depth
            title["verbatim"] = has_verbatim

def setup(app):
    """Setup the Sphinx extension."""
    # Register builder.
    app.add_builder(BeamerBuilder)
    # Register close_environments node.
    app.add_node(CloseEnvironment,
                 beamer=(BeamerTranslator.visit_close_environment_node,
                         BeamerTranslator.depart_close_environment_node))
    # Add setting for allowframebreaks.
    app.add_config_value("beamer_allowframebreaks", True, "beamer")
    # Add setting for Beamer theme.
    app.add_config_value("beamer_theme", "Warsaw", "beamer")
    # Adjust titles upon doctree-resolved.
    app.connect("doctree-resolved", adjust_titles)
    # Connect close_environments.
    app.connect("doctree-resolved", close_environments)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
