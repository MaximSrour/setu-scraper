import os
from bs4 import BeautifulSoup

from config import DIR_HTML
from scrape_data import get_html, scrape_data


def test_title_1():
	html = get_html("sample.html")
	assert html == "<div>This is a test</div>"

	soup = BeautifulSoup(html, 'html.parser')
	
	return True


def test_2024_S2():
	test_path = os.path.join(DIR_HTML, "0a0bdb68457de6833229107c03e12a458eaa8363fe4e93b1010a79d02de3acf71553fdfc232e995390a5d8f99b1c1876.html")
	data = scrape_data(test_path)

	print(data)


def main():
	test_2024_S2()


if __name__ == "__main__":
	main()

