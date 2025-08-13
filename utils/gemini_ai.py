import json
import re

from django.conf import settings
from google import genai
from google.genai import types


class RequestGemini:
    first_response = None
    # client = openai.OpenAI(api_key=openai_api_key)
    # engine = getattr(settings, 'OPENAI_ENGINE', 'gpt-4.1-2025-04-14')

    def __init__(
            self,
            engine="gemini-2.5-flash"
    ):

        api_key_name = "GEMINI_API_KEY"
        api_key = getattr(settings, api_key_name, None)


        self.client = genai.Client(api_key=api_key)
        self.engine = engine
        self.messages: list[dict] = []
        self.base_messages: list[str] = []
        self.msgs = []
        self.system_msg = None
        self.response = None
        self.cache = None
        self.errors = []

    def build_chat(self, prompt_path: str):
        with open(prompt_path, "r", encoding="utf-8") as file:
            init_prompt = file.read()
        self.msgs = init_prompt.split("\n====\n")
        self.system_msg = self.msgs[0]

        # for idx, msg in enumerate(self.msgs[1:]):
        #     role = "sections: " if idx % 2 == 0 else "JSON: "
        #     new_prompt = self.format_prompt(msg)
        #     new_prompt = f"{role}{new_prompt}"
        #     self.base_messages.append(new_prompt)

    def create_cache(
            self, name:str = 'criteria_v1_single', seconds:int = 300
    ):
        model = f"models/{self.engine}"
        try:
            self.cache = self.client.caches.create(
                model=model,
                config=types.CreateCachedContentConfig(
                    display_name=name,
                    system_instruction=self.system_msg,
                    # ttl="300s",
                    ttl=f"{seconds}s",
                )
            )
        except Exception as e:
            print(f"Error creating cache: {e}")
            self.cache = None

    def format_prompt(self, prompt):
        if not prompt:
            return None
        if isinstance(prompt, str):
            new_prompt = prompt.strip()
        elif isinstance(prompt, dict) or isinstance(prompt, list):
            new_prompt = json.dumps(prompt, ensure_ascii=False, indent=2)
        else:
            print(f"Unsupported prompt type: {type(prompt)}")
            return None
        return new_prompt

    def send_gemini_prompt(
            self, new_prompt, schema_clss=None, main_name='article'
    ):
        new_prompt = self.format_prompt(new_prompt)

        cache_name = self.cache.name if self.cache else None
        if cache_name:
            system_instruction = None
        else:
            system_instruction = self.system_msg

        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            system_instruction=system_instruction,
            response_schema=schema_clss,
            response_mime_type="application/json",
            cached_content=cache_name,
        )
        # content = f"{content}\nsections: {new_prompt}\nJSON:"
        content = f"{main_name}: {new_prompt}"
        try:
            response = self.client.models.generate_content(
                model=self.engine,
                contents=content,
                config=config,
            )
        except Exception as e:
            error = f"Error calling Gemini API: {e}"
            print(error)
            self.errors.append(error)
            return None
        self.response = response
        if not self.first_response:
            self.first_response = response
        # request_id = response.id
        return response.parsed
