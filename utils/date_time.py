import pytz

from datetime import date, datetime, timedelta
from typing import List, Optional

from django.conf import settings


def parse_gmt_date_list(published_parsed: Optional[list]) -> Optional[datetime]:
    if not published_parsed:
        return None

    try:
        published_at_naive = datetime(*published_parsed[:6])
    except ValueError:
        return None
    timezone = pytz.timezone(settings.TIME_ZONE)
    published_at_utc = pytz.utc.localize(published_at_naive)
    return published_at_utc.astimezone(timezone)


def get_range_dates(
        when: Optional[str], from_date: Optional[date], to_date: Optional[date]
) -> List[List[date]]:
    if not (from_date and to_date):
        if not when:
            when_int = 1
        elif when.isdigit():
            when_int = int(when)
        elif when[-1] == 'd':
            try:
                when_int = int(when[:-1])
            except ValueError:
                when_int = 1
        else:
            when_int = 1
        to_date = date.today()
        from_date = to_date - timedelta(days=when_int)

    if from_date > to_date:
        aux = from_date
        from_date = to_date
        to_date = aux

    when_int = (to_date - from_date).days
    dates = []

    for i in range(0, when_int + 1):
        dates.append([from_date + timedelta(days=i),
                     from_date + timedelta(days=i + 1)])

    return dates
