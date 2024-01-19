# Using selenium with firefox, this script will open "https://monash.bluera.com/monash/rpvl.aspx?rid=8da682a1-c771-41c2-9bb1-1becb27b1ad0&regl=en-US"
# Then, using bs4 it will extract the table with id "ctl00_ContentPlaceHolder1_ViewList_ctl01_listing" in the page source and leave a placeholder for processing
# Then, it will find the button with id "ctl00_ContentPlaceHolder1_ViewList_ctl01_listing_ctl14_btnNext" and click it to load a new page

import csv
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def get_driver() -> webdriver:
    options = Options()
    #options.headless = True # preferred
    options.add_argument("--disable-gpu")  # Last I checked this was necessary.
    options.add_argument("-profile")
    options.add_argument("/home/msrour/snap/firefox/common/.mozilla/firefox/1fdc0a4l.default")

    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)
    #set path to /usr/bin/firefox
    options.binary_location = "/usr/bin/firefox"

    driver = webdriver.Firefox(service=Service("/usr/local/bin/geckodriver"), options=options)

    return driver

def wait_for_page_load(driver: webdriver, delay: int):
    try:
        myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "ctl00_headerImage")))
    except TimeoutException:
        print("Loading took too much time!")
        exit(1)

def save_table(table: BeautifulSoup):
    trs = table.find_all('tr')
    trs[-1].decompose()
    trs[1].decompose()
    trs[0].decompose()

    #remove the first td in each tr
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        tds[-1].decompose()
        tds[2].decompose()
        tds[0].decompose()

    return table

    #save table to a new html file, by savnig into the body tag
    new_soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    new_soup.body.append(table)
    with open("table.html", "w") as file:
        file.write(str(new_soup))

def save_table_to_csv(table: BeautifulSoup):
    with open("table.csv", "a", newline="") as file:
        for tr in table.find_all('tr'):
            data = []

            tds = tr.find_all('td')
            data.append("\"" + tds[0].text + "\"")

            a = tr.find('a')
            try:
                if a:
                    data.append("\"" + a['href'] + "\"")
            except Exception as e:
                data.append("")

            file.write(",".join(data) + "\n")

def run_driver(driver: webdriver):
    try:
        driver.get("https://monash.bluera.com/monash/rpvl.aspx?rid=8da682a1-c771-41c2-9bb1-1becb27b1ad0&regl=en-US")

        with open("table.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["unit_title", "conditions_met", "link_fragment"])

        while True:
            try:
                wait_for_page_load(driver, 5)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                table = soup.find(id="ctl00_ContentPlaceHolder1_ViewList_ctl01_listing")

                save_table_to_csv(save_table(table))

                button = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_ViewList_ctl01_listing_ctl14_btnNext")
                button.click()

            except Exception as e:
                print(e)
                break
    
    except Exception as e:
        print(e)
        pass

    driver.quit()

run_driver(get_driver())