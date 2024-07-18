from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import (
    Book,
    CompositeForeignKey,
    JoinOnAnotherField,
)
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class JoinsTests(TypesenseCollectionTestCase):
    """Tests for JOINs."""

    def test_joins(self) -> None:
        """Test that it can handle multiple joins."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            index_fields={
                Book._meta.get_field('title'),
            },
            parents={Book._meta.get_field('author')},
            children={Book._meta.get_field('chapter')},
            use_joins=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
            },
        )
        self.assertEqual(
            collection.parents,
            {
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.children,
            {
                Book._meta.get_field('chapter'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'author_id',
                    'reference': 'author.id',
                    'type': 'string',
                    'facet': False,
                    'index': True,
                },
            ],
        )

    def test_joins_other_than_id(self) -> None:
        """Test that it can handle joins on fields other than id."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=JoinOnAnotherField,
            use_joins=True,
        )

        self.assertEqual(collection.name, 'join_on_another_field')
        self.assertEqual(
            collection.index_fields,
            set(),
        )
        self.assertEqual(
            collection.parents,
            {
                JoinOnAnotherField._meta.get_field('reference'),
            },
        )

        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'facet': False,
                    'index': True,
                    'name': 'reference_number',
                    'reference': 'reference.number',
                    'type': 'int32',
                },
            ],
        )

    def test_joins_composite_key(self) -> None:
        """Test that it can handle composite keys in joins."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=CompositeForeignKey,
                parents={CompositeForeignKey._meta.get_field('reference')},  # type: ignore[arg-type]
                use_joins=True,
            )
