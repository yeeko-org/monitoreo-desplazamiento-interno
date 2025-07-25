def nombre_or_pk(obj, pk, attr='nombre'):
    name = getattr(obj, attr, None) or pk
    return str(name)


def camel_to_snake(name):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
