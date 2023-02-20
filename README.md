# html2mdfm
Convert Zoho Notebook HTML export to (Markdown + Front Matter) that can be imported to Joplin

Some features:
- It should work witn any OS, provided Python >= 3.8 is installed
- Attachments are copied and should be imported into Joplin properly
- A list of links are added to the end of the note (workaround for Web/Bookmark notes, can be disabled)
- Properly convert ToDo lists (note with checkbox list)
- Properly import reminders (the code tries to import the times converting them to Zulu timezone, but please check them in Joplin after importing since, for me at least, the expored HTML used a timezone that has nothing to do with my settings in Notebook)
- A line break is added between `</div><div>` found in the original HTML to better display lists, etc (can be disabled)
- Illegal characters from notebook and note titles are replaced by a space (or removed from the title) to avoid errors when importing into Joplin

Known limitation: it seems that the exported HTML files contain the creation and modification date for the notebook only, and not for the note itself, so the note creation and update dates are lost when exporting the notes from Zoho.


## Requirements
- Python >= 3.8
- BeautifulSoup (bs4)
- rich (Console theming)
- markdownify

It is recommended that you use a virtual environment to install dependecies with `pip`, unless you are sure all dependencies are installed system-wide (PS: _never_ use `sudo pip`).


## How to install
1. Clone the repo or download the zipped code and extract its contents
2. Go to the directory with the cloned/unzipped files, i.e. `cd html2mdfm`
3. Make sure the file is executable: `chmod u+x ./html2mdfm.py`
4. Create the virtual environemnt and install dependencies (optional)
```
virtualenv -p python3 .
source ./bin/activate
pip install --upgrade pip setuptools
pip install --upgrade bs4 markdownify rich
```
PS: when you finish using the utiliy, either use `deactivate` to exit the virtual environment or close/exit the terminal.


## How to use
If you haven't exported the notebooks from Zoho yet, then follow [these instructions](https://help.zoho.com/portal/en/kb/notebook/import-and-export/articles/export-all-your-notecards-from-notebook).

```
usage: html2mdfm.py [-h] [--nolinebreaks] infolder [outfolder]

Convert Zoho Notebook HTML export to (Markdown + Front Matter) that can be imported to Joplin

positional arguments:
  infolder        Folder that contains the exported HTML files
  outfolder       Destination folder [if not provided, the current folder will be used]

options:
  -h, --help      show this help message and exit
  --nolinebreaks  Disables adding line breaks between divs (text lines may get merged into blocks)
```

Example:
```
./html2mdfm.py 188155

```
will convert the files from the folder **188155** located at the current directory to a folder named **export_data**, also in the currect directory, that can be later imported to Joplin.


### Acknowledgements
- [main.py by use](https://discourse.joplinapp.org/t/how-to-export-notes-from-the-zoho-notebook-in-joplin/22409/3) - Base code


### License

MIT © [lfom](https://lfom.tk)
