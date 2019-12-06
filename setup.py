import os
from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()


setup(
    name="sphinxcontrib-beamer",
    version="0.0.1",
    author="Olle Hynén Ulfsjöö",
    author_email="ollehu@gmail.com",
    description="Beamer extension for Sphinx",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/ollehu/sphinxcontrib-beamer",
    package_data={'': [os.path.join('templates/beamer.tex_t')]},
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Documentation :: Sphinx",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["Sphinx"],
)
