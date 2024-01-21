"""
This script extracts tables from the SETU PDF.

It is not used in the final product, but is kept here for reference.
It works, but don't use it. Will be removed in a future commit.
"""

import fitz
import re

def extract_text_from_page(page):
    text = page.get_text()
    potential_rows = re.findall(r"[\w\s]+(?:\s{2,}[\w\s]+)+", text)
    return potential_rows

def extract_tables_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_rows = []

    for i in range(len(doc)):
        page = doc.load_page(i)
        rows = extract_text_from_page(page)
        all_rows.extend(rows)

    return all_rows

def get_all_text(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""

    for i in range(len(doc)):
        page = doc.load_page(i)
        all_text += page.get_text()
    
    return all_text

def sanitise_text(text):
    lines = text.split("\n")

    line_index = 0
    while line_index < len(lines):
        if lines[line_index] == "University Wide Items":
            break

        line_index += 1

    return "\n".join(lines[line_index:])

def get_tables(text):
    expression = "\d\. (?:.*\n){1,3}Options\nScore\nCount\nPercentage\n(?:.*\n\d*\n\d*\n\d*\.\d*%\n)*Statistics\nValue\nResponse Count\n\d*\nMean\n\d*\.\d*\nMedian\n\d*\.\d*"

    # get the first regex match and return it
    tables = re.findall(expression, text)

    tables = [format_table(table) for table in tables]

    return tables

def format_table(text):
    def aspect(text, target):
        expression = target+"\n\d+\n\d+\n\d+\.\d+%"

        result = re.findall(expression, text)

        if len(result) == 0:
            return 0
        
        return result[0].split("\n")[2]
    
    def mean_median(text, target):
        expression = target+"\n\d+\.\d+"

        result = re.findall(expression, text)

        if len(result) == 0:
            return 0
        
        return result[0].split("\n")[1]

    lines = text.split("\n")

    table = Table(lines[0][3:], mean_median(text, "Mean"), mean_median(text, "Median"), sa=aspect(text, "Strongly Agree"), a=aspect(text, "Agree"), n=aspect(text, "Neutral"), d=aspect(text, "Disagree"), sd=aspect(text, "Strongly Disagree"))

    return table

class Table:
    def __init__(self, table_name, mean, median, sa = 0, a = 0, n = 0, d = 0, sd = 0):
        self.table_name = table_name
        self.sa = sa
        self.a = a
        self.n = n
        self.d = d
        self.sd = sd
        self.mean = mean
        self.median = median

    def __str__(self):
        return f"""Table: {self.table_name}
Strongly Agree: {self.sa}
Agree: {self.a}
Neutral: {self.n}
Disagree: {self.d}
Strongly Disagree: {self.sd}
Mean: {self.mean}
Median: {self.median}"""


# Path to your PDF file
pdf_path = "./docs/UE00402-Unit_Evaluation_Report-FIT1045_CLAYTON_ON-CAMPUS_ON_S2-01-2075752_96910036-0c12-4c11-979a-1b1491f21e8een-US.pdf"  # Replace with your PDF file path

# Extract tables
extracted_data = get_all_text(pdf_path)
sanitised_text = sanitise_text(extracted_data)
tables = get_tables(sanitised_text)

print(tables[8])

# print(len(tables))

# for table in tables:
#     print(table.table_name)
