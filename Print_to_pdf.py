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
#   Copyright (C) 2017  Benjamin Dowell     Email: TODO                        #
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
# * The html file may have added margins with print to file in browser.        #
# * There is no config file to save settings between uses                      #
# * The method of rearranging images can't be turned off.                      #
# * There is no method to disable pdf conversion dependencies.                 #
#                                                                              #
#==============================================================================#

import re, urllib
import pdfkit
##TODO check if no need later
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

    #get ids from tables(cards and notes)
    #keep card id if it is in deck ids and the note id matches the card nid, order by card front alphabetically
    return mw.col.db.list("select c.id from cards c, notes n where did in %s and c.nid = n.id order by n.sfld" % ids2str(deckIDs))

#remove uncessary style and repeated answer section of notes
def extractUsefulText(text):
    text = re.sub("(?si)^.*<hr id=answer>\n*", "", text)
    text = re.sub("(?si)<style.*?>.*?</style>", "", text)
    return text

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

    #default empty fields to 0
    for item in optionsList:
        if not item.text():
            item.setText("0")

    #TODO make these interactive to adjust
    LEFT_MARGIN = float(optionsList[0].text())
    RIGHT_MARGIN = float(optionsList[1].text())
    TOP_MARGIN = float(optionsList[2].text())
    BOTTOM_MARGIN = float(optionsList[3].text())
    WIDTH = float(optionsList[4].text())
    HEIGHT = float(optionsList[5].text())

    #html table values
    TABLE_WIDTH = WIDTH - LEFT_MARGIN - RIGHT_MARGIN
    TABLE_HEIGHT = HEIGHT - TOP_MARGIN - BOTTOM_MARGIN

    #options for pdf conversion
    OPTIONS = {
        'disable-smart-shrinking': None,
        'page-height': '{0}in'.format(str(HEIGHT)),
        'page-width': '{0}in'.format(str(WIDTH)),
        'margin-left': '{0}in'.format(str(LEFT_MARGIN)),
        'margin-right': '{0}in'.format(str(RIGHT_MARGIN)),
        'margin-top': '{0}in'.format(str(TOP_MARGIN)),
        'margin-bottom': '{0}in'.format(str(BOTTOM_MARGIN)),
    }

    #progress bar start
    mw.progress.start(immediate=True)

    #joins user path to filename
    htmlPath = os.path.join(mw.pm.profileFolder(), "print.html")
    pdfPath = os.path.join(mw.pm.profileFolder(), "print.pdf")

    #pulls list of card ids from DB
    cardIDs = getCardIDList(mw.col.decks.selected())

    #TODO could optimize these string concatenations
    #html header
    header = u"<html>\n"
    header += u"<head>\n"
    header += u"\t<meta charset=\"utf-8\">\n"
    header += u"\t{0}\n".format(getBase(mw.col))
    header += u"</head>\n"

    #style section
    style = u"<style type=\"text/css\">\n"
    style += u"\t* { margin: 0px; padding: 0px; }\n"
    style += u"\ttable {{ height: {0}in; width: {1}in; }}\n".format(str(TABLE_HEIGHT), str(TABLE_WIDTH))
    style += u"\ttable { page-break-after: always; table-layout: fixed; border-spacing: 0px; }\n"
    style += u"\ttd { text-align: center; vertical-align: middle; }\n"
    style += u"\timg {{ max-height: {0}in; max-width: 100%; }}\n".format(str(TABLE_HEIGHT))
    style += u"</style>\n"

    #start writing to html file
    buf = open(htmlPath, "w")
    buf.write(header.encode("utf8"))
    buf.write(style.encode("utf8"))
    buf.write(u"<body>\n".encode("utf8"))

    #loop through all card IDs and write note text to html file
    for i, cardID in enumerate(cardIDs):

        #get card from DB, retrieve question and answer, strip whitespace
        card = mw.col.getCard(cardID)
        question = extractUsefulText(card.q()).strip()
        answer = extractUsefulText(card.a()).strip()

        #seperate images and text into seperate strings
        (qText, qImages) = seperateOutImages(question)
        (aText, aImages) = seperateOutImages(answer)

        #TODO optimize body html string handling
        rowHtml = u"<table>\n"
        rowHtml += u"<tr>\n"
        if qText:
            rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(qText)
        if qImages:
            for qImage in qImages:
                rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(qImage)
        rowHtml += u"</tr>\n"
        rowHtml += u"</table>\n"

        #new tables are used for each page, so column widths are independent
        if i+1 < len(cardIDs):
            rowHtml += u"<table>\n"
        else:
            #modify table style on last card so pdfkit doesn't add an extra blank page
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
    buf.close()

    #progress bar finish
    mw.progress.finish()

    #convert html to pdf
    pdfkit.from_file(htmlPath, pdfPath, options=OPTIONS)

    #opens pdf
    openLink(uniPathPrefix(pdfPath))

