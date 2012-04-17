#!/usr/bin/env python

from lxml import etree
import sys

tags = set()
classes = set()
ids = set()

def process(fd):
    root = etree.parse(fd, etree.HTMLParser())
    #root = etree.parse(fd)

    for child in root.iter():
        tags.add(child.tag)

        classes.update(child.attrib.get('class', '').split())
        if 'id' in child.attrib:
            ids.add(child.attrib.get('id'))


if __name__ == '__main__':
    for file in sys.argv[1:]:
        with open(file) as fd:
            process(fd)
    print "TAGS = %s" % (', '.join([a for a in tags]))
    print "CLASSES = %s" % (', '.join([a for a in classes]))
    print "IDS = %s" % (', '.join([a for a in ids]))
