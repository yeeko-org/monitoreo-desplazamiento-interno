from ps_schema.models import Level, Collection, CollectionLink, FilterGroup
from ps_schema.constants import all_collections, filter_groups


class InitLevels:

    def __init__(self):
        init_levels = (
            ('primary', 'Colección principal', '0'),
            ('secondary', 'Colección secundaria', '1'),
            ('relational', 'Colección relacional', '2'),
            ('category_group', 'Grupo de categorías', '3'),
            ('category_type', 'Tipo de categoría', '4'),
            ('category_subtype', 'Subtipo de categoría', '5'),
        )
        for key_name, name, order in init_levels:
            Level.objects.get_or_create(
                key_name=key_name,
                defaults=dict(
                    name=name,
                    order=order
                )
            )


def field_of_models(collection: Collection):
    from django.apps import apps
    from utils.obj_str import camel_to_snake
    from django.db.models import CharField, TextField, IntegerField
    app_name = collection.app_label
    if not app_name:
        raise Exception("app_name is required")
    model_name = collection.model_name
    my_model = apps.get_model(app_name, model_name)
    all_fields = my_model._meta.get_fields(
        include_parents=False, include_hidden=False)
    new_fields = []
    for field in all_fields:
        relation_type = "simple"
        is_primary_key = False
        if field.one_to_many:
            relation_type = "one_to_many"
        elif field.is_relation:
            if field.many_to_many:
                relation_type = "many_to_many"
            elif field.one_to_one:
                relation_type = "one_to_one"
            else:
                # many_to_one
                relation_type = "relation"
        else:
            is_primary_key = field.primary_key

        complement = "_id" if field.is_relation else ""
        # field_name = f"{field.name}{complement}"
        # is_string = isinstance(field, TextField) or is_char
        field_type = "unknown"
        width = 100
        is_string, is_char = False, False
        if isinstance(field, TextField):
            field_type = "text"
            width = 200
            is_string = True
        if isinstance(field, CharField):
            field_type = "char"
            width = 150
            is_string = True
            is_char = True
        if isinstance(field, IntegerField):
            field_type = "integer"
            width = 80

        final_field = {
            "name": field.name,
            "real_name": f"{field.name}{complement}",
            "primary_key": is_primary_key,
            "relation_type": relation_type,
            "field_type": field_type,
            "is_string": is_string,
            "is_massive": False,
            "is_editable": True,
            "width": width,
            "null": field.null,
        }
        try:
            final_field["verbose_name"] = field.verbose_name
        except AttributeError:
            pass
        try:
            if type(field.default) in [str, int, bool]:
                final_field["default"] = field.default
        except AttributeError:
            pass

        if is_char:
            final_field["max_length"] = field.max_length
        # set related_name if exists
        # final_field["is_primary_key"] = field.primary_key
        if field.is_relation:
            try:
                final_field["related_name"] = field.related_query_name()
            except TypeError:
                pass
            try:
                meta = field.related_model._meta
                camel_name = camel_to_snake(meta.object_name)
                final_field["related_snake_name"] = camel_name
                final_field["related_model"] = meta.object_name
                final_field["related_app_label"] = meta.app_label
            except AttributeError:
                pass
        new_fields.append(final_field)
    # sort_by_relation_type = sorted(
    #     fields, key=lambda x: x['relation_type'])
    return new_fields


class InitCollections:

    def __init__(self):
        from django.apps import apps
        levels_dict = {level.key_name: level for level in Level.objects.all()}
        # Collection.objects.all().delete()
        order_base = 0
        order = 0
        for app_label, collections in all_collections.items():
            for collection in collections:
                order += 1
                model_name = collection['model_name']
                new_collection, _ = Collection.objects.get_or_create(
                    snake_name=collection['snake_name'],
                    level=levels_dict[collection['level']],
                    app_label=app_label)
                my_model = apps.get_model(app_label, model_name)
                meta_data = my_model._meta
                verbose_name = meta_data.verbose_name
                verbose_name_plural = meta_data.verbose_name_plural
                name = collection.get('name', verbose_name)
                plural_name = collection.get('plural_name', verbose_name_plural)
                # if (name != verbose_name):
                #     print(f"Name: {name} - Verbose: {verbose_name}")
                # if (plural_name != verbose_name_plural):
                #     print(f"Plural: {plural_name} - Verbose: {verbose_name_plural}")
                new_collection.name = name
                new_collection.plural_name = plural_name
                new_collection.model_name = model_name
                new_collection.optional_category = collection.get(
                    'optional_category', False)
                new_collection.icon = collection.get('icon', None)
                new_collection.color = collection.get('color', None)
                new_collection.open_insertion = collection.get(
                    'open_insertion', None)
                new_collection.available_actions = collection.get(
                    'available_actions', [])
                new_collection.order = order_base + order
                new_collection.xls_export = collection.get(
                    'xls_export', False)
                new_collection.all_filters = collection.get('all_filters', [])
                new_collection.save()
                # print(f"Order: {order_base + order}\n{defaults}")
            order_base += 10
        for collection in Collection.objects.all():
            collection.fields = field_of_models(collection)
            collection.save()


class InitFilterGroups:
    def __init__(self):
        # FilterGroup.objects.all().delete()
        # collections_dict = {
        #     f"{collection.app_label}-{collection.snake_name}": collection
        #     for collection in Collection.objects.all()}
        collections_dict = {}
        for collection in Collection.objects.all():
            collections_dict[collection.snake_name] = collection
            collections_dict[f"{collection.app_label}-{collection.snake_name}"] = collection

        print("collections_dict", collections_dict)
        for group in filter_groups:
            # category_group = group.get('category_group', None)
            # print("category_group", category_group)
            # print("collection_group", collections_dict.get(category_group, None))
            filter_group, _ = FilterGroup.objects.get_or_create(
                key_name=group['key_name'],
                defaults=dict(
                    main_collection=collections_dict.get(
                        group['main_collection'], None),
                )
            )
            filter_group.name = group.get('name', "Sin nombre")
            filter_group.plural_name = group.get('plural_name', "Sin nombre plural")
            # filter_group.main_collection = collections_dict.get(
            #     group['main_collection'], None)
            filter_group.category_group = collections_dict.get(
                group.get('category_group', None), None)
            filter_group.category_type = collections_dict.get(
                group.get('category_type', None), None)
            filter_group.category_subtype = collections_dict.get(
                group.get('category_subtype', None), None)
            filter_group.addl_config = group.get('addl_config', {})
            filter_group.save()
            # print("-" * 50)
