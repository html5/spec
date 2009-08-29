from lxml import etree
import urlparse
import urllib2
from collections import defaultdict
import sys

statuses =   {"UNKNOWN": "Unknown",
              "TBW": "Idea; yet to be specified",
              "WIP": "Being edited right now",
              "OCBE": "Overcome by events",
              "FD": "First draft",
              "WD": "Working draft",
              "CWD": "Controversial Working Draft",
              "LC": "Last call for comments",
              "ATRISK": "Being considered for removal",
              "CR": "Awaiting implementation feedback",
              "REC": "Implemented and widely deployed",
              "SPLITFD": "Marked for extraction - First draft",
              "SPLIT": "Marked for extraction - Awaiting implementation feedback",
              "SPLITREC": "Marked for extraction - Implemented and widely deployed"}

url = 'http://www.whatwg.org/specs/web-apps/current-work/status.cgi?action=get-all-annotations'

w3c_statuses = ["WD", "LC", "CR", "PR", "REC"]

w3c_status_names = {"WD":"Working Draft",
                    "LC":"Last Call",
                    "CR":"Candidate Recommendation",
                    "PR":"Proposed Recommendation",
                    "REC":"W3C Recommendation"}


def annotate(ElementTree, **kwargs):
    if not "annotation" in kwargs or not  kwargs["annotation"]:
        return
    else:
        annotation_location = kwargs["annotation"]

    if urlparse.urlsplit(annotation_location)[0]:
        annotations_data = urllib2.urlopen(annotation_location)
    else:
        annotations_data = open(annotation_location)

    annotations = etree.parse(annotations_data)
    entries = {}
    used_entries = set([])
    for entry in annotations.xpath("//entry"):
        entries[entry.attrib["section"]] = entry


    add_w3c_issues = ("annotate_w3c_issues" in kwargs and 
                      kwargs["annotate_w3c_issues"])

    issues = defaultdict(list)
    spec_status = None
    if add_w3c_issues:
        spec_status = annotations.getroot().attrib["status"]
        assert spec_status in w3c_statuses

        for entry in annotations.xpath("//entry[issue]"):
            for issue in entry.xpath("./issue"):
                issues[entry.attrib["section"]].append(issue)

    heading_elements = set(["h1", "h2", "h3", "h4", "h5", "h6"])
    for element in ElementTree.getroot().iterdescendants():
        if ("id" in element.attrib and 
            element.attrib["id"] in entries  and           
            element.tag in heading_elements):    
            entry = entries.get(element.attrib["id"], None)
            issue_list = issues.get(element.attrib["id"], None)
            annotation = make_annotation(entry, issue_list, spec_status)
            element.addnext(annotation)
            used_entries.add(element.attrib["id"])

def make_annotation(entry, issues, spec_status):

    container = etree.Element("p")
    container.attrib["class"] = "XXX annotation"
    
    if entry.attrib["status"] != "UNKNOWN":
        status = etree.Element("b")
        status.text = "Status: "
        status_text = etree.Element("i")
        status_text.text = statuses[entry.attrib["status"]]
        container.append(status)
        container.append(status_text)
        if issues:
            status_text.text += ". "

    if issues:
        span_issue = etree.Element("span")
        multiple_issues = len(issues) > 1

        for i, issue in enumerate(sorted(issues)):
            a = etree.Element("a", attrib={"href":issue.attrib["url"]})
            a.text = issue.attrib["name"]
            a.tail = " (%s)"%issue.attrib["shortname"]
            if multiple_issues and i == len(issues) - 2:
                a.tail += " and "
            elif i < len(issues) - 1:
                a.tail += ", "
            else:
                a.tail += " "
            span_issue.append(a)
        next_status_name = w3c_status_names[w3c_statuses[
                w3c_statuses.index(spec_status)+1]]
        if multiple_issues:
            span_issue[-1].tail += "block progress to %s"%next_status_name
        else:
            span_issue[-1].tail += "blocks progress to %s"%next_status_name
        container.append(span_issue)

    return container
