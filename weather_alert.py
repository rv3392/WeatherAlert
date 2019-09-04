from warning_scraper import WarningScraper
from pprint import pprint

def main():
    warning_scraper = WarningScraper()
    warning_list = warning_scraper.get_current_warnings()
    warning_scraper.write_to_db()

if __name__ == "__main__":
	main()