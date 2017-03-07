#==============================================================================#
#   print_to_file {ver 2.0} Description:                                       #
#------------------------------------------------------------------------------#
#   print_to_file is an Anki addon that exports cards from a selected deck     #
#   and its child decks. It will always generate an html file that can be      #
#   converted to a pdf if the optional dependency is met. wkhtmltopdf is       #
#   used for an automated pdf conversion. The main purpose for creating this   #
#   addon is to have customizable page size and margins.                       #
#                                                                              #
#   The html file is generated with a customizable css style block. The        #
#   question and answer sections are split into separate pages. This is so     #
#   the cards can be printed to the front and back of pages. Each section      #
#   has a page break between it. When viewing the html file in a browser,      #
#   print or print preview needs to be selected before the page breaks will    #
#   be visible. If printing from html, the page size and margins in the        #
#   viewer need to match what is entered into print_to_file.                   #
#                                                                              #
#   I have included an option to separate images and note text into their      #
#   own table cells. I have found it useful for index cards printed in         #
#   landscape with one or two images. This addon was created for my own use,   #
#   but if there are situations that should be accommodated better, please     #
#   let me know.                                                               #
#                                                                              #
#   The output and settings files will be placed into the Anki user profile    #
#   directory under the directory print_to_file.                               #
#                                                                              #
#   GitHub: https://github.com/wetriner/print_to_file                          #
#                                                                              #
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
#   Known Limitations of this Addon Script:                                    #
#------------------------------------------------------------------------------#
#   * The Anki card style is removed                                           #
#   * The default css style is not a good starter style                        #
#                                                                              #
#==============================================================================#

import print_to_file.addon_main
