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

from PyQt4 import QtGui
from PyQt4.QtCore import Qt
from print_to_file.shelltools import get_os_search


class DialogWindow(object):
    """Dialog window intended to be set up upon initilization."""

    def __init__(self, xml_dict, error_dict, style_dict, pdf_status):
        """Checks dependency and calls dialog creation method."""

        self.popup_error = error_dict["incomplete_form"]
        self.default_style = style_dict["css_style"]
        self.window = QtGui.QDialog()

        if not pdf_status:
            search = get_os_search()
            error_message = " ".join(
                ["Note:", error_dict["no_wkhtml"],
                 error_dict["path_info"].format(search),
                 error_dict["only_html"]]
            )
            error_label = self.create_error_label(error_message)
        else:
            error_label = None

        #create all widget groups, set class attributes
        dimensions_box, self.entry_widgets = self.create_dimensions_box(
            xml_dict["dimensions"])
        radio_box, self.radio_groups = self.create_radio_buttons_box(
            xml_dict["radio_buttons"], pdf_status)
        style_page, self.style_editor = self.create_style_edit_page(style_dict)
        button_box = self.create_pushbutton_box()

        #collect widget groups into a list
        widget_groups = [
            error_label, dimensions_box, radio_box, style_page, button_box]

        self.window = self.configure_window(widget_groups, self.window)

        return


    #called when print is pressed, to check if any empty fields
    def print_clicked(self):
        """Checks if all fields are filled when print button is pressed."""

        empty = False
        #check for empty entry widgets
        for widget in self.entry_widgets:
            if not widget.text():
                empty = True
                break

        #show popup error message
        if empty:
            error_message = QtGui.QErrorMessage(self.window)
            error_message.showMessage(self.popup_error)

        #when all fields are filled out, signal accept
        else:
            self.window.accept()

        return


    #sets up and connects all pushbuttons, returns buttonbox
    def create_pushbutton_box(self):
        """Creates buttonbox for all window pushbuttons."""

        button_box = QtGui.QDialogButtonBox()
        button_box.addButton(QtGui.QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.window.reject)
        print_button = QtGui.QPushButton("Print to File")
        button_box.addButton(print_button, QtGui.QDialogButtonBox.AcceptRole)
        print_button.clicked.connect(self.print_clicked)
        restore_button = QtGui.QPushButton("Restore Style")
        button_box.addButton(restore_button, QtGui.QDialogButtonBox.ResetRole)
        restore_button.clicked.connect(
            lambda: self.style_editor.setPlainText(self.default_style))

        return button_box


    #arrange window layout with all widget components
    @staticmethod
    def configure_window(widget_groups, window):
        """Assembles all groups of widgets to create window layout"""

        #unpack group list
        [error_label,
         dimensions_box, radio_box, style_page, button_box] = widget_groups

        #configure dialog window
        window.setWindowTitle("Page Setup")
        window.setStyleSheet(
            ("QGroupBox { border: 1px solid gray; font-weight: bold; }\n"
             "QGroupBox::title { color: black; }"))

        #arrange page layout widgets into a single widget
        layout = QtGui.QHBoxLayout()
        layout.addWidget(dimensions_box)
        layout.addWidget(radio_box)
        dimensions_page = QtGui.QWidget()
        dimensions_page.setLayout(layout)

        #create tabs
        tab_widget = QtGui.QTabWidget()
        tab_widget.addTab(dimensions_page, "Page Layout")
        tab_widget.addTab(style_page, "Style Editor")

        #create and add widgets to main layout
        main_layout = QtGui.QVBoxLayout()
        if error_label:
            main_layout.addWidget(error_label)
        main_layout.addWidget(tab_widget)
        main_layout.addWidget(button_box)

        #set main layout to dialog window
        window.setLayout(main_layout)
        window.setMinimumSize(window.minimumSizeHint())

        return window


    #generate lists of stored input from the widgets
    def collect_input(self):
        """Pulls input from user modifiable widgets."""

        #collect all dimensions inputs
        line_input = []
        for widget in self.entry_widgets:
            line_input.append(widget.text())

        #collect all radio button group positions
        positions = []
        for group in self.radio_groups:
            positions.append(group.checkedId())

        style_text = self.style_editor.toPlainText()

        return line_input, positions, style_text


    #constructs line edit widgets, returns groupbox
    @staticmethod
    def create_dimensions_box(widget_details):
        """Creates groupbox for all line edit widgets."""

        layout = QtGui.QGridLayout()
        layout.setContentsMargins(11, 30, 11, 11)
        entry_widgets = []
        validator = QtGui.QDoubleValidator(0, 5000, 5)
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)

        #set up all widgets based on xml values
        for i, widget_detail in enumerate(widget_details[1:]):

            #create label first
            label = QtGui.QLabel(widget_detail["label"])

            #create line edit widget next
            edit = QtGui.QLineEdit()
            edit.setValidator(validator)
            edit.setText(widget_detail["value"])
            edit.setFixedWidth(80)

            #add both to the grid layout
            layout.addWidget(label, i, 1)
            layout.addWidget(edit, i, 0)

            #add edit widget to list to be used later
            entry_widgets.append(edit)

        #create group box and set the layout
        box_header = widget_details[0]
        box = QtGui.QGroupBox(box_header)
        box.setLayout(layout)
        box.setFixedSize(box.minimumSizeHint())

        return box, entry_widgets


    #set up radio button groups, returns groupbox
    @staticmethod
    def create_radio_buttons_box(widget_details, pdf_status):
        """Creates groupbox for all radio button widgets."""

        layout = QtGui.QGridLayout()
        layout.setContentsMargins(11, 30, 11, 11)
        groups = []
        for i, widget_detail in enumerate(widget_details[1:]):

            #create label and button widgets
            label = QtGui.QLabel(widget_detail["label"])
            button_left = QtGui.QRadioButton(widget_detail["left"])
            button_right = QtGui.QRadioButton(widget_detail["right"])

            #create group and add widgets to it
            group = QtGui.QButtonGroup()
            group.addButton(button_left, 1)
            group.addButton(button_right, 2)

            #if no conversion, override settings to select only html button
            if not pdf_status and widget_detail["name"] == "output":
                button_right.setEnabled(False)
                button_left.setChecked(True)
            else:
                group.button(int(widget_detail["position"])).setChecked(True)

            #add widgets to layout
            layout.addWidget(label, i*2, 0, 1, 2)
            layout.addWidget(button_left, (i*2)+1, 0)
            layout.addWidget(button_right, (i*2)+1, 1)

            groups.append(group)

        #create group box and set layout
        box_header = widget_details[0]
        box = QtGui.QGroupBox(box_header)
        box.setLayout(layout)
        box.setFixedSize(box.minimumSizeHint())

        return box, groups


    #set up text edit section, returns groupbox
    @staticmethod
    def create_style_edit_page(widget_details):
        """Creates groupbox for the text editor widget."""

        #create edit widget and set default text
        edit = QtGui.QTextEdit()
        edit.setPlainText(widget_details["css_style"])

        #create label
        label = QtGui.QLabel(widget_details["label"])
        label.setWordWrap(True)

        #create layout and add widgets
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(11, 30, 11, 11)
        layout.addWidget(label)
        layout.addWidget(edit)

        #create group box and set layout
        page = QtGui.QWidget()
        page.setLayout(layout)

        return page, edit


    #create error label, returns label
    @staticmethod
    def create_error_label(error_message):
        """Creates label for the error message if it exists."""

        if error_message:
            label = QtGui.QLabel(error_message)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignCenter)

            return label
        else:

            return None



