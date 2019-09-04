import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import unicodedata

class WarningScraper:
	""" Class that reads data from the BOM warnings page, parses it and stores
	it into a dictionary of warnings and writes this to a db"""

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
				if warning_details[0] != "No Warning Id":
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

		issue_timestamp = self._parse_datetime(issue_date)

		next_warning = warning_data.find('p', attrs={'class' : 'dt'})
		if next_warning != None:
			next_warning = self._clean_text(next_warning)
		else:
			next_warning = "No Next Date"

		return tuple([warning_id, name, description, issue_timestamp, 
						warning_link])
	
	def write_to_db(self):
		""" Writes the warning list to a database so that it can be easily 
			accessed and compared regardless of if the script crashes. 
		"""
		db = sqlite3.connect('warnings.db')
		cursor = db.cursor()

		cursor.execute('''CREATE TABLE IF NOT EXISTS warnings 
						(warning_id TEXT, state TEXT,
						short_name TEXT, description TEXT, issue_date TEXT, 
						link TEXT, status TEXT, PRIMARY KEY (warning_id, issue_date))''')
		
		for state in self._warning_list:
			for  warning in self._warning_list.get(state):

				warning_id, name, description, issue_date, warning_link = warning

				cursor.execute('''SELECT * FROM warnings WHERE 
								  warnings.warning_id = ?''', (warning_id,))	  
				warning_with_id = cursor.fetchall()
				if len(warning_with_id) == 0:
					cursor.execute('''INSERT INTO warnings 
									  VALUES (?, ?, ?, ?, ?, ?, "NEW")''', 
									  (warning_id, state, name, description, 
									  issue_date, warning_link))

				cursor.execute('''SELECT issue_date FROM warnings WHERE 
								  warnings.warning_id = ?''', (warning_id,))
				issue_date_with_id = cursor.fetchall()
				
				if (issue_date,) not in issue_date_with_id:
					for old_issue_date in issue_date_with_id:
						cursor.execute('''UPDATE warnings SET status="EXPIRED" 
										WHERE warnings.warning_id = ? 
										AND warnings.issue_date = ?''',
										(warning_id, old_issue_date[0]))

					cursor.execute('''INSERT INTO warnings 
									VALUES (?, ?, ?, ?, ?, ?, "UPDATED")''', 
									(warning_id, state, name, description, 
									issue_date, warning_link))
					
		db.commit()
		db.close()

	def _parse_datetime(self, datetime):
		""" Takes a datetime string and converts it into a machine readable
			version. Warning: Lots of Regex
		"""

		months = {"January":"01", "February":"02", "March":"03", "April":"04", 
					"May":"05", "June":"06", "July":"07", "August":"08", 
					"September":"09", "October":"10", "November":"11", 
					"December":"12"}

		#Time difference with EST for each timezone in minutes
		timezone_diff = {"EST":0, "WST":120, "CST":30}

		new_datetime = re.search(r"(.*)(for)(.*)", datetime)
		if new_datetime != None:
			datetime = new_datetime.group(1)
		else:
			datetime = datetime
			
		timezone = re.search(r"[E,C,W](ST)", datetime)
		if timezone != None:
			timezone = timezone.group(0)

		time = re.search(r"\d{1}:\d{2} (am)?(pm)?", datetime)
		if time != None:
			time = time.group(0)
			hour = re.search(r"(\d{1}):(\d{2})", time ).group(1)
			minute = re.search(r"(\d{1}):(\d{2})", time).group(2)
			hour_minute = int(hour) * 60 + int(minute)

			#Convert to 24hr time and add time difference to convert to AEST
			if re.search(r"(am)", time) != None:
				hour_minute = hour_minute + timezone_diff.get(timezone)
			elif re.search(r"(pm)", time) != None:
				hour_minute = hour_minute + 12 * 60 + timezone_diff.get(timezone)
			
			hour = str(hour_minute // 60)
			minute = str(hour_minute % 60)
			time = hour + ":" + minute + ":00"
		else:
			time = ""

		date = re.search(r"(\d?\d) ([A-Z,a-z]+) (\d{4})", datetime)
		day = ""
		month = ""
		year = ""

		if date != None:
			day = date.group(1)
			month = months.get(date.group(2))
			year = date.group(3)

		timestamp = year + "-" + month + "-" + day + " " + time
		return timestamp