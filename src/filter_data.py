from config import SEMESTERS, DIR_RAW_LINKS, DIR_FILTERED_LINKS
import csv
import os

# loop through all semester key in the SEMSETER dict
# use each key as the filename (key.csv) in the output dir
# open the csv and filter only a certain subset of rows that contain any unit code in a list, UNITCODES
# output the filtered data to a new csv file, key_filtered.csv in the filter dir

UNITCODES = ["FIT1008", "FIT1054", "FIT1033", "FIT1045", "FIT1053", "FIT1073", "FIT2073", "FIT2096", "FIT5057"]
#UNITCODES = ["FIT1045"]

DIR_RAW_LINKS
DIR_FILTERED_LINKS

if not os.path.exists("filter"):
    os.makedirs("filter")

for semester_key in SEMESTERS:
    filename = f"{semester_key}.csv"
    output_filepath = f"{DIR_RAW_LINKS}/{filename}"
    filter_filepath = f"{DIR_FILTERED_LINKS}/{semester_key}_filtered.csv"

    with open(output_filepath, "r") as input_file, open(filter_filepath, "w", newline="") as output_file:
        csv_reader = csv.reader(input_file)
        csv_writer = csv.writer(output_file)

        for row in csv_reader:
            if any(unit_code in row[0] for unit_code in UNITCODES):
                csv_writer.writerow(row)