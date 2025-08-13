from utils.open_ai import JsonRequestOpenAI
from utils.gemini_ai import RequestGemini
from pydantic import BaseModel
import enum


class OriginClassify(BaseModel):
    mexican: list[int] = []
    international: list[int] = []
    foreign: list[int] = []
    unknown: list[int] = []


class PreClassify(BaseModel):
    valid: list[int] = []
    invalid: list[int] = []
    maybe: list[int] = []
    unknown: list[int] = []


class GeminiRequest:

    @staticmethod
    def get_pre_classify_response(clean_entries:dict):
        all_entries = []
        print("Clean entries:", clean_entries)
        for entry in clean_entries:
            summary = entry.get("summary", "")
            new_entry = {
                "id": entry["id"],
                "title": entry["title"],
                "source_name": entry.get("source", {}).get("title", ""),
                "source_url": entry.get("source", {}).get("href", ""),
            }
            if summary:
                new_entry["summary"] = summary
            all_entries.append(new_entry)
        pre_classify_request = RequestGemini()
        pre_classify_request.build_chat(
            "search/ai_clean/prompt_gemini_pre_classify.txt")
        pre_classify_response = pre_classify_request.send_gemini_prompt(
            all_entries, schema_clss=PreClassify, main_name="entries")
        if isinstance(pre_classify_response, dict):
            return pre_classify_response
