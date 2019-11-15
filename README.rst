==========================================
Description of the Beamer Sphinx Extension
==========================================

This extension to `Sphinx <https://www.sphinx-doc.org/en/master/>`__ adds a
`Builder <https://www.sphinx-doc.org/en/master/usage/builders/index.html>`__ for
the `Beamer <https://ctan.org/pkg/beamer>`__ LaTeX class.

Installation
============
The extension is distributed through the Python Package Index and installed with

.. code-block::

   pip install sphinxcontrib-beamer

Usage
=====
Load the extension in the Sphinx project configuration file ``conf.py``::

   extensions = ['sphinxcontrib.beamer']

and build your Beamer LaTeX output using the new builder::

   sphinx-build -b beamer build/doctrees . build

Configuration
-------------
Some variables are configurable in ``conf.py``:

**Theming:** Change the theme used by Beamer (defaults to ``Warsaw``) with::

   beamer_theme = <string>

where ``beamertheme<string>.sty`` is a LaTeX style file in the
``templates_path`` path specified in ``conf.py``.

**Frame breaks:** Change if frame breaks are allowed (defaults to True) with::

   beamer_allowframebreaks = <True or False>

which sets the ``allowframebreaks`` option to all frames. This Beamer feature
splits a frame environment into multiple slides if the content extends beyond
what can be viewed on one slide.

**Custom frame options:** Add custom frame options with

.. code-block::

   Frame Title
   -----------
   .. frame_options:plain

   Frame content.

which will generate a frame environment

.. code-block::

   \begin{frame}[plain]{Frame Title}

      Frame content.

   \end{frame}

``plain`` in the example above can be replaced with any comma-separated string
of valid frame options.

**This extension is still in its beta stage and has not been thorougly tested.
Use it with caution.**
