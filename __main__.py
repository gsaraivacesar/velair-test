import email
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime

IN_FILE = "in.mbox"
TITLE_SEARCH = ["Informações do curso"]
BODY_SEARCH = ["piloto privado", "pp", "piloto comercial", "pc", "instrutor de voo", "inva"]
INTEREST_TRANSLATE = {
    "piloto privado": "PP",
    "pp": "PP",
    "piloto comercial": "PC",
    "pc": "PC",
    "instrutor de voo": "INVA",
    "inva": "INVA"
}

def email_info_to_csv(info_list):
    csv_text = "data,mes,nome,telefone,email,interesse\n"
    for info in info_list:
        date = format_email_date(info['date'])
        month = ""
        name = ""
        phone = ""
        mail = info["to"]

        if info['subject_keyword_flags'][TITLE_SEARCH[0]] == False: continue

        interest = ""

        for bs in BODY_SEARCH:
            if info['body_keyword_flags'][bs]:
                interest += INTEREST_TRANSLATE[bs] + " "

        csv_text += f"{date},,,,{mail},{interest}"

    return csv_text

        
def format_email_date(date_str):
    """
    Convert an email Date header into dd/mm/yyyy format.
    """
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return None


def extract_email_info(raw_email: str, subject_keywords=None, body_keywords=None):
    """
    Extract info from a raw email string.
    subject_keywords: list of keywords to search in the subject (optional)
    body_keywords: list of keywords to search in the body (optional)

    Returns a dict with all information.
    """
    subject_keywords = subject_keywords or []
    body_keywords = body_keywords or []

    # Parse using email module
    msg = email.message_from_string(raw_email, policy=policy.default)

    # Extract simple fields
    recipient = msg.get("To")
    subject   = msg.get("Subject", "")
    date      = msg.get("Date")

    # Extract body (handle multipart or plain)
    if msg.is_multipart():
        body = ""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_content()
    else:
        body = msg.get_content()

    # Lowercase for keyword matching
    subject_lower = subject.lower() if subject else ""
    body_lower = body.lower() if body else ""

    # Keyword match dicts
    subject_flags = {
        kw: (kw.lower() in subject_lower)
        for kw in subject_keywords
    }

    body_flags = {
        kw: (kw.lower() in body_lower)
        for kw in body_keywords
    }

    return {
        "to": recipient,
        "date": date,
        "subject_keyword_flags": subject_flags,
        "body_keyword_flags": body_flags,
    }

def split_mbox_emails(mbox_string: str):
    """
    Receives a .mbox file as a single string and returns a list of individual emails.
    Emails in mbox files are separated by lines beginning with 'From '.
    """
    
    # Split only on lines that *start* with 'From '
    parts = mbox_string.split("\nFrom ")
    
    emails = []
    for i, part in enumerate(parts):
        # Restore the 'From ' prefix for all parts except the first
        if i == 0:
            emails.append(part.strip())
        else:
            emails.append("From " + part.strip())
    
    return emails


def read_mail_box():
    with open(IN_FILE) as f:
        content = f.read()
        emails = split_mbox_emails(content)
        info_list = []
        for email in emails:
            info_list.append(extract_email_info(email, TITLE_SEARCH, BODY_SEARCH))
        csv_result = email_info_to_csv(info_list)
        print(csv_result)

if __name__ == '__main__':
    read_mail_box()