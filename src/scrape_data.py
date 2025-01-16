import csv
from dataclasses import dataclass
import os
import re
from bs4 import BeautifulSoup

from config import DIR_HTML
from get_data import PATH_ASPECT_DATA, PATH_OFFERINGS
from tqdm import tqdm

def clean_text(text):
	return " ".join(text.replace("\n", "").split())


def round(number, decimals=0):
	factor = 10 ** decimals
	rounded = int(number * factor + 0.5) / factor

	if decimals == 0:
		return int(rounded)
	else:
		return rounded


def as_percent(number, decimals=2):
	return round(number * 100, decimals)


@dataclass
class StudentMetrics:
	number_completed: int
	invited: int

	def __init__(self, soup):
		table_rows = soup.find_all("table")[2].find_all("tr")

		answered = int(table_rows[1].find("td").text)
		asked = int(table_rows[2].find("td").text)

		self.number_completed = answered
		self.invited = asked

	
	def __str__(self):
		return f"Invited: {self.invited} | Completed: {self.number_completed} ({self.get_completion()}%)"


	def get_completion(self):
		return as_percent(self.number_completed / self.invited)
	

	def is_valid(self):
		return self.invited >= self.number_completed


@dataclass
class AspectMetrics:
	blocks = None

	type: str
	number: int
	title: str

	strong_agree: int
	agree: int
	neutral: int
	disagree: int
	strong_disagree: int

	response_count: int
	mean: float
	median: float

	def __init__(self):
		self.type = None
		self.number = None
		self.title = None

		self.strong_agree = None
		self.agree = None
		self.neutral = None
		self.disagree = None
		self.strong_disagree = None

		self.response_count = None
		self.mean = None
		self.median = None


	def __str__(self):
		output = f"{self.get_id()} - {self.title}"
		output += f"\nResponses: {self.response_count}, Mean: {self.mean}, median: {self.median}"
		output += f"\nSA: {self.strong_agree}, A: {self.agree}, N: {self.neutral}, D: {self.disagree}, SD: {self.strong_disagree}"

		return output


	def is_complete(self):
		things = [self.type, self.number, self.title, self.strong_agree, self.agree, self.neutral, self.disagree, self.strong_disagree, self.response_count, self.mean, self.median]

		for item in things:
			if item is None:
				return False

		return True
	

	def is_valid(self):
		measures = [self.strong_agree, self.agree, self.neutral, self.disagree, self.strong_disagree]
		calculated_total = sum(measures)
		likart_weights = [5, 4, 3, 2, 1]
		
		calculated_mean = 0
		for i in range(len(measures)):
			calculated_mean += measures[i] * likart_weights[i]
		calculated_mean = round(calculated_mean / calculated_total, 2)

		# TODO: Find out how to calculate a Likart median correctly in this context
		# It needs to be a value up to 5 - unsure about the lower bounds
		# It must be a continuous, decimal scale
		calculated_median = None
		valid_median = self.median >= 0 and self.median <= 5

		return calculated_total == self.response_count and calculated_mean == self.mean and valid_median # and calculated_median == self.median
	

	def get_id(self):
		return f"{self.type}{self.number}"


	def _get_blocks(soup):
		if AspectMetrics.blocks is not None:
			return AspectMetrics.blocks
		
		AspectMetrics.blocks = []

		for block in soup.find_all("div", class_="FrequencyBlock_HalfMain"):
			AspectMetrics.blocks.append(block)

		return AspectMetrics.blocks


	def _set_block_number(self, block):
		# Title is in the format "###. TEXT", hence the operations
		self.number = int(clean_text(block.find(class_="FrequencyQuestionTitle").text.split(". ")[0]))


	def _set_block_type(self, block_number, block_index):
		if block_number == (block_index + 1):
			self.type = "U"
		else:
			self.type = "F"

	def _set_block_title(self, block):
		# Title is in the format "###. TEXT", hence the operations
		self.title = clean_text(block.find(class_="FrequencyQuestionTitle").text.split(". ")[1])
	

	def _set_block_metrics(self, block):
		data = {"Strongly Agree": 0, "Agree": 0, "Neutral": 0, "Disagree": 0, "Strongly Disagree": 0}

		for container in block.find_all("div", class_="frequency-data-item-container"):
			key = clean_text(container.find(class_="frequency-data-item-choice-text text-ellipsis").text)
			value = int(clean_text(container.find(class_="frequency-data-item-choice-nb").text))

			data[key] = value

		for key in data:
			if key == "Strongly Agree":
				self.strong_agree = data[key]
			elif key == "Agree":
				self.agree = data[key]
			elif key == "Neutral":
				self.neutral = data[key]
			elif key == "Disagree":
				self.disagree = data[key]
			elif key == "Strongly Disagree":
				self.strong_disagree = data[key]
	

	def _set_block_stats(self, block):
		containers = block.find_all("table")[1].find_all("td")

		data = {
			"response_count": int(containers[0].text),
			"mean": float(containers[1].text),
			"median": float(containers[2].text),
		}

		for key in data:
			if key == "response_count":
				self.response_count = data[key]
			elif key == "mean":
				self.mean = data[key]
			elif key == "median":
				self.median = data[key]


	def get_metrics(soup):
		blocks = AspectMetrics._get_blocks(soup)

		aspects = [None] * len(blocks)
		for i in range(len(blocks)):
			aspect = AspectMetrics()
			aspects[i] = aspect

			aspect._set_block_number(blocks[i])
			aspect._set_block_type(aspect.number, i)
			aspect._set_block_title(blocks[i])
			aspect._set_block_metrics(blocks[i])
			aspect._set_block_stats(blocks[i])

			if sum([aspect.strong_agree, aspect.agree, aspect.neutral, aspect.disagree, aspect.strong_disagree]) != aspect.response_count:
				print("Something went wrong")
				print(aspect)
				exit(2)
			
		return aspects


