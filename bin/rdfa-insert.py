#!/usr/bin/env python
#
# Inserts the RDFa specification into the HTML5 specification
# at a given offset.
import sys

# open all of the input and output files
html5spec = open(sys.argv[1], "r")
rdfaspec = open(sys.argv[2], "r")
combinedspec = open(sys.argv[3], "w")

# merge the specifications
for line in html5spec.readlines():
    if(line.find("<h2><dfn>Microdata</dfn></h2>") != -1):
        combinedspec.write(rdfaspec.read())
        combinedspec.write("\n" + line + "\n")
    else:
        combinedspec.write(line + "\n")

# close all of the input and output files
html5spec.close()
rdfaspec.close()
combinedspec.close()

