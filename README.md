# print_to_file #

print_to_file exports cards from a selected deck and its child decks. 
It will always generate an html file that can be converted to a pdf if 
the optional dependency is met. wkhtmltopdf is used for an automated pdf 
conversion. The main purpose for creating this addon is to have 
customizable page size and margins.

The html file is generated with a customizable css style block. The
question and answer sections are split into separate pages. This is so
the cards can be printed to the front and back of pages. Each section 
has a page break between it. When viewing the html file in a browser,
print or print preview needs to be selected before the page breaks will
be visible. If printing from html, the page size and margins in the
viewer need to match what is entered into print_to_file.

I have included an option to separate images and note text into their
own table cells. I have found it useful for index cards printed in
landscape with one or two images. This addon was created for my own use,
but if there are situations that should be accommodated better, please
let me know.

The output and settings files will be placed into the Anki user profile
directory under the directory print_to_file.

## Optional Pdf Dependency: ##

**wkhtmltopdf**  
wkhtmltopdf can be placed in {Anki addon path}/print_to_file or in any  
executable path that **where** or **which** can locate wkhtmltopdf.  
http://wkhtmltopdf.org/

## Changelog: ##

**2.1 - Switched to qt ui**  
&nbsp;&nbsp;- PyQt4/PyQt5 compatability  
2.0 - Complete rewrite of addon code  
&nbsp;&nbsp;- Switched to a package layout of files  
&nbsp;&nbsp;- Switched to a tab menu  
&nbsp;&nbsp;- Added pdf support for windows  
1.02 - Added text box for easier editing of css style section  
1.01 - Centered front page text  
1.0 - Initial working addon
