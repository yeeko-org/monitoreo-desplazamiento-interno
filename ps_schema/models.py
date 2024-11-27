from django.db import models


class Level(models.Model):
    key_name = models.CharField(
        max_length=225, verbose_name="Nombre", primary_key=True)
    name = models.CharField(
        max_length=225, verbose_name="Nombre público")
    order = models.SmallIntegerField(
        default=5, verbose_name="Orden de aparición")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Nivel de Colección"
        verbose_name_plural = "1.3 Niveles de Colección"
        ordering = ['order', 'name']


something = [{"key_name": "primary"}, "secondary", "relational"]


class Collection(models.Model):

    GROUP_CHOICES = [
        ("register", "Registro"),
        ("validation", "Validación"),
        ('location', 'Ubicación'),
    ]

    snake_name = models.CharField(
        max_length=225, primary_key=True)
    name = models.CharField(
        max_length=225, verbose_name="verbose_name_plural",
        help_text="Nombre del Modelo público (Meta.verbose_name_plural)")
    plural_name = models.CharField(
        max_length=225, verbose_name="Nombre plural")
    model_name = models.CharField(
        max_length=225,
        verbose_name="Nombre en Django",
        help_text="Nombre del modelo en Django (Meta.model_name)")
    app_label = models.CharField(
        max_length=40, verbose_name="App label", default="null")
    level = models.ForeignKey(
        Level, on_delete=models.CASCADE, verbose_name="Nivel")
    order = models.SmallIntegerField(
        default=5, verbose_name="Orden")
    icon = models.CharField(
        max_length=225, blank=True, null=True, verbose_name="Ícono")
    color = models.CharField(
        max_length=225, blank=True, null=True, verbose_name="Color")
    help_text = models.TextField(
        blank=True, null=True, verbose_name="Texto de ayuda")
    fields = models.JSONField(default=list, verbose_name="Campos")
    sort_fields = models.JSONField(
        default=list, verbose_name="Campos de ordenamiento")

    optional_category = models.BooleanField(
        default=False, verbose_name="Colección opcional")
    # status_group = models.CharField(
    #     max_length=20, choices=GROUP_CHOICES, blank=True, null=True)
    status_groups = models.JSONField(blank=True, null=True)
    all_filters = models.JSONField(
        default=list, verbose_name="Grupos de filtros")

    open_insertion = models.BooleanField(blank=True, null=True)
    description = models.TextField(
        blank=True, null=True)
    cat_params = models.JSONField(
        default=dict, verbose_name="Parámetros para el catálogo")

    @property
    def parent_list(self):
        # build HTML list of filter_collections for admin
        return ', '.join([f"{c.parent.app_label}-{c.parent.model_name}"
                          for c in self.parent_links.all()])

    def get_massive_fields(self):
        return [f for f in self.fields if f.get('is_massive', False)]

    # def save(self, *args, **kwargs):
    #     from utils.obj_str import camel_to_snake
    #     self.snake_name = camel_to_snake(self.model_name)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.app_label}-{self.model_name}"

    class Meta:
        verbose_name = "Modelo (Colección)"
        verbose_name_plural = "1.1 Modelos (Colecciones)"
        ordering = ['order']


class FilterGroup(models.Model):
    key_name = models.CharField(
        max_length=90, primary_key=True, verbose_name="Nombre")
    name = models.CharField(
        max_length=225, verbose_name="Nombre público")
    plural_name = models.CharField(
        max_length=225, verbose_name="Nombre plural")
    description = models.TextField(
        blank=True, null=True, verbose_name="Descripción")
    order = models.SmallIntegerField(
        default=5, verbose_name="Orden de aparición")
    main_collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE,
        verbose_name="Colección principal",
        related_name='filters')
    # filter_collections = models.ManyToManyField(
    #     Collection, blank=True, verbose_name="Filtros de la colección")

    category_group = models.ForeignKey(
        Collection, on_delete=models.CASCADE, blank=True, null=True,
        related_name='filter_groups')
    category_type = models.ForeignKey(
        Collection, on_delete=models.CASCADE, blank=True, null=True,
        related_name='filter_types')
    category_subtype = models.ForeignKey(
        Collection, on_delete=models.CASCADE, blank=True, null=True,
        related_name='filter_subtypes')
    addl_config = models.JSONField(
        default=dict, verbose_name="Configuración adicional")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grupo de Filtros"
        verbose_name_plural = "1.2 Grupos de Filtros"
        ordering = ['order', 'name']


class CollectionLink(models.Model):
    LINK_TYPES = (
        ('category', 'Categoría'),
        ('grouper', 'Agrupador'),
        ('relational', 'Relacional'),
    )

    parent = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name='child_links')
    child = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name='parent_links')
    link_type = models.CharField(
        max_length=20, choices=LINK_TYPES, default='category')
    is_multiple = models.BooleanField(default=False)
    is_provisional = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    filter_group = models.ForeignKey(
        FilterGroup, on_delete=models.CASCADE, blank=True, null=True,
        related_name='links')

    def __str__(self):
        return f"{self.parent} - {self.child}"

    class Meta:
        verbose_name = "Enlace de Colección"
        verbose_name_plural = "1.4 Enlaces de Colecciones"



