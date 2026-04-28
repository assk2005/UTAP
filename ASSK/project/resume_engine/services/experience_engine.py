import re
from datetime import datetime


def extract_experience(text):
    text=text.lower()
    current_year=datetime.now().year
    current_month=datetime.now().month

    onsite_years=0
    remote_years=0

    date_ranges=re.findall(
        r'(\d{2})/(\d{4}).{0,15}?(\d{2}/\d{4}|present)',
        text
    )

    for start_m,start_y,end in date_ranges:

        start_m=int(start_m)
        start_y=int(start_y)

        if end=='present':
            end_m=current_month
            end_y=current_year
        else:
            end_m=int(end.split('/')[0])
            end_y=int(end.split('/')[1])

        months=(end_y-start_y)*12+(end_m-start_m)
        years=months/12

        snippet_pattern=f"{start_m}/{start_y}.*?{end}"
        snippet=re.search(snippet_pattern,text,re.DOTALL)

        if snippet and 'remote' in snippet.group():
            remote_years+=years
        else:
            onsite_years+=years


    phrase_match=re.search(
        r'(\d+)\+?\s*(years|yrs)',
        text
    )

    if phrase_match:
        phrase_years=int(phrase_match.group(1))
        onsite_years=max(onsite_years,phrase_years)


    return round(onsite_years,2),round(remote_years,2)



def compute_experience_score(onsite_years,remote_years,min_experience):

    adjusted=onsite_years+(0.8*remote_years)

    if min_experience==0:
        return adjusted,1.0

    score=min(adjusted/min_experience,1)

    return adjusted,round(score,3)