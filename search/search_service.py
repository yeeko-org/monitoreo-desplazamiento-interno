from datetime import date
from typing import Any, Optional


from search.gnews_search import GNewsSearch
from search.pre_classify_openai import PreClassifyOpenAI


class SearchService:
    gnews_search: GNewsSearch
    pre_classify_request: PreClassifyOpenAI

    search_entries: dict
    all_negative_words: list

    def __init__(
            self, gnews_query: str, when: Optional[Any],
            from_date: Optional[date], to_date: Optional[date],
            all_negative_words: list
    ):
        self.gnews_search = GNewsSearch(gnews_query, when, from_date, to_date)
        self.pre_classify_request = PreClassifyOpenAI()

        self.all_negative_words = all_negative_words

    def check_entries_exist(self):
        if not self.search_entries:
            raise ValueError("No entries in search entries")

    def search(self):

        self.search_entries = self.gnews_search.search()

        self.filter_negative_words()

        if not self.gnews_search.when:
            self.pre_classify_openai()

    def filter_negative_words(self):
        self.check_entries_exist()

        entries_filtered = []
        for entry in self.search_entries["entries"]:
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            if any([
                word in title or word in summary
                for word in self.all_negative_words
            ]):
                continue

            entries_filtered.append(entry)
        self.search_entries["entries"] = entries_filtered

    def pre_classify_openai(self):
        from note.models import ValidOption
        self.check_entries_exist()

        pre_classify_response = self.pre_classify_request\
            .get_pre_classify_response(self.search_entries["entries"])

        if not pre_classify_response:
            return

        valid_options = {
            vo.name.lower(): vo.pk for vo in ValidOption.objects.all()
        }
        for entry in self.search_entries["entries"]:
            prov_id = entry.get("prov_id")

            valid_option = pre_classify_response.get(str(prov_id))
            if valid_option is None or valid_option == "desconocido":
                continue
            entry["pre_valid_option"] = valid_options.get(valid_option)
