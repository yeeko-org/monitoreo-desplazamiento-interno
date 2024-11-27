all_collections = {
    "source": [
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
            "snake_name": "mention",
            "name": "Mención de proyecto en nota",
            "plural_name": "Menciones de proyectos en notas",
            "model_name": "Mention",
            "level": "relational",
        },
        {
            "snake_name": "status_history",
            "name": "Historial de estatus",
            "plural_name": "Historial de estatus",
            "model_name": "StatusHistory",
            "level": "secondary",
        },
    ],
    "project": [
        {
            "snake_name": "project",
            "name": "Proyecto",
            "plural_name": "Proyectos",
            "model_name": "Project",
            "level": "primary",
            "status_groups": ["validation", "location"],
            "icon": 'factory',
            "color": 'purple',
            "sort_fields": [
                'id', 'status_validation__order', 'name',
                'status_location__order'
            ],
            "all_filters": [
                {"filter_name": "project_types", "hidden": False},
                {"filter_name": "states", "hidden": False},
                {"filter_name": "status_projects", "hidden": True},
                {"filter_name": "impact_types", "hidden": True},
                {"filter_name": "event_types", "hidden": True},
            ],
        },
        {
            "snake_name": "status_project",
            "name": "Status de Proyecto",
            "plural_name": "Status de Proyectos",
            "model_name": "StatusProject",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "extractivism_type",
            "name": "Tipo de Extractivismo",
            "plural_name": "Tipos de Extractivismo",
            "model_name": "ExtractivismType",
            "level": "category_type",
            "sort_fields": [
                # 'status_validation__order',
                'count',
                {'count': 'Cantidad de proyectos'},
            ],
        },
        {
            "snake_name": "megaproject_type",
            "name": "Tipo de Megaproyecto",
            "plural_name": "Tipos de Megaproyecto",
            "model_name": "MegaprojectType",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "conflict",
            "name": "Conflicto Socioambiental",
            "plural_name": "Conflictos Socioambientales",
            "model_name": "Conflict",
            "level": "primary",
            "icon": 'local_fire_department',
            "color": 'lime',
            "status_groups": ["validation"],
        },
        # {
        #     "snake_name": "project_location",
        #     "name": "Ubicación de Proyecto",
        #     "plural_name": "Ubicaciones de Proyecto",
        #     "model_name": "ProjectLocation",
        #     "level": "relational",
        #     "status_groups": ["location"],
        # },
    ],
    "impact": [
        {
            "snake_name": "impact_group",
            "name": "Grupo de Afectación",
            "plural_name": "Grupos de Afectación",
            "model_name": "ImpactGroup",
            "level": "category_group",
        },
        {
            "snake_name": "impact_type",
            "name": "Tipo de Afectación",
            "plural_name": "Tipos de Afectación",
            "model_name": "ImpactType",
            "level": "category_type",
            "status_groups": ["validation"],
        },
        {
            "snake_name": "impact_subtype",
            "name": "Subtipo de Afectación",
            "plural_name": "Subtipos de Afectación",
            "model_name": "ImpactSubtype",
            "level": "category_subtype",
            "optional_category": True,
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "impact",
            "name": "Afectación",
            "plural_name": "Afectaciones",
            "model_name": "Impact",
            "level": "secondary",
        }
    ],
    "actor": [
        {
            "snake_name": "actor",
            "name": "Actor",
            "plural_name": "Actores",
            "model_name": "Actor",
            "level": "primary",
            "status_groups": ["validation"],
            "icon": 'recent_actors',
            "color": 'blue',
            "sort_fields": [
                'status_validation__order', 'name',
                {'mentions_count': 'Cantidad de menciones'},
            ],
            "all_filters": [
                {"filter_name": "participant_types", "hidden": False},
                {"filter_name": "belongs", "hidden": False},
                {"filter_name": "indigenous_groups", "hidden": True},
                {"filter_name": "sectors", "hidden": False},
                {"filter_name": "countries", "hidden": True},
            ],
        },
        {
            "snake_name": "participant",
            "name": "Participante",
            "plural_name": "Participantes",
            "model_name": "Participant",
            "level": "relational",
        },
        {
            "snake_name": "interest",
            "name": "Interés",
            "plural_name": "Intereses",
            "model_name": "Interest",
            "level": "secondary",
            "color": "cyan",
        },
    ],
    "classify": [
        {
            "snake_name": "participant_group",
            "name": "Tipo de Part.",
            "plural_name": "Tipos de Participación",
            "model_name": "ParticipantGroup",
            "level": "category_type",
        },
        {
            "snake_name": "participant_type",
            "name": "Subtipo de Part.",
            "plural_name": "Subtipos de Participación en Proyecto",
            "model_name": "ParticipantType",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "belong",
            "name": "Grupo de Pertenencia (Vulnerabilidad)",
            "plural_name": "Grupos de Pertenencia (Vulnerabilidades)",
            "model_name": "Belong",
            "level": "category_subtype",
            "cat_params": {"item_id": "key_name"},
            "open_insertion": True,
        },
        {
            "snake_name": "indigenous_group",
            "name": "Pueblo Indígena",
            "plural_name": "Pueblos Indígenas",
            "model_name": "IndigenousGroup",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "sector_group",
            "name": "Grupo Sectorial",
            "plural_name": "Grupos Sectoriales",
            "model_name": "SectorGroup",
            "level": "category_type",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "sector",
            "name": "Sector",
            "plural_name": "Sectores",
            "model_name": "Sector",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "interest_group",
            "name": "Agrupador de tipos de interés",
            "plural_name": "Agrupadores de tipos de interés",
            "model_name": "InterestGroup",
            "level": "category_type",
        },
        {
            "snake_name": "interest_type",
            "name": "Tipo de interés",
            "plural_name": "Tipos de interés",
            "model_name": "InterestType",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "interest_subtype",
            "name": "Subtipo de interés",
            "plural_name": "Subtipos de interés",
            "model_name": "InterestSubtype",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "country",
            "name": "País",
            "plural_name": "Paises",
            "model_name": "Country",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
    ],
    "event": [
        {
            "snake_name": "event",
            "name": "Evento",
            "plural_name": "Eventos",
            "model_name": "Event",
            "level": "secondary",
            "icon": 'notifications_active',
            "color": 'lime',
        },
        {
            "snake_name": "event_group",
            "name": "Grupo de Evento",
            "plural_name": "Grupos de Eventos",
            "model_name": "EventGroup",
            "level": "category_group",
            "all_filters": [
                {"filter_name": "event_types", "hidden": False},
                # {"name": "involved_roles", "hidden": False},
            ],
        },
        {
            "snake_name": "event_type",
            "name": "Tipo de Evento",
            "plural_name": "Tipos de Eventos",
            "model_name": "EventType",
            "level": "category_type",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "event_subtype",
            "name": "Subtipo de Evento",
            "plural_name": "Subtipos de Eventos",
            "model_name": "EventSubtype",
            "level": "category_subtype",
            "status_groups": ["validation"],
            "open_insertion": True,
        },
        {
            "snake_name": "involved_role",
            "name": "Rol en Actividad",
            "plural_name": "Roles en Actividades",
            "model_name": "InvolvedRole",
            "level": "category_subtype",
        },
        {
            "snake_name": "involved",
            "name": "Involucrado en Evento",
            "plural_name": "Involucrados en Eventos",
            "model_name": "Involved",
            "level": "relational",
        },
        # {
        #     "snake_name": "event_location",
        #     "name": "Ubicación de Evento",
        #     "plural_name": "Ubicaciones de Eventos",
        #     "model_name": "EventLocation",
        #     "level": "relational",
        #     "status_groups": ["location"],
        # },
    ],
    "space_time": [
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
        "main_collection": "source-note",
        "filter_collections": [
            "source-note",
        ],
        "category_subtype": "source-source",
    },
    {
        "key_name": "project_types",
        "name": "Clasificación de Proyecto",
        "plural_name": "Clasificaciones de Proyecto",
        "main_collection": "project-project",
        "filter_collections": [
            "project-project",
            "actor-actor",
        ],
        "category_type": "project-extractivism_type",
        "category_subtype": "project-megaproject_type",
    },
    {
        "key_name": "participant_types",
        "name": "Tipo de Participación",
        "plural_name": "Tipos de Participación",
        "main_collection": "actor-actor",
        "filter_collections": [
            "actor-actor",
        ],
        "category_type": "classify-participant_group",
        "category_subtype": "classify-participant_type",
    },
    {
        "key_name": "belongs",
        "name": "Grupo de Pertenencia",
        "plural_name": "Grupos de Pertenencia",
        "main_collection": "actor-actor",
        "filter_collections": [
            "actor-actor",
        ],
        "category_subtype": "classify-belong",
        "addl_config": {"item_id": "key_name"},
    },
    {
        "key_name": "indigenous_groups",
        "name": "Grupo Indígena",
        "plural_name": "Grupos Indígenas",
        "main_collection": "actor-actor",
        "filter_collections": [
            "actor-actor",
        ],
        "category_subtype": "classify-indigenous_group",
    },
    {
        "key_name": "sectors",
        "name": "Sector",
        "plural_name": "Sectores",
        "main_collection": "actor-actor",
        "filter_collections": [
            "actor-actor",
        ],
        "category_type": "classify-sector_group",
        "category_subtype": "classify-sector",
    },
    {
        "key_name": "interest_types",
        "name": "Tipo de interés",
        "plural_name": "Tipos de interés",
        "main_collection": "actor-interest",
        "filter_collections": [
            "actor-interest",
            "actor-actor",
        ],
        "category_group": "classify-interest_group",
        "category_type": "classify-interest_type",
        "category_subtype": "classify-interest_subtype",
        "addl_config": {
            "short_prev": "Int.",
            "prev": "Interés",
        },
    },
    {
        "key_name": "event_types",
        "name": "Clasificación de Evento",
        "plural_name": "Clasificaciones de Eventos",
        "main_collection": "event-event",
        "filter_collections": [
            "event-event",
        ],
        "category_group": "event-event_group",
        "category_type": "event-event_type",
        "category_subtype": "event-event_subtype",
        "addl_config": {
            "short_prev": "Ev.",
            "prev": "Evento",
        },
    },
    {
        "key_name": "involved_roles",
        "name": "Rol en Actividad",
        "plural_name": "Roles en Actividades",
        "main_collection": "event-event",
        "filter_collections": [
            "event-event",
        ],
        "category_subtype": "event-involved_role",
    },
    {
        "key_name": "impact_types",
        "name": "Clasificación de Afectación",
        "plural_name": "Clasificaciones de Afectación",
        "main_collection": "impact-impact",
        "filter_collections": [
            "impact-impact",
        ],
        "category_group": "impact-impact_group",
        "category_type": "impact-impact_type",
        "category_subtype": "impact-impact_subtype",
        "addl_config": {
            "short_prev": "Af.",
            "prev": "Afectación",
        },
    },
    {
        "key_name": "states",
        "name": "Estado",
        "plural_name": "Estados",
        "main_collection": "space_time-location",
        "category_subtype": "space_time-state",
    },
    {
        "key_name": "geographicals",
        "name": "Geográficos",
        "plural_name": "Geográficos",
        "main_collection": "space_time-location",
        "filter_collections": [
            "space_time-location",
        ],
        "category_group": "space_time-state",
        "category_type": "space_time-municipality",
        "category_subtype": "space_time-locality",
    },
    {
        "key_name": "status_projects",
        "name": "Status de Proyecto",
        "plural_name": "Status de Proyectos",
        "main_collection": "project-project",
        "filter_collections": [
            "project-project",
        ],
        "category_subtype": "project-status_project",
    },
    {
        "key_name": "countries",
        "name": "País",
        "plural_name": "Paises",
        "main_collection": "actor-actor",
        "filter_collections": [
            "actor-actor",
        ],
        "category_subtype": "classify-country",
    }
]

