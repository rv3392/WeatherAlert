import requests
from api_details import MAILGUN_API_KEY, MAILGUN_API_DOMAIN
from email import Email

class WarningEmail(Email):
    def __init__(self, to_email, subect, text):
        pass

    def create_email():
        pass

    def load_template(self):
        return requests.get(".\warning_email_template.html").content

def main():
    email = Email("richalverma00@gmail.com", "Test", "Test")
    email.send()

if __name__ == "__main__":
    main()