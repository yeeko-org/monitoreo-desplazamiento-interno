all_collections = {
    "search": [
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
        {
            "snake_name": "apply_query",
            "name": "Aplicación de Consulta",
            "plural_name": "Aplicaciones de Consulta",
            "model_name": "ApplyQuery",
            "level": "relational",
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
    ],
    "note": [
        {
            "snake_name": "note_content",
            "name": "Contenido de Nota",
            "plural_name": "Contenidos de Notas",
            "model_name": "NoteContent",
            "level": "secondary",
            "status_groups": ["register"],
            "color": 'deep-purple',
            "icon": 'article',
            "all_filters": [
                {"filter_name": "sources", "hidden": False},
            ],
        },
        {
            "snake_name": "note_link",
            "name": "Enlace de Nota",
            "plural_name": "Enlaces de Notas",
            "model_name": "NoteLink",
            "level": "secondary",
            "color": 'purple',
            "icon": 'insert_link',
            "all_filters": [
                {
                    "filter_name": "sources", "hidden": False,
                    "is_multiple": True,
                },
                {
                    "filter_name": "valid_options", "hidden": False,
                    "filter_null": True,
                },
            ],
        },
        {
            "snake_name": "valid_option",
            "name": "Opción de validación",
            "plural_name": "Opciones de validación",
            "model_name": "ValidOption",
            "level": "category_subtype",
        },
    ],
    "source": [
        {
            "snake_name": "source_origin",
            "name": "Origen de fuente",
            "plural_name": "Orígenes de fuentes",
            "model_name": "SourceOrigin",
            "level": "category_type",
        },
        {
            "snake_name": "source",
            "name": "Fuente de información",
            "plural_name": "Fuentes de información",
            "model_name": "Source",
            "level": "category_subtype",
            "all_filters": [
                {
                    "title": "Es scrapeable", "field": "has_content",
                    "component": "TripleBooleanFilter",
                },
            ],
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
        "main_collection": "note_link",
        "filter_collections": [
            "news-note_link"
        ],
        "category_type": "source-source_origin",
        "category_subtype": "source-source",
    },
    {
        "key_name": "word_lists",
        "name": "Lista de palabras",
        "plural_name": "Listas de palabras",
        "main_collection": "search_query",
        "filter_collections": [
            "note_link",
        ],
        "category_type": "search-cluster",
        "category_subtype": "search-word_list",
        # "category_subtype": "news-cluster",
    },
    {
        "key_name": "valid_options",
        "name": "Clasificación de validación",
        "plural_name": "Clasificaciones de validación",
        "main_collection": "note_link",
        "filter_collections": [
            "note_link",
        ],
        "category_subtype": "note-valid_option",
    },
    # {
    #     "key_name": "states",
    #     "name": "Estado",
    #     "plural_name": "Estados",
    #     "main_collection": "location",
    #     "category_subtype": "geo-state",
    # },
    # {
    #     "key_name": "geographicals",
    #     "name": "Geográficos",
    #     "plural_name": "Geográficos",
    #     "main_collection": "location",
    #     "filter_collections": [
    #         "geo-location",
    #     ],
    #     "category_group": "geo-state",
    #     "category_type": "geo-municipality",
    #     "category_subtype": "geo-locality",
    # },
]
