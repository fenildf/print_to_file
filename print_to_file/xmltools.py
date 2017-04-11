# -*- coding: utf-8 -*-
#==============================================================================#
#   License:                                                                   #
#------------------------------------------------------------------------------#
#   Copyright (C) 2017  Benjamin Dowell     Email: bdanki@gmx.com              #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                              #
#==============================================================================#

"""Tools for reading and writing from xml file."""

from print_to_file.filepaths import FilePath
import xml.etree.ElementTree as ET

#parse xml and format into usable layout list
def parse_xml(xml_path):
    """Parse xml file to an organized data structures.

    line_edit:
    {"Left": .25, ...}

    radio_buttons:
    ["Inch", ...]
    """

    tree = ET.parse(xml_path)
    root = tree.getroot()

    line_edits = {}
    for line_edit in root.findall("line-edit"):
        line_edits[line_edit.get("name")] = line_edit.text

    radio_buttons = []
    for radio_button in root.findall("radio-button"):
        radio_buttons.append(radio_button.get("name"))

    style = root.find("text-edit").text

    return line_edits, radio_buttons, style

#write settings to xml file
def write_xml(line_edits, radio_buttons, style, xml_path):
    """Uses user selections, and saves them to xml as a default."""

    root = ET.Element("settings")

    #set all values for line edit inputs
    for i, key in enumerate(line_edits):
        ET.SubElement(root, "line-edit", name=key).text = line_edits[key]

    #set all selections from radio buttons
    for radio_button in radio_buttons:
        ET.SubElement(root, "radio-button", name=radio_button)

    #set style
    ET.SubElement(root, "text-edit").text = style

    indent(root)
    tree = ET.ElementTree(root)

    tree.write(xml_path)

#adds the unecessary but pleasing whitespace
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
