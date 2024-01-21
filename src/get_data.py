"""
This script scrapes the SETU data from the Monash SETU site, using links provided by another script
"""

import os
import csv
import requests
from bs4 import BeautifulSoup

from config import DIR_FILTERED_LINKS, DIR_OUTPUT
PATH_ASPECT_DATA = os.path.join(DIR_OUTPUT, "aspectData.csv")
PATH_OFFERINGS = os.path.join(DIR_OUTPUT, "offerings.csv")

class Table:
    def __init__(self, table_name, mean, median, sa = 0, a = 0, n = 0, d = 0, sd = 0):
        self.table_name = table_name
        self.sa = sa if sa else 0
        self.a = a if a else 0
        self.n = n if n else 0
        self.d = d if d else 0
        self.sd = sd if sd else 0
        self.mean = mean
        self.median = median

    def get_data(self):
        return [self.table_name, self.sa, self.a, self.n, self.d, self.sd, self.mean, self.median]

def get_html(url: str) -> BeautifulSoup:
    """
    Makes a request to the specified URL and returns the response.

    @param {str} url - The URL to make the request to
    @returns {BeautifulSoup} - The response from the request
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup

def get_report_details(url_object: tuple):
    """
    Takes a URL object and returns a tuple containing the following data:
    - unit
    - year
    - semester
    - campus
    - mode
    - title

    @param {tuple} url_object - The URL object to extract data from
    @returns {tuple} - A tuple containing the extracted data
    """

    unit = url_object[1].split("_")[0]
    year = url_object[0].split("_")[0]
    semester = url_object[1].split("_")[-1].split("-")[0]
    match(url_object[1].split("_")[1]):
        case "CLAYTON":
            campus = "CL"
        case "MALAYSIA":
            campus = "MA"
        case "CAULFIELD":
            campus = "CA"
        case _:
            campus = ""
            print(f"Unknown campus: {url_object[1].split('_')[1]}")
    mode = url_object[1].split("_")[2]
    
    # Get the title from the document, provided it exists
    if url_object[3] != "":
        soup = get_html(url_object[3])
        title = soup.find('table').find_all('tr')[4].find('td').text
    else:
        title = ""

    return (unit, year, semester, campus, mode, title)

def get_tables_from_report(blocks: list):
    """
    Takes a list of div containers and returns a list of Table objects

    @param {list} blocks - The list of div containers to extract data from
    @returns {list} - A list of Table objects containing the extracted data
    """

    tables = []
    for i, block in enumerate(blocks):
        title = str(i + 1)

        table_divs = block.find_all('table')

        # Remove occasional header row in the tbody
        for table in table_divs:
            try:
                table.find_all('tr', class_='CondensedTabularHeaderRows')[0].decompose()
            except:
                pass

        # Extract mean and median from stats table
        statsTRs = table_divs[1].find_all('tr')
        mean = statsTRs[1].find('td').text
        median = statsTRs[2].find('td').text

        # Extract aspect counts from counts table
        countsTRs = table_divs[0].find_all('tr')
        counts = dict()
        for tr in countsTRs:
            aspect = tr.find('th').text
            value = tr.find_all('td')[1].text

            counts[aspect] = value
        
        table = Table(title,
            mean,
            median,
            sa=counts.get("Strongly Agree"),
            a=counts.get("Agree"),
            n=counts.get("Neutral"),
            d=counts.get("Disagree"),
            sd=counts.get("Strongly Disagree")
        )

        tables.append(table)

    return tables
    
def version1(url_object, soup):
    blocks = []
    for block in soup.find_all('div', class_='FrequencyBlock_HalfMain'):
        blocks.append(block)

    header_results = get_report_details(url_object)[:-1]

    output = []

    for table in get_tables_from_report(blocks[:8]):
        if table == None:
            continue
        output.append([*header_results, "U", *table.get_data()])

    for table in get_tables_from_report(blocks[-5:]):
        if table == None:
            continue
        output.append([*header_results, "F", *table.get_data()])

    return output

def tranform_html_to_data(url_object: tuple) -> list:
    """
    Takes a URL and returns a list of lists containing the data extracted from the HTML.
    
    @param {str} url - The URL to extract data from
    @returns {list} - A list of lists containing the extracted data
    """

    if url_object[3] == "":
        return []

    soup = get_html(url_object[3])

    blocks = []
    for block in soup.find_all('div', class_='FrequencyBlock_HalfMain'):
        blocks.append(block)

    header_results = get_report_details(url_object)[:-1]

    output = []

    # Gets the uni aspects
    for table in get_tables_from_report(blocks[:8]):
        if table == None:
            continue
        output.append([*header_results, "U", *table.get_data()])

    # Gets the faculty aspects
    for table in get_tables_from_report(blocks[8:]):
        if table == None:
            continue
        output.append([*header_results, "F", *table.get_data()])

    return output

def get_url_objects_from_filter_dir():
    """
    Gets all the urls from the filter directory.

    @returns {list} - A list of all the urls
    """

    url_objects = []

    for filename in os.listdir(DIR_FILTERED_LINKS):
        with open(os.path.join(DIR_FILTERED_LINKS, filename), "r") as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                url_objects.append([filename] + row)

    return url_objects

def main():
    url_objects = get_url_objects_from_filter_dir()

    with open(PATH_OFFERINGS, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["unit", "year", "semester", "campus", "mode", "title", "ce_email"])

    with open(PATH_ASPECT_DATA, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["unit", "year", "semester", "campus", "mode", "aspect_type", "aspect", "strong_agree", "agree", "neutral", "disagree", "strong_disagree", "mean", "median"])

    for url_object in url_objects:
        print(f"Working on {url_object[1]}...")

        try:
            offering = get_report_details(url_object)
            with open(PATH_OFFERINGS, "a", newline="") as file:
                writer = csv.writer(file)
                
                writer.writerow(list(offering) + [""])

            data = tranform_html_to_data(url_object)
            if len(data) == 0:
                continue

            with open(PATH_ASPECT_DATA, "a", newline="") as file:
                writer = csv.writer(file)
                
                for row in data:
                    writer.writerow(row)

        except Exception as e:
            print(e)
            print("Error parsing URL Object: " + " - ".join(url_object))
            break

if __name__ == "__main__":
    main()
