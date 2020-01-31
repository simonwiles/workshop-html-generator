#!/usr/bin/env python3

""" gen_html.py
    Module Description
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from mako.lookup import TemplateLookup
from mako.template import Template
import markdown
from markdown.extensions.toc import TocExtension
from tidylib import tidy_document


def get_git_revision(working_dir):
    """ Return the git commit hash of the current revision, or False
        if the file is not under a git repo. """

    try:
        return subprocess.check_output(
            "git describe --always".split(),
            cwd=working_dir,
            universal_newlines=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return False


def render_html(template_fn, template_vars):

    mytemplate = Template(
        filename=template_fn, lookup=TemplateLookup(directories=["./"])
    )
    document, errors = tidy_document(
        mytemplate.render(**template_vars),
        # http://api.html-tidy.org/tidy/quickref_5.2.0.html
        options={"wrap": 100, "indent-spaces": 2, "doctype": "html5"},
    )

    print(document, file=sys.stdout)
    print(errors, file=sys.stderr)


def main():
    """ Command-line entry-point. """

    parser = argparse.ArgumentParser(description="Description: {}".format(__file__))

    parser.add_argument(
        "markdown_file",
        metavar="markdown-file",
        help="path/to/markdown/file/for/conversion.md",
    )
    parser.add_argument(
        "-t",
        "--template",
        action="store",
        required=True,
        help="path/to/your/template.html",
    )

    args = parser.parse_args()

    markdown_path = Path(args.markdown_file)
    title = markdown_path.stem.replace("_", " ")

    md = markdown.Markdown(
        extensions=["extra", TocExtension(permalink=True, anchorlink=True)],
        output_format="html5",
    )

    with markdown_path.open() as _fh:
        content = md.convert(_fh.read())

    template_vars = {
        "title": title,
        "content": content,
        "toc": md.toc,
        "modified": datetime.now().date().isoformat(),
        "revision": get_git_revision(markdown_path.parent),
    }

    render_html(args.template, template_vars)


if __name__ == "__main__":
    main()
