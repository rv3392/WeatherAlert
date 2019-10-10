import requests
from api_details import MAILGUN_API_KEY, MAILGUN_API_DOMAIN

class Email:
    def __init__(self, to_email, subject = "", text = "", api_key = MAILGUN_API_KEY, api_domain = MAILGUN_API_DOMAIN):
        self._subject = subject
        self._text = text
        self._to = to_email
        self._api_key = api_key
        self._api_domain = api_domain
        self._html = "" 

    def send(self):
        return requests.post("https://api.mailgun.net/v3/" +
        self._api_domain +"/messages",
		auth=("api", self._api_key),
		data={"from": "WeatherAlert <mailgun@" + self._api_domain + ">",
			"to": [self._to],
			"subject": self._subject,
			"text": self._text,
            "html": self._html})