#TODO File IO
#TODO pass input to print code
#TODO turn widget creation into a dictionary of sorts, to iterate everything, if/then for groupbox
#options dialog window for making changes to page size and margin
def showDialog():
    optionsDialog = QtGui.QDialog(mw)
    optionsDialog.setWindowTitle("Page Setup")
    optionsDialog.setStyleSheet(
            "QGroupBox { border: 1px solid gray; font-weight: bold; }\n"
            +"QGroupBox::title { color: black; }")

    #label text and additional note text
    mLabelText = [ "Left Margin:",
            "Right Margin:",
            "Top Margin:",
            "Bottom Margin:" ]
    pLabelText = [ "Page Width:",
            "Page Height:" ]
    noteText = "Units are in inches."
    noteLabel = QtGui.QLabel(noteText)
    noteLabel.setWordWrap(True)

    #iterate through widgets and apply settings
    def widgetSetup(widgets, parent, text):
        for i, widget in enumerate(widgets):
            label = QtGui.QLabel(text[i])
            label.setAlignment(Qt.AlignRight)
            #validator will allow values in range 0:50000 with accuracy of 10 decimals
            validator = QtGui.QDoubleValidator(0, 50000, 10)
            validator.setNotation(QDoubleValidator.StandardNotation)
            widget.setValidator(validator)
            widget.setFixedWidth(100)
            parent.addWidget(label, i, 0)
            parent.addWidget(widget, i, 1)

    #text entry widgets creation and addition for margins section
    leftMargin = QtGui.QLineEdit()
    rightMargin = QtGui.QLineEdit()
    topMargin = QtGui.QLineEdit()
    bottomMargin = QtGui.QLineEdit()
    mWidgets = [ leftMargin, rightMargin, topMargin, bottomMargin ]
    mBox = QtGui.QGridLayout()
    mBox.setContentsMargins(11, 30, 11, 30)
    widgetSetup(mWidgets, mBox, mLabelText)
    marginBox = QtGui.QGroupBox("Margins")
    marginBox.setLayout(mBox)

    #text entry widgets necessary for the page size and notes for instructions
    pageWidth = QtGui.QLineEdit()
    pageHeight = QtGui.QLineEdit()
    pWidgets = [ pageWidth, pageHeight ]
    pBox = QtGui.QGridLayout()
    pBox.setContentsMargins(11, 30, 11, 30)
    widgetSetup(pWidgets, pBox, pLabelText)
    pBox.addWidget(noteLabel, len(pWidgets), 0, 1, 2, Qt.AlignCenter)
    pSizeBox = QtGui.QGroupBox("Page Size")
    pSizeBox.setLayout(pBox)

    #widget for the print and cancel buttons with signal handling
    buttonBox = QtGui.QDialogButtonBox()
    buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
    buttonBox.addButton("Print", QtGui.QDialogButtonBox.AcceptRole)
    buttonBox.accepted.connect(optionsDialog.accept)
    buttonBox.rejected.connect(optionsDialog.reject)

    #create main grid, populate, and apply to dialog window
    ##(item, row, column, rowSpan, columnSpan, alignment)
    ##SetFixedSize for no resizing
    grid = QtGui.QGridLayout()
    grid.setSizeConstraint(QLayout.SetMinimumSize)
    grid.addWidget(marginBox, 1, 0)
    grid.addWidget(pSizeBox, 1, 1)
    grid.addWidget(buttonBox, 2, 1)
    optionsDialog.setLayout(grid)

    debug = open('/home/ben/Desktop/debug.txt', 'w')
    #if accept button is pressed
    if optionsDialog.exec_():
        debug.write("accepted\n")
        debug.close()
        printToFile(mWidgets+pWidgets)
        return
        ##if I want to correct if fields aren't filled out
        ##could be solved with just default as 0
        #for text in mWidgets + pWidgets:
        #    if not text.text():
        #        ##TODO Error Dialog
        #        showDialog()
        #        break
    else:
        debug.write("rejected\n")
        debug.close()
        #printToFile(mWidgets+pWidgets)
        return

q = QAction(mw)
q.setText("Print to file(pdf)")
q.setShortcut(QKeySequence("Ctrl+U"))
mw.form.menuTools.addAction(q)
mw.connect(q, SIGNAL("triggered()"), showDialog)
