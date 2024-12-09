from datetime import date
import json
from typing import List, Optional, Any, Union


from django.db import models
from utils.open_ai import JsonRequestOpenAI
from utils.yeeko_gnews import YeekoGoogleNews

from category.models import StatusControl
from utils.date_time import get_range_dates, parse_gmt_date_list

from source.models import Source, SourceOrigin


class Cluster(models.Model):
    # key_name = models.CharField(max_length=60, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Cluster'
        verbose_name_plural = 'Clusters'


class WordList(models.Model):
    cluster = models.ForeignKey(
        Cluster, on_delete=models.CASCADE, related_name='words')
    name = models.CharField(max_length=255, unique=True)
    query_words = models.TextField(blank=True, null=True)
    soft_query_words = models.TextField(blank=True, null=True)

    def get_all_words(self, enclose_sentences=True, include_soft=False):
        if not self.query_words:
            return []
        else:
            words = self.query_words.split(",")

        if include_soft and self.soft_query_words:
            words.extend(self.soft_query_words.split(","))

        words = list(set(words))

        standard_words = [word.strip() for word in words if word.strip()]
        return [
            f'"{word}"' if " " in word and enclose_sentences else word
            for word in standard_words
        ]

    def get_or_query(self, include_soft=False):
        return " OR ".join(self.get_all_words())

    def get_negative_query(self, include_soft=False):
        return " ".join([f"-{word}" for word in
                         self.get_all_words(include_soft=include_soft)])

    def __str__(self):
        if not self.query_words:
            return self.name

        query_list = self.query_words.split(",")
        alt_words = ", ".join(query_list[:2])
        if len(query_list) > 2:
            alt_words = alt_words + ", ..."
        return f"{self.name} ({alt_words})"

    class Meta:
        verbose_name = 'Lista de palabras'
        verbose_name_plural = 'Listas de palabras'
        ordering = ['cluster', 'name']


def words_query_union(
        words_query, union="OR", funtion="get_or_query", include_soft=False):
    if funtion not in ["get_or_query", "get_negative_query"]:
        raise ValueError("Invalid function")
    if not union:
        union = " "
    else:
        union = f" {union} "
    return union.join(
        [getattr(word_list, funtion)(include_soft=include_soft)
         for word_list in words_query])


