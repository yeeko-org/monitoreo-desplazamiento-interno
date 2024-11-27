from news.models import Cluster


class InitClusters:

    def __init__(self):
        init_clusters = [
            ('main', 'Principales'),
            ('complementary', 'Complementarios'),
            ('negative', 'Negativos'),
        ]

        for name, public_name in init_clusters:
            Cluster.objects.get_or_create(
                name=name,
                public_name=public_name
            )
