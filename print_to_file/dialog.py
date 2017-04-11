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

"""A PyQt dialog window used for printing options."""

import sys
import re

#try to import PyQt5 and then fall back to PyQt4
try:
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets
except ImportError:
    from PyQt4 import QtCore
    from PyQt4 import QtGui
    QtWidgets = QtGui

from aqt import mw
from print_to_file.dialog_ui import Ui_Dialog
from print_to_file.filepaths import FilePath
from print_to_file import shelltools
from print_to_file import xmltools

class DialogWindow(object):
    """Dialog window intended to be set up upon initilization."""

    def __init__(self, dimensions, positions, style):
    #def __init__(self, xml_dict, error_dict, style_dict, pdf_status):
        """Checks dependency and calls dialog creation methods."""

        #create and setup ui dialog
        self.window = QtWidgets.QDialog()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.window)

        #assemble widget dictionaries for more abstract iteration
        self.lineEditDict = self.create_widget_dict(
            self.ui.groupBoxSetup, QtWidgets.QLineEdit)
        self.radioButtonDict = self.create_widget_dict(
            self.ui.groupBoxOther, QtWidgets.QRadioButton)
        self.buttonGroupDict = self.create_widget_dict(
            self.window, QtWidgets.QButtonGroup)

        if not FilePath.wkhtmltopdf:
            error_label = self.create_error_label(self.ui.layoutMain)
            self.ui.radioButtonPdf.setEnabled(False)

        #setup non-designer settings
        self.connect_pushbuttons()
        self.set_validator()

        #fill out defaults based on user settings
        self.set_defaults(dimensions, positions, style)

        return

    @staticmethod
    def create_widget_dict(parent, widget_type):
        """Create a dictionary of widgets based on object name."""
        widgets = parent.findChildren(widget_type)
        widget_dict = {}
        for widget in widgets:
            key = re.search(r'[A-Z][a-z]+$', widget.objectName()).group(0)
            widget_dict[key] = widget

        return widget_dict

    def set_validator(self):
        validator = QtGui.QDoubleValidator(0, 5000, 5)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        for widget in self.ui.groupBoxSetup.findChildren(QtWidgets.QLineEdit):
            widget.setValidator(validator)

    #create error label, returns label
    @staticmethod
    def create_error_label(layout):
        """Creates label for the error message."""

        message = (
            "wkhtmltopdf was not found. The executable can be placed in the "
            "Anki/addons/print_to_file directory or in any path that can be "
            "found by the command <b>{} wkhtmltopdf</b>. Output will be limited "
            "to html only."
        ).format(shelltools.get_os_search())
        label = QtWidgets.QLabel(message)
        label.setStyleSheet("QLabel { background-color: lightgrey; border: 2px inset grey }")
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignCenter)

        #add layout to first position of the given layout
        layout.insertWidget(0, label)

        return

    def verify_input(self):
        """Show an error if all input fields haven't been filled out."""
        empty = False
        for key in self.lineEditDict:
            if not self.lineEditDict[key].text():
                empty = True
                break
        #show popup error message
        if empty:
            error_message = QtWidgets.QErrorMessage(self.window)
            error_message.showMessage("All fields must be filled out.")
        #when all fields are filled out, signal accept
        else:
            self.window.accept()
        return

    def restore_style(self):
        _,_,style_text = xmltools.parse_xml(FilePath.addon_xml)
        self.ui.textEdit.setPlainText(style_text)

    def connect_pushbuttons(self):
        """Set up methods to be called when buttons are pushed."""

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.verify_input)
        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText("Print to File")
        self.ui.pushButtonRestore.clicked.connect(self.restore_style)

    def set_defaults(self, dimensions, positions, style):
        """Set user default values to all input widgets."""

        #widgets = self.ui.groupBoxSetup.findChildren(QtWidgets.QLineEdit)
        for key in self.lineEditDict:
            self.lineEditDict[key].setText(str(dimensions[key]))

        #set default checked positions for radio buttons
        for name in positions:
            key = re.search(r'[A-Z][a-z]+$', name).group(0)
            button = self.radioButtonDict[key]
            if button.isEnabled():
                button.setChecked(True)
            else:
                self.ui.radioButtonHtml.setChecked(True)

        self.ui.textEdit.setPlainText(style)

        return

    def collect_input(self):
        """Take all input fields and convert them to usable data structures."""

        #create an entry widget input dictionary
        line_edits = {}
        for key in self.lineEditDict:
            line_edits[key] = self.lineEditDict[key].text()

        #collect all checked radio button names into a list
        radio_buttons = []
        for key in self.buttonGroupDict:
            checked = self.buttonGroupDict[key].checkedButton()
            name = re.search(r'[A-Z][a-z]+$', checked.objectName()).group(0)
            radio_buttons.append(name)

        style_text = self.ui.textEdit.toPlainText()

        return line_edits, radio_buttons, style_text

