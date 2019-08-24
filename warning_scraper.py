import requests
from bs4 import BeautifulSoup
from pprint import pprint

class WarningScraper:
	def __init__(self):
		self._state_list = []
		self._warning_list = {}
		self._bom_url = "http://www.bom.gov.au"
		self._data_url = "/australia/warnings/"

	def get_html_data(self):
		html_data = BeautifulSoup(
			requests.get(self._bom_url + self._data_url).text, "html.parser")
		return html_data

	def get_current_warnings(self):
		""" Parses the BOM HTML data and returns a dictionary of warnings for each state.
		    
			Returns:
				warning_list: A dictionary of states/locations and their 
					respective warnings.
		"""
		html_data = self.get_html_data()
		unparsed_warning_list = (html_data.find("div", {"id" : "content"}))
		self._state_list.append("Weather Services")
		for index, state in enumerate(unparsed_warning_list.find_all('h2')):
			self._state_list.append(state.text)

		for index, warning_list in enumerate(unparsed_warning_list.find_all('ul')):
			state_warnings = []
			for warning in warning_list.find_all('a', href=True):
				state_warnings.append([warning.text.replace('\n', ' ').replace('  ', ''), warning['href']])
			self._warning_list[self._state_list[index]] = state_warnings

		return self._warning_list
	
	def get_warning_details(self):
		pass


def main():
	warning_scraper = WarningScraper()
	warning_list = warning_scraper.get_current_warnings()
	pprint(warning_list)

if __name__ == "__main__":
	main()