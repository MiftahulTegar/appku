from datetime import datetime
import markdown

def convert_date(date):
    return date.strftime('%Y-%m-%d')

def format_date(date):
    return date.strftime('%d %B %Y')

def format_time(date):
    return date.strftime('%X')

def to_raw_date(date):
    return date.strftime('%d/%m/%Y')

def day_and_date(date):
    return date.strftime('%A, %d %B %Y')

def str_to_date(str):
    if isinstance(str, datetime):
        return str
    return datetime.strptime(str, '%Y-%m-%d %H:%M:%S')

def new_str_to_date(str):
    if isinstance(str, datetime):
        return str
    return datetime.strptime(str, '%d/%m/%Y')

def to_html(md):
    return markdown.markdown(md).replace('\n', '<br>')


def date_range(first_date, second_date):
    if first_date.year == second_date.year:
        new_date = f"{first_date.strftime('%d %B')} - {second_date.strftime('%d %B %Y')}"
    else:
        new_date = f"{first_date.strftime('%d %B %Y')} - {second_date.strftime('%d %B %Y')}"
    return new_date


def enum(value):
    return enumerate(value)

def comma_join(datas):
    datas = [item.degree.name for item in datas]
    return ', '.join(datas)