@dataclass
class Data:
	unit_code: str
	year: int
	semester: str
	campus: str
	mode: str

	unit_name: str
	faculty: str

	student_metrics: StudentMetrics
	aspects: list[AspectMetrics]

	def __init__(self):
		self.unit_code = None
		self.year = None
		self.semester = None
		self.campus = None
		self.mode = None

		self.unit_name = None
		self.faculty = None

		self.student_metrics = None
		
		self.aspects = None

	
	def __str__(self):
		output = f"{self.unit_code}_{self.year}_{self.semester}_{self.campus}_{self.mode}"
		output += f"\n{self.unit_name}"
		output += f"\n{self.faculty}"

		output += f"\n{str(self.student_metrics)}"

		for aspect in self.aspects:
			temp = str(aspect)

			# TODO: Why doesn't this bloody work??
			# temp = "  \n".join(temp.split("\n"))
			temp = temp.split("\n")
			for i in range(len(temp)):
				if i == 0:
					temp[i] = f"- {temp[i]}"
				else:
					temp[i] = f"  {temp[i]}"

			temp = "\n".join(temp)

			output += f"\n{temp}"

		return output

	
	def is_complete(self):
		things = [self.unit_code, self.year, self.semester, self.campus, self.mode, self.unit_name, self.faculty, self.student_metrics]
		return all(things) and all(self.aspects)
	

	def is_valid(self):
		valid_year = self.year >= 2016

		valid_aspects = all([aspect.is_valid() for aspect in self.aspects])
		valid_aspects = valid_aspects and len(self.aspects) >= 8 and len(self.aspects) <= 13
		unique_ids = [aspect.get_id() for aspect in self.aspects]
		# TODO: Check that all IDs are in fact unique and in the correct order
		# TODO: Check that there are 8 uni-wide Qs and the remainder are faculty-wide

		return self.is_complete() & self.student_metrics.is_valid() and valid_year and valid_aspects
	

	def to_csv_rows(self):
		primary_key = (self.unit_code, self.year, self.semester, self.campus, self.mode)

		unit_details = (*primary_key, self.unit_name, self.faculty, self.student_metrics.invited, self.student_metrics.number_completed)

		aspect_rows = []
		for aspect in self.aspects:
			aspect_row = (*primary_key, aspect.type, aspect.number, aspect.title, aspect.strong_agree, aspect.agree, aspect.neutral, aspect.disagree, aspect.strong_disagree, aspect.response_count, aspect.mean, aspect.median)
			aspect_rows.append(aspect_row)

		return unit_details, aspect_rows


