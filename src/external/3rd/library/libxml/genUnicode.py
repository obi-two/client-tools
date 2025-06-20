#!/usr/bin/python -u
import sys
import string
import time

sources = "Blocks-4.txt UnicodeData-3.1.0.txt"

try:
    blocks = open("Blocks-4.txt", "r")
except:
    print "Missing Blocks-4.txt, aborting ..."
    sys.exit(1)

BlockNames = {}
for line in blocks.readlines():
    if line[0] == '#':
        continue
    line = string.strip(line)
    if line == '':
	continue
    try:
	fields = string.split(line, ';')
	range = string.strip(fields[0])
	(start, end) = string.split(range, "..")
	name = string.strip(fields[1])
	name = string.replace(name, ' ', '')
    except:
        print "Failed to process line: %s" % (line)
	continue
    BlockNames[name] = ("0x"+start, "0x"+end)
blocks.close()
print "Parsed %d blocks descriptions" % (len(BlockNames.keys()))

try:
    data = open("UnicodeData-3.1.0.txt", "r")
except:
    print "Missing UnicodeData-3.1.0.txt, aborting ..."
    sys.exit(1)

nbchar = 0;
Categories = {}
for line in data.readlines():
    if line[0] == '#':
        continue
    line = string.strip(line)
    if line == '':
	continue
    try:
	fields = string.split(line, ';')
	point = string.strip(fields[0])
	value = 0
	while point != '':
	    value = value * 16
	    if point[0] >= '0' and point[0] <= '9':
	        value = value + ord(point[0]) - ord('0')
	    elif point[0] >= 'A' and point[0] <= 'F':
	        value = value + 10 + ord(point[0]) - ord('A')
	    elif point[0] >= 'a' and point[0] <= 'f':
	        value = value + 10 + ord(point[0]) - ord('a')
	    point = point[1:]
	name = fields[2]
    except:
        print "Failed to process line: %s" % (line)
	continue
    
    nbchar = nbchar + 1
    try:
	Categories[name].append(value)
    except:
        try:
	    Categories[name] = [value]
	except:
	    print "Failed to process line: %s" % (line)
    try:
	Categories[name[0]].append(value)
    except:
        try:
	    Categories[name[0]] = [value]
	except:
	    print "Failed to process line: %s" % (line)
	
blocks.close()
print "Parsed %d char generating %d categories" % (nbchar, len(Categories.keys()))
#reduce the number list into ranges
for cat in Categories.keys():
    list = Categories[cat]
    start = -1
    prev = -1
    end = -1
    ranges = []
    for val in list:
        if start == -1:
	    start = val
	    prev = val
	    continue
	elif val == prev + 1:
	    prev = val
	    continue
	elif prev == start:
	    ranges.append((prev, prev))
	    start = val
	    prev = val
	    continue
	else:
	    ranges.append((start, prev))
	    start = val
	    prev = val
	    continue
    if prev == start:
        ranges.append((prev, prev))
    else:
        ranges.append((start, prev))
    Categories[cat] = ranges
        
#
# Generate the resulting files
#
try:
    header = open("xmlunicode.h", "w")
except:
    print "Failed to open xmlunicode.h"
    sys.exit(1)

try:
    output = open("xmlunicode.c", "w")
except:
    print "Failed to open xmlunicode.c"
    sys.exit(1)

date = time.asctime(time.localtime(time.time()))

header.write(
"""/*
 * xmlunicode.h: this header exports interfaces for the Unicode character APIs
 *
 * This file is automatically generated from the
 * UCS description files of the Unicode Character Database
 * http://www.unicode.org/Public/3.1-Update/UnicodeCharacterDatabase-3.1.0.html
 * using the genUnicode.py Python script.
 *
 * Generation date: %s
 * Sources: %s
 * Daniel Veillard <veillard@redhat.com>
 */

#ifndef __XML_UNICODE_H__
#define __XML_UNICODE_H__

#ifdef __cplusplus
extern "C" {
#endif

""" % (date, sources));
output.write(
"""/*
 * xmlunicode.c: this module implements the Unicode character APIs
 *
 * This file is automatically generated from the
 * UCS description files of the Unicode Character Database
 * http://www.unicode.org/Public/3.1-Update/UnicodeCharacterDatabase-3.1.0.html
 * using the genUnicode.py Python script.
 *
 * Generation date: %s
 * Sources: %s
 * Daniel Veillard <veillard@redhat.com>
 */

#define IN_LIBXML
#include "libxml.h"

#ifdef LIBXML_UNICODE_ENABLED

#include <string.h>
#include <libxml/xmlversion.h>
#include <libxml/xmlunicode.h>

""" % (date, sources));

