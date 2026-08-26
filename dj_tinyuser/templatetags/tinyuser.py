import datetime

from django import template
from django.utils.translation import gettext as _

register = template.Library()


@register.filter("birthday")
def birthday_from_date(date: datetime.date | datetime.datetime) -> str:
    if isinstance(date, datetime.datetime):
        date = date.date()
    # Birthday format: Month day (e.g. January 1)
    return date.strftime(_("%B %-d"))
