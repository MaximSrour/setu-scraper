import csv
import math
from time import sleep
from tqdm import tqdm
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from config import get_semester_links, setup, DIR_RAW_LINKS, BASE_URL

def get_driver() -> webdriver:
    """
    Returns a webdriver with the correct options set

    @returns {webdriver} - A webdriver with the correct options set
    """

    options = Options()

    #options.headless = True # preferred true, but false is nice to monitor progress visually
    options.add_argument("--disable-gpu") # TODO: check if this is actually necessary
    options.add_argument("-profile")
    options.add_argument("/home/maxim/snap/firefox/common/.mozilla/firefox/n6wbpn07.default")

    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)

    options.binary_location = "/usr/bin/firefox"

    driver = webdriver.Firefox(service=Service("/usr/local/bin/geckodriver"), options=options)

    return driver

def wait_for_page_load(driver: webdriver, max_delay: int) -> None:
    """
    Waits for a page to load and blocks the main thread until it does

    @param {webdriver} driver - The webdriver to use
    @param {int} delay - The maximum amount of time to wait for the page to load
    @returns {None}
    """

    try:
        WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.ID, "blueOcean_content")))
    except TimeoutException:
        print("Loading took too much time!")
        exit(1)

def clean_table_html(table: BeautifulSoup) -> BeautifulSoup:
    """
    Cleans the table html of unncessary elements

    @param {BeautifulSoup} table - The table to clean
    @returns {BeautifulSoup} - The cleaned table
    """

    trs = table.find_all('tr')
    trs[-1].decompose()
    trs[1].decompose()
    trs[0].decompose()

    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        tds[-1].decompose()
        tds[2].decompose()
        tds[0].decompose()

    return table

def save_table_to_csv(table: BeautifulSoup, output_file: str = "table.csv") -> None:
    """
    Saves a table to a csv file

    @param {BeautifulSoup} table - The table to save
    @param {str} output_file - The file to save the table to
    @returns {None}
    """

    with open(output_file, "a", newline="") as file:
        for tr in table.find_all('tr'):
            data = []

            tds = tr.find_all('td')
            text = tds[0].text.split(" : ")
            data.append(text[1])
            data.append("\"" + text[2][1:-1] + "\"")

            a = tr.find('a')
            try:
                if a:
                    data.append(f"\"{BASE_URL}{a['href']}\"")
            except Exception as e:
                data.append("")

            file.write(",".join(data) + "\n")

def run_driver(driver: webdriver, url, output_file: str = "table.csv") -> None:
    """
    Runs the driver to get the links

    @param {webdriver} driver - The webdriver to use
    @param {str} url - The url to use
    @param {str} output_file - The file to save the table to
    @returns {None}
    """

    try:
        driver.get(url)
        
        # Set up the output file
        if not os.path.exists("output"):
            os.makedirs("output")

        output_file = os.path.join(DIR_RAW_LINKS, output_file)

        with open(output_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["offering_id", "faculty_full", "link_fragment"])

        wait_for_page_load(driver, 5)
        
        # Pulls the number of items from the page and calculates the number of pages
        cycles_to_complete = math.ceil(int(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ViewList_ctl01_lblTopPageStatus").text.split(" ")[-2])/10)

        # Loop through all pages
        # First page is set up from the initial page load. Every subsequent page is loaded by clicking the next button from the previous iteration
        for cycles in tqdm(range(cycles_to_complete)):
            try:
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                table = soup.find(id="ctl00_ContentPlaceHolder1_ViewList_ctl01_listing")

                save_table_to_csv(clean_table_html(table), output_file)

                button = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_ViewList_ctl01_listing_ctl14_btnNext")
                button.click()

                wait_for_page_load(driver, 5)

            except Exception as e:
                pass

        # This is to ensure that TQDM is at 100% when the loop is done as it takes some time for it to update
        sleep(1)
    
    except Exception as e:
        print(e)
        pass

def main():
    """
    The main function of the script
    
    @returns {None}
    """
    setup()

    semester_links = get_semester_links()

    driver = get_driver()

    for semester in semester_links:
        print(f"Processing {semester}...")
        run_driver(driver, semester_links[semester], f"{semester}.csv")

    driver.quit()

if __name__ == "__main__":
    main()