def get_html(file_path: str):
	if os.path.exists(file_path):
		with open(file_path, "r") as file:
			return file.read()
		
	return None


def get_title(soup):
	return clean_text(soup.find("title").text)


def get_year(soup):
	return int(clean_text(soup.find("table").find_all("tr")[1].text)[-4:])


def set_unit_data(soup, data: Data):
	title = get_title(soup)
	data.year = get_year(soup)

	strings = title.split(" : ")

	unit_details = strings[1].split("_")

	data.unit_code = unit_details[0]
	data.campus = unit_details[1]
	data.mode = unit_details[2]
	data.semester = unit_details[4]


def set_unit_details(soup, data: Data):
	collection: str = soup.find("table").find_all("tr")

	data.unit_name = clean_text(collection[4].text)
	data.faculty = clean_text(collection[2].text)


def scrape_data(file_path):
	data = Data()

	html = get_html(file_path)
	soup = BeautifulSoup(html, "html.parser")

	set_unit_details(soup, data)
	set_unit_data(soup, data)

	data.student_metrics = StudentMetrics(soup)

	data.aspects = AspectMetrics.get_metrics(soup)

	return data


def scrape_all():
	with open(PATH_OFFERINGS, "w", newline="") as unit_file:
		unit_writer = csv.writer(unit_file)
		unit_writer.writerow(["unit", "year", "semester", "campus", "mode", "title", "faculty", "invited", "number_completed"])

	with open(PATH_ASPECT_DATA, "w", newline="") as aspect_file:
		aspect_writer = csv.writer(aspect_file)
		aspect_writer.writerow(["unit", "year", "semester", "campus", "mode", "aspect_type", "aspect", "aspect_title", "strong_agree", "agree", "neutral", "disagree", "strong_disagree", "response_count", "mean", "median"])

	with open(PATH_OFFERINGS, "a", newline="") as unit_file, open(PATH_ASPECT_DATA, "a", newline="") as aspect_file:
		unit_writer = csv.writer(unit_file)
		aspect_writer = csv.writer(aspect_file)
		for unit_file in tqdm(os.listdir(DIR_HTML), desc="Scraping data"):
			file_path = os.path.join(DIR_HTML, unit_file)

			data = scrape_data(file_path)
			if not data.is_valid():
				print(f"Uh ohh - {file_path}")
			unit, aspects = data.to_csv_rows()
			
			unit_writer.writerow(unit)
		
			for aspect in aspects:
				aspect_writer.writerow(aspect)


