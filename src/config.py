"""
A source file to contain the necessary configs for all scripts
"""

import os

def generate_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

DIR_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_OUTPUT = os.path.join(DIR_ROOT, "output")
DIR_LINK_OUTPUT = os.path.join(DIR_OUTPUT, "links")
DIR_RAW_LINKS = os.path.join(DIR_LINK_OUTPUT, "raw")
DIR_FILTERED_LINKS = os.path.join(DIR_LINK_OUTPUT, "filtered")

generate_dir(DIR_OUTPUT)
generate_dir(DIR_LINK_OUTPUT)
generate_dir(DIR_RAW_LINKS)
generate_dir(DIR_FILTERED_LINKS)

SEMESTERS = {
    "2023_other": "https://monash.bluera.com/monash/rpvl.aspx?rid=5936ffd9-90dc-444c-9538-fe71c344720b&regl=en-US",
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

CAMPUS_MAPPING = {
    "CLAYTON": "CL",
    "CAULFIELD": "CA",
    "MALAYSIA": "MA",
    "PARKVILLE": "PA",
    "PENINSULA": "PE",
    "BERWICK": "BE",
    "CITY": "CBD",
    "SOUTHBANK": "SB",
    "NOTT HILL": "NH",
    "ALFRED": "AL",
    "MMS-ALFRED": "MMS",
    "MMC": "MMC",
    "GIPPSLAND": "GI",
    "SAFRICA": "SA",
    "PRATO": "PR",
    "MC-JAKARTA": "JA",
    "OS-SLA-CMB": "SLA",
    "OS-CHI-SEU": "SEU",
    "OS-SGP": "SGP",
    "OS-HKG": "HKG",
    "OTHER-OS": "OS",
    "ONLINE": "ON",
    "MOE": "MOE"
}