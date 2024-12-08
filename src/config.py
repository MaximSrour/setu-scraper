"""
A source file to contain the necessary configs for all scripts
"""

import os
import csv

BASE_URL = "https://monash.bluera.com/monash/"

DIR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_OUTPUT = os.path.join(DIR_ROOT, "output")
DIR_LINK_OUTPUT = os.path.join(DIR_OUTPUT, "links")
DIR_RAW_LINKS = os.path.join(DIR_LINK_OUTPUT, "raw")
DIR_FILTERED_LINKS = os.path.join(DIR_LINK_OUTPUT, "filtered")
DIR_HTML = os.path.join(DIR_OUTPUT, "html")

def generate_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def get_semester_links():
    with open("semester_links.csv", "r") as file:
        reader = csv.reader(file)
        links = {}

        next(reader)
        for row in reader:
            links[row[0]] = row[1]

        return links
    
def setup():
    generate_dir(DIR_OUTPUT)
    generate_dir(DIR_LINK_OUTPUT)
    generate_dir(DIR_RAW_LINKS)
    generate_dir(DIR_FILTERED_LINKS)
    generate_dir(DIR_HTML)

if __name__ == "__main__":
    links = get_semester_links()

    for semester, link in links.items():
        print(f"{semester}: {link}")