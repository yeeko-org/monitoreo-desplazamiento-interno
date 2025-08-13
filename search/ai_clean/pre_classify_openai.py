from typing import List
from source.models import Source, SourceOrigin
from search.ai_clean.open_ai_request import GeminiRequest, PreClassify


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


class FindOrigin:
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
        self.pending_sources: dict = {}

    def get_pre_classify_response(self, all_entries: List[dict]):
        from search.ai_clean.open_ai_request import OpenAIRequest

        for current_id, entry_data in enumerate(all_entries, 1):
            entry_data["prov_id"] = current_id
            try:
                self._pre_classify_entry(entry_data, current_id)
            except IsForeign:
                continue

        clean_entries = self._get_valid_entries_for_openai()
        return OpenAIRequest.get_pre_classify_response(clean_entries)

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
            new_entry["source_id"] = source_saved.id

        except Source.DoesNotExist:
            source_id = self.search_source(
                gnews_source_url, gnews_source_title)
            new_entry["source_id"] = source_id
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

    def _get_valid_entries_for_openai(self):
        clean_entries = []
        new_sources = self._pre_classify_sources()
        if self.pending_sources:

            new_foreign_sources = new_sources.foreign
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
        if not self.pending_sources:
            print("No pending sources to pre-classify.")
            return PreClassify()

        gemini_response: PreClassify = GeminiRequest\
            .get_pre_classify_origin_response(self.pending_sources)
        self._save_gemini_sources_response(gemini_response)

        return gemini_response

    def _save_gemini_sources_response(self, gemini_response: PreClassify):

        fields = PreClassify.model_fields
        for category in fields:
            origin_name = ORIGINS_EQUIVALENCES.get(category, None)
            origin_obj = SourceOrigin.objects \
                .filter(name__iexact=origin_name).first()
            if not origin_obj:
                print(f"Origin '{origin_name}' not found.")
                continue
            for source_id in getattr(gemini_response, category, []):
                source_id = int(source_id)
                source = Source.objects.filter(id=source_id).first()
                if not source:
                    print(f"Source with ID {source_id} not found.")
                    continue
                source.source_origin = origin_obj
                source.save()
