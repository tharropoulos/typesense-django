from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import Book, Reference
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class DefaultSortingFieldTests(TypesenseCollectionTestCase):
    """Tests for the Default Sorting Field."""

    def test_default_sorting_field(self) -> None:
        """Test that it can handle default sorting fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Reference,
            default_sorting_field=Reference._meta.get_field('number'),
        )

        self.assertEqual(
            collection.default_sorting_field,
            Reference._meta.get_field('number'),
        )

    def test_raises_default_sorting_field_not_number(self) -> None:
        """Test that it raises if default sorting field is not a number."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                default_sorting_field=Book._meta.get_field('title'),  # type: ignore[arg-type]
            )

    def test_raises_default_sorting_field_not_in_index_fields(self) -> None:
        """Test that it raises if default sorting field is not in indexed fields."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Reference,
            skip_index_fields={Reference._meta.get_field('number')},
            default_sorting_field=Reference._meta.get_field('number'),
        )

        self.assertEqual(
            collection.default_sorting_field,
            Reference._meta.get_field('number'),
        )

        self.assertEqual(
            collection.skip_index_fields,
            {Reference._meta.get_field('number')},
        )

        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'number',
                    'type': 'int32',
                    'facet': False,
                    'index': False,
                },
            ],
        )

    def test_raises_default_sorting_field_not_in_model(self) -> None:
        """Test that it raises if default sorting field is not in model."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                default_sorting_field=Reference._meta.get_field('number'),
            )

    def test_warns_default_sorting_field_not_in_model(self) -> None:
        """Test that it warns if a default sorting field is not in the model, but is indexed."""
        mock_client_instance = self.mock_client()

        with self.assertWarns(UserWarning):
            collection = TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={Reference._meta.get_field('number')},
                default_sorting_field=Reference._meta.get_field('number'),
            )

            self.assertEqual(
                collection.default_sorting_field,
                Reference._meta.get_field('number'),
            )
