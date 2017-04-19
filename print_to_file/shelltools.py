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

"""Checks for dependency conflicts and handles shell calls."""

import os
import sys
import subprocess

#return search command based on os
def get_os_search():
    """Get shell command based on os"""

    search = "where" if os.name == "nt" else "which"
    return search

#call wkhtmltopdf with given arguments
def call_wkhtmltopdf(wkhtml_path, wkhtml_arguments):
    """Calls wkhtmltopdf with a given list of arguments"""

    startupinfo = get_startupinfo()
    subprocess.call([wkhtml_path] + wkhtml_arguments, startupinfo=startupinfo)

    return

#check environment to return suitable startupinfo for subprocess
def get_startupinfo():
    """Returns startupinfo based on if os is nt or not"""

    #create startupinfo to avoid a visible shell on nt
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    return startupinfo

#use environmental checks to determine the status of dependencies
def check_wkhtmltopdf(addon_dir):
    """Checks if wkhtmltopdf is available to use."""

    #use os specific search command
    search = get_os_search()

    #get the subprocess startupinfo
    startupinfo = get_startupinfo()

    #check if wkhtmltopdf executable can be found to make pdf conversion
    try:
        #start search in addon code path
        wkhtml_path = subprocess.check_output(
            [search, "wkhtmltopdf"], startupinfo=startupinfo,
            cwd=addon_dir).splitlines()[0]
    except subprocess.CalledProcessError:
        wkhtml_path = None

    return wkhtml_path

#launch file based on system environment
def launch_file(file_path):
    """Launch output file based on system environment."""

    if sys.platform.startswith("linux"):
        subprocess.call(["xdg-open", filename])
    elif sys.platform == "darwin":
        subprocess.call(["open", file_path])
    elif sys.platform == "win32":
        os.startfile(file_path)
    else:
        raise Exception(
            "Can't launch {}, but it was still created.".format(file_path))
