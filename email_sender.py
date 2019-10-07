import requests
from api_details import MAILGUN_API_KEY, MAILGUN_API_DOMAIN

class Email:
    def __init__(self, to_email, subject, text):
        self._subject = subject
        self._text = text
        self._to = to_email
        self._api_key = MAILGUN_API_KEY #Constant representing the api key
        self._api_domain = MAILGUN_API_DOMAIN #Constant representing the domain

    def send(self):
        return requests.post("https://api.mailgun.net/v3/" +
        self._api_domain +"/messages",
		auth=("api", self._api_key),
		data={"from": "WeatherAlert <mailgun@" + self._api_domain + ">",
			"to": [self._to],
			"subject": self._subject,
			"text": self._text})

class WeatherEmail(Email):
    def __init__(self, to_email, subect, text):
        pass

    def create_email():
        pass

def main():
    email = Email("richalverma00@gmail.com", "Test", "Test")
    email.send()

if __name__ == "__main__":
    main()