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
import time
from lxml import etree
from copy import deepcopy

from anolislib import utils

latest_version = re.compile(u"latest[%s]+version" % utils.spaceCharacters,
                            re.IGNORECASE)

w3c_tr_url_status = r"http://www\.w3\.org/TR/[^/]*/(MO|WD|CR|PR|REC|PER|NOTE)-"
w3c_tr_url_status = re.compile(w3c_tr_url_status)

year = re.compile(r"\[YEAR[^\]]*\]")
year_sub = time.strftime(u"%Y", time.gmtime())
year_identifier = u"[YEAR"

date = re.compile(r"\[DATE[^\]]*\]")
date_sub = time.strftime(u"%d %B %Y", time.gmtime()).lstrip(u"0")
date_identifier = u"[DATE"

cdate = re.compile(r"\[CDATE[^\]]*\]")
cdate_sub = time.strftime(u"%Y%m%d", time.gmtime())
cdate_identifier = u"[CDATE"

title = re.compile(r"\[TITLE[^\]]*\]")
title_identifier = u"[TITLE"

status = re.compile(r"\[STATUS[^\]]*\]")
status_identifier = u"[STATUS"

longstatus = re.compile(r"\[LONGSTATUS[^\]]*\]")
longstatus_identifier = u"[LONGSTATUS"
longstatus_map = {
    u"MO": u"W3C Member-only Draft",
    u"ED": u"Editor's Draft",
    u"WD": u"W3C Working Draft",
    u"CR": u"W3C Candidate Recommendation",
    u"PR": u"W3C Proposed Recommendation",
    u"REC": u"W3C Recommendation",
    u"PER": u"W3C Proposed Edited Recommendation",
    u"NOTE": u"W3C Working Group Note"
}

w3c_stylesheet = re.compile(r"http://www\.w3\.org/StyleSheets/TR/W3C-[A-Z]+")
w3c_stylesheet_identifier = u"http://www.w3.org/StyleSheets/TR/W3C-"

string_subs = ((year, year_sub, year_identifier),
               (date, date_sub, date_identifier),
               (cdate, cdate_sub, cdate_identifier))

logo = u"logo"
logo_sub = etree.fromstring(u'<p><a href="http://www.w3.org/"><img alt="W3C" src="http://www.w3.org/Icons/w3c_home"/></a></p>')

copyright = u"copyright"
copyright_sub = etree.fromstring(u'<p class="copyright"><a href="http://www.w3.org/Consortium/Legal/ipr-notice#Copyright">Copyright</a> &#xA9; %s <a href="http://www.w3.org/"><acronym title="World Wide Web Consortium">W3C</acronym></a><sup>&#xAE;</sup> (<a href="http://www.csail.mit.edu/"><acronym title="Massachusetts Institute of Technology">MIT</acronym></a>, <a href="http://www.ercim.org/"><acronym title="European Research Consortium for Informatics and Mathematics">ERCIM</acronym></a>, <a href="http://www.keio.ac.jp/">Keio</a>), All Rights Reserved. W3C <a href="http://www.w3.org/Consortium/Legal/ipr-notice#Legal_Disclaimer">liability</a>, <a href="http://www.w3.org/Consortium/Legal/ipr-notice#W3C_Trademarks">trademark</a> and <a href="http://www.w3.org/Consortium/Legal/copyright-documents">document use</a> rules apply.</p>' % time.strftime(u"%Y", time.gmtime()))

basic_comment_subs = ()


