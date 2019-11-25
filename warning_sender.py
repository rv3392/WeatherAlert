from urllib import request
from i_email import Email
from datetime import datetime

class WarningEmail(Email):
    def __init__(self, to_email, content):
        super().__init__(to_email)
        self._create_email(content)

    def _create_email(self, content):
        email_html = self._load_template()
        state_lists = self._parse_content(content)

        for state in state_lists.keys():
            state_warning_list = ""
            if (len(state_lists.get(state)) == 0):
                state_warning_list = "No warnings current for " + state
            else:
                for record in state_lists.get(state):
                    state_warning_list += self._format_warning(record)
                
            email_html = email_html.replace("{" + state + " List}", state_warning_list)  


        time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        email_html = email_html.replace("{date}{time}", str(time))

        self._html = email_html
        self._text = "Email does not support html. Try using a different client."
        self._subject = "Warnings Current at " + str(time) + " UTC"

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

    def _format_warning(self, record):
        record_string = ""

        warning_id, state, description, more_details, issue_date, link, status = record
        record_string += "<h3>" + warning_id + " - Issued " + issue_date + "</h3>"
        record_string += "<p class=\"small\">" + status + " - "+ description + "\n"

        #if more_details != "No Description":
        if more_details == "No Description":
            record_string += "<a href=\"www.bom.gov.au" + link + "\">www.bom.gov.au" + link + "</a></p>"
        else:
            record_string += more_details + "<a href=\"www.bom.gov.au" + link + "\">www.bom.gov.au" + link + "</a></p>"

        return record_string

def main():
    email = WarningEmail("richalverma00@gmail.com", "Test")
    email.send()

if __name__ == "__main__":
    main()