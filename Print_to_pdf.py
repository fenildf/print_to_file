#==============================================================================#
#   Print_to_pdf Description:                                                  #
#------------------------------------------------------------------------------#
#   The addon exports cards from a selected deck and children to a pdf.        #
#   It generates an html file that gets converted to pdf.                      #
#   Pdfkit and Wkhtmltopdf are necessary dependencies.                         #
#   The cards are organized with question and answer on seperate pages.        #
#   Note text is rearrange for better image sizing for small page sizes.       #
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
# * The html file may have unwanted margins depending on the browser           #
# * The method of rearranging the images can't be turned off.                  #
# * There is no method to disable pdf conversion dependencies.                 #
#                                                                              #
#==============================================================================#

import re, urllib
import pdfkit
from PyQt4 import QtGui, QtCore, QtWebKit
from aqt.qt import *
from anki.utils import isWin
from anki.hooks import runHook, addHook
from aqt.utils import getBase, openLink
from aqt import mw
from anki.utils import ids2str

#merge file path with prefix
def uniPathPrefix(path):
    if isWin:
        prefix = u"file:///"
    else:
        prefix = u"file://"
    return prefix + unicode(
        urllib.quote(path.encode("utf-8")), "utf-8")

#returns sorted list of card ids from selected deck and child decks
def getCardIDList(deckID):

    #create deck list with selected deck to start
    deckIDs = [deckID]

    #iterate through sub-decks and append deck ids
    for name, id in mw.col.decks.children(deckID):
        deckIDs.append(id)

    #keep card id if it is in deck ids and the note id matches the card nid, order by card front alphabetically
    query = "select c.id from cards c, notes n where did in {0} and c.nid = n.id order by n.sfld".format(ids2str(deckIDs))

    #return ids from tables with query
    return mw.col.db.list(query)

#pull images out of the notes into lists
def seperateOutImages(note):

    #check for images in note
    if re.match('.*<img src=".*', note):

        #split by html element and replace delimiter. index 0 never needs the delimiter
        subNotes = note.split("<")
        for j in range(1, len(subNotes)):
            subNotes[j] = "<" + subNotes[j]

        #iterate through subnotes and pull out images and their corresponding <div> tags if they exist
        images = []
        for subNote in subNotes:
            if re.match('.*<img src=".*', subNote):
                k = subNotes.index(subNote)
                if subNotes[k-1] == "<div>" and subNotes[k+1] == "</div>":
                    images.append(''.join(subNotes[k-1:k+2]))
                    del subNotes[k-1:k+2]
                else:
                    images.append(subNotes[k])
                    del subNotes[k]

        #join note back into a string
        note = ''.join(subNotes)

        #if no note, just return the images
        if len(note) == 0:
            return (None, images)
        else:
            return (note, images)

    #if no image, just return the note
    return (note, None)

