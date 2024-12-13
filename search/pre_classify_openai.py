from typing import List
from source.models import Source, SourceOrigin


ORIGINS_EQUIVALENCES = {
    "mexican": "Nacional",
    "international": "Internacional",
    "foreign": "Extranjera",
    "unknown": "Desconocido"
}

SPANISH_COUNTRIES = (
    'cr', 'cu', 'do', 'sv', 'gt', 'hn', 'ni', 'pa', 'ar', 'bo', 'cl',
    'co', 'ec', 'py', 'pe', 'uy', 've', 'gq')


class IsForeign(Exception):
    pass


class PreClassifyOpenAI:

    def __init__(
            self
    ):
        self.source_origin_nacional = SourceOrigin.objects\
            .get(name="Nacional")
        self.source_origin_foreign = SourceOrigin.objects\
            .get(name="Extranjera")
        self.source_origin_unknown = SourceOrigin.objects\
            .get(name="Desconocido")

        self.valid_name_sources = ["Nacional", "Internacional"]

        self.entries_for_openai = []
        self.pending_sources = {}

    def get_pre_classify_response(self, entries: List[dict]):
        from search.open_ai_request import OpenAIRequest

        for current_id, entry_data in enumerate(entries, 1):
            entry_data["prov_id"] = current_id
            try:
                self._pre_classify_entry(entry_data, current_id)
            except IsForeign:
                continue

        return OpenAIRequest.get_pre_classify_response(
            self._clean_entries_for_openai())

    def search_source(
            self, gnews_source_url: str, gnews_source_title: str,
            source_obj: Source = None):

        origin = self.get_origin_by_domain(gnews_source_url)

        if source_obj and origin:
            source_obj.source_origin = origin
            source_obj.save()
        if not source_obj:
            source_obj, _ = Source.objects.get_or_create(
                name=gnews_source_title,
                main_url=gnews_source_url,
                source_origin=origin or self.source_origin_unknown
            )

        if not origin:
            source_dict = {
                "title": gnews_source_title,
                "main_url": gnews_source_url,
                "id": source_obj.pk
            }
            self.pending_sources.setdefault(gnews_source_url, source_dict)
        elif origin == self.source_origin_foreign:
            raise IsForeign

        return source_obj.pk

    def _pre_classify_entry(self, entry_data: dict, temporal_entry_id: int):
        from note.models import NoteLink
        new_entry = {
            "title": entry_data.get("title"),
            "prov_id": temporal_entry_id
        }

        gnews_url = entry_data.get("link")
        gnews_source_title = entry_data.get("source", {}).get("title")
        gnews_source_url = entry_data.get("source", {}).get("href")
        try:
            source_saved = Source.objects\
                .get(main_url=gnews_source_url, name=gnews_source_title)
            if source_saved.source_origin == self.source_origin_foreign:
                raise IsForeign
            elif source_saved.source_origin.name in self.valid_name_sources:
                pass
            else:
                self.search_source(
                    gnews_source_url, gnews_source_title, source_saved)
            new_entry["source_id"] = source_saved.pk

        except Source.DoesNotExist:
            new_entry["source_id"] = self.search_source(
                gnews_source_url, gnews_source_title)
        except Source.MultipleObjectsReturned:
            sources_saved = Source.objects\
                .filter(main_url=gnews_source_url, name=gnews_source_title)
            for source_saved in sources_saved:
                print("Multiple sources", source_saved.main_url, source_saved.name)
            raise

        note_link = NoteLink.objects.filter(gnews_url=gnews_url).first()
        if note_link:
            if note_link.valid_option or note_link.pre_valid_option:
                return

        new_entry.update({
            "source_url": gnews_source_url,
            "source_title": gnews_source_title
        })
        self.entries_for_openai.append(new_entry)

    def _clean_entries_for_openai(self):
        clean_entries = []
        if self.pending_sources:
            new_foreign_sources = self._pre_classify_sources()
            for entry in self.entries_for_openai:
                source_id = entry.get("source_id")
                if source_id and source_id in new_foreign_sources:
                    continue
                clean_entries.append(entry)
        return clean_entries

    def get_origin_by_domain(self, domain: str):
        if domain.endswith(".mx"):
            return self.source_origin_nacional
        if domain.endswith(SPANISH_COUNTRIES):
            return self.source_origin_foreign
        return None

    def _get_pre_classify_origins_dict(self):
        from source.models import SourceOrigin
        origins_dict = {}
        for key, value in ORIGINS_EQUIVALENCES.items():
            origin = SourceOrigin.objects.filter(name__iexact=value).first()
            if origin:
                origins_dict[key] = origin
        return origins_dict

    def _pre_classify_sources(self):
        from source.models import Source
        from search.open_ai_request import OpenAIRequest

        origins_dict = self._get_pre_classify_origins_dict()
        origin_response = OpenAIRequest.get_pre_classify_origin_response(
            self.pending_sources)
        if not origin_response:
            return

        new_foreign_sources = []
        for source_id, classification in origin_response.items():
            source_id = int(source_id)
            if classification in ["unknown"]:
                continue
            if classification == "foreign":
                new_foreign_sources.append(source_id)
            source_id = int(source_id)
            origin = origins_dict.get(classification)
            if origin:
                source = Source.objects.get(id=source_id)
                source.source_origin = origin
                source.save()
            else:
                print("Invalid classification", classification)
        return new_foreign_sources
