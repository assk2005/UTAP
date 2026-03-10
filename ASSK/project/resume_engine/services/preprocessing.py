import re
from langdetect import detect


def is_english(text):
    try:
        return detect(text)=='en'
    except:
        return False


def clean_text(text):
    text=text.lower()
    text=re.sub(r'\s+',' ',text)
    text=re.sub(r'[^a-z0-9\s\.\,\-\+\/]',' ',text)
    return text.strip()


def anonymize_text(text):
    text=_remove_emails(text)
    text=_remove_phone_numbers(text)
    return text


def _remove_emails(text):
    return re.sub(r'\S+@\S+',' ',text)


def _remove_phone_numbers(text):
    return re.sub(r'\+?\d[\d\s\-]{8,}\d',' ',text)