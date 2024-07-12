from django.db import models
from typesense import Client

class TypesenseCollection:
    """Class for mapping a Django model to a Typesense collection."""

    def __init__(
        self,
        *,
        client: Client,
        model: models.Model,
    ) -> None:
        """
        Initializes a new instance of TypesenseCollection.

        :param client: An instance of Client to interact with the Typesense API.
        :param model: The Django model that this instance is associated with.
        """
        self.model = model
        self.client = client
        self._validate_client_and_model()

    def _validate_client_and_model(self):
        if not isinstance(self.client, Client):
            raise typesense_exceptions.ConfigError(
                'Client must be an instance of Typesense Client.',
            )
        if not issubclass(self.model, models.Model):
            raise typesense_exceptions.ConfigError(
                'Model must be an instance of the default models.Model class.',
            )

