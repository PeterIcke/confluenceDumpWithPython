import os
from bs4 import BeautifulSoup

driver_manual_directory = os.path.join(os.getcwd(), "output\\DM\\")
# Get all the files in the driver directory
html_files = []
# r = root, d = directories, f = files
for r, d, f in os.walk(driver_manual_directory):
    for file in f:
        if file.endswith(".html"):
            found = os.path.join(r, file)
            html_files.append(found)

for html_file in html_files:
    with open(html_file, encoding="utf8") as open_file:
        soup = BeautifulSoup(open_file, 'html.parser')
        if soup.body is None:
            print("ERROR: No page body found. " + html_file)
            continue

        found_div = soup.body.find("div", class_="view")
        if found_div is None:
            print("ERROR: view / content class div not found. " + html_file)
            continue

        new_tag = soup.new_tag('h1', id="page-title")
        if soup.title.string is None:
            print("ERROR: Page title is invalid. " + html_file)
            continue

        if soup.find('h1', id="page-title") is not None:
            print("WARN: Page title has already been added for: " + html_file)
            continue

        new_tag.string = soup.title.string
        found_div.insert(1, new_tag)
        print("Successfully added a title div to " + html_file)

    with open(html_file, 'w', encoding="utf8") as output_file:
        output_file.write(soup.prettify())
