from warning_scraper import WarningScraper
from pprint import pprint
import sqlite3
from warning_sender import WarningEmail

def get_warnings():
    warning_scraper = WarningScraper()
    warning_list = warning_scraper.get_current_warnings()
    warning_scraper.write_to_db()

def send_email():
    db = sqlite3.connect('warnings.db')
    cursor = db.cursor()

    email_content = cursor.execute('''SELECT * FROM warnings ORDER BY status''').fetchall()

    email = WarningEmail("richalverma00@gmail.com", email_content)
    email.send()

def main():
    get_warnings()
    send_email()

if __name__ == "__main__":
	main()