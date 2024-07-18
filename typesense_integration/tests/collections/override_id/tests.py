from __future__ import annotations

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import Book
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class OverrideIdTests(TypesenseCollectionTestCase):
    """Test for overriding the default id field."""

    def test_override_id_field(self) -> None:
        """Test that it can override the default id field."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            override_id=True,
        )
        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('id'),
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(collection.parents, {Book._meta.get_field('author')})
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )

    def test_ignore_override_when_explicit_id(self) -> None:
        """Test that it ignores the override if id is explicitly set."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            override_id=True,
            index_fields={Book._meta.get_field('title')},
        )
        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
            },
        )
        self.assertEqual(collection.parents, set())
        self.assertEqual(
            collection.children,
            set(),
        )