keys = BlockNames.keys()
keys.sort()
for block in keys:
    (start, end) = BlockNames[block]
    name = string.replace(block, '-', '')
    header.write("int\txmlUCSIs%s\t(int code);\n" % name)
    output.write("/**\n * xmlUCSIs%s:\n * @code: UCS code point\n" % (name))
    output.write(" *\n * Check whether the character is part of %s UCS Block\n"%
                 (block))
    output.write(" *\n * Returns 1 if true 0 otherwise\n */\n");
    output.write("int\nxmlUCSIs%s(int code) {\n" % name)
    output.write("    return((code >= %s) && (code <= %s));\n" % (start, end))
    output.write("}\n\n")

header.write("\nint\txmlUCSIsBlock\t(int code,\n\t\t\t const char *block);\n\n")
output.write("/**\n * xmlUCSIsBlock:\n * @code: UCS code point\n")
output.write(" * @block: UCS block name\n")
output.write(" *\n * Check whether the character is part of the UCS Block\n")
output.write(" *\n * Returns 1 if true, 0 if false and -1 on unknown block\n */\n");
output.write("int\nxmlUCSIsBlock(int code, const char *block) {\n")
keys = BlockNames.keys()
keys.sort()
for block in keys:
    name = string.replace(block, '-', '')
    output.write("    if (!strcmp(block, \"%s\"))\n        return(xmlUCSIs%s(code));\n" %
                 (block, name));
output.write("    return(-1);\n}\n\n")


keys = Categories.keys()
keys.sort()
for name in keys:
    ranges = Categories[name]
    header.write("int\txmlUCSIsCat%s\t(int code);\n" % name)
    output.write("/**\n * xmlUCSIsCat%s:\n * @code: UCS code point\n" % (name))
    output.write(" *\n * Check whether the character is part of %s UCS Category\n"%
                 (name))
    output.write(" *\n * Returns 1 if true 0 otherwise\n */\n");
    output.write("int\nxmlUCSIsCat%s(int code) {\n" % name)
    start = 1
    for range in ranges:
        (begin, end) = range;
	if start:
	    output.write("    return(");
	    start = 0
	else:
	    output.write(" ||\n           ");
	if (begin == end):
	    output.write("(code == %s)" % (hex(begin)))
	else:
	    output.write("((code >= %s) && (code <= %s))" % (
	                 hex(begin), hex(end)))
    output.write(");\n}\n\n")

header.write("\nint\txmlUCSIsCat\t(int code,\n\t\t\t const char *cat);\n")
output.write("/**\n * xmlUCSIsCat:\n * @code: UCS code point\n")
output.write(" * @cat: UCS Category name\n")
output.write(" *\n * Check whether the character is part of the UCS Category\n")
output.write(" *\n * Returns 1 if true, 0 if false and -1 on unknown category\n */\n");
output.write("int\nxmlUCSIsCat(int code, const char *cat) {\n")
keys = Categories.keys()
keys.sort()
for name in keys:
    output.write("    if (!strcmp(cat, \"%s\"))\n        return(xmlUCSIsCat%s(code));\n" %
                 (name, name));
output.write("    return(-1);\n}\n\n")

header.write("""
#ifdef __cplusplus
}
#endif
#endif /* __XML_UNICODE_H__ */
""");
output.write("""
#endif /* LIBXML_UNICODE_ENABLED */
""");
header.close()
output.close()
