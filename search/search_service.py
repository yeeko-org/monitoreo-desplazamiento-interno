from search.ai_clean.pre_classify_openai import PreClassifyOpenAI


class SearchNotesService:
    pre_classify_request: PreClassifyOpenAI

    search_entries: dict

    def pre_classify_openai(self):
        from note.models import ValidOption

        pre_classify_request = PreClassifyOpenAI()
        pre_classify_response = pre_classify_request\
            .get_pre_classify_response(self.search_entries["entries"])

        if not pre_classify_response:
            return

        valid_options = {
            vo.name.lower(): vo.pk for vo in ValidOption.objects.all()
        }
        for entry in self.search_entries["entries"]:
            prov_id = entry.get("prov_id")

            valid_option = pre_classify_response.get(str(prov_id))
            if valid_option is None or valid_option == "desconocido":
                continue
            entry["pre_valid_option"] = valid_options.get(valid_option)
