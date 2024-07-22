from __future__ import annotations

from typesense import exceptions as typesense_exceptions

from typesense_integration.models import TypesenseCollection
from typesense_integration.tests.collections.models import Book
from typesense_integration.tests.collections.tests import TypesenseCollectionTestCase


class FacetTests(TypesenseCollectionTestCase):
    """Tests for facets."""

    def test_all_facets(self) -> None:
        """Test that it can handle all facets."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            facets=True,
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
            collection.facets,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'title',
                    'type': 'string',
                    'facet': True,
                    'sort': False,
                    'locale': '',
                    'infix': False,
                    'stem': False,
                    'optional': False,
                    'index': True,
                },
                {
                    'name': 'published_date',
                    'type': 'int64',
                    'facet': True,
                    'sort': True,
                    'locale': '',
                    'infix': False,
                    'stem': False,
                    'optional': False,
                    'index': True,
                },
            ],
        )

    def test_some_facets(self) -> None:
        """Test that it can handle some facets."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            facets={
                Book._meta.get_field('title'),
            },
        )

        self.assertEqual(collection.name, 'book')
        self.assertEqual(
            collection.facets,
            {
                Book._meta.get_field('title'),
            },
        )
        self.assertEqual(
            collection.index_fields,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
            },
        )
        self.assertEqual(
            collection.typesense_fields,
            [
                {
                    'name': 'title',
                    'type': 'string',
                    'facet': True,
                    'sort': False,
                    'locale': '',
                    'infix': False,
                    'stem': False,
                    'optional': False,
                    'index': True,
                },
                {
                    'name': 'published_date',
                    'type': 'int64',
                    'facet': False,
                    'sort': True,
                    'locale': '',
                    'infix': False,
                    'stem': False,
                    'optional': False,
                    'index': True,
                },
            ],
        )

    def test_facets_with_joins(self) -> None:
        """Test that it can handle all facets with joins."""
        mock_client_instance = self.mock_client()

        collection = TypesenseCollection(
            client=mock_client_instance,
            model=Book,
            use_joins=True,
            facets=True,
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
            collection.facets,
            {
                Book._meta.get_field('title'),
                Book._meta.get_field('published_date'),
                Book._meta.get_field('author'),
            },
        )
        self.assertEqual(
            collection.typesense_relations,
            [
                {
                    'name': 'author_id',
                    'type': 'string',
                    'reference': 'author.id',
                    'facet': True,
                    'sort': False,
                    'locale': '',
                    'infix': False,
                    'stem': False,
                    'optional': False,
                    'index': True,
                },
            ],
        )

    def test_warns_facets_on_relation_with_no_joins(self) -> None:
        """Test that it warns if a facet field is a relation but there's no join."""
        mock_client_instance = self.mock_client()

        with self.assertWarns(UserWarning):
            collection = TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('title'),
                },
                parents={Book._meta.get_field('author')},
                facets={Book._meta.get_field('author'), Book._meta.get_field('title')},
            )

            self.assertEqual(collection.name, 'book')
            self.assertEqual(
                collection.parents,
                {
                    Book._meta.get_field('author'),
                },
            )
            self.assertEqual(
                collection.facets,
                {
                    Book._meta.get_field('author'),
                    Book._meta.get_field('title'),
                },
            )
            self.assertEqual(collection.typesense_relations, [])

    def test_raises_facets_not_a_subset(self) -> None:
        """Test that it raises if a facet is not a subset of `index_fields` or relations."""
        mock_client_instance = self.mock_client()

        with self.assertRaises(typesense_exceptions.RequestMalformed):
            TypesenseCollection(
                client=mock_client_instance,
                model=Book,
                index_fields={
                    Book._meta.get_field('title'),
                },
                facets={
                    Book._meta.get_field('author'),
                },
            )
