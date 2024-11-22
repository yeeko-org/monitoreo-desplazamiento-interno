import pytz

from datetime import datetime
from typing import Optional

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
