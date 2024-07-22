from django.apps import AppConfig


class TypesenseConfig(AppConfig):
    """App Config for the Django Typesense Integration package."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'typesense'
