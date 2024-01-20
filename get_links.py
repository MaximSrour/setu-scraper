# Using selenium with firefox, this script will open "https://monash.bluera.com/monash/rpvl.aspx?rid=8da682a1-c771-41c2-9bb1-1becb27b1ad0&regl=en-US"
# Then, using bs4 it will extract the table with id "ctl00_ContentPlaceHolder1_ViewList_ctl01_listing" in the page source and leave a placeholder for processing
# Then, it will find the button with id "ctl00_ContentPlaceHolder1_ViewList_ctl01_listing_ctl14_btnNext" and click it to load a new page

import csv
import math
from time import sleep
from tqdm import tqdm
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://monash.bluera.com/monash/"

SEMESTERS = {
    "2023_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=caa302c2-ba58-4ef8-978f-369208ca3716&regl=en-US",
    "2023_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=8da682a1-c771-41c2-9bb1-1becb27b1ad0&regl=en-US",
    "2023_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=136f4382-7657-4913-b11b-15deb5b8d462&regl=en-US",
    "2022_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=75af4287-7a33-414d-9750-0d2aefe11000&regl=en-US",
    "2022_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=c1371ed2-02e9-4424-b3cd-81b0bb1a301f&regl=en-US",
    "2022_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=f7ef66fb-18f9-46bf-88f7-58ef83ec16b5&regl=en-US",
    "2021_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=4e5167d0-b7e5-492b-a7b9-659cce231c90&regl=en-US",
    "2021_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=cc7dce80-b9a4-47a5-8f26-3df3354962da&regl=en-US",
    "2021_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=ea281b2c-f7a8-4cf4-8d65-4ee486b5aa54&regl=en-US",
    "2020_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=0e437893-caeb-4e52-b77b-ae42a0ffdb0e&regl=en-US",
    "2020_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=b268b6e4-c662-4774-ae76-94d266f68c33&regl=en-US",
    "2020_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=558472e5-69ab-436e-bf42-4212a0284eaf&regl=en-US",
    "2019_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=c7ce38bc-a312-4a88-93ae-e18575e9e192&regl=en-US",
    "2019_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=f16fd366-e38c-444d-8293-c1366b17d4da&regl=en-US",
    "2019_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=cd9de556-a53f-4ef1-b4d5-eaa9ed149af7&regl=en-US",
    "2018_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=c62cc94b-800f-4b73-9bba-dffeda433eca&regl=en-US",
    "2018_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=0214632f-b17a-4764-ab74-1e107ad5a857&regl=en-US",
    "2018_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=de081d80-a5f5-4348-8b82-024c956c6c47&regl=en-US",
    "2017_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=9f297a0b-0b97-40c6-883e-443ce6d414c1&regl=en-US",
    "2017_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=46b09f45-de94-4fbd-b314-61e5882c3387&regl=en-US",
    "2017_s1": "https://monash.bluera.com/monash/rpvl.aspx?rid=c8b26628-12b3-44da-8ce7-91a50d45cdaa&regl=en-US",
    "2016_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=1dc10fc3-04a3-4647-ae42-d84267314541&regl=en-US",
    "2016_s2": "https://monash.bluera.com/monash/rpvl.aspx?rid=76c58866-ab40-4b7d-879e-6a1f252f5cd7&regl=en-US",   
}

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

def save_table_to_csv(table: BeautifulSoup, output_file: str = "table.csv"):
    with open(output_file, "a", newline="") as file:
        for tr in table.find_all('tr'):
            data = []

            tds = tr.find_all('td')
            text = tds[0].text.split(" : ")
            data.append(text[1])
            data.append("\"" + text[2] + "\"")

            a = tr.find('a')
            try:
                if a:
                    data.append(f"\"{BASE_URL}{a['href']}\"")
            except Exception as e:
                data.append("")

            file.write(",".join(data) + "\n")

def run_driver(driver: webdriver, url, output_file: str = "table.csv"):
    try:
        driver.get(url)

        #save to output dir, make sure it exists
        if not os.path.exists("output"):
            os.makedirs("output")
        output_file = f"output/{output_file}"

        with open(output_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["offering_id", "faculty_full", "link_fragment"])

            wait_for_page_load(driver, 5)
            
            cycles_to_complete = math.ceil(int(driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_ViewList_ctl01_lblTopPageStatus").text.split(" ")[-2])/10)
            cycles = 0

        with tqdm(total=cycles_to_complete) as pbar:
            while True:
                try:

                    html = driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    table = soup.find(id="ctl00_ContentPlaceHolder1_ViewList_ctl01_listing")

                    save_table_to_csv(save_table(table), output_file)

                    button = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_ViewList_ctl01_listing_ctl14_btnNext")
                    button.click()

                    wait_for_page_load(driver, 5)

                except Exception as e:
                    print(e)
                    break
                
                cycles += 1
                pbar.update(1)

                # if(cycles >= 5):
                #     break
    
    except Exception as e:
        print(e)
        pass

driver = get_driver()

for semester in SEMESTERS:
    print(f"Processing {semester}...")
    run_driver(driver, SEMESTERS[semester], f"{semester}.csv")

driver.quit()