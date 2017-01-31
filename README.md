# Print_to_pdf
Addon intended for printing anki decks on adjustable sized pdf pages

The selected deck will be formatted to an html file. The html file will then be converted to a pdf. I chose this last step so that there are less problems due to browser inconsistencies. The pdf has the margins built in, so it should print the same no matter the reader. Either way, the html file will exist, so those who prefer that will have that option.

I wrote this specifically for the purpose of being able to print Anki decks on index cards. Hopefully more people than me find use for it as well.

###Dependencies:

wkhtmltopdf 12.4 with patched qt http://wkhtmltopdf.org/

pdfkit `pip install pdfkit` https://github.com/JazzCore/python-pdfkit
