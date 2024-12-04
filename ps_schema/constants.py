all_collections = {
    "news": [
        {
            "snake_name": "note",
            "name": "Nota",
            "plural_name": "Notas",
            "model_name": "Note",
            "level": "primary",
            "status_groups": ["register"],
            "color": 'deep-purple',
            "icon": 'newspaper',
            "all_filters": [
                {"filter_name": "source_types", "hidden": False},
            ],
        },
        {
            "snake_name": "source",
            "name": "Fuente de información",
            "plural_name": "Fuentes de información",
            "model_name": "Source",
            "level": "category_subtype",
        },
        {
            "snake_name": "cluster",
            "name": "Cluster",
            "plural_name": "Clusters",
            "model_name": "Cluster",
            "level": "category_type",
        },
        {
            "snake_name": "word_list",
            "name": "Lista de palabras",
            "plural_name": "Listas de palabras",
            "model_name": "WordList",
            "level": "category_subtype",
        },
        {
            "snake_name": "search_query",
            "name": "Consulta de palabras",
            "plural_name": "Consultas de palabras",
            "model_name": "SearchQuery",
            "level": "primary",
            "status_groups": ["register"],
            "color": 'blue',
            "icon": 'search',
            "cat_params": {
                "init_display": True,
            },
        },
    ],
    "geo": [
        {
            "snake_name": "state",
            "name": "Estado",
            "plural_name": "Estados",
            "model_name": "State",
            "level": "category_group",
        },
        {
            "snake_name": "municipality",
            "name": "Municipio",
            "plural_name": "Municipios",
            "model_name": "Municipality",
            "level": "category_type",
        },
        {
            "snake_name": "locality",
            "name": "Localidad",
            "plural_name": "Localidades",
            "model_name": "Locality",
            "level": "category_subtype",
        },
        {
            "snake_name": "location",
            "name": "Ubicación",
            "plural_name": "Ubicaciones",
            "model_name": "Location",
            "level": "primary",
            "status_groups": ["location"],
        },
    ]
}

filter_groups = [
    {
        "key_name": "sources",
        "name": "Fuente de información",
        "plural_name": "Fuentes de información",
        "main_collection": "news-note",
        "filter_collections": [
            "news-note",
        ],
        "category_subtype": "news-source",
    },
    {
        "key_name": "word_lists",
        "name": "Lista de palabras",
        "plural_name": "Listas de palabras",
        "main_collection": "news-search_query",
        "filter_collections": [
            "news-word_list",
        ],
        "category_type": "news-cluster",
        "category_subtype": "news-word_list",
        # "category_subtype": "news-cluster",
    },
    {
        "key_name": "states",
        "name": "Estado",
        "plural_name": "Estados",
        "main_collection": "geo-location",
        "category_subtype": "geo-state",
    },
    {
        "key_name": "geographicals",
        "name": "Geográficos",
        "plural_name": "Geográficos",
        "main_collection": "geo-location",
        "filter_collections": [
            "geo-location",
        ],
        "category_group": "geo-state",
        "category_type": "geo-municipality",
        "category_subtype": "geo-locality",
    },
]

collection_links = [
    {
        "parent": "news-source",
        "child": "news-note",
        "link_type": "category",
        "is_mandatory": True,
    },
    # {
    #     "parent": "news-note",
    #     "child": "news-mention",
    #     "link_type": "relational",
    #     "is_multiple": True,
    #     "is_mandatory": True,
    # },
    # {
    #     "parent": "news-mention",
    #     "child": "actor-participant",
    #     "link_type": "relational",
    #     "is_multiple": True,
    #     "is_mandatory": True,
    # },
    {
        "parent": "news-cluster",
        "child": "news-word_list",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "news-word_list",
        "child": "news-search_query",
        "link_type": "category",
        "is_mandatory": True,
        "is_multiple": True,
    },
    {
        "parent": "geo-state",
        "child": "geo-municipality",
        "link_type": "grouper",
        "filter_group": "geographicals",
        "is_mandatory": True,
    },
    {
        "parent": "geo-municipality",
        "child": "geo-locality",
        "link_type": "grouper",
        "filter_group": "geographicals",
        "is_mandatory": True,
    },
]


def send_many_requests():
    import requests
    import json
    import time

    error_ids = [2107]
    # 2075
    all_ids = [
        2107, 2005, 1902, 1896, 1833, 1832, 1737, 1571, 1501,
        1450, 1405, 1270, 797, 760, 718, 49]
    url = "https://ocsa.ibero.mx/api/rpc/approve_draft"
    headers = {
        'Content-Type': 'application/json',
        "Authorization": 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoib2Nzd2ViYWRtaW4iLCJlbWFpbCI6InNlYmFzdGlhbi5vbHZlcmFAaWJlcm8ubXgifQ.boDDaOPQXa9Q3LMohHXQvuw85fR5rEKPcMxr4nqzGms'
    }

    for elem_id in all_ids:
        payload = {'_id': elem_id}
        with requests.Session() as session:
            response = session.post(
                url, headers=headers, data=json.dumps(payload))
            if response.text:
                print(f"elem_id: {elem_id} | response: {response.text}")
        time.sleep(35)
