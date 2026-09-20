import re
from langdetect import detect


def is_english(text):
    if len(text.split()) < 20:
        return True
    try:
        return detect(text) == 'en'
    except:
        return True


def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\s\.\,\-\+\/\#]', ' ', text)
    return text.strip()


def anonymize_text(text):
    text = _remove_emails(text)
    text = _remove_phone_numbers(text)
    return text


def _remove_emails(text):
    return re.sub(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        ' ',
        text
    )


def _remove_phone_numbers(text):
    return re.sub(
        r'(\+?\d[\d\-\s\(\)]{8,}\d)',
        ' ',
        text
    )
