from bs4 import BeautifulSoup
import glob, sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--folder', type=str, default='output',
                    help='Folder to scan and update the html files', required=True)
parser.add_argument('--recursive', '-r', action='store_true', default=False,
                    help='Will also scan subfolders', required=False)
args = parser.parse_args()
dir = args.folder
recursive = args.recursive

# Make sure the path ends with a '\'
if not dir.endswith("\\"):
    dir += "\\"

print("updating dir: {}".format(dir))

# Go through each html file in the directory.
for file in glob.glob(dir +"*.html", recursive = recursive):
    try:
        # Parse the html file with BeautifulSoup.
        soup = BeautifulSoup(open(file, encoding="utf8"),'html.parser')
        updatedFile = False
        # Note. Update the note div content with a new class and add a 'span' to act as the image container
        for note in soup.findAll('div',attrs={"class":"panel", "style":"background-color: #EAE6FF;border-color: #998DD9;border-width: 1px;"}):
            note['class'] = "confluence-information-macro confluence-information-macro-general"
            del note['style']
            tag = soup.new_tag('span')
            tag['class'] = "aui-icon aui-icon-general confluence-information-macro-icon"
            note.insert(0,tag)
            updatedFile = True
        # Note. Change the inner div class so that the text is alligned the same way as the other info panels.
        for content in soup.findAll('div',attrs={"class":"panelContent", "style":"background-color: #EAE6FF;"}):
            content['class'] = "confluence-information-macro-body"
            del content['style']
            updatedFile = True
        # Update the info pannels with the correct icon class.
        # Error. 
        for error in soup.findAll('span',attrs={"class":"aui-icon aui-icon-small aui-iconfont-error confluence-information-macro-icon"}):
            error['class'] ="aui-icon aui-icon-error confluence-information-macro-icon"
            updatedFile = True
        # Info.
        for info in soup.findAll('span',attrs={"class":"aui-icon aui-icon-small aui-iconfont-info confluence-information-macro-icon"}):
            info['class'] ="aui-icon aui-icon-info confluence-information-macro-icon"
            updatedFile = True
        # Check.
        for check in soup.findAll('span',attrs={"class":"aui-icon aui-icon-small aui-iconfont-approve confluence-information-macro-icon"}):
            check['class'] ="aui-icon aui-icon-approve confluence-information-macro-icon"
            updatedFile = True
        # Warning.
        for warning in soup.findAll('span',attrs={"class":"aui-icon aui-icon-small aui-iconfont-warning confluence-information-macro-icon"}):
            warning['class'] ="aui-icon aui-icon-warning confluence-information-macro-icon"
            updatedFile = True
        # Write updated data to disk.
        if updatedFile:
            with open(file, "w", encoding='utf-8') as file:
                file.write(soup.prettify())
                print("updated : {}".format(file))
    except:
        print("Failed to update: {}".format(file))
