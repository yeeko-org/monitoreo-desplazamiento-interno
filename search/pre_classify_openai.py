from typing import List


ORIGINS_EQUIVALENCES = {
    "mexican": "Nacional",
    "international": "Internacional",
    "foreign": "Extranjera",
    "unknown": "Desconocido"
}

SPANISH_COUNTRIES = [
    'cr', 'cu', 'do', 'sv', 'gt', 'hn', 'ni', 'pa', 'ar', 'bo', 'cl',
    'co', 'ec', 'py', 'pe', 'uy', 've', 'gq']


class IsForeign(Exception):
    pass


class PreClassifyOpenAI:

    def __init__(
            self
    ):
        from source.models import Source, SourceOrigin
        self.source_origin_nacional = SourceOrigin.objects\
            .get(name="Nacional")
        self.source_origin_foreign = SourceOrigin.objects\
            .get(name="Extranjera")
        self.source_origin_unknown = SourceOrigin.objects\
            .get(name="Desconocido")

        self.entries_for_openai = []
        self.pending_sources = {}
        self.new_sources_ids = []
        self.valid_origins = SourceOrigin.objects\
            .filter(name__in=["Nacional", "Internacional"])\
            .values_list("id", flat=True)

        self.valid_sources = Source.objects\
            .filter(source_origin__in=self.valid_origins)
        self.valid_sources_dict = {
            source.main_url: source for source in self.valid_sources}

        self.unknown_sources = Source.objects\
            .filter(source_origin__name="Desconocido")
        self.unknown_dict = {
            source.main_url: {"id": source.pk, "name": source.name}
            for source in self.unknown_sources}

        self.foreign_sources = Source.objects\
            .filter(source_origin__name="Extranjera")\
            .values_list("main_url", flat=True)

    def get_pre_classify_response(self, entries: List[dict]):
        from search.open_ai_request import OpenAIRequest

        for current_id, entry_data in enumerate(entries, 1):
            entry_data["prov_id"] = current_id
            try:
                self._pre_classify_entry(entry_data, current_id)
            except IsForeign:
                continue

        return OpenAIRequest.get_pre_classify_response(
            self._clean_entries_for_openia())

    def search_source(self, gnews_source_url: str, gnews_source_title: str):
        from source.models import Source
        source_dict = {
            "title": gnews_source_title,
            "main_url": gnews_source_url,
        }
        origin = self.get_origin_by_domain(gnews_source_url)
        if source_obj := self.unknown_dict.get(gnews_source_url):
            source_dict["id"] = source_obj["id"]
        else:
            new_source, created = Source.objects.get_or_create(
                name=gnews_source_title,
                main_url=gnews_source_url,
            )
            if created:
                self.new_sources_ids.append(new_source.pk)
            source_dict["id"] = new_source.pk
            if origin:
                new_source.source_origin = origin
                new_source.save()
            else:
                self.pending_sources.setdefault(
                    gnews_source_url, source_dict)
        if origin and origin.name == "Extranjera":
            raise IsForeign

        return source_dict["id"]

    def _pre_classify_entry(self, entry_data: dict, temporal_entry_id: int):
        from note.models import NoteLink
        new_entry = {
            "title": entry_data.get("title"),
            "prov_id": temporal_entry_id
        }

        gnews_url = entry_data.get("link")
        gnews_source_title = entry_data.get("source", {}).get("title")
        gnews_source_url = entry_data.get("source", {}).get("href")

        if gnews_source_url in self.foreign_sources:
            return

        if gnews_source_url not in self.valid_sources_dict:
            new_entry["source_id"] = self.search_source(
                gnews_source_url, gnews_source_title)

        note_link = NoteLink.objects.filter(gnews_url=gnews_url).first()
        if note_link:
            if note_link.valid_option or note_link.pre_is_dfi is not None:
                return

        new_entry.update({
            "source_url": gnews_source_url,
            "source_title": gnews_source_title
        })
        self.entries_for_openai.append(new_entry)

    def _clean_entries_for_openia(self):
        clean_entries = []
        if self.pending_sources:
            new_foreign_sources = self._pre_classify_sources()
            # print("New foreign sources", new_foreign_sources)
            # self.entries_for_openai = [
            #     entry for entry in self.entries_for_openai
            #     if entry.get("source_id") not in new_foreign_sources
            # ]
            for entry in self.entries_for_openai:
                source_id = entry.get("source_id")
                if source_id and source_id in new_foreign_sources:
                    continue
                clean_entries.append(entry)
        return clean_entries

    def get_origin_by_domain(self, domain: str):
        if domain.endswith(".mx"):
            return self.source_origin_nacional

        country_code = domain.split(".")[-1]
        if country_code in SPANISH_COUNTRIES:
            return self.source_origin_foreign
        return None

    def _get_pre_classify_origins_dict(self):
        from source.models import SourceOrigin
        # origins_dict = {
        #     origin.name: origin for origin in SourceOrigin.objects.all()
        # }
        # origins_dict = {
        #     key: origins_dict.get(equivalences.get(key, key))
        #     for key in origins_dict
        # }
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
