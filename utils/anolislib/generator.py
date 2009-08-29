# coding=UTF-8
# Copyright (c) 2008 Geoffrey Sneddon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys

import html5lib
from html5lib import treebuilders, treewalkers
from html5lib.serializer import htmlserializer

import lxml.html
from lxml import etree


def process(tree, processes=["sub", "toc", "xref"], **kwargs):
    """ Process the given tree. """

    # Find number of passes to do
    for process in processes:
        try:
            process_module = getattr(__import__('processes', globals(),
                                                locals(), [process], -1),
                                    process)
        except AttributeError:
            process_module = __import__(process, globals(), locals(), [], -1)

        getattr(process_module, process)(tree, **kwargs)


def fromFile(input, processes=set(["sub", "toc", "xref"]), parser="html5lib",
             profile=False, **kwargs):
    # Parse as XML:
    #if parser == "lxml.etree":
    if False:
        tree = etree.parse(input)
    # Parse as HTML using lxml.html
    elif parser == "lxml.html":
        tree = lxml.html.parse(input)
    # Parse as HTML using html5lib
    else:
        builder = treebuilders.getTreeBuilder("lxml", etree)
        parser = html5lib.HTMLParser(tree=builder)
        tree = parser.parse(input)

    # Close the input file
    input.close()

    # Run the generator, and profile, or not, as the case may be
    if profile:
        import os
        import tempfile
        statfile = tempfile.mkstemp()[1]
        try:
            import cProfile
            import pstats
            cProfile.runctx("process(tree, processes, **kwargs)", globals(),
                            locals(), statfile)
            stats = pstats.Stats(statfile)
        except None:
            import hotshot
            import hotshot.stats
            prof = hotshot.Profile(statfile)
            prof.runcall(process, tree, processes, **kwargs)
            prof.close()
            stats = hotshot.stats.load(statfile)
        stats.strip_dirs()
        stats.sort_stats('time')
        stats.print_stats()
        os.remove(statfile)
    else:
        process(tree, processes, **kwargs)

    # Return the tree
    return tree


def toString(tree, output_encoding="utf-8", serializer="html5lib", **kwargs):
    # Serialize to XML
    #if serializer == "lxml.etree":
    if False:
        rendered = etree.tostring(tree, encoding=output_encoding)
    # Serialize to HTML using lxml.html
    elif serializer == "lxml.html":
        rendered = lxml.html.tostring(tree, encoding=output_encoding)
    # Serialize to HTML using html5lib
    else:
        walker = treewalkers.getTreeWalker("lxml")
        s = htmlserializer.HTMLSerializer(**kwargs)
        rendered = s.render(walker(tree), encoding=output_encoding)
    return rendered

def toFile(tree, output, output_encoding="utf-8", serializer="html5lib",
           **kwargs):
    rendered = toString(tree, output_encoding=output_encoding,
                        serializer=serializer, **kwargs)

    # Write to the output
    output.write(rendered)


def fromToFile(input, output, **kwargs):
    tree = fromFile(input, **kwargs)
    toFile(tree, output, **kwargs)