#function responsible for generating html and pdf from note text
def printToFile(optionsList):

    #names for html and pdf file joined to profile folder
    outputPath = os.path.join(mw.pm.profileFolder(), "print_to_pdf")
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    htmlPath = os.path.join(outputPath, "print.html")
    pdfPath = os.path.join(outputPath, "print.pdf")

    #default empty fields to 0
    for item in optionsList:
        if not item:
            item = "0"

    #could utilize a dict here instead with descriptive names: optionsList["leftMargin"]
    LEFT_MARGIN = float(optionsList[0])
    RIGHT_MARGIN = float(optionsList[1])
    TOP_MARGIN = float(optionsList[2])
    BOTTOM_MARGIN = float(optionsList[3])
    WIDTH = float(optionsList[4])
    HEIGHT = float(optionsList[5])

    #html table values
    TABLE_WIDTH = WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    TABLE_HEIGHT = HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

    #options for pdf conversion
    pdfOptions = {
        'disable-smart-shrinking': None,
        'page-height': '{0:.5f}in'.format(HEIGHT),
        'page-width': '{0:.5f}in'.format(WIDTH),
        'margin-left': '{0:.5f}in'.format(LEFT_MARGIN),
        'margin-right': '{0:.5f}in'.format(RIGHT_MARGIN),
        'margin-top': '{0:.5f}in'.format(TOP_MARGIN),
        'margin-bottom': '{0:.5f}in'.format(BOTTOM_MARGIN),
    }

    #progress bar start
    mw.progress.start(immediate=True)

    #pulls list of card ids from DB
    cardIDs = getCardIDList(mw.col.decks.selected())

    #html header
    header = u"<html>\n"
    header += u"<head>\n"
    header += u"\t<meta charset=\"utf-8\">\n"
    header += u"\t{0}\n".format(getBase(mw.col))
    header += u"</head>\n"

    #style section
    style = u"<style type=\"text/css\">\n"
    style += u"\t* { margin: 0px; padding: 0px; }\n"
    style += u"\ttable {{ height: {0:.5f}in; width: {1:.5f}in; }}\n".format(TABLE_HEIGHT, TABLE_WIDTH)
    style += u"\ttable { page-break-after: always; table-layout: fixed; border-spacing: 0px; }\n"
    style += u"\ttd { text-align: center; vertical-align: middle; }\n"
    style += u"\timg {{ max-height: {0:.5f}in; max-width: 100%; }}\n".format(TABLE_HEIGHT)
    style += u"</style>\n"

    #start writing to html file
    with open(htmlPath, "w") as buf:
        buf.write(header.encode("utf8"))
        buf.write(style.encode("utf8"))
        buf.write(u"<body>\n".encode("utf8"))

        #loop through all card IDs and write note text to html file
        for i, cardID in enumerate(cardIDs):

            #get card from DB, retrieve question and answer, strip whitespace
            card = mw.col.getCard(cardID)
            question = re.sub("(?si)^.*<hr id=answer>\n*", "", card.q())
            question = re.sub("(?si)<style.*?>.*?</style>", "", question).strip()
            answer = re.sub("(?si)^.*<hr id=answer>\n*", "", card.a())
            answer = re.sub("(?si)<style.*?>.*?</style>", "", answer).strip()

            #seperate images and text into seperate strings
            (qText, qImages) = seperateOutImages(question)
            (aText, aImages) = seperateOutImages(answer)

            #question html
            rowHtml = u"<table>\n"
            rowHtml += u"<tr>\n"
            if qText:
                rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(qText)
            if qImages:
                for qImage in qImages:
                    rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(qImage)
            rowHtml += u"</tr>\n"
            rowHtml += u"</table>\n"

            #answer html
            if i+1 < len(cardIDs):
                rowHtml += u"<table>\n"
            else:
                #modify table style on last card so wkhtmltopdf doesn't add an extra blank page
                rowHtml += u"<table style=\"page-break-after: avoid\">\n"
            rowHtml += u"<tr>\n"
            if aText:
                rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(aText)
            if aImages:
                for aImage in aImages:
                    rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(aImage)
            rowHtml += u"</tr>\n"
            rowHtml += u"</table>\n"

            #write card html to file
            buf.write(rowHtml.encode("utf8"))

            #progress bar update
            mw.progress.update("Cards exported: {0}".format(i+1))

        #close out html file writing
        buf.write("</body>\n".encode("utf8"))
        buf.write("</html>".encode("utf8"))

    #progress bar finish
    mw.progress.finish()

    #convert html to pdf
    pdfkit.from_file(htmlPath, pdfPath, options=pdfOptions)

    #opens pdf
    openLink(uniPathPrefix(pdfPath))