class sub(object):
    """Perform substitutions."""

    def __init__(self, ElementTree, w3c_compat=False,
                 w3c_compat_substitutions=False,
                 w3c_compat_crazy_substitutions=False, **kwargs):
        if w3c_compat or w3c_compat_substitutions or \
           w3c_compat_crazy_substitutions:
            self.w3c_status = self.getW3CStatus(ElementTree, **kwargs)
        self.stringSubstitutions(ElementTree, w3c_compat,
                                 w3c_compat_substitutions,
                                 w3c_compat_crazy_substitutions, **kwargs)
        self.commentSubstitutions(ElementTree, w3c_compat,
                                  w3c_compat_substitutions,
                                  w3c_compat_crazy_substitutions, **kwargs)

    def stringSubstitutions(self, ElementTree, w3c_compat=False,
                            w3c_compat_substitutions=False,
                            w3c_compat_crazy_substitutions=False, **kwargs):
        # Get doc_title from the title element
        try:
            doc_title = utils.textContent(ElementTree.getroot().find(u"head")
                                                               .find(u"title"))
        except (AttributeError, TypeError):
            doc_title = u""

        if w3c_compat or w3c_compat_substitutions:
            # Get the right long status
            doc_longstatus = longstatus_map[self.w3c_status]

        if w3c_compat_crazy_substitutions:
            # Get the right stylesheet
            doc_w3c_stylesheet = u"http://www.w3.org/StyleSheets/TR/W3C-" + \
                                 self.w3c_status

        # Get all the subs we want
        instance_string_subs = string_subs + \
                               ((title, doc_title, title_identifier), )

        # And even more in compat. mode
        if w3c_compat or w3c_compat_substitutions:
            instance_string_subs += ((status, self.w3c_status,
                                      status_identifier),
                                     (longstatus, doc_longstatus,
                                      longstatus_identifier))

        # And more that aren't even enabled by default in compat. mode
        if w3c_compat_crazy_substitutions:
            instance_string_subs += ((w3c_stylesheet, doc_w3c_stylesheet,
                                      w3c_stylesheet_identifier), )

        for node in ElementTree.iter():
            for regex, sub, identifier in instance_string_subs:
                if node.text is not None and identifier in node.text:
                    node.text = regex.sub(sub, node.text)
                if node.tail is not None and identifier in node.tail:
                    node.tail = regex.sub(sub, node.tail)
                for name, value in node.attrib.items():
                    if identifier in value:
                        node.attrib[name] = regex.sub(sub, value)

    def commentSubstitutions(self, ElementTree, w3c_compat=False, \
                             w3c_compat_substitutions=False,
                             w3c_compat_crazy_substitutions=False, **kwargs):
        # Basic substitutions
        instance_basic_comment_subs = basic_comment_subs

        # Add more basic substitutions in compat. mode
        if w3c_compat or w3c_compat_substitutions:
            instance_basic_comment_subs += ((logo, logo_sub),
                                            (copyright, copyright_sub))

        # Set of nodes to remove
        to_remove = set()

        # Link
        in_link = False
        for node in ElementTree.iter():
            if in_link:
                if node.tag is etree.Comment and \
                   node.text.strip(utils.spaceCharacters) == u"end-link":
                    if node.getparent() is not link_parent:
                        raise DifferentParentException(u"begin-link and end-link have different parents")
                    utils.removeInteractiveContentChildren(link)
                    link.set(u"href", utils.textContent(link))
                    in_link = False
                else:
                    if node.getparent() is link_parent:
                        link.append(deepcopy(node))
                    to_remove.add(node)
            elif node.tag is etree.Comment and \
                 node.text.strip(utils.spaceCharacters) == u"begin-link":
                link_parent = node.getparent()
                in_link = True
                link = etree.Element(u"a")
                link.text = node.tail
                node.tail = None
                node.addnext(link)

        # Basic substitutions
        for comment, sub in instance_basic_comment_subs:
            begin_sub = u"begin-" + comment
            end_sub = u"end-" + comment
            in_sub = False
            for node in ElementTree.iter():
                if in_sub:
                    if node.tag is etree.Comment and \
                       node.text.strip(utils.spaceCharacters) == end_sub:
                        if node.getparent() is not sub_parent:
                            raise DifferentParentException(u"%s and %s have different parents" % begin_sub, end_sub)
                        in_sub = False
                    else:
                        to_remove.add(node)
                elif node.tag is etree.Comment:
                    if node.text.strip(utils.spaceCharacters) == begin_sub:
                        sub_parent = node.getparent()
                        in_sub = True
                        node.tail = None
                        node.addnext(deepcopy(sub))
                    elif node.text.strip(utils.spaceCharacters) == comment:
                        node.addprevious(etree.Comment(begin_sub))
                        node.addprevious(deepcopy(sub))
                        node.addprevious(etree.Comment(end_sub))
                        node.getprevious().tail = node.tail
                        to_remove.add(node)

        # Remove nodes
        for node in to_remove:
            node.getparent().remove(node)

    def getW3CStatus(self, ElementTree, **kwargs):
        # Get all text nodes that contain case-insensitively "latest version"
        # with any amount of whitespace inside the phrase, or contain
        # http://www.w3.org/TR/
        for text in ElementTree.xpath(u"//text()[contains(translate(., 'LATEST', 'latest'), 'latest') and contains(translate(., 'VERSION', 'version'), 'version') or contains(., 'http://www.w3.org/TR/')]"):
            if latest_version.search(text):
                return u"ED"
            elif w3c_tr_url_status.search(text):
                return w3c_tr_url_status.search(text).group(1)
        # Didn't find any status, return the default (ED)
        else:
            return u"ED"


class DifferentParentException(utils.AnolisException):
    """begin-link and end-link do not have the same parent."""
    pass
