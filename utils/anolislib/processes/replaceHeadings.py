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

from anolislib import utils
from anolislib.processes import outliner

numered_headings = frozenset([u"h1", u"h2", u"h3", u"h4", u"h5", u"h6"])


class replaceHeadings(object):
    """Replace numeric headings with the numeric headings appropriate for their
       depth."""

    def __init__(self, ElementTree, **kwargs):
        self.replaceHeadings(ElementTree, **kwargs)

    def replaceHeadings(self, ElementTree, **kwargs):
        # Build the outline of the document
        outline_creator = outliner.Outliner(ElementTree, **kwargs)
        outline = outline_creator.build(**kwargs)

        # Get a list of all the top level sections, and their depth (1)
        sections = [(section, 1) for section in reversed(outline)]

        # Loop over all sections in a DFS
        while sections:
            # Get the section and depth at the end of list
            section, depth = sections.pop()

            # If we have a header, regardless of how deep we are
            if section.header is not None and section.header.tag in \
                                              numered_headings:
                if depth <= 6:
                    section.header.tag = u"h" + unicode(depth)
                else:
                    raise TooDeepException(u"Too deep for numbered headers")
            
            # Add subsections in reverse order (so the next one is executed
            # next) with a higher depth value
            sections.extend([(child_section, depth + 1)
                             for child_section in reversed(section)])


class TooDeepException(utils.AnolisException):
    """That's real deep. But we only have six levels of numbered headers."""
    pass
