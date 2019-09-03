import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import unicodedata

class WarningScraper:
	""" Class that reads data from the BOM warnings page, parses it and stores
	it into a dictionary of warnings """

	def __init__(self):
		""" Constructor for WarningScraper """
		self._state_list = []
		self._warning_list = {}
		self._bom_url = "http://www.bom.gov.au"
		self._data_url = "/australia/warnings/"

	def get_html_data(self):
		""" Reads HTML data from BOM warnings page 
			(http://www.bom.gov.au/australia/warnings) and returns it

			Returns:
				html_data: Raw HTML from the BOM warnings page
		"""
		html_data = BeautifulSoup(
			requests.get(self._bom_url + self._data_url).text, "html.parser")
		return html_data

	def get_current_warnings(self):
		""" Parses the BOM HTML data and returns a dictionary of warnings for 
			each state.
		    
			Returns:
				warning_list: A dictionary of states/locations and their 
					respective warnings.
		"""
		html_data = self.get_html_data()
		unparsed_warning_list = (html_data.find("div", {"id" : "content"}))
		self._state_list.append("Weather Services")
		
		for index, state in enumerate(unparsed_warning_list.find_all('h2')):
			self._state_list.append(state.text)

		for index, warning_list in enumerate(
				unparsed_warning_list.find_all('ul')):

			state_warnings = []
			for warning in warning_list.find_all('a', href=True):
				warning_details = self.get_warning_details(
					self._clean_text(warning), warning['href'])
				state_warnings.append(warning_details)
			self._warning_list[self._state_list[index]] = state_warnings

		return self._warning_list
	
	def _clean_text(self, warning):
		"""(String) Takes the warning text and cleans it into a single line 
			format.
		"""
		warning_text = ""
		if warning != None:
			warning_text = warning.get_text(strip = True)
			warning_text = unicodedata.normalize("NFKD", warning_text)
			warning_text.replace('    ', ' ').replace(u'\n', u' ')
		return warning_text
	
	def get_warning_details(self, warning_text, warning_link):
		""" Takes the warning title and link and fetches more details on the
			warning from the link. 

			Returns: List<id, title, description, issue_date, link>
		"""
		warning_data = BeautifulSoup(
			requests.get(self._bom_url + warning_link).text, "html.parser")

		name = warning_text
		description = warning_data.find('p', attrs={'class' : 'sl'})
		if description != None:
			description = self._clean_text(description)
		else:
			description = "No Description Exists"

		warning_id = warning_data.find('p', attrs={'class' : 'p-id'})
		if warning_id != None:
			warning_id = warning_id.text
		else:
			warning_id = "No Warning Id"

		issue_date = warning_data.find('p', attrs={'class' : 'date'})
		if issue_date == None:
			issue_date = warning_data.find('p', attrs={'class' : 'dt'})

		if issue_date != None:
			issue_date = self._clean_text(issue_date)
		else:
			issue_date = "No Issue Date"

		next_warning = warning_data.find('p', attrs={'class' : 'dt'})
		if next_warning != None:
			next_warning = self._clean_text(next_warning)
		else:
			next_warning = "No Next Date"

		return [warning_id, name, description, issue_date, warning_link]
	
	def write_to_db(self):
		""" Writes the warning list to a database so that it can be easily 
			accessed and compared regardless of if the script crashes. 
		"""
		db = sqlite3.connect('warnings.db')
		cursor = db.cursor()

		cursor.execute('''CREATE TABLE IF NOT EXISTS warnings 
					(warning_id INTEGER PRIMARY KEY, state VARCHAR(20), description TEXT, link TEXT, status TEXT)''')
		
		for state in self._warning_list:
			for warning in state:
				pass
				#cursor.execute(''' SELECT ''')
		
		#cursor.execute('''INSERT INTO test VALUES (1, 'hello')''')
		
		db.commit()
		db.close()

	def _connect_db(self, database):
		pass

class Warning:
	""" Stub for future Warning object if needed """
	pass