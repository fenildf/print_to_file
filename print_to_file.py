#==============================================================================#
#   print_to_file {ver 1.0} Description:                                       #
#------------------------------------------------------------------------------#
#   print_to_file is an Anki addon that exports cards from a selected deck     #
#   and any child decks. It will generate an html file that can get            #
#   converted to a pdf file if the optional dependencies are met. pdfkit and   #
#   wkhtmltopdf are used for this process. The option is only available to     #
#   Linux users. All platforms can use this to create html files. The main     #
#   reason for this addon is to have customizable page size and margins.       #
#                                                                              #
#   The question and answer sections are split into separate pages. I have     #
#   included an option to separate images into their own cells. I found it     #
#   useful for small landscape page layouts with one or two images.            #
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
#   * Card style is removed                                                    #
#   * The html header style section isn't easily customized                    #
#                                                                              #
#==============================================================================#

import re, urllib, subprocess, platform
from PyQt4 import QtGui, QtCore, QtWebKit
from aqt.qt import *
from anki.utils import isWin
from anki.hooks import runHook, addHook
from aqt.utils import getBase
from aqt import mw
from anki.utils import ids2str

#if pdfkit is installed, load it
try:
    import pdfkit
    PDF = True
except:
    PDF = False

#check if wkhtmltopdf is installed and correct version
try:
    output = subprocess.check_output(["wkhtmltopdf", "--version"])
    if "(with patched qt)" in output:
        WK = "installed"
    else:
        WK = "not-patched"
except:
    WK = "not-installed"

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
        if note:
            return (None, images)
        else:
            return (note, images)

    #if no image, just return the note
    return (note, None)

#function responsible for generating html and pdf from note text
def printToFile(optionsList):

    #names for html and pdf file joined to profile folder
    outputPath = os.path.join(mw.pm.profileFolder(), "print_to_pdf")
    htmlPath = os.path.join(outputPath, "print.html")
    pdfPath = os.path.join(outputPath, "print.pdf")

    #options dictionary
    optionsDict = dict(zip([ "marginLeft", "marginRight", "marginTop", "marginBottom",
            "pageWidth", "pageHeight", "units", "imageStyle", "output", ], optionsList))

    if optionsDict["units"] == 1:
        optionsDict["units"] = "in"
    else:
        optionsDict["units"] = "mm"

    #html table values
    tableWidth = optionsDict["pageWidth"] - optionsDict["marginLeft"] - optionsDict["marginRight"]
    tableHeight = optionsDict["pageHeight"] - optionsDict["marginTop"] - optionsDict["marginBottom"]

    #options for pdf conversion
    pdfOptions = { 'disable-smart-shrinking': None,
            'page-height': '{0:.5f}{1}'.format(optionsDict["pageHeight"], optionsDict["units"]),
            'page-width': '{0:.5f}{1}'.format(optionsDict["pageWidth"], optionsDict["units"]),
            'margin-left': '{0:.5f}{1}'.format(optionsDict["marginLeft"], optionsDict["units"]),
            'margin-right': '{0:.5f}{1}'.format(optionsDict["marginRight"], optionsDict["units"]),
            'margin-top': '{0:.5f}{1}'.format(optionsDict["marginTop"], optionsDict["units"]),
            'margin-bottom': '{0:.5f}{1}'.format(optionsDict["marginBottom"], optionsDict["units"]), }

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
    style += u"\ttable {{ height: {0:.5f}{2}; width: {1:.5f}{2}; }}\n".format(tableHeight, tableWidth, optionsDict["units"])
    style += u"\ttable { page-break-after: always; table-layout: fixed; border-spacing: 0px; }\n"
    style += u"\ttd { vertical-align: middle; }\n"
    style += u"\timg {{ max-height: {0:.5f}{1}; max-width: 100%; }}\n".format(tableHeight, optionsDict["units"])
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

            #seperate images and text into seperate strings if option is selected
            if optionsDict["imageStyle"] == 2:
                (question, qImages) = seperateOutImages(question)
                (answer, aImages) = seperateOutImages(answer)
            else:
                qImages = None
                aImages = None

            #question html
            rowHtml = u"<table>\n"
            rowHtml += u"<tr>\n"
            if question:
                rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(question)
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
            if answer:
                rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(answer)
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

    #convert and open file
    if PDF and WK != "not-installed" and optionsDict["output"] != 1:
        pdfkit.from_file(htmlPath, pdfPath, options=pdfOptions)
        QtGui.QDesktopServices.openUrl(QUrl.fromEncoded(uniPathPrefix(pdfPath)))
    else:
        QtGui.QDesktopServices.openUrl(QUrl.fromEncoded(uniPathPrefix(htmlPath)))

