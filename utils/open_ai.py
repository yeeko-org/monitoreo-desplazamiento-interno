import json
import re
from typing import Optional
import openai

from django.conf import settings
import tiktoken

TOKENS_MAX_LENGTH = getattr(settings, 'OPENAI_TOKENS_MAX_LENGTH', 128000)
MODEL_NAME = getattr(settings, 'OPENAI_ENGINE', 'gpt-4o')


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

    def __init__(self, prompt_path: str, to_json: bool = True):
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)

        self.client = openai.OpenAI(api_key=openai_api_key)
        self.engine = getattr(settings, 'OPENAI_ENGINE', 'gpt-4o')
        self.messages: list[dict] = []
        self.to_json = to_json
        self.response = None
        with open(prompt_path, "r", encoding="utf-8") as file:
            init_prompt = file.read()
        msgs = init_prompt.split("\n====\n")
        self.build_msg(msgs[0], "system")
        for idx, msg in enumerate(msgs[1:]):
            role = "user" if idx % 2 == 0 else "assistant"
            self.build_msg(msg, role)
        self.first_example = ""
        self.first_response = {}
        self.prompt = ""

    def send_prompt(self, new_prompt):
        if not new_prompt:
            return None
        self.build_msg(new_prompt, "user")
        response_format = {"type": "json_object"} \
            if self.to_json else None
        try:
            response = self.client.chat.completions.create(
                model=self.engine,
                response_format=response_format,
                messages=self.messages,
                temperature=0.6,
                max_tokens=16000,
                top_p=0.8,
                frequency_penalty=0,
                presence_penalty=0
            )
            self.response = response
        except openai.BadRequestError as e:
            print(f"messages: {self.messages}")
            print(f"OpenAI BadRequestError: {e}")
            raise e

        if self.to_json:
            json_response = response.choices[0].message.content
            if not json_response:
                return None
            try:
                return json.loads(json_response)
            except Exception:
                return None
        else:
            return response.choices[0].message.content

    def build_msg(self, prompt, role="user"):
        # print("-"*50)
        # print(f"role: {role}\nprompt: {prompt}\n")
        if len(prompt) > 9000:
            prompt = prompt[:9000]
        if self.to_json and role == "assistant":
            try:
                prompt = json.dumps(json.loads(prompt))
            except Exception as e:
                print(f"Error converting to json: {e}")
        self.messages.append({
            "role": role,
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        })


def truncate_text(plain_text, limit=None):
    encoding = tiktoken.encoding_for_model(MODEL_NAME)
    tokens = encoding.encode(plain_text)
    token_count = len(tokens)

    tokens_max_length = int((limit or TOKENS_MAX_LENGTH)/2)

    if token_count > tokens_max_length:
        tokens = tokens[:tokens_max_length]
        truncated_text = encoding.decode(tokens)
    else:
        truncated_text = plain_text

    return {
        "original_token_count": token_count,
        "truncated_text": truncated_text,
        "truncated_text_count": len(encoding.encode(truncated_text))
    }
