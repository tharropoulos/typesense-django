from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import Book
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class DetailedRelationTests(TypesenseCollectionTestCase):
    """Tests for detailed relations."""

    def test_all_detail_relations(self) -> None:
        """Test that it can handle all relations with detailed relations."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            detailed_parents=True,
            detailed_children=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
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
                    'name': 'author',
                    'type': 'object',
                    'index': True,
                    'facet': False,
                },
                {
                    'name': 'chapter',
                    'type': 'object[]',
                    'index': True,
                    'facet': False,
                },
            ],
        )

    def test_detailed_relations_with_joins(self) -> None:
        """Test that it can handle all relations with detailed references and joins."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            detailed_parents=True,
            detailed_children=True,
            use_joins=True,
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
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
                    'type': 'string',
                    'reference': 'author.id',
                    'index': True,
                    'facet': False,
                },
                {'name': 'author', 'type': 'object', 'index': True, 'facet': False},
                {
                    'name': 'chapter',
                    'type': 'object[]',
                    'index': True,
                    'facet': False,
                },
            ],
        )

    def test_some_detail_relations(self) -> None:
        """Test that it can handle some relations with detailed references."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            detailed_parents={
                Book._meta.get_field('author'),
            },
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
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
                    'name': 'author',
                    'type': 'object',
                    'index': True,
                    'facet': False,
                },
            ],
        )

    def test_raises_detail_relation_not_a_subset(self) -> None:
        """Test that it raises if detailed relation is not a subset of relations."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                detailed_parents={
                    Book._meta.get_field('chapter'),  # type: ignore[arg-type]
                },
            )

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                detailed_children={
                    Book._meta.get_field('author'),  # type: ignore[arg-type]
                },
            )
