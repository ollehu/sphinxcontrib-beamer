from sphinx.util import logging

from .builder import BeamerBuilder
from .directive import BeamerDirective

logger = logging.getLogger(__name__)

def setup(app):
    # Initialize logger.
    logger.info("Initializing Beamer Builder")

    # Register builder.
    app.add_builder(BeamerBuilder)
    # Register directive.
    app.add_directive("beamer", BeamerDirective)

    # Add fake option to test functionality.
    add.add_config_value("option_1", True, "env")

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
