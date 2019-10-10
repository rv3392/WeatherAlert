from warning_scraper import WarningScraper
from pprint import pprint

def get_warnings():
    warning_scraper = WarningScraper()
    warning_list = warning_scraper.get_current_warnings()
    warning_scraper.write_to_db()

def check_database_updates():
    pass

def main():
    get_warnings()

if __name__ == "__main__":
	main()