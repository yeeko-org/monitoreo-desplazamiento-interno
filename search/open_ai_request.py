import json
from utils.open_ai import JsonRequestOpenAI
from utils.gemini_ai import RequestGemini
from pydantic import BaseModel
import enum


class OpenAIRequest:

    @staticmethod
    def get_pre_classify_response(clean_entries):
        if not clean_entries:
            return
        try:
            full_prompt = json.dumps(clean_entries)
        except Exception as e:
            print("Error creating prompt", e)
            return

        pre_classify_request = JsonRequestOpenAI(
            "search/prompt_pre_clasify.txt")
        pre_classify_response = pre_classify_request.send_prompt(full_prompt)
        if isinstance(pre_classify_response, dict):
            return pre_classify_response

    @staticmethod
    def get_pre_classify_origin_response(pending_sources):
        user_prompt = ""
        # print("Pending sources\n", self.pending_sources)
        for source_url, values in pending_sources.items():
            simple_url = source_url.split("//")[-1]
            user_prompt += f"{values['id']}: {values['title']} ({simple_url})\n"

        origin_request = JsonRequestOpenAI(
            "source/prompt_origin.txt")
        # print("User prompt\n", user_prompt)
        origin_response = origin_request.send_prompt(user_prompt)
        # print("Origin response\n", origin_response)
        if isinstance(origin_response, dict):
            return origin_response


class PreClassify(BaseModel):
    mexican: list[int] = []
    international: list[int] = []
    foreign: list[int] = []
    unknown: list[int] = []


class GeminiRequest:

    @staticmethod
    def get_pre_classify_response(clean_entries:dict):
        pass

    @staticmethod
    def get_pre_classify_origin_response(pending_sources:dict):
        all_sources = []
        for entry in pending_sources.values():
            all_sources.append({
                "id": entry["id"],
                "name": entry["title"],
                "url": entry["main_url"]
            })

        pre_classify_request = RequestGemini()
        pre_classify_request.build_chat("source/prompt_gemini_origin.txt")
        pre_classify_response = pre_classify_request.send_gemini_prompt(
            all_sources, schema_clss=PreClassify, main_name="media_landscapes")
        return pre_classify_response