"""-------------------------------------------------------------------------------
===============================  END TO END TESTS  ===============================
-------------------------------------------------------------------------------"""
def test_2024_S2():
	test_path = os.path.join(DIR_HTML, "1e193f08b57121e791bc5b9dd4d1e07eda11fb7e768be36ac3765d26ddb69e6216b94c27d7ff0b36d089f49c79faa147.html")
	data = scrape_data(test_path)

	expected = "Data(unit_code='FIT1045', year=2024, semester='S2-01', campus='CLAYTON', mode='ON-CAMPUS', unit_name='Introduction to programming', faculty='Faculty of Information Technology', student_metrics=StudentMetrics(number_completed=259, invited=503), aspects=[AspectMetrics(type='U', number=1, title='The Learning Outcomes for this unit were clear to me', strong_agree=111, agree=100, neutral=34, disagree=6, strong_disagree=4, response_count=255, mean=4.21, median=4.34), AspectMetrics(type='U', number=2, title='The instructions for Assessment tasks were clear to me', strong_agree=117, agree=89, neutral=29, disagree=13, strong_disagree=6, response_count=254, mean=4.17, median=4.39), AspectMetrics(type='U', number=3, title='The Assessment in this unit allowed me to demonstrate the learning outcomes', strong_agree=112, agree=87, neutral=39, disagree=9, strong_disagree=6, response_count=253, mean=4.15, median=4.33), AspectMetrics(type='U', number=4, title='The Feedback helped me achieve the Learning Outcomes for the unit', strong_agree=94, agree=95, neutral=47, disagree=8, strong_disagree=6, response_count=250, mean=4.05, median=4.17), AspectMetrics(type='U', number=5, title='The Resources helped me achieve the Learning Outcomes for the unit', strong_agree=97, agree=86, neutral=36, disagree=22, strong_disagree=11, response_count=252, mean=3.94, median=4.16), AspectMetrics(type='U', number=6, title='The Activities helped me achieve the Learning Outcomes for the unit', strong_agree=96, agree=96, neutral=35, disagree=14, strong_disagree=11, response_count=252, mean=4.0, median=4.19), AspectMetrics(type='U', number=7, title='I attempted to engage in this unit to the best of my ability', strong_agree=116, agree=96, neutral=30, disagree=5, strong_disagree=4, response_count=251, mean=4.25, median=4.4), AspectMetrics(type='U', number=8, title='Overall, I was satisfied with this unit', strong_agree=102, agree=86, neutral=45, disagree=9, strong_disagree=11, response_count=253, mean=4.02, median=4.22), AspectMetrics(type='F', number=1, title='As the unit progressed I could see how the various topics were related to each other', strong_agree=100, agree=123, neutral=25, disagree=3, strong_disagree=2, response_count=253, mean=4.25, median=4.28), AspectMetrics(type='F', number=2, title='The online resources for this unit helped me succeed in this unit', strong_agree=92, agree=92, neutral=52, disagree=13, strong_disagree=5, response_count=254, mean=4.0, median=4.12), AspectMetrics(type='F', number=3, title='The workload in this unit was manageable', strong_agree=67, agree=98, neutral=42, disagree=28, strong_disagree=16, response_count=251, mean=3.69, median=3.9), AspectMetrics(type='F', number=4, title='The practical or tutorial exercises assisted my learning', strong_agree=79, agree=104, neutral=52, disagree=11, strong_disagree=5, response_count=251, mean=3.96, median=4.05), AspectMetrics(type='F', number=5, title='I found the pre-class activities for this unit useful', strong_agree=87, agree=97, neutral=58, disagree=8, strong_disagree=3, response_count=253, mean=4.02, median=4.09)])"
	actual = repr(data)

	assert expected == actual
	assert data.is_valid()


def test_2024_S1():
	test_path = os.path.join(DIR_HTML, "9c3da0e920f9ed42f8692c2e1bbdee9e54eb9e67dea7a65441fba6c301b8e4efe4d0eac86faf5867d9ea859233273b66.html")
	data = scrape_data(test_path)

	expected = "Data(unit_code='FIT1045', year=2024, semester='S1-01', campus='CLAYTON', mode='FLEXIBLE', unit_name='Introduction to programming', faculty='Faculty of Information Technology', student_metrics=StudentMetrics(number_completed=586, invited=1407), aspects=[AspectMetrics(type='U', number=1, title='The Learning Outcomes for this unit were clear to me', strong_agree=111, agree=100, neutral=34, disagree=6, strong_disagree=4, response_count=255, mean=4.21, median=4.34), AspectMetrics(type='U', number=2, title='The instructions for Assessment tasks were clear to me', strong_agree=117, agree=89, neutral=29, disagree=13, strong_disagree=6, response_count=254, mean=4.17, median=4.39), AspectMetrics(type='U', number=3, title='The Assessment in this unit allowed me to demonstrate the learning outcomes', strong_agree=112, agree=87, neutral=39, disagree=9, strong_disagree=6, response_count=253, mean=4.15, median=4.33), AspectMetrics(type='U', number=4, title='The Feedback helped me achieve the Learning Outcomes for the unit', strong_agree=94, agree=95, neutral=47, disagree=8, strong_disagree=6, response_count=250, mean=4.05, median=4.17), AspectMetrics(type='U', number=5, title='The Resources helped me achieve the Learning Outcomes for the unit', strong_agree=97, agree=86, neutral=36, disagree=22, strong_disagree=11, response_count=252, mean=3.94, median=4.16), AspectMetrics(type='U', number=6, title='The Activities helped me achieve the Learning Outcomes for the unit', strong_agree=96, agree=96, neutral=35, disagree=14, strong_disagree=11, response_count=252, mean=4.0, median=4.19), AspectMetrics(type='U', number=7, title='I attempted to engage in this unit to the best of my ability', strong_agree=116, agree=96, neutral=30, disagree=5, strong_disagree=4, response_count=251, mean=4.25, median=4.4), AspectMetrics(type='U', number=8, title='Overall, I was satisfied with this unit', strong_agree=102, agree=86, neutral=45, disagree=9, strong_disagree=11, response_count=253, mean=4.02, median=4.22), AspectMetrics(type='F', number=1, title='As the unit progressed I could see how the various topics were related to each other', strong_agree=100, agree=123, neutral=25, disagree=3, strong_disagree=2, response_count=253, mean=4.25, median=4.28), AspectMetrics(type='F', number=2, title='The online resources for this unit helped me succeed in this unit', strong_agree=92, agree=92, neutral=52, disagree=13, strong_disagree=5, response_count=254, mean=4.0, median=4.12), AspectMetrics(type='F', number=3, title='The workload in this unit was manageable', strong_agree=67, agree=98, neutral=42, disagree=28, strong_disagree=16, response_count=251, mean=3.69, median=3.9), AspectMetrics(type='F', number=4, title='The practical or tutorial exercises assisted my learning', strong_agree=79, agree=104, neutral=52, disagree=11, strong_disagree=5, response_count=251, mean=3.96, median=4.05), AspectMetrics(type='F', number=5, title='I found the pre-class activities for this unit useful', strong_agree=87, agree=97, neutral=58, disagree=8, strong_disagree=3, response_count=253, mean=4.02, median=4.09)])"
	actual = repr(data)

	assert expected == actual
	assert data.is_valid()


