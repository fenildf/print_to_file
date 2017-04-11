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

"""Holds file path attributes."""

import os
from aqt import mw
from print_to_file.shelltools import check_wkhtmltopdf

#generate path strings based on anki environment
class FilePath(object):
    """Creates file path strings using anki environment."""

    def __init__(self):
        FilePath.addon_dir = os.path.join(mw.pm.addonFolder(), "print_to_file")
        FilePath.addon_xml = os.path.join(FilePath.addon_dir, "settings.xml")
        FilePath.user_dir = os.path.join(mw.pm.profileFolder(), "print_to_file")
        FilePath.user_xml = os.path.join(FilePath.user_dir, "settings.xml")
        FilePath.html = os.path.join(FilePath.user_dir, "print.html")
        FilePath.pdf = os.path.join(FilePath.user_dir, "print.pdf")
        FilePath.wkhtmltopdf = check_wkhtmltopdf(FilePath.addon_dir)
