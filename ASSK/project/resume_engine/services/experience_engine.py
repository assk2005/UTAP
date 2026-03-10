import re
from datetime import datetime


def extract_experience(text):
    text = text.lower()
    current_year = datetime.now().year

    onsite_years = 0
    remote_years = 0

    # 1️⃣ Flexible year range detection (handles messy formatting)
    year_ranges = re.findall(
        r'(20\d{2}).{0,15}?(20\d{2}|present)',
        text,
        flags=re.IGNORECASE
    )

    for start, end in year_ranges:
        start = int(start)

        if end.lower() == 'present':
            end = current_year
        else:
            end = int(end)

        duration = max(end - start, 0)

        # detect remote context nearby
        pattern = f"{start}.*?{end}"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match and 'remote' in match.group():
            remote_years += duration
        else:
            onsite_years += duration

    # 2️⃣ Detect explicit phrases like "2+ years", "3 years experience"
    phrase_match = re.search(r'(\d+)\+?\s+years', text)
    if phrase_match:
        phrase_years = int(phrase_match.group(1))
        onsite_years = max(onsite_years, phrase_years)

    return onsite_years, remote_years


def compute_experience_score(onsite_years, remote_years, min_experience):
    adjusted = onsite_years + (0.8 * remote_years)

    if min_experience == 0:
        return adjusted, 1.0

    if adjusted >= min_experience:
        return adjusted, 1.0

    return adjusted, adjusted / min_experience