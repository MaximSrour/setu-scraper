from config import SEMESTERS, DIR_RAW_LINKS, DIR_FILTERED_LINKS
import csv
import os

# loop through all semester key in the SEMSETER dict
# use each key as the filename (key.csv) in the output dir
# open the csv and filter only a certain subset of rows that contain any unit code in a list, UNITCODES
# output the filtered data to a new csv file, key_filtered.csv in the filter dir

#UNITCODES = ["FIT1008", "FIT1054", "FIT1033", "FIT1045", "FIT1053", "FIT1073", "FIT2073", "FIT2096", "FIT5057"]
#UNITCODES = ["FIT1045"]
UNITCODES = ["FIT"]

DIR_RAW_LINKS
DIR_FILTERED_LINKS

def main():
    if not os.path.exists("filter"):
        os.makedirs("filter")

    for semester_key in SEMESTERS:
        filename = f"{semester_key}.csv"
        path_raw_links = f"{DIR_RAW_LINKS}/{filename}"
        path_filtered_links = f"{DIR_FILTERED_LINKS}/{semester_key}_filtered.csv"

        with open(path_raw_links, "r") as input_file, open(path_filtered_links, "w", newline="") as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)

            for row in csv_reader:
                if not any(unit_code in row[0] for unit_code in UNITCODES):
                    csv_writer.writerow(row)

def find_unique_campuses():
    campuses = []

    for semester_key in SEMESTERS:
        filename = f"{semester_key}.csv"
        path_raw_links = f"{DIR_RAW_LINKS}/{filename}"
    
    with open(path_raw_links, "r") as input_file:
        csv_reader = csv.reader(input_file)
        
        for row in csv_reader:
            campus = row[0].split("_")[1]
            
            if campus not in campuses:
                campuses.append(campus)
    
    return campuses

def count_offerings():
    count = 0

    for semester_key in SEMESTERS:
        filename = f"{semester_key}.csv"
        path_raw_links = f"{DIR_RAW_LINKS}/{filename}"
    
        with open(path_raw_links, "r") as input_file:
            csv_reader = csv.reader(input_file)

            count += sum(1 for row in csv_reader)

    return count

def find_unique_units():
    units = []

    for semester_key in SEMESTERS:
        filename = f"{semester_key}.csv"
        path_raw_links = f"{DIR_RAW_LINKS}/{filename}"
    
    with open(path_raw_links, "r") as input_file:
        csv_reader = csv.reader(input_file)
        
        for row in csv_reader:
            unit = row[0].split("_")[0]
            
            if unit not in units:
                units.append(unit)
    
    return units

if __name__ == "__main__":
    main()