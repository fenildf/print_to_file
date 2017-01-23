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
# * The html table inch isn't the same as the printable inch.                  #
# * There is no configurable dialog box for page size and margins.             #
# * The method of rearranging images can't be turned off.                      #
# * There is no method to disable pdf conversion dependencies.                 #
#                                                                              #
#==============================================================================#

import re, urllib
from aqt.qt import *
from anki.utils import isWin
from anki.hooks import runHook, addHook
from aqt.utils import getBase, openLink
from aqt import mw
from anki.utils import ids2str
import pdfkit

#TODO make these interactive to adjust
MARGIN = .25
HEIGHT = 4
WIDTH = 6
BORDER = False

#factor to adjust the table inch to pdf inch (default is 1.21)
FUDGE = 1.21

#options for pdf conversion
OPTIONS = {
    'page-height': '{0}in'.format(str(HEIGHT)),
    'page-width': '{0}in'.format(str(WIDTH)),
    'margin-top': '{0}in'.format(str(MARGIN)),
    'margin-right': '{0}in'.format(str(MARGIN)),
    'margin-bottom': '{0}in'.format(str(MARGIN)),
    'margin-left': '{0}in'.format(str(MARGIN)),
}  

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

        #join note and images back into a string
        note = ''.join(subNotes)
        images = ''.join(images)

        #if no note, just return the images
        if len(note) == 0:
            return (None, images)
        else:
            return (note, images)

    #if no image, just return the note
    return (note, None)

#excution begins here when triggered in anki
def onPrint():

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
    header += u"\t" + '<meta charset="utf-8">' + "\n"
    header += u"\t{0}\n".format(getBase(mw.col))
    header += u"</head>\n"

    #style section
    style = u"<style>\n"
    style += u"\timg { width: 100%; }\n"
    style += u"\ttd { text-align: center; vertical-align: middle; }\n"
    style += u"\ttd tr { page-break-after: avoid; }\n"
    if BORDER:
        style += u"\ttd { border: 1px solid black; }\n"
    style += u"\ttable {{ page-break-after: always; width: {0}in; height: {1}in; table-layout: fixed; }}\n" \
        .format(str((WIDTH-MARGIN*2)*FUDGE), str((HEIGHT-MARGIN*2)*FUDGE))
    style += u"</style>\n"

    #start writing to html file
    buf = open(htmlPath, "w")
    buf.write(header.encode("utf8"))
    buf.write(style.encode("utf8"))

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
            rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(qImages)
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
            rowHtml += u"\t<td>\n\t\t{0}\n\t</td>\n".format(aImages)
        rowHtml += u"</tr>\n"
        rowHtml += u"</table>\n"

        #write card html to file
        buf.write(rowHtml.encode("utf8"))

        #progress bar update
        mw.progress.update("Cards exported: {0}".format(i+1))

    #close out html file writing
    buf.write("</html>".encode("utf8"))
    buf.close()

    #progress bar finish
    mw.progress.finish()

    #convert html to pdf
    pdfkit.from_file(htmlPath, pdfPath, options=OPTIONS)

    #opens pdf
    openLink(uniPathPrefix(pdfPath))

q = QAction(mw)
q.setText("Print")
q.setShortcut(QKeySequence("Ctrl+U"))
mw.form.menuTools.addAction(q)
mw.connect(q, SIGNAL("triggered()"), onPrint)
