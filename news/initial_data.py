from news.models import Cluster


class InitClusters:

    def __init__(self):
        init_clusters = [
            ('main', 'Principales'),
            ('complementary', 'Complementarios'),
            ('negative', 'Negativos'),
        ]

        for key_name, name in init_clusters:
            Cluster.objects.get_or_create(
                key_name=key_name, name=name)
