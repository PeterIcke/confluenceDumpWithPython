import os
import logging
import argparse
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('--folder', type=str, default='output/DM',
                    help='Folder to scan and update the html files', required=True)
parser.add_argument('--loglevel', default='warning',
                    choices=['critical', 'error', 'warning', 'info', 'debug'],
                    help='Provide logging level. Example --loglevel debug, default=warning')
parser.add_argument('--logformat',
                    help='Provide the logging format. See the documentation of the logging module for more details.')
args = parser.parse_args()
dir = args.folder

logging.basicConfig(level=args.loglevel.upper(), format=args.logformat)

documentation_directory = os.path.join(os.getcwd(), dir)
# Get all the files in the driver directory
html_files = []
# r = root, d = directories, f = files
for r, d, f in os.walk(documentation_directory):
    for file in f:
        if file.endswith(".html"):
            found = os.path.join(r, file)
            html_files.append(found)

for html_file in html_files:
    with open(html_file, encoding="utf8") as open_file:
        soup = BeautifulSoup(open_file, 'html.parser')
        if soup.body is None:
            logging.error("No page body found. " + html_file)
            continue

        found_div = soup.body.find("div", class_="view")
        if found_div is None:
            logging.error("view / content class div not found. " + html_file)
            continue

        new_tag = soup.new_tag('h1', id="page-title")
        if soup.title.string is None:
            logging.error("Page title is invalid. " + html_file)
            continue

        if soup.find('h1', id="page-title") is not None:
            logging.warning("Page title has already been added for: " + html_file)
            continue

        new_tag.string = soup.title.string
        found_div.insert(1, new_tag)
        logging.info("Successfully added a title div to " + html_file)

    with open(html_file, 'w', encoding="utf8") as output_file:
        output_file.write(soup.prettify())
