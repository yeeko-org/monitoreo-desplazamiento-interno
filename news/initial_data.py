from news.models import Cluster


class InitClusters:

    def __init__(self):
        init_clusters = [
            ('main', 'Principales',
             'Las palabras o frases que por sí mismas son suficientes'),
            ('complementary', 'Complementarios',
                'Las palabras o frases que acompañan a las principales'),
            ('negative', 'Negativos',
             'Su existencia descarta la noticia'),
        ]
        order = 1
        for key_name, name, description in init_clusters:
            cluster, _ = Cluster.objects.get_or_create(name=name)
            cluster.description = description
            cluster.order = order
            cluster.save()
            order += 1
