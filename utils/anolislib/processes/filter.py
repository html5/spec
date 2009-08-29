from lxml import cssselect

def filter(ElementTree, **kwargs):
    if not "filter" in kwargs or kwargs["filter"] == None:
        return
    selector = cssselect.CSSSelector(kwargs["filter"])
    for element in selector(ElementTree.getroot()):
        remove(element)

def remove(element):
    if element.tail:
        if element.getprevious() is not None:
            target = element.getprevious()
            if target.tail:
                target.tail += element.tail
            else:
                target.tail = element.tail
        else:
            target = element.getparent()
            if target.text:
                target.text += element.text
            else:
                target.text = element.text
        
    element.getparent().remove(element)

        
