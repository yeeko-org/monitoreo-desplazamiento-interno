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
        "key_name": "source_types",
        "name": "Fuente de información",
        "plural_name": "Fuentes de información",
        "main_collection": "news-note",
        "filter_collections": [
            "news-note",
        ],
        "category_subtype": "news-source",
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