collection_links = [
    {
        "parent": "source-source",
        "child": "source-note",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "source-note",
        "child": "source-mention",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "project-project",
        "child": "source-mention",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "source-mention",
        "child": "source-status_history",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "project-status_project",
        "child": "source-status_history",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "project-extractivism_type",
        "child": "project-megaproject_type",
        "link_type": "grouper",
        "filter_group": "project_types",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "project-megaproject_type",
        "child": "project-project",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "project-conflict",
        "child": "project-project",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": False,
    },
    {
        "parent": "project-status_project",
        "child": "project-project",
        "link_type": "category",
        "is_mandatory": False,
    },
    # {
    #     "parent": "project-status_location",
    #     "child": "project-project",
    #     "link_type": "category",
    # },
    {
        "parent": "classify-participant_group",
        "child": "classify-participant_type",
        "link_type": "grouper",
        "filter_group": "participant_types",
        "is_mandatory": True,
    },
    {
        "parent": "classify-sector_group",
        "child": "classify-sector",
        "link_type": "grouper",
        "filter_group": "sectors",
        "is_mandatory": True,
    },
    {
        "parent": "classify-interest_group",
        "child": "classify-interest_type",
        "link_type": "grouper",
        "filter_group": "interest_types",
        "is_mandatory": True,
    },
    {
        "parent": "classify-interest_type",
        "child": "classify-interest_subtype",
        "link_type": "grouper",
        "filter_group": "interest_types",
        "is_mandatory": True,
    },
    {
        "parent": "classify-sector",
        "child": "actor-actor",
        "link_type": "category",
        "is_mandatory": False,
    },
    {
        "parent": "classify-belong",
        "child": "actor-actor",
        "link_type": "category",
        "is_multiple": True,
        "is_mandatory": False,
    },
    {
        "parent": "classify-indigenous_group",
        "child": "actor-actor",
        "link_type": "category",
        "is_mandatory": False,
    },
    {
        "parent": "classify-country",
        "child": "actor-actor",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": False,
    },
    {
        "parent": "classify-participant_type",
        "child": "actor-participant",
        "link_type": "category",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "source-mention",
        "child": "actor-participant",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "actor-actor",
        "child": "actor-participant",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "classify-interest_subtype",
        "child": "actor-interest",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "actor-participant",
        "child": "actor-interest",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "event-event_group",
        "child": "event-event_type",
        "link_type": "grouper",
        "filter_group": "event_types",
        "is_mandatory": True,
    },
    {
        "parent": "event-event_type",
        "child": "event-event_subtype",
        "link_type": "grouper",
        "filter_group": "event_types",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "event-event_type",
        "child": "event-event",
        "link_type": "category",
        "is_provisional": True,
        "is_mandatory": False,
    },
    {
        "parent": "event-event_subtype",
        "child": "event-event",
        "link_type": "category",
        "is_provisional": False,
    },
    {
        "parent": "source-mention",
        "child": "event-event",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "event-event",
        "child": "event-involved",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "event-involved_role",
        "child": "event-involved",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "actor-participant",
        "child": "event-involved",
        "link_type": "relational",
        "is_mandatory": True,
    },
    {
        "parent": "impact-impact_group",
        "child": "impact-impact_type",
        "link_type": "grouper",
        "filter_group": "impact_types",
        "is_mandatory": True,
    },
    {
        "parent": "impact-impact_type",
        "child": "impact-impact_subtype",
        "link_type": "grouper",
        "filter_group": "impact_types",
        "is_mandatory": True,
    },
    {
        "parent": "impact-impact_type",
        "child": "impact-impact",
        "link_type": "category",
        "is_mandatory": True,
    },
    {
        "parent": "impact-impact_subtype",
        "child": "impact-impact",
        "link_type": "category",
        "is_mandatory": False,
    },
    {
        "parent": "source-mention",
        "child": "impact-impact",
        "link_type": "relational",
        "is_multiple": True,
        "is_mandatory": True,
    },
    {
        "parent": "space_time-state",
        "child": "space_time-municipality",
        "link_type": "grouper",
        "filter_group": "geographicals",
        "is_mandatory": True,
    },
    {
        "parent": "space_time-municipality",
        "child": "space_time-locality",
        "link_type": "grouper",
        "filter_group": "geographicals",
        "is_mandatory": True,
    },
]