def test_2023_S2():
	test_path = os.path.join(DIR_HTML, "9c7aa7ee431258f1e440f30712c753852060308494c342eabadeefbbfb625bdf3fb30ef32c156e6fda4d49d2eb1aedfe.html")
	data = scrape_data(test_path)

	expected = "Data(unit_code='FIT1045', year=2023, semester='S2-01', campus='CLAYTON', mode='ON-CAMPUS', unit_name='Introduction to programming', faculty='Faculty of Information Technology', student_metrics=StudentMetrics(number_completed=140, invited=590), aspects=[AspectMetrics(type='U', number=1, title='The Learning Outcomes for this unit were clear to me', strong_agree=111, agree=100, neutral=34, disagree=6, strong_disagree=4, response_count=255, mean=4.21, median=4.34), AspectMetrics(type='U', number=2, title='The instructions for Assessment tasks were clear to me', strong_agree=117, agree=89, neutral=29, disagree=13, strong_disagree=6, response_count=254, mean=4.17, median=4.39), AspectMetrics(type='U', number=3, title='The Assessment in this unit allowed me to demonstrate the learning outcomes', strong_agree=112, agree=87, neutral=39, disagree=9, strong_disagree=6, response_count=253, mean=4.15, median=4.33), AspectMetrics(type='U', number=4, title='The Feedback helped me achieve the Learning Outcomes for the unit', strong_agree=94, agree=95, neutral=47, disagree=8, strong_disagree=6, response_count=250, mean=4.05, median=4.17), AspectMetrics(type='U', number=5, title='The Resources helped me achieve the Learning Outcomes for the unit', strong_agree=97, agree=86, neutral=36, disagree=22, strong_disagree=11, response_count=252, mean=3.94, median=4.16), AspectMetrics(type='U', number=6, title='The Activities helped me achieve the Learning Outcomes for the unit', strong_agree=96, agree=96, neutral=35, disagree=14, strong_disagree=11, response_count=252, mean=4.0, median=4.19), AspectMetrics(type='U', number=7, title='I attempted to engage in this unit to the best of my ability', strong_agree=116, agree=96, neutral=30, disagree=5, strong_disagree=4, response_count=251, mean=4.25, median=4.4), AspectMetrics(type='U', number=8, title='Overall, I was satisfied with this unit', strong_agree=102, agree=86, neutral=45, disagree=9, strong_disagree=11, response_count=253, mean=4.02, median=4.22), AspectMetrics(type='F', number=1, title='As the unit progressed I could see how the various topics were related to each other', strong_agree=100, agree=123, neutral=25, disagree=3, strong_disagree=2, response_count=253, mean=4.25, median=4.28), AspectMetrics(type='F', number=2, title='The online resources for this unit helped me succeed in this unit', strong_agree=92, agree=92, neutral=52, disagree=13, strong_disagree=5, response_count=254, mean=4.0, median=4.12), AspectMetrics(type='F', number=3, title='The workload in this unit was manageable', strong_agree=67, agree=98, neutral=42, disagree=28, strong_disagree=16, response_count=251, mean=3.69, median=3.9), AspectMetrics(type='F', number=4, title='The practical or tutorial exercises assisted my learning', strong_agree=79, agree=104, neutral=52, disagree=11, strong_disagree=5, response_count=251, mean=3.96, median=4.05), AspectMetrics(type='F', number=5, title='I found the pre-class activities for this unit useful', strong_agree=87, agree=97, neutral=58, disagree=8, strong_disagree=3, response_count=253, mean=4.02, median=4.09)])"
	actual = repr(data)

	assert expected == actual
	assert data.is_valid()


