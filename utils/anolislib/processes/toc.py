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

from lxml import etree
from copy import deepcopy

from anolislib import utils
from anolislib.processes import outliner

# These are just the non-interactive elements to be removed
remove_elements_from_toc = frozenset([u"dfn", ])
# These are, however, all the attributes to be removed
remove_attributes_from_toc = frozenset([u"id", ])


class toc(object):
    """Build and add TOC."""

    toc = None

    def __init__(self, ElementTree, **kwargs):
        self.toc = etree.Element(u"ol", {u"class": u"toc"})
        self.buildToc(ElementTree, **kwargs)
        self.addToc(ElementTree, **kwargs)

    def buildToc(self, ElementTree, min_depth=2, max_depth=6, w3c_compat=False,
                 w3c_compat_class_toc=False, **kwargs):
        # Build the outline of the document
        outline_creator = outliner.Outliner(ElementTree, **kwargs)
        outline = outline_creator.build(**kwargs)

        # Get a list of all the top level sections, and their depth (0)
        sections = [(section, 0) for section in reversed(outline)]

        # Numbering
        num = []

        # Loop over all sections in a DFS
        while sections:
            # Get the section and depth at the end of list
            section, depth = sections.pop()

            # If we have a header, regardless of how deep we are
            if section.header is not None:
                # Get the element that represents the section header's text
                if section.header.tag == u"hgroup":
                    i = 1
                    while i <= 6:
                        header_text = section.header.find(u".//h" + unicode(i))
                        if header_text is not None:
                            break
                        i += 1
                    else:
                        header_text = None
                else:
                    header_text = section.header
            else:
                header_text = None

            # If we have a section heading text element, regardless of depth
            if header_text is not None:
                # Remove any existing number
                for element in header_text.findall(u".//span"):
                    if utils.elementHasClass(element, u"secno"):
                        # Copy content, to prepare for the node being
                        # removed
                        utils.copyContentForRemoval(element, text=False,
                                                    children=False)
                        # Remove the element (we can do this as we're not
                        # iterating over the elements, but over a list)
                        element.getparent().remove(element)

            # Check we're in the valid depth range (min/max_depth are 1 based,
            # depth is 0 based)
            if depth >= min_depth - 1 and depth <= max_depth - 1:
                # Calculate the corrected depth (i.e., the actual depth within
                # the numbering/TOC)
                corrected_depth = depth - min_depth + 1

                # Numbering:
                # No children, no sibling, move back to parent's sibling
                if corrected_depth + 1 < len(num):
                    del num[corrected_depth + 1:]
                # Children
                elif corrected_depth == len(num):
                    num.append(0)

                # Increment the current section's number
                if header_text is not None and \
                   not utils.elementHasClass(header_text, u"no-num") or \
                   header_text is None and section:
                    num[-1] += 1

                # Get the current TOC section for this depth, and add another
                # item to it
                if header_text is not None and \
                   not utils.elementHasClass(header_text, u"no-toc") or \
                   header_text is None and section:
                    # Find the appropriate section of the TOC
                    i = 0
                    toc_section = self.toc
                    while i < corrected_depth:
                        try:
                            # If the final li has no children, or the last
                            # children isn't an ol element
                            if len(toc_section[-1]) == 0 or \
                               toc_section[-1][-1].tag != u"ol":
                                toc_section[-1].append(etree.Element(u"ol"))
                                self.indentNode(toc_section[-1][-1],
                                                (i + 1) * 2, **kwargs)
                                if w3c_compat or w3c_compat_class_toc:
                                    toc_section[-1][-1].set(u"class", u"toc")
                        except IndexError:
                            # If the current ol has no li in it
                            toc_section.append(etree.Element(u"li"))
                            self.indentNode(toc_section[0], (i + 1) * 2 - 1,
                                            **kwargs)
                            toc_section[0].append(etree.Element(u"ol"))
                            self.indentNode(toc_section[0][0], (i + 1) * 2,
                                            **kwargs)
                            if w3c_compat or w3c_compat_class_toc:
                                toc_section[0][0].set(u"class", u"toc")
                        # TOC Section is now the final child (ol) of the final
                        # item (li) in the previous section
                        assert toc_section[-1].tag == u"li"
                        assert toc_section[-1][-1].tag == u"ol"
                        toc_section = toc_section[-1][-1]
                        i += 1
                    # Add the current item to the TOC
                    item = etree.Element(u"li")
                    toc_section.append(item)
                    self.indentNode(item, (i + 1) * 2 - 1, **kwargs)

                # If we have a header
                if header_text is not None:
                    # Add ID to header
                    id = utils.generateID(header_text, **kwargs)
                    if header_text.get(u"id") is not None:
                        del header_text.attrib[u"id"]
                    section.header.set(u"id", id)

                    # Add number, if @class doesn't contain no-num
                    if not utils.elementHasClass(header_text, u"no-num"):
                        header_text[0:0] = [etree.Element(u"span", {u"class":
                                                                    u"secno"})]
                        header_text[0].tail = header_text.text
                        header_text.text = None
                        header_text[0].text = u".".join(map(unicode, num))
                        header_text[0].text += u" "
                    # Add to TOC, if @class doesn't contain no-toc
                    if not utils.elementHasClass(header_text, u"no-toc"):
                        link = deepcopy(header_text)
                        item.append(link)
                        # Make it link to the header
                        link.tag = u"a"
                        link.set(u"href", u"#" + id)
                        # Remove interactive content child elements
                        utils.removeInteractiveContentChildren(link)
                        # Remove other child elements
                        for element_name in remove_elements_from_toc:
                            # Iterate over all the desendants of the new link
                            # with that element name
                            for element in link.findall(u".//" + element_name):
                                # Copy content, to prepare for the node being
                                # removed
                                utils.copyContentForRemoval(element)
                                # Remove the element (we can do this as we're
                                # not iterating over the elements, but over a
                                # list)
                                element.getparent().remove(element)
                        # Remove unwanted attributes
                        for element in link.iter(tag=etree.Element):
                            for attribute_name in remove_attributes_from_toc:
                                if element.get(attribute_name) is not None:
                                    del element.attrib[attribute_name]
                        # We don't want the old tail
                        link.tail = None
                        # Check we haven't changed the content in all of that
                        assert utils.textContent(header_text) == \
                               utils.textContent(link)
            # Add subsections in reverse order (so the next one is executed
            # next) with a higher depth value
            sections.extend([(child_section, depth + 1)
                             for child_section in reversed(section)])

    def addToc(self, ElementTree, **kwargs):
        to_remove = set()
        in_toc = False
        for node in ElementTree.iter():
            if in_toc:
                if node.tag is etree.Comment and \
                   node.text.strip(utils.spaceCharacters) == u"end-toc":
                    if node.getparent() is not toc_parent:
                        raise DifferentParentException(u"begin-toc and end-toc have different parents")
                    in_toc = False
                else:
                    to_remove.add(node)
            elif node.tag is etree.Comment:
                if node.text.strip(utils.spaceCharacters) == u"begin-toc":
                    toc_parent = node.getparent()
                    in_toc = True
                    node.tail = None
                    node.addnext(deepcopy(self.toc))
                    self.indentNode(node.getnext(), 0, **kwargs)
                elif node.text.strip(utils.spaceCharacters) == u"toc":
                    node.addprevious(etree.Comment(u"begin-toc"))
                    self.indentNode(node.getprevious(), 0, **kwargs)
                    node.addprevious(deepcopy(self.toc))
                    self.indentNode(node.getprevious(), 0, **kwargs)
                    node.addprevious(etree.Comment(u"end-toc"))
                    self.indentNode(node.getprevious(), 0, **kwargs)
                    node.getprevious().tail = node.tail
                    to_remove.add(node)
        for node in to_remove:
            node.getparent().remove(node)

    def indentNode(self, node, indent=0, newline_char=u"\n", indent_char=u" ",
                   **kwargs):
        whitespace = newline_char + indent_char * indent
        if node.getprevious() is not None:
            if node.getprevious().tail is None:
                node.getprevious().tail = whitespace
            else:
                node.getprevious().tail += whitespace
        else:
            if node.getparent().text is None:
                node.getparent().text = whitespace
            else:
                node.getparent().text += whitespace


class DifferentParentException(utils.AnolisException):
    """begin-toc and end-toc do not have the same parent."""
    pass
