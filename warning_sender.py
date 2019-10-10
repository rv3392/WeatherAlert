from urllib import request
from i_email import Email

class WarningEmail(Email):
    def __init__(self, to_email, content):
        super().__init__(to_email)
        self._create_email(content)

    def _create_email(self, content):
        email_html = self._load_template()
        state_lists = self._parse_content(content)
        
        for state in state_lists.keys():
            print(state)
            email_html = email_html.replace("{" + state + " List}", str(state_lists.get(state)))  

        self._html = email_html
        self._text = "Email does not support html?"
        self._subject = "Current Warnings for "

    def _load_template(self):
        return str(open("warning_email_template.html").read())

    def _parse_content(self, content):
        state_list_dictionary = {"Northern Territory":list(), \
        "Queensland":list(), "NSW and ACT":list(), "Victoria":list(), \
        "Tasmania":list(), "South Australia":list(), \
        "Western Australia":list()}

        for record in content:
            state_list_dictionary.get(record[1]).append(record)

        return state_list_dictionary

def main():
    email = WarningEmail("richalverma00@gmail.com", "Test")
    email.send()

if __name__ == "__main__":
    main()