from utils.open_ai import JsonRequestOpenAI


class NewOpenAI(JsonRequestOpenAI):
    def __init__(self):
        super().__init__()
        self.first_example = ""
        self.first_response = {}
        self.prompt = ""