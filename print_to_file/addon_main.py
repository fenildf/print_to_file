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

"""Main control flow of addon."""

import os
from shutil import copyfile
from aqt import mw
from print_to_file import convert
from print_to_file import xmltools
from print_to_file.dialog import DialogWindow
from print_to_file.filepaths import FilePath
from print_to_file.shelltools import launch_file

#addon point of entry if clicked
def main():
    """Entry point for addon execution."""

    #initialize profile dependent paths
    FilePath()

    #if user output directory doesn't exist, create it
    if not os.path.exists(FilePath.user_dir):
        os.makedirs(FilePath.user_dir)

    #if user settings file doesn't exist. copy over default xml
    if not os.path.isfile(FilePath.user_xml):
        copyfile(FilePath.addon_xml, FilePath.user_xml)

    #parse xml into group and error dictionaries
    xml_dicts = xmltools.parse_xml(FilePath.user_xml)

    #create dialog window
    dialog = DialogWindow(*xml_dicts)

    #run dialog window and catch closing signal
    signal = dialog.window.exec_()

    #if window is accepted, collect and return user input
    if signal:
        dimensions, selections, style_text = dialog.collect_input()
    #TODO standardize these names throughout

    #if the dialog is closed without printing, just return to anki
    else:
        return

    #save user settings to xml
    xmltools.write_xml(
        dimensions, selections, style_text, FilePath.user_xml)

    #progress bar start
    #TODO: add cancellable to options when Anki is updated
    mw.progress.start(label="Converting cards...", immediate=True)

    #convert selections to more usable form
    units = "in" if "Inch" in selections else "mm"
    split_images = True if "Split" in selections else False

    #output cards as html file
    convert.create_html(dimensions, units, split_images, style_text)

    if "Pdf" in selections:
        #output cards as pdf file
        convert.create_pdf(dimensions, units)
        output_path = FilePath.pdf
    else:
        output_path = FilePath.html

    mw.progress.update("Launching file...")
    launch_file(output_path)

    #progress bar close
    mw.progress.finish()

    return