class SearchQuery(models.Model):
    name = models.CharField(max_length=100)

    query = models.TextField(blank=True, null=True)
    # soft_negative_words = models.TextField(blank=True, null=True)
    manual_query = models.TextField(blank=True, null=True)
    use_manual_query = models.BooleanField(default=False)

    main_words = models.ManyToManyField(
        WordList, related_name='main_queries', blank=True)
    complementary_words = models.ManyToManyField(
        WordList, related_name='complementary_queries', blank=True)
    negative_words = models.ManyToManyField(
        WordList, related_name='negative_queries', blank=True)
    # soft_negative_words = models.ManyToManyField(
    #     WordList, related_name='soft_negative_queries', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    status_register = models.ForeignKey(
        StatusControl, on_delete=models.CASCADE, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, do_words=False, **kwargs):
        print("Saving search query", do_words)
        if do_words:
            self.query_words()

        return super().save(*args, **kwargs)

    def get_query_words(self, include_soft=False):
        main_query = words_query_union(self.main_words.all())
        # print("Main query", main_query)
        if not main_query:
            return

        complementary_query = words_query_union(
            self.complementary_words.all())
        negative_terms = words_query_union(
            self.negative_words.all(), union="",
            funtion="get_negative_query", include_soft=include_soft)

        if complementary_query or negative_terms:
            query = f"({main_query})"
        else:
            query = main_query

        if complementary_query:
            query += f" AND ({complementary_query})"

        query += "{{DATE}}"

        if negative_terms:
            query += f" {negative_terms}"
        # print("Query words", query)
        return query

    def query_words(self):
        print("Querying words")
        self.query = self.get_query_words()

    @property
    def query_words_soft(self):
        return words_query_union(
            self.negative_words.all(), union="",
            funtion="get_negative_query", include_soft=True)

    def search(
            self, when: Optional[Any], from_date: Optional[date],
            to_date: Optional[date]
    ):
        if self.use_manual_query:
            if not self.manual_query:
                raise ValueError("Manual query is empty")
            final_query = self.manual_query
        else:
            self.query_words()
            if not self.query:
                raise ValueError("Query is empty")
            final_query = self.query

        if when:
            links_data = self.search_when(when, final_query)
        elif from_date and to_date:
            links_data = self.search_from_to(from_date, to_date, final_query)
        else:
            raise ValueError("No dates provided")

        entries = self.search_filter_soft(
            links_data.get("entries", []))

        if not when:
            entries = self.pre_classify_openai(entries)

        return {
            "entries": entries,
            "feed": links_data.get("feed"),
            "errors": links_data.get("errors")  # type: ignore
        }

    def search_from_to(
            self, from_date: date, to_date: date, search_query: str
    ):

        search_kwargs = {}
        range_dates = get_range_dates(None, from_date, to_date)
        all_links_data = []
        last_feed = None
        errors = []
        for from_date_r, to_date_r in range_dates:

            search_kwargs["from_"] = from_date_r.strftime("%Y-%m-%d")
            search_kwargs["to_"] = to_date_r.strftime("%Y-%m-%d")

            gn = YeekoGoogleNews("es", "MX")
            print("Searching...\n", search_query, "\n", search_kwargs)
            try:
                links_data = gn.search(
                    search_query, helper=False, **search_kwargs)
            except Exception as e:
                errors.append(str(e))
                continue
            all_links_data.extend(links_data.get("entries", []))
            last_feed = links_data.get("feed", None)

        return {
            "entries": all_links_data,
            "feed": last_feed,
            "errors": errors
        }

    def search_when(
            self, when: Any, search_query: str
    ):
        try:
            when = int(when)
            when = f"{when}d"
        except ValueError:
            pass
        search_kwargs = {"when": when or "1d"}
        gn = YeekoGoogleNews("es", "MX")
        print("Searching...\n", search_query, "\n", search_kwargs)
        return gn.search(search_query, helper=False, **search_kwargs)

    def search_filter_soft(self, entries: List[dict]):
        entries_filtered = []
        all_negative_words = []
        for word_list in self.negative_words.all():
            all_negative_words.extend(
                word_list.get_all_words(
                    enclose_sentences=False, include_soft=True))

        all_negative_words = [
            word.strip().lower() for word in all_negative_words if word.strip()]

        for entry in entries:
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            if any([
                word in title or word in summary
                for word in all_negative_words
            ]):
                continue

            entries_filtered.append(entry)
        return entries_filtered

    def pre_classify_openai(self, entries: List[dict]):
        from note.models import NoteLink, ValidOption

        entries_for_openai = []
        pending_sources = {}
        new_sources_ids = []
        valid_origins = SourceOrigin.objects.filter(
            name__in=["Nacional", "Internacional"]).values_list("id", flat=True)
        valid_sources = Source.objects.filter(source_origin__in=valid_origins)
        valid_sources_dict = {source.main_url: source
                              for source in valid_sources}
        unknown_sources = Source.objects\
            .filter(source_origin__name="Desconocido")
        unknown_dict = {source.main_url: {"id": source.id, "name": source.name}
                        for source in unknown_sources}
        foreign_sources = Source.objects\
            .filter(source_origin__name="Extranjera")\
            .values_list("main_url", flat=True)

        current_id = 1
        for openai_entry in entries:

            new_entry = {
                "title": openai_entry.get("title"),
                "prov_id": current_id
            }
            openai_entry["prov_id"] = current_id
            # openai_entry["prov_id"] = current_id
            current_id += 1
            # gnews_id = openai_entry.get("id", "")
            gnews_url = openai_entry.get("link")
            gnews_source_title = openai_entry.get("source", {}).get("title")
            gnews_source_url = openai_entry.get("source", {}).get("href")
            if gnews_source_url in foreign_sources:
                continue

            if gnews_source_url not in valid_sources_dict:
                source_dict = {
                    "title": gnews_source_title,
                    "main_url": gnews_source_url,
                }
                origin = self.get_origin_by_domain(gnews_source_url)
                if source_obj := unknown_dict.get(gnews_source_url):
                    source_dict["id"] = source_obj["id"]
                else:
                    new_source, created = Source.objects.get_or_create(
                        name=gnews_source_title,
                        main_url=gnews_source_url,
                    )
                    if created:
                        new_sources_ids.append(new_source.id)
                    source_dict["id"] = new_source.id
                    if origin:
                        new_source.source_origin = origin
                        new_source.save()
                    else:
                        pending_sources.setdefault(
                            gnews_source_url, source_dict)
                if origin and origin.name == "Extranjera":
                    continue
                new_entry["source_id"] = source_dict["id"]

            note_link = NoteLink.objects.filter(gnews_url=gnews_url).first()
            if note_link:
                # if note_link.is_dfi is not None or note_link.pre_is_dfi is not None:
                if note_link.valid_option or note_link.pre_is_dfi is not None:
                    continue
            new_entry.update({
                "source_url": gnews_source_url,
                "source_title": gnews_source_title
            })
            entries_for_openai.append(new_entry)

        clean_entries = []
        if pending_sources:
            new_foreign_sources = self.pre_classify_sources(pending_sources)
            # print("New foreign sources", new_foreign_sources)
            # entries_for_openai = [
            #     entry for entry in entries_for_openai
            #     if entry.get("source_id") not in new_foreign_sources
            # ]
            for entry in entries_for_openai:
                source_id = entry.get("source_id")
                if source_id and source_id in new_foreign_sources:
                    continue
                clean_entries.append(entry)

        if not clean_entries:
            return entries

        full_prompt = json.dumps(clean_entries)

        pre_classify_request = JsonRequestOpenAI("search/prompt_pre_clasify.txt")
        pre_classify_response = pre_classify_request.send_prompt(full_prompt)
        print("Pre classify response:", pre_classify_response)
        if not isinstance(pre_classify_response, dict) or not pre_classify_response:
            return entries

        """
        title, id, source_url, source_title, is_dfi, source_is_foreign
        """
        valid_options = {
            vo.name.lower(): vo.id for vo in ValidOption.objects.all()
        }
        # print("Valid options", valid_options)
        for entry in entries:
            # gnews_id = entry.get("id")
            # if not gnews_id:
            #     continue
            prov_id = entry.get("prov_id")

            valid_option = pre_classify_response.get(str(prov_id))
            if valid_option is None or valid_option == "desconocido":
                # print("Valid option not processed", valid_option)
                continue
            # print("valid final", prov_id, valid_options.get(valid_option))
            entry["pre_valid_option"] = valid_options.get(valid_option)

        return entries

    def get_origin_by_domain(self, domain: str):
        if domain.endswith(".mx"):
            return SourceOrigin.objects.get(name="Nacional")
        spanish_countries = [
            'cr', 'cu', 'do', 'sv', 'gt', 'hn', 'ni', 'pa', 'ar', 'bo', 'cl',
            'co', 'ec', 'py', 'pe', 'uy', 've', 'gq']
        country_code = domain.split(".")[-1]
        if country_code in spanish_countries:
            return SourceOrigin.objects.get(name="Extranjera")
        return None

    def pre_classify_valid(self):
        pass

    def pre_classify_sources(self, pending_sources: dict):
        equivalences = {
            "mexican": "Nacional",
            "international": "Internacional",
            "foreign": "Extranjera",
            "unknown": "Desconocido"
        }
        # origins_dict = {
        #     origin.name: origin for origin in SourceOrigin.objects.all()
        # }
        # origins_dict = {
        #     key: origins_dict.get(equivalences.get(key, key))
        #     for key in origins_dict
        # }
        origins_dict = {}
        for key, value in equivalences.items():
            origin = SourceOrigin.objects.filter(name__iexact=value).first()
            if origin:
                origins_dict[key] = origin
        user_prompt = ""
        # print("Pending sources\n", pending_sources)
        for source_url, values in pending_sources.items():
            simple_url = source_url.split("//")[-1]
            user_prompt += f"{values['id']}: {values['title']} ({simple_url})\n"
        origin_request = JsonRequestOpenAI(
            "source/prompt_origin.txt")
        # print("User prompt\n", user_prompt)
        origin_response = origin_request.send_prompt(user_prompt)
        # print("Origin response\n", origin_response)
        if not isinstance(origin_response, dict) or not origin_response:
            return
        new_foreign_sources = []
        for source_id, classification in origin_response.items():
            source_id = int(source_id)
            if classification in ["unknown"]:
                continue
            if classification == "foreign":
                new_foreign_sources.append(source_id)
            source_id = int(source_id)
            origin = origins_dict.get(classification)
            if origin:
                source = Source.objects.get(id=source_id)
                source.source_origin = origin
                source.save()
            else:
                print("Invalid classification", classification)
        return new_foreign_sources

    class Meta:
        verbose_name = 'Consulta'
        verbose_name_plural = 'Consultas'


