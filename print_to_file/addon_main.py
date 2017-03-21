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
import urllib
import urlparse
from PyQt4 import QtCore
from PyQt4 import QtGui
from aqt import mw
from print_to_file import convert
from print_to_file import xmltools
from print_to_file.dialog import DialogWindow
from print_to_file.shelltools import check_wkhtmltopdf

#generate path files
def anki_paths():
    """Creates a dict of addon used paths from anki methods."""

    #create dict of paths
    path_dict = {}
    path_dict["addon"] = os.path.join(mw.pm.addonFolder(), "print_to_file")
    path_dict["addon_xml"] = os.path.join(path_dict["addon"], "settings.xml")
    path_dict["user"] = os.path.join(mw.pm.profileFolder(), "print_to_file")
    path_dict["user_xml"] = os.path.join(path_dict["user"], "settings.xml")
    path_dict["html"] = os.path.join(path_dict["user"], "print.html")
    path_dict["pdf"] = os.path.join(path_dict["user"], "print.pdf")

    return path_dict

#addon point of entry if clicked
def main():
    """Entry point for addon execution."""

    path_dict = anki_paths()

    #if user output directory doesn't exist, create it
    if not os.path.exists(path_dict["user"]):
        os.makedirs(path_dict["user"])

    #if user settings doesn't exist. copy over default xml
    if not os.path.isfile(path_dict["user_xml"]):
        copyfile(path_dict["addon_xml"], path_dict["user_xml"])

    #parse xml into group and error dictionaries
    xml_dicts = xmltools.parse_xml(path_dict["user_xml"])

    #check if pdf output is possible
    (pdf_status,
     path_dict["wkhtmltopdf"]) = check_wkhtmltopdf(path_dict["addon"])

    #create dialog window
    dialog = DialogWindow(*xml_dicts, pdf_status=pdf_status)

    #run dialog window and catch closing signal
    signal = dialog.window.exec_()

    #if window is accepted, collect and return user input
    if signal:
        dimensions, selections, style_text = dialog.collect_input()

    #if the dialog is closed without printing, just return to anki
    else:
        return

    #save user settings to xml
    xmltools.write_xml(
        dimensions, selections, style_text, path_dict["user_xml"])

    #convert selections to better form
    units = "in" if selections[0] == 1 else "mm"
    image_separation = True if selections[1] == 2 else False
    pdf_output = True if selections[2] == 2 else False

    #progress bar start
    #TODO: add cancellable to options when Anki is updated
    mw.progress.start(label="Converting cards...", immediate=True)

    #output cards as html file
    convert.create_html(
        dimensions, units, image_separation, style_text, path_dict["html"])

    if pdf_output:
        #output cards as html file
        convert.create_pdf(dimensions, units, path_dict)
        key = "pdf"
    else:
        key = "html"

    #progress bar close
    mw.progress.finish()

    #open file
    file_link = urlparse.urljoin("file:", urllib.pathname2url(path_dict[key]))
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(file_link))

    return


MENUITEM = QtGui.QAction(mw)
MENUITEM.setText("Print to file")
MENUITEM.setShortcut(QtGui.QKeySequence("Ctrl+U"))
mw.form.menuTools.addAction(MENUITEM)
mw.connect(MENUITEM, QtCore.SIGNAL("triggered()"), main)
