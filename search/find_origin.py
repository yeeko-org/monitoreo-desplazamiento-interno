from source.models import Source, SourceOrigin
from search.models import ApplyQuery
from api.note.serializers import SourceGeminiSerializer
from search.ai_clean.gemini_request import OriginClassify
from utils.gemini_ai import RequestGemini


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
        self.errors: list[str] = []
        self.pending_sources: list[Source] = []
        self.origins_dict = {}
        self._get_pre_classify_origins_dict()

    def find_sources_by_apply_query(self, apply_query: ApplyQuery):

        self.pending_sources = []

        init_pending_sources = Source.objects\
            .filter(note_links__queries=apply_query)\
            .exclude(pre_source_origin__isnull=False)\
            .distinct()

        for source in init_pending_sources:
            source_origin = self.get_origin_by_domain(source.main_url)
            if source_origin:
                source.source_origin = source_origin
                source.pre_source_origin = source_origin
                source.save()
            else:
                self.pending_sources.append(source)

        if not self.pending_sources:
            print("No pending sources to classify.")
            return
        self._pre_classify_sources()

    def get_origin_by_domain(self, domain: str):
        if domain.endswith(".mx"):
            return self.source_origin_nacional
        if domain.endswith(SPANISH_COUNTRIES):
            return self.source_origin_foreign
        return None

    def _get_pre_classify_origins_dict(self):
        from source.models import SourceOrigin
        for key, value in ORIGINS_EQUIVALENCES.items():
            origin = SourceOrigin.objects.filter(name__iexact=value).first()
            if origin:
                self.origins_dict[key] = origin

    def _pre_classify_sources(self):
        pending_sources_data = SourceGeminiSerializer(
            self.pending_sources, many=True).data

        pre_classify_request = RequestGemini()
        pre_classify_request.build_chat(
            "source/prompt_gemini_origin.txt")
        pre_classify_response = pre_classify_request.send_gemini_prompt(
            pending_sources_data, schema_clss=OriginClassify, main_name="entries")
        self.errors.extend(pre_classify_request.errors)

        self._save_gemini_sources_response(pre_classify_response)

    def _save_gemini_sources_response(self, gemini_response: OriginClassify):

        fields = OriginClassify.model_fields
        for category in fields:
            origin_obj = self.origins_dict.get(category, None)
            if not origin_obj:
                print(f"Origin '{category}' not found in origins_dict.")
                continue
            source_ids = getattr(gemini_response, category, [])
            int_source_ids = [int(source_id) for source_id in source_ids]
            Source.objects\
                .filter(id__in=int_source_ids)\
                .update(source_origin=origin_obj, pre_source_origin=origin_obj)