class ApplyQuery(models.Model):

    search_query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name='apply_queries')
    created_at = models.DateTimeField(auto_now_add=True)
    # when = models.CharField(
    #     max_length=10, help_text='1d', blank=True, null=True
    # )
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField(blank=True, null=True)

    has_errors = models.BooleanField(default=False)
    errors = models.JSONField(blank=True, null=True)
    last_feed = models.JSONField(blank=True, null=True)

    def search_and_save_entries(self):
        links_data = self.search_query.search(
            None, self.from_date, self.to_date)
        entries = links_data.get("entries", [])

        sources = {}
        created_count = 0
        for entry in entries:
            note_link, is_created = self.save_entry(entry, sources)
            if is_created:
                created_count += 1

        return {
            "created": created_count,
            "total": len(entries)
        }

    def save_entry(self, entry: dict, sources: dict):
        from note.models import NoteLink
        source_name = entry.get("source", {}).get("title")
        if source_name not in sources:
            source_url = entry.get("source", {}).get("href")
            try:
                source, _ = Source.objects.get_or_create(
                    main_url=source_url,
                    defaults={"name": source_name}
                )
            except Exception as e:
                source = Source.objects.filter(main_url=source_url).first()
            sources[source_name] = source
        else:
            source = sources[source_name]

        note_link, is_created = NoteLink.objects.get_or_create(
            gnews_url=entry.get("link"),
            defaults=dict(
                title=entry.get("title"),
                description=entry.get("summary"),
                source=source,
                published_at=parse_gmt_date_list(
                    entry.get("published_parsed"))
            )
        )
        note_link.queries.add(self)
        return note_link, is_created

    def add_errors(self, errors: Union[str, List[str]], save=True):
        if isinstance(errors, str):
            errors = [errors]

        self.has_errors = True
        if not self.errors:
            self.errors = errors
        elif isinstance(self.errors, list):
            self.errors.extend(errors)
        else:
            self.errors = [self.errors] + errors

        self.errors = list(set(self.errors))

        if save:
            self.save()

    def __str__(self):
        return self.search_query.name

    class Meta:
        verbose_name = 'Aplicación de consulta'
        verbose_name_plural = 'Aplicaciones de consulta'