#options dialog window for making changes to page size and margin
def showDialog():

    optionsDialog = QtGui.QDialog(mw)
    optionsDialog.setWindowTitle("Page Setup")
    optionsDialog.setStyleSheet(
            "QGroupBox { border: 1px solid gray; font-weight: bold; }\n"
            +"QGroupBox::title { color: black; }")

    #display text for note and widget labels
    noteText = "Units are in inches."
    noteLabel = QtGui.QLabel(noteText)
    noteLabel.setWordWrap(True)
    widgetText = [ "Left Margin:",
            "Right Margin:",
            "Top Margin:",
            "Bottom Margin:",
            "Page Width:",
            "Page Height:", ]

    #create, configure, layout all core widgets and put them into lists
    leWidgets = []
    lblWidgets = []
    gridLayouts = { "margin" : QtGui.QGridLayout(),
            "pagesize" : QtGui.QGridLayout(), }
    gridLayouts["margin"].setContentsMargins(11, 30, 11, 30)
    gridLayouts["pagesize"].setContentsMargins(11, 30, 11, 30)
    j = 0
    for i in range(len(widgetText)):
        lblWidgets.append(QtGui.QLabel(widgetText[i]))
        lblWidgets[i].setAlignment(Qt.AlignRight)
        leWidgets.append(QtGui.QLineEdit())
        validator = QtGui.QDoubleValidator(0, 5000, 5)
        validator.setNotation(QDoubleValidator.StandardNotation)
        leWidgets[i].setValidator(validator)
        leWidgets[i].setFixedWidth(100)
        if i < 4:
            gridLayouts["margin"].addWidget(lblWidgets[i], i, 0)
            gridLayouts["margin"].addWidget(leWidgets[i], i, 1)
        else:
            gridLayouts["pagesize"].addWidget(lblWidgets[i], j, 0)
            gridLayouts["pagesize"].addWidget(leWidgets[i], j, 1)
            j += 1
    gridLayouts["pagesize"].addWidget(noteLabel, j, 0, 1, 2, Qt.AlignCenter)

    #widget for the print and cancel buttons with signal handling
    buttonBox = QtGui.QDialogButtonBox()
    buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
    buttonBox.addButton("Print", QtGui.QDialogButtonBox.AcceptRole)
    buttonBox.accepted.connect(optionsDialog.accept)
    buttonBox.rejected.connect(optionsDialog.reject)

    #create main grid, populate, and apply to dialog window
        ##(item, row, column, rowSpan, columnSpan, alignment)
        ##SetFixedSize for no resizing
    mGroup = QtGui.QGroupBox("Margins")
    pGroup = QtGui.QGroupBox("Page Size")
    mGroup.setLayout(gridLayouts["margin"])
    pGroup.setLayout(gridLayouts["pagesize"])
    grid = QtGui.QGridLayout()
    grid.addWidget(mGroup, 1, 0)
    grid.addWidget(pGroup, 1, 1)
    grid.addWidget(buttonBox, 2, 1)
    grid.setSizeConstraint(QLayout.SetMinimumSize)
    optionsDialog.setLayout(grid)

    #get initial setting from file if it exists
    settingsPath = os.path.join(mw.pm.profileFolder(), "print_to_pdf", "settings.txt")
    if os.path.isfile(settingsPath):
        with open(settingsPath, "r") as buf:
            i = 0
            for line in buf.read().splitlines():
                leWidgets[i].setText(line)
                i += 1

    #if accept button is pressed
    if optionsDialog.exec_():

        #convert widget text to list
        oList = []
        for widget in leWidgets:
            oList.append(widget.text())

        #overwrite settings file if accepted
        settingsPath = os.path.join(mw.pm.profileFolder(), "print_to_pdf", "settings.txt")
        with open(settingsPath, "w") as buf:
            for option in oList:
                buf.write(option + "\n")

        printToFile(oList)
        return
    else:
        debug.close()
        return

q = QAction(mw)
q.setText("Print to file(pdf)")
q.setShortcut(QKeySequence("Ctrl+U"))
mw.form.menuTools.addAction(q)
mw.connect(q, SIGNAL("triggered()"), showDialog)
