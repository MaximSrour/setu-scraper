"""
This script scrapes the data from the Monash University SETU website and outputs it to a CSV file.
"""

import requests
from bs4 import BeautifulSoup
import csv

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

def get_html(url: str) -> BeautifulSoup:
    """
    Makes a request to the specified URL and returns the response.

    @param {str} url - The URL to make the request to
    @returns {BeautifulSoup} - The response from the request
    """

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup

def cleanse(document: BeautifulSoup):
    """
    Takes a BeautifulSoup object and removes all unnecessary elements from the HTML.

    @param {BeautifulSoup} soup - The BeautifulSoup object to cleanse
    """

    for div in document.find_all('div', class_='FrequencyBlock_chart'):
        div.decompose()

    for caption in document.find_all('caption'):
        caption.decompose()

def get_report_details(document: BeautifulSoup):
    """
    Takes a BeautifulSoup object and returns a tuple containing the unit code, year, semester, and campus.

    @param {BeautifulSoup} soup - The BeautifulSoup object to extract data from
    @returns {tuple} - A tuple containing the unit code, year, semester, and campus
    """

    # Find the first div with class "report-block"
    report_block_div = document.find('div', class_='report-block')
    report_trs = report_block_div.find("table").find_all("tr")

    offering_list = report_trs[3].text.split("_")
    timeframe_list = [x for x in report_trs[1].text.split(" ") if x.strip()]

    unit = offering_list[0]
    year = timeframe_list[3]
    semester = timeframe_list[1][0] + timeframe_list[2]
    match(offering_list[1]):
        case "CLAYTON":
            campus = "CL"
        case "MALAYSIA":
            campus = "MA"

    return (unit, year, semester, campus)

def get_tables_from_report(report_block):
    """
    Takes a report block div and returns a list of tables.

    @param {BeautifulSoup} report_block - The report block div to extract data from
    @returns {list} - A list of tables
    """

    # Find the parent div with class "FrequencyBlockRow"
    parent_divs = report_block.find_all('div', class_='FrequencyBlockRow')

    internal_divs = []
    for parent_div in parent_divs:
        internal_divs.extend(parent_div.find_all('div', class_='FrequencyBlock_HalfMain'))

    # For each div with class "FrequencyBlock_HalfMain", save the text in the div "FrequencyQuestionTitle" in an object. Save each object in a list. Save this list as a CSV file.
    tables = []
    for div in report_block.find_all('div', class_='FrequencyBlock_HalfMain'):
        tables.append(create_table(div))

    return tables
    
def create_table(container: BeautifulSoup) -> Table:
    """
    Takes a container div and returns a Table object

    @param {BeautifulSoup} container - The div container from which to extract data
    @returns {Table} - A Table object containing the extracted data
    """

    title = container.find('div', class_='FrequencyQuestionTitle').find("span", class_="question-index").text

    block_table_divs = container.find_all('table', class_='block-table')

    statsTRs = block_table_divs[1].find('tbody').find_all('tr')
    mean = statsTRs[1].find('td').text
    median = statsTRs[2].find('td').text

    countsTRs = block_table_divs[0].find('tbody').find_all('tr')

    # For each tr in countsTRs, find the th tag text to determine which aspect this refers to. Then, get the value of the second TD
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

    return table

def tranform_html_to_data(url: str) -> list:
    """
    Takes a URL and returns a list of lists containing the data extracted from the HTML.
    
    @param {str} url - The URL to extract data from
    @returns {list} - A list of lists containing the extracted data
    """

    output = []

    soup = get_html(url)

    # cleanse(soup)

    report_blocks = soup.find_all('div', class_='report-block')[1:3]

    for table in get_tables_from_report(report_blocks[0]):
        output.append([*get_report_details(soup), "U", table.table_name, table.sa, table.a, table.n, table.d, table.sd, table.mean, table.median])

    for table in get_tables_from_report(report_blocks[1]):
        output.append([*get_report_details(soup), "F", table.table_name, table.sa, table.a, table.n, table.d, table.sd, table.mean, table.median])

    return output

def get_user_url_inputs() -> str:
    """
    Gets the user's input for any number of urls.

    @returns {str} - The URL entered by the user
    """

    urls = []

    while True:
        url = input("Enter a URL: ")

        if url == "":
            break

        urls.append(url)

    return urls

def main():
    urls = get_user_url_inputs()

    data = []
    for url in urls:
        try:
            data.extend(tranform_html_to_data(url))
        except:
            print("Error parsing URL: " + url)

    with open("output.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["unit", "year", "semester", "campus", "aspect_type", "aspect", "strongly agree", "agree", "neutral", "disagree", "strongly disagree", "mean", "median"])

        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    main()