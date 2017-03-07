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

"""Turns Anki cards into printable formats."""

import re
from anki.utils import ids2str
from aqt import mw
from aqt.utils import getBase
from print_to_file.shelltools import call_wkhtmltopdf

#output pdf file
def create_pdf(dimensions, units, path_dict):
    """Converts an html document into pdf."""

    #options for pdf conversion
    options = [
        "--margin-left",
        "--margin-right",
        "--margin-top",
        "--margin-bottom",
        "--page-width",
        "--page-height",
    ]

    #build wkhtml arguments from user input argument
    arguments = []
    for dimension, option in zip(dimensions, options):
        arguments.append(option)
        arguments.append(dimension + units)
    arguments.extend(["--zoom", "1.2", path_dict["html"], path_dict["pdf"]])

    #send arguments to call wkhtmltopdf
    call_wkhtmltopdf(path_dict["wkhtmltopdf"], arguments)

    return

#output html file
def create_html(dimensions, units, image_handling, style_text, output_path):
    """Creates a formatted html file fron Anki content."""

    #convert strings to float values
    dimensions = [float(x) for x in dimensions]

    #create adjusted html table values with subtracted margins
    table_width = dimensions[4]-(dimensions[0]+dimensions[1])
    table_height = dimensions[5]-(dimensions[2]+dimensions[3])

    #replace all variables in the style text with their values
    style_text = (
        style_text.replace("$HEIGHT", str(table_height))
        .replace("$WIDTH", str(table_width))
        .replace("$UNITS", units)
    )

    #pulls list of card ids from DB
    card_ids = get_card_id_list(mw.col.decks.selected())

    #pull out style. seperate out images, if selected
    processed_cards = process_card_ids(card_ids, image_handling)

    html_block = generate_html_block(style_text, processed_cards)

    with open(output_path, "w") as buf:
        buf.write(html_block)

    return


#iterates through card text and generates the html
def generate_html_block(style_text, processed_cards):
    """Iterates through all cards to generate the html table layout."""

    #html header
    header = (
        "<html>\n"
        "<head>\n"
        "\t<meta charset=\"utf-8\">\n"
        "\t{0}\n"
        "</head>\n"
        "<style type=\"text/css\">\n"
        "{1}\n"
        "</style>\n"
    ).format(getBase(mw.col), style_text.encode("utf8"))

    html_block = [header]

    #loop through all cards and add to html block
    for i, (question, answer,
            front_images, back_images) in enumerate(processed_cards):

        #front side table section
        html_block.append("<table>\n" + "<tr class=\"front\">\n")
        if question:
            html_block.append("\t<td>\n\t\t{0}\n\t</td>\n".format(question))
        if front_images:
            for front_image in front_images:
                html_block.append(
                    "\t<td>\n\t\t{0}\n\t</td>\n".format(front_image))
        html_block.append("</tr>\n" + "</table>\n")

        #back_side table section
        if i+1 < len(processed_cards):
            html_block.append("<table>\n")
        else:
            #avoid line break on last page
            html_block.append("<table style=\"page-break-after: avoid\">\n")
        html_block.append("<tr class=\"back\">\n")
        if answer:
            html_block.append("\t<td>\n\t\t{0}\n\t</td>\n".format(answer))
        if back_images:
            for back_image in back_images:
                html_block.append(
                    "\t<td>\n\t\t{0}\n\t</td>\n".format(back_image))
        html_block.append("</tr>\n" + "</table>\n")

    html_block.append("</body>\n" + "</html>")

    return "".join(html_block)


#returns sorted list of card ids from selected deck and child decks
def get_card_id_list(deck_id):
    """Creates a list of cards from Anki deck and subdecks."""

    #create deck list with selected deck to start
    deck_ids = [deck_id]

    #iterate through sub-decks and append deck ids
    for _, child_id in mw.col.decks.children(deck_id):
        deck_ids.append(child_id)

    #query for card ids and sort by card front text
    query = ("select c.id from cards c, "
             "notes n where did in {0} and "
             "c.nid = n.id order by n.sfld").format(ids2str(deck_ids))

    #return ids from tables with query
    return mw.col.db.list(query)


#pull images out of the notes into lists
def slice_out_images(note):
    """Separates note text and images into different components."""

    #check for images in note
    if re.match('.*<img src=".*', note):

        #split by html element and replace delimiter
        sub_notes = note.split("<")
        for i, sub_note in enumerate(sub_notes[1:]):
            sub_notes[i+1] = "<" + sub_note

        #iterate through sub_notes and seperate out img and div tags
        images = []
        for sub_note in sub_notes:
            if re.match('.*<img src=".*', sub_note):
                k = sub_notes.index(sub_note)
                if sub_notes[k-1] == "<div>" and sub_notes[k+1] == "</div>":
                    images.append(''.join(sub_notes[k-1: k+2]))
                    del sub_notes[k-1: k+2]
                else:
                    images.append(sub_notes[k])
                    del sub_notes[k]

        #join note back into a string
        note = ''.join(sub_notes)

        #if no note, just return the images
        if note:
            return (note, images)
        else:
            return (None, images)

    #if no image, just return the note
    return (note, None)


#strips hrs, style and seperates images if option is selected
def process_card_ids(card_ids, image_handling):
    """Removes style and hr blocks, and seperates images if selected."""

    processed_cards = []
    for card_id in card_ids:
        card = mw.col.getCard(card_id)
        question = re.sub("(?si)^.*<hr id=answer>\n*", "", card.q().encode("utf8"))
        question = re.sub("(?si)<style.*?>.*?</style>", "", question).strip()
        answer = re.sub("(?si)^.*<hr id=answer>\n*", "", card.a().encode("utf8"))
        answer = re.sub("(?si)<style.*?>.*?</style>", "", answer).strip()

        #separate images and text into strings if option is selected
        if image_handling:
            (question, front_images) = slice_out_images(question)
            (answer, back_images) = slice_out_images(answer)
        else:
            front_images = None
            back_images = None

        processed_cards.append((question, answer, front_images, back_images))

    return processed_cards

