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
from mako.runtime import capture
from mako.template import Template
import markdown
from markdown.extensions.toc import TocExtension
from rcssmin import cssmin
from tidylib import tidy_document


def css(fn):
    """ Decorator to minify blocks of CSS. """

    def decorate(context, *args, **kwargs):
        css_block = capture(context, fn, *args, **kwargs).strip()
        context.write(cssmin(css_block))

    return decorate


def get_git_revision_for_file(file_path: Path):
    """ Return the git commit hash of the last commit to touch file_path, or False
        if the file is not under a git repo. """

    try:
        return subprocess.check_output(
            "git log -n 1 --pretty=format:%h --".split() + [file_path.name],
            cwd=str(file_path.parent),
            universal_newlines=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return False


def render_html(template_fn, template_vars):

    template_path = Path(template_fn).resolve()
    mytemplate = Template(
        filename=str(template_path),
        lookup=TemplateLookup(
            directories=[str(template_path.parent)], input_encoding="utf-8"
        ),
        imports=["from typogrify.filters import typogrify", "from gen_html import css"],
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
        "revision": get_git_revision_for_file(markdown_path),
    }

    render_html(args.template, template_vars)


if __name__ == "__main__":
    main()
