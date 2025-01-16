from dataclasses import dataclass
import os
import re
from bs4 import BeautifulSoup

from config import DIR_HTML

def clean_html(file_path):
	html = None

	with open(file_path, "r") as file:
		html = file.read()

	if not html:
		return

	# Remove </hr> usibg regex
	html = re.sub(r"</hr>", "", html)

	# save
	with open(file_path, "w") as file:
		file.write(html)


def main():
	test_path = os.path.join(DIR_HTML, "0a0bdb68457de6833229107c03e12a458eaa8363fe4e93b1010a79d02de3acf71553fdfc232e995390a5d8f99b1c1876.html")
	clean_html(test_path)


if __name__ == "__main__":
	main()