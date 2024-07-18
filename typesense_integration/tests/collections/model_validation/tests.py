from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import Author, VerboseName, Wrong
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class ModelValidationTests(TypesenseCollectionTestCase):
    """Tests for model validation."""

    def test_missing_args(self) -> None:
        """Test that it raises an exception when missing required args."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(KeyError):
            TypesenseCollection(client=mock_client_instance)  # type: ignore[call-arg]

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(model=Author)  # type: ignore[call-arg]

    def test_malformed_args(self) -> None:
        """Test that it raises an exception when args are malformed."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(client=mock_client_instance, model=Wrong)  # type: ignore[arg-type]

        with self.assertRaises(typesense_exceptions.ConfigError):
            TypesenseCollection(client=Wrong, model=Author)

    def test_verbose_model_name(self) -> None:
        """Test that it can handle verbose model names."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=VerboseName,
        )

        self.assertEqual(collection.name, 'custom_name')
