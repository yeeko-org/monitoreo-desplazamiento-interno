import json
import re
from typing import Optional
import openai

from django.conf import settings


def format_prompt_text(text: str, has_pipe: bool = False):
    if has_pipe:
        new_text = text
        new_text = re.sub(r"\s{2,}", " ", new_text)
    else:
        new_text = text.replace("\n", "|")
        new_text = re.sub(r"\s{2,}", " ", new_text)
    new_text = new_text.replace("|", "\n")
    new_text = new_text.strip()
    return new_text


class JsonRequestOpenAI:
    first_example: str
    first_response: dict
    prompt: str

    def __init__(self):
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)

        self.client = openai.OpenAI(api_key=openai_api_key)
        self.engine = getattr(settings, 'OPENAI_ENGINE', 'gpt-4o')
        self.first_example = ""
        self.first_response = {}
        self.prompt = ""

    def extract_information(self, text) -> Optional[dict]:

        if not text:
            return None

        messages = [
            {
                "role": "system",
                "content": [
                        {
                            "type": "text",
                            "text": format_prompt_text(self.prompt)
                        }
                ]
            },
            {
                "role": "user",
                "content": [
                        {
                            "type": "text",
                            "text": self.first_example
                        }
                ]
            },
            {
                "role": "assistant",
                "content": [
                        {
                            "type": "text",
                            "text": format_prompt_text(
                                json.dumps(self.first_response), has_pipe=True)
                        }
                ]
            },
            {
                "role": "user",
                "content": [
                        {
                            "type": "text",
                            "text": text
                        }
                ]
            },

        ]

        response = self.client.chat.completions.create(
            model=self.engine,
            response_format={"type": "json_object"},
            messages=messages,  # type: ignore
            temperature=1,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        json_response = response.choices[0].message.content
        if not json_response:
            return None
        try:
            return json.loads(json_response)
        except Exception:
            return None
