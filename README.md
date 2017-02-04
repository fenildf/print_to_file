# print_to_file
Addon intended for printing anki decks in a printable format

This addon exports cards from a selected deck and child decks. An html file will be generated in the user profile directory. pdfkit and wkhtmltopdf are optional dependencies for a pdf format. Currently, the pdf output only works on Linux. The cards are organized with question and answer on seperate pages. The note text is left-aligned so that bullet points look correct. Note text and images are split to fit better for small page sizes.

###Linux Pdf Dependencies:

wkhtmltopdf 12.4 with patched qt http://wkhtmltopdf.org/

pdfkit `pip install pdfkit` https://github.com/JazzCore/python-pdfkit
