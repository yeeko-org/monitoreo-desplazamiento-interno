
from note.models import ValidOption, NoteLink
from search.models import ApplyQuery
from utils.gemini_ai import RequestGemini
from typing import List, Dict
from django.db.models.query import QuerySet as queryset
from api.note.serializers import NoteLinkGeminiSerializer
from pydantic import BaseModel


class PreClassify(BaseModel):
    valid: list[int] = []
    invalid: list[int] = []
    maybe: list[int] = []
    unknown: list[int] = []


class PreClassifier:
    """
    Pre-classification class for AI clean.
    This class is used to pre-classify the data before processing.
    """
    fields = PreClassify.model_fields

    def __init__(self):
        self.pending_note_links: queryset[NoteLink] = NoteLink.objects.none()
        self.errors: List[str] = []
        self.valid_options_dict: Dict[str, ValidOption] = {}
        self._get_valid_options_dict()

    def _get_valid_options_dict(self):
        valid_options = ValidOption.objects.all()
        self.valid_options_dict = {
            valid_option.description: valid_option
            for valid_option in valid_options
        }

    def pre_classify_notes(self, apply_query: ApplyQuery):
        """
        Run the pre-classification process on the provided note links.
        :param apply_query: The ApplyQuery instance containing the query data.
        """
        note_links = NoteLink.objects.filter(queries=apply_query)
        self.pending_note_links = note_links\
            .filter(
                pre_valid_option__isnull=True,
                valid_option__isnull=True)\
            .exclude(source__source_origin__in_scope=False)
        if not self.pending_note_links.exists():
            print("No pending note links to pre-classify.")
            return
        self.pre_classify_with_gemini()

    def pre_classify_with_gemini(self):

        len_pending = self.pending_note_links.count()
        chunks = [self.pending_note_links[i:i + 50]
                  for i in range(0, len_pending, 50)]
        pre_classify_request = RequestGemini()
        pre_classify_request.build_chat(
            "search/ai_clean/prompt_gemini_pre_classify.txt")

        for chunk in chunks:
            chunk_data = NoteLinkGeminiSerializer(chunk, many=True).data
            classified_ids = pre_classify_request.send_gemini_prompt(
                chunk_data, schema_clss=PreClassify, main_name="articles")
            if not classified_ids:
                print("No classified ids returned from Gemini.")
                continue
            self._save_valid_options(classified_ids, chunk)
        self.errors = pre_classify_request.errors

    def _save_valid_options(
            self, classified_ids: PreClassify, note_links: queryset[NoteLink]):

        for valid_option in self.fields:
            valid_option_obj = self.valid_options_dict.get(valid_option)
            if not valid_option_obj:
                print(f"Valid option '{valid_option}' not found.")
                continue
            ids = getattr(classified_ids, valid_option, [])
            if not ids:
                continue
            NoteLink.objects\
                .filter(id__in=ids)\
                .update(pre_valid_option=valid_option_obj)