def test_2023_S1():
	pass


def test_2022_S2():
	pass


def test_2022_S1():
	pass


def test_2021_S2():
	pass


def test_2021_S1():
	pass


def test_2020_S2():
	pass


def test_2020_S1():
	pass


def test_2019_S2():
	pass


def test_2019_S1():
	pass


def test_2018_S2():
	pass


def test_2018_S1():
	pass


def test_2017_S2():
	pass


def test_2017_S1():
	pass


def test_2016_S2():
	pass
"""-------------------------------------------------------------------------------
===========================  END OF END TO END TESTS  ============================
-------------------------------------------------------------------------------"""


def test():
	test_2024_S2()
	test_2024_S1()
	test_2023_S2()
	test_2023_S1()
	test_2022_S2()
	test_2022_S1()
	test_2021_S2()
	test_2021_S1()
	test_2020_S2()
	test_2020_S1()
	test_2019_S2()
	test_2019_S1()
	test_2018_S2()
	test_2018_S1()
	test_2017_S2()
	test_2017_S1()
	test_2016_S2()


def find_1045():
	# outcomes = {}
	
	# for unit_file in tqdm(os.listdir(DIR_HTML), desc="Scraping data"):
	# 	file_path = os.path.join(DIR_HTML, unit_file)

	# 	data = scrape_data(file_path)

	# 	if data.unit_code == "FIT1045" and data.campus == "CLAYTON":
	# 		outcomes[f"{data.year}_{data.semester}"] = file_path

	# print(outcomes)

	values = {
		'2024_S2-01': '/home/maxim/Documents/git/setu-scraper/output/html/1e193f08b57121e791bc5b9dd4d1e07eda11fb7e768be36ac3765d26ddb69e6216b94c27d7ff0b36d089f49c79faa147.html',
		'2024_S1-01': '/home/maxim/Documents/git/setu-scraper/output/html/9c3da0e920f9ed42f8692c2e1bbdee9e54eb9e67dea7a65441fba6c301b8e4efe4d0eac86faf5867d9ea859233273b66.html',
		'2023_S2-01': '/home/maxim/Documents/git/setu-scraper/output/html/9c7aa7ee431258f1e440f30712c753852060308494c342eabadeefbbfb625bdf3fb30ef32c156e6fda4d49d2eb1aedfe.html',
		'2022_OCT12': '/home/maxim/Documents/git/setu-scraper/output/html/6a7634c8f43df6ad04bb339fedefb5994c56868bf56336509baec892f13f3f4a8f694ebf6c089b6c4ce1561dcbbe159e.html',
		'2020_S1-01': '/home/maxim/Documents/git/setu-scraper/output/html/0c9b4b34c0816125c132b1171e502d17c7139773c6f3efee64ae53fe22a74488dd986b5f1dbfbab7d89124d999796767.html',
		'2020_S1-FF': '/home/maxim/Documents/git/setu-scraper/output/html/46ad2f630fdfbe8a03e206974f1a9d75f8cc078a7de7ef82adef2a86dc25cfbedec32825fac47beb14f3611f7f25b5d7.html',
	}

	for key in values:
		print(f"{key}: {values[key]}")


def main():
	# scrape_all()
	# find_1045()
	test()


if __name__ == "__main__":
	main()