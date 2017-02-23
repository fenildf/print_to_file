# print_to_file
Addon intended for formatting anki decks in a printable format

print_to_file is an Anki addon that exports cards from a selected deck
and any child decks. It will generate an html file that can get
converted to a pdf file if the optional dependencies are met. pdfkit and
wkhtmltopdf are used for this process. The option is only available to
Linux users. All platforms can use this to create html files. The main
purpose for this addon is to have customizable page size and margins.

The question and answer sections are split into separate pages. I have
included an option to separate images into their own cells. I found it
useful for small landscape page layouts with one or two images. This
addon was created for my own use, but if you find cases that I should
accommodate better, please let me know.

###Optional Linux Pdf Dependencies:

wkhtmltopdf 12.4 with patched qt http://wkhtmltopdf.org/
wkhtmltopdf must be placed in an executable path

pdfkit `pip install pdfkit` https://github.com/JazzCore/python-pdfkit

###Changelog:
1.01 - Centered front page text
1.0 - Initial working addon
