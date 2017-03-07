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

import xml.etree.ElementTree as ET


#parse xml and format into usable layout list
def parse_xml(settings_path):
    """Parse xml file to an organized dictionary.

    xml_dict:
    {"group1": ["Header", {"attrib1": "", "attrib2": ""},
                          {"attrib1": "", "attrib2": ""}, ...]
     "group2": [...]
     ...
    }
        "group": xml group tag
        "Header": xml group header for groupbox
        "attrib": text and other attributes of widgets
    """

    tree = ET.parse(settings_path)
    root = tree.getroot()

    #accumulate all widgets and attributes to iterate through later
    group_dict = {}
    for section in list(root.find("groups")):
        widget_group = [section.get("header")]
        for element in list(section):
            attribute_dict = {}
            for attribute in list(element):
                attribute_dict[attribute.tag] = attribute.text
            widget_group.append(attribute_dict)
        group_dict[section.tag] = widget_group

    #accumulate attributes into a dictionary
    for section in list(root.find("other")):
        attribute_dict = {}
        for element in list(section):
            attribute_dict[element.tag] = element.text

        if section.tag == "style_editor":
            style_dict = attribute_dict
        elif section.tag == "errors":
            error_dict = attribute_dict

    return (group_dict, error_dict, style_dict)


#write settings to xml file
def write_xml(dimensions_input, radio_positions, css_style, settings_path):
    """Uses user selections, and saves them to xml as a default."""

    #load tree again so values can be modified
    tree = ET.parse(settings_path)
    root = tree.getroot()
    groups = root.find("groups")

    #set all values from dimension inputs
    for i, widget in enumerate(list(groups.find("dimensions"))):
        widget.find("value").text = str(dimensions_input[i])

    #set all positions from radio positions
    for i, widget in enumerate(list(groups.find("radio_buttons"))):
        widget.find("position").text = str(radio_positions[i])

    #set style
    (root.find("other")
     .find("style_editor")
     .find("css_style").text) = css_style

    tree.write(settings_path)
