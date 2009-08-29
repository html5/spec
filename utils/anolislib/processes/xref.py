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

import re
from lxml import etree
from copy import deepcopy

from anolislib import utils

instance_elements = frozenset([u"span", u"abbr", u"code", u"var", u"i"])
w3c_instance_elements = frozenset([u"abbr", u"acronym", u"b", u"bdo", u"big",
                                   u"code", u"del", u"em", u"i", u"ins",
                                   u"kbd", u"label", u"legend", u"q", u"samp",
                                   u"small", u"span", u"strong", u"sub",
                                   u"sup", u"tt", u"var"])

# Instances cannot be in the stack with any of these element, or with
# interactive elements
instance_not_in_stack_with = frozenset([u"dfn", ])

non_alphanumeric_spaces = re.compile(r"[^a-zA-Z0-9 \-]+")


class xref(object):
    """Add cross-references."""

    def __init__(self, ElementTree, **kwargs):
        self.dfns = {}
        self.buildReferences(ElementTree, **kwargs)
        self.addReferences(ElementTree, **kwargs)

    def buildReferences(self, ElementTree, allow_duplicate_dfns=False,
                        **kwargs):
        for dfn in ElementTree.iter(u"dfn"):
            term = self.getTerm(dfn, **kwargs)

            if len(term) > 0:
                if not allow_duplicate_dfns and term in self.dfns:
                    raise DuplicateDfnException(u'The term "%s" is defined more than once' % term)

                link_to = dfn

                for parent_element in dfn.iterancestors(tag=etree.Element):
                    if parent_element.tag in utils.heading_content:
                        link_to = parent_element
                        break

                id = utils.generateID(link_to, **kwargs)

                link_to.set(u"id", id)

                self.dfns[term] = id

    def addReferences(self, ElementTree, w3c_compat=False,
                      w3c_compat_xref_elements=False,
                      w3c_compat_xref_a_placement=False, **kwargs):
        for element in ElementTree.iter(tag=etree.Element):
            if element.tag in instance_elements or \
               (w3c_compat or w3c_compat_xref_elements) and \
               element.tag in w3c_instance_elements:
                term = self.getTerm(element, w3c_compat=w3c_compat, **kwargs)

                if term in self.dfns:
                    goodParentingAndChildren = True

                    for parent_element in \
                        element.iterancestors(tag=etree.Element):
                        if (parent_element.tag in instance_not_in_stack_with or
                            utils.isInteractiveContent(parent_element)):
                            goodParentingAndChildren = False
                            break
                    else:
                        for child_element in \
                            element.iterdescendants(tag=etree.Element):
                            if child_element.tag in instance_not_in_stack_with\
                               or utils.isInteractiveContent(child_element):
                                goodParentingAndChildren = False
                                break

                    if goodParentingAndChildren:
                        if element.tag == u"span":
                            element.tag = u"a"
                            element.set(u"href", u"#" + self.dfns[term])
                        else:
                            link = etree.Element(u"a",
                                                 {u"href":
                                                  u"#" + self.dfns[term]})
                            if w3c_compat or w3c_compat_xref_a_placement:
                                for node in element:
                                    link.append(node)
                                link.text = element.text
                                element.text = None
                                element.append(link)
                            else:
                                element.addprevious(link)
                                link.append(element)
                                link.tail = link[0].tail
                                link[0].tail = None

    def getTerm(self, element, w3c_compat=False,
                w3c_compat_xref_normalization=False, **kwargs):
        if element.get(u"data-anolis-xref") is not None:
            term = element.get(u"data-anolis-xref")
        elif element.get(u"title") is not None:
            term = element.get(u"title")
        else:
            term = utils.textContent(element)

        term = term.strip(utils.spaceCharacters).lower()

        term = utils.spacesRegex.sub(u" ", term)

        if w3c_compat or w3c_compat_xref_normalization:
            term = non_alphanumeric_spaces.sub(u"", term)

        return term


class DuplicateDfnException(utils.AnolisException):
    """Term already defined."""
    pass
