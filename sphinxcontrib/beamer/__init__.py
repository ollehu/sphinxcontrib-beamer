"""
Sphinxextension for Beamer.
Outputs a Beamer LaTeX file.
"""

from os import path
from sphinx.builders.latex import LaTeXBuilder
from sphinx.writers.latex import LaTeXTranslator
from sphinx.util.template import SphinxRenderer

from docutils import nodes
import re


class BeamerTranslator(LaTeXTranslator):
    """
    Beamer translator class.
    Overloaded to define directives and render
    the correct template.
    """

    def __init__(self, document, builder):
        """
        Set up Beamer elements.
        """
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

    def astext(self):
        """
        Pass the Beamer template to the renderer.
        """
        self.elements.update({
            'body': u''.join(self.body),
            'indices': self.generate_indices()
        })
        return self.render('beamer.tex_t', self.elements)

    def render(self, template_name, variables):
        """
        Render Beamer using template.
        """
        template_dir = 'templates'
        template = path.join(path.dirname(path.abspath(__file__)),
                             template_dir, template_name)
        return BeamerRenderer(template_dir).render(template, variables)

    def visit_title(self, node):
        """
        Prepend titles with begin frame.
        Also, append options such as allowframebreaks and fragile.
        """
        # Calculate (saturated) node depth and check if previous frame should
        # be closed.
        node_depth = min(node["depth"], len(self.section_levels) - 1)
        if node_depth == 0 and not node["first_section"]:
            self.body.append(r"\end{frame}")
            self.body.append("\n\n")

        # Set up options.
        options = node["frame_options"]
        if self.elements["allowframebreaks"]:
            options.append("allowframebreaks")

        # If frame environment, add options.
        self.body.append(self.section_levels[node_depth])
        if node_depth == 0:
            if options:
                self.body.append("[" + ", ".join(options) + "]")

        # Close environments.
        self.body.append(r"{")
        self.context.append("}\n")

    def depart_title(self, node):
        """
        Append with closing bracket.
        """
        self.body.append("}\n")

    def depart_document(self, node):
        """
        Close document by closing last frame environment.
        """
        self.body.append(r"\end{frame}")


class BeamerRenderer(SphinxRenderer):
    """
    Beamer renderer.
    Overloaded to pass along the custom
    template path.
    """

    def __init__(self, template_path=""):
        # type: () -> None
        super(BeamerRenderer, self).__init__(template_path)

        # Use JSP/eRuby like tagging instead because of curly brackets -  the
        # default tagging of jinja2 is not good for LaTeX sources.
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


def adjust_titles(_app, doctree, _docname):
    """Function which adjust titles. Chapters
    are kept as titles where CONTINUE..."""

    def calc_node_depth(depth, node):
        """
        Recursively find depth of a section node.
        This will always terminate as the top node
        is a document instance.
        """
        if not isinstance(node, nodes.section):
            return depth - 1
        return calc_node_depth(depth + 1, node.parent)

    def is_frame_option(node):
        return ("frame_options:" in node.astext()
                and isinstance(node, nodes.comment))

    first_section = True
    for section in doctree.traverse(nodes.section):
        # Calculate depth.
        depth = calc_node_depth(0, section)

        # Look for verbatim in root nodes.
        frame_options = []
        for node in section.traverse():
            if isinstance(node, nodes.literal_block) and depth == 0:
                frame_options.append('fragile')
                break

        for title in section.traverse(nodes.title):
            title["depth"] = depth
            title["first_section"] = first_section

            if depth == 0:
                for comment in section.traverse(condition=is_frame_option):
                    options = re.search("^frame_options:(.*$)",
                                         comment.astext()).groups()[0]
                    for opt in options.split(","):
                        if opt.strip() not in frame_options:
                            frame_options.append(opt.strip())
            title["frame_options"] = frame_options

        # First section covered.
        if first_section:
            first_section = False


def setup(app):
    """Setup the Sphinx extension."""
    # Register builder.
    app.add_builder(BeamerBuilder)

    # Add setting for allowframebreaks.
    app.add_config_value("beamer_allowframebreaks", True, "beamer")
    # Add setting for Beamer theme.
    app.add_config_value("beamer_theme", "Warsaw", "beamer")
    # Adjust titles upon doctree-resolved.
    app.connect("doctree-resolved", adjust_titles)

    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
