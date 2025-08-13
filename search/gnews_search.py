from datetime import date
from typing import Any, Optional, Union


from utils.date_time import get_range_dates
from utils.yeeko_gnews import YeekoGoogleNews


class GNewsSearch:
    gnews_query: str
    when: Optional[Union[str, int]]
    from_date: Optional[date]
    to_date: Optional[date]

    def __init__(
            self, gnews_query: str, when: Optional[Any],
            from_date: Optional[date], to_date: Optional[date],
            negative_words:list = None
    ):

        if not (when or (from_date and to_date)):
            raise ValueError("No dates provided")

        self.when = when
        self.gnews_query = gnews_query
        self.from_date = from_date
        self.to_date = to_date
        self.search_entries = []
        self.feed = {}
        self.errors = []
        if negative_words is None:
            negative_words = []
        self.negative_words = negative_words

    def search_in_gnews(self):
        self.search_entries = []

        if self.when:
            self._search_when()
        elif self.from_date and self.to_date:
            self._search_from_to()
        else:
            raise ValueError("No dates provided")
        self.filter_negative_words()

    def _search_from_to(self):

        search_kwargs = {}
        range_dates = get_range_dates(None, self.from_date, self.to_date)

        for from_date_r, to_date_r in range_dates:

            search_kwargs["from_"] = from_date_r.strftime("%Y-%m-%d")
            search_kwargs["to_"] = to_date_r.strftime("%Y-%m-%d")

            gn = YeekoGoogleNews("es", "MX")
            print("Searching...\n", self.gnews_query, "\n", search_kwargs)
            try:
                links_data = gn.search(
                    self.gnews_query, helper=False, **search_kwargs)
            except Exception as e:
                self.errors.append(str(e))
                continue
            self.search_entries.extend(links_data.get("entries", []))
            self.feed = links_data.get("feed", None)

    def _search_when(self):
        try:
            self.when = int(self.when)  # type: ignore
            self.when = f"{self.when}d"
        except ValueError:
            pass
        search_kwargs = {"when": self.when or "1d"}
        print("search_kwargs", search_kwargs)
        gn = YeekoGoogleNews("es", "MX")
        print("Searching...\n", self.gnews_query, "\n", search_kwargs)
        result = gn.search(
            self.gnews_query, helper=False, **search_kwargs)
        self.search_entries = result.get("entries", [])
        self.feed = result.get("feed", None)

    def filter_negative_words(self):

        entries_filtered = []
        for entry in self.search_entries:
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            if any([
                word in title or word in summary
                for word in self.negative_words
            ]):
                continue

            entries_filtered.append(entry)
        self.search_entries = entries_filtered
