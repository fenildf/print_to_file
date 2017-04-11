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

"""Creates the menu item to be used for the addon."""

import sys
from aqt import mw

#try to import PyQt5 and then fall back to PyQt4
try:
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets
except ImportError:
    from PyQt4 import QtCore
    from PyQt4 import QtGui
    QtWidgets = QtGui

from print_to_file import addon_main

MENUITEM = QtWidgets.QAction("Print to file", mw)
MENUITEM.setShortcut(QtGui.QKeySequence("Ctrl+U"))
MENUITEM.triggered.connect(addon_main.main)
mw.form.menuTools.addAction(MENUITEM)