#options dialog window for making changes to page size and margin
def showDialog():
    optionsDialog = QtGui.QDialog(mw)
    optionsDialog.setWindowTitle("Page Setup")
    optionsDialog.setStyleSheet(
            "QGroupBox { border: 1px solid gray; font-weight: bold; }\n"
            +"QGroupBox::title { color: black; }")

    #display text used for errors
    errorMsgs = [ "pdfkit is not installed.",
            "wkhtmltopdf is not installed.",
            "wkhtmltopdf is installed, but it is not the patched qt version.", 
            "Cards may not fit properly on pdf.",
            "Conversion will be to html only.", ]

    #construct error message label
    errorText = []
    if not PDF:
        errorText.append(errorMsgs[0])
    if WK == "not-installed":
        errorText.append(errorMsgs[1])
        if PDF:
            errorText.append(errorMsgs[4])
    elif WK == "not-patched":
        errorText.append(errorMsgs[2])
        if PDF:
            errorText.append(errorMsgs[3])
    if not PDF:
        errorText.append(errorMsgs[4])
    errorLabel = QtGui.QLabel(" ".join(errorText))
    errorLabel.setWordWrap(True)
    errorLabel.setAlignment(Qt.AlignCenter)

    #inner grid layouts for main sections
    gridLayouts = { "margin" : QtGui.QGridLayout(),
            "pagesize" : QtGui.QGridLayout(),
            "radio" : QtGui.QGridLayout(), }

    #text used for label widgets in margin and page layout groups
    leLabelText = [ "Left Margin:",
        "Right Margin:",
        "Top Margin:",
        "Bottom Margin:",
        "Page Width:",
        "Page Height:", ]

    #create, configure, layout line edit and label widgets
    leWidgets = []
    j = 0
    for i in range(len(leLabelText)):
        leLabel = QtGui.QLabel(leLabelText[i])
        leLabel.setAlignment(Qt.AlignRight)
        leWidgets.append(QtGui.QLineEdit())
        validator = QtGui.QDoubleValidator(0, 5000, 5)
        validator.setNotation(QDoubleValidator.StandardNotation)
        leWidgets[i].setValidator(validator)
        leWidgets[i].setFixedWidth(100)
        if i < 4:
            gridLayouts["margin"].addWidget(leLabel, i, 0)
            gridLayouts["margin"].addWidget(leWidgets[i], i, 1)
        else:
            gridLayouts["pagesize"].addWidget(leLabel, j, 0)
            gridLayouts["pagesize"].addWidget(leWidgets[i], j, 1)
            j += 1

    #text used for radio buttons and labels in other options group
    radButtonText = [ "Inches",
            "mm",
            "Keep layout",
            "Reposition images",
            "html only",
            "html and pdf", ]

    radLabelText = [ "Units used for page layout:",
            "Image handling(intended for landscape):",
            "Output file format:", ]

    #create and setup other options group
    radButtons = []
    radKeys = [ "unit", "imageStyle", "output", ]
    radGroups = dict.fromkeys(radKeys)
    for i, key in enumerate(radKeys):
        j = i*2
        radGroups[key] = QtGui.QButtonGroup()
        radLabel = QtGui.QLabel(radLabelText[i])
        radButtons.append(QtGui.QRadioButton(radButtonText[j]))
        radButtons.append(QtGui.QRadioButton(radButtonText[j+1]))
        radGroups[key].addButton(radButtons[j], 1)
        radGroups[key].addButton(radButtons[j+1], 2)
        gridLayouts["radio"].addWidget(radLabel, j, 0, 1, 2)
        gridLayouts["radio"].addWidget(radButtons[j], j+1, 0)
        gridLayouts["radio"].addWidget(radButtons[j+1], j+1, 1)

    #buttons for the print and cancel buttons with signal handling
    buttonBox = QtGui.QDialogButtonBox()
    buttonBox.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
    buttonBox.addButton("Print", QtGui.QDialogButtonBox.AcceptRole)
    buttonBox.accepted.connect(optionsDialog.accept)
    buttonBox.rejected.connect(optionsDialog.reject)

    #group box creation layout sections
    marginGroup = QtGui.QGroupBox("Margins")
    marginGroup.setLayout(gridLayouts["margin"])
    gridLayouts["margin"].setContentsMargins(11, 30, 11, 11)
    pSizeGroup = QtGui.QGroupBox("Page Size")
    pSizeGroup.setLayout(gridLayouts["pagesize"])
    gridLayouts["pagesize"].setContentsMargins(11, 30, 11, 11)
    otherGroup = QtGui.QGroupBox("Other Options")
    otherGroup.setLayout(gridLayouts["radio"])
    gridLayouts["radio"].setContentsMargins(11, 30, 11, 11)
    otherGroup.setStyleSheet("QLabel { text-decoration: underline }")

    #create main grid, populate, and apply to dialog window
        ##(item, row, column, rowSpan, columnSpan, alignment)
        ##SetFixedSize for no resizing
    grid = QtGui.QGridLayout()
    if errorText:
        errorBox = QtGui.QHBoxLayout()
        errorBox.addWidget(errorLabel)
        if platform.system() != "Linux":
            errorLabel.setText("Pdf conversion is only supported on linux. An html file will still be generated.")
        grid.addLayout(errorBox, 0, 0, 1, 2)
    grid.addWidget(marginGroup, 1, 0)
    grid.addWidget(pSizeGroup, 2, 0)
    grid.addWidget(otherGroup, 1, 1, 2, 1)
    grid.addWidget(buttonBox, 3, 1)
    grid.setSizeConstraint(QLayout.SetMinimumSize)
    optionsDialog.setLayout(grid)

    #get initial setting from file if it exists
    settingsPath = os.path.join(mw.pm.profileFolder(), "print_to_pdf", "settings.txt")
    if os.path.isfile(settingsPath):
        defaults = []
        with open(settingsPath, "r") as buf:
            for i, line in enumerate(buf.read().splitlines()):
                if i < len(leWidgets):
                    leWidgets[i].setText(line)
                else:
                    defaults.append(int(line))
        for i, key in enumerate(radKeys):
            radGroups[key].button(defaults[i]).setChecked(True)
    else:
        for i, key in enumerate(radKeys):
            radGroups[key].button(1).setChecked(True)

    if WK == "not-installed" or not PDF:
        radGroups["output"].button(2).setEnabled(False)

    while True:
        signal = optionsDialog.exec_()

        #if print button is pressed
        if signal:
            #convert widget text to list
            oList = []
            for widget in leWidgets:
                if widget.text():
                    oList.append(float(widget.text()))
            #cancel print and show error if any fields are blank
            if len(oList) != len(leWidgets):
                errorMsg = QtGui.QErrorMessage(optionsDialog)
                errorMsg.showMessage("No fields can be left empty. Please fill out all options.")
                continue
            for key in radKeys:
                oList.append(radGroups[key].checkedId())

            #overwrite settings file only if printed
            outputPath = os.path.join(mw.pm.profileFolder(), "print_to_pdf")
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
            settingsPath = os.path.join(outputPath, "settings.txt")
            with open(settingsPath, "w") as buf:
                for option in oList:
                    buf.write(str(option) + "\n")

            printToFile(oList)
            break
        else:
            break

q = QAction(mw)
q.setText("Print to file(pdf)")
q.setShortcut(QKeySequence("Ctrl+U"))
mw.form.menuTools.addAction(q)
mw.connect(q, SIGNAL("triggered()"), showDialog)
