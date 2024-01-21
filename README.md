# SETU Data Scraper

The purpose of this project is to enable easier data scraping from the SETU reports provided by Monash university. The data is presented in a HTML/PDF format, making it difficult to extract the data. This code base automates this process and rips that data out to be saved into a CSV file.

More information to come later.

## Steps to install

1. Clone the repository
1. Install the dependencies using `pip install -r requirements.txt`

## Using the tools

To download the links to each of the SETU reports, run `python3 src/get_links.py`. This will generate output files at `output/links/raw/` which contains every offerings SETU report link. This will take a while to run as it has to scrape the entire SETU website.

To filter this data, run `python3 src/filter_data.py`. This will generate output files at `output/links/filtered/` which contains every offerings SETU report based on filters in the code (better solution to come).

To download the SETU reports, run `python3 src/get_data.py`. This will generate output files at `output/` which contains every offerings SETU report. This is based on the filtered data from the previous step.

## Testing

Currently, the tests are no longer functional. They will be implemented in a future PR.
