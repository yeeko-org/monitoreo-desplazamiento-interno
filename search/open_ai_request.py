import json
from utils.open_ai import JsonRequestOpenAI